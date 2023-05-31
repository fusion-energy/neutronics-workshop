# This simulation a dose map and exports it as a vtk file and an image

import openmc
import matplotlib.pyplot as plt


mat = openmc.Material()
mat.add_element("Al", 1)
mat.set_density("g/cm3", 2.7)
my_materials = openmc.Materials([mat])

cylinder_surface = openmc.ZCylinder(r=10)
cylinder_upper_surface = openmc.ZPlane(z0=100)
cylinder_lower_surface = openmc.ZPlane(z0=0)

outer_surface = openmc.Sphere(r=200, boundary_type="vacuum")

cylinder_region = -cylinder_surface & -cylinder_upper_surface & +cylinder_lower_surface

# void region is below the outer surface and not the cylinder region
void_region = -outer_surface & ~cylinder_region

void_cell = openmc.Cell(region=void_region)
cylinder_cell = openmc.Cell(region=cylinder_region)
cylinder_cell.fill = mat

my_geometry = openmc.Geometry([cylinder_cell, void_cell])

# 14MeV point source
source = openmc.Source()
source.angle = openmc.stats.Isotropic()
source.energy = openmc.stats.Discrete([14e6], [1])
source.space = openmc.stats.Point((0.0, 50.0, 50.0))

# Instantiate a Settings object
my_settings = openmc.Settings()
# when running a mesh tally simulation you might want to tell openmc not to save
# the tallies.out file which is a ASCII file containing the tally results.
# for mesh tallies this can get very large and take a long time to write.
# the statepoint.h5 is smaller and quicker as it is a binary file
my_settings.output = {"tallies": False}
my_settings.batches = 2
my_settings.particles = 500000
my_settings.run_mode = "fixed source"
my_settings.source = source

# these are the dose coefficients coded into openmc
# originally from ICRP https://journals.sagepub.com/doi/10.1016/j.icrp.2011.10.001
energy_bins_n, dose_coeffs_n = openmc.data.dose_coefficients(
    particle="neutron",
    geometry="ISO",  # we are using the ISO direction as this is a dose field with dose
)
energy_function_filter_n = openmc.EnergyFunctionFilter(energy_bins_n, dose_coeffs_n)
energy_function_filter_n.interpolation = "cubic"  # cubic interpolation is recommended by ICRP

# just getting the dose for neutrons, not photons or other particles
neutron_particle_filter = openmc.ParticleFilter("neutron")

mesh = openmc.RegularMesh().from_domain(my_geometry, dimension=(30, 30, 30))
mesh_filter = openmc.MeshFilter(mesh)

# Create tally to score dose
dose_cell_tally = openmc.Tally(name="neutron_dose_on_mesh")
# note that the EnergyFunctionFilter is included as a filter
dose_cell_tally.filters = [
    mesh_filter,
    neutron_particle_filter,
    energy_function_filter_n,
]
dose_cell_tally.scores = ["flux"]
my_tallies = openmc.Tallies([dose_cell_tally])

model = openmc.Model(my_geometry, my_materials, my_settings, my_tallies)

statepoint_filename = model.run()

# makes use of a context manager "with" to automatically close the statepoint file
with openmc.StatePoint(statepoint_filename) as statepoint:
    my_mesh_tally_result = statepoint.get_tally(name="neutron_dose_on_mesh")

# tally.mean is in units of pSv-cm3/source neutron
# multiplication by neutrons_per_second changes units to neutron to pSv-cm3/second
neutrons_per_second = 1e8  # units of neutrons per second

# multiplication by pico_to_milli converts from (pico) pSv/second to (milli) mSv/second
pico_to_milli = 1e-9

# exports the mesh tally result to a vtk file with unit conversion
mesh.write_data_to_vtk(
    datasets={
        "Dose [milli Sv per second]": my_mesh_tally_result.mean.flatten()
        * neutrons_per_second
        * pico_to_milli,
    },
    volume_normalization=True,  # this converts from dose-cm3/second to dose/second
    filename="dose_on_mesh.vtk",
)

# this part of the script plots the images, so these imports are only needed to plot
import openmc_geometry_plot  # extends openmc.Geometry class with plotting functions
import regular_mesh_plotter  # extends openmc.Mesh class with plotting functions
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import numpy as np

# gets a 2d slice of data to later plot
data_slice = mesh.slice_of_data(dataset=my_mesh_tally_result.mean, view_direction="x")

data_slice = data_slice * neutrons_per_second * pico_to_milli

plot_1 = plt.imshow(
    data_slice,
    extent=mesh.bounding_box.extent['xy'],
    interpolation=None,
    norm=LogNorm(
        vmin=1e-12,  # trims out the lower section of the colors
        vmax=max(data_slice.flatten()),
    ),
)
cbar = plt.colorbar(plot_1)
cbar.set_label(f"Dose [milli Sv per second]")


# gets unique levels for outlines contour plot and for the color scale
material_ids = my_geometry.get_slice_of_material_ids(view_direction="x")
# gets unique levels for outlines contour plot and for the color scale
levels = np.unique([item for sublist in material_ids for item in sublist])

plt.contour(
    material_ids,
    origin="upper",
    colors="k",
    linestyles="solid",
    levels=levels,
    linewidths=2.0,
    extent=my_geometry.bounding_box.extent['xy'],
)
xlabel, ylabel = my_geometry.get_axis_labels(view_direction="x")
plt.xlabel(xlabel)
plt.ylabel(ylabel)
plt.title('Dose map showing some shielding of the source')


plt.show()
