# %% [markdown]
# ---
# title: 3D mesh tallies
# ---

# %% [markdown]
# Mesh tallies can also be used to visualise neutron interactions spatially throughout a geometry in 3D.
#
# This task allows users to create a simple geometry from a few different materials and plot the results of a 3D regular mesh tally applied to the geometry.

# %% [markdown]
# This first code block defines the model geometry, materials and neutron source.

# %% [markdown]
# First import OpenMC and configure the nuclear data path

# %%
import openmc
from pathlib import Path

import pyvista as pv
import numpy as np

# Setting the cross section path to the correct location in the docker image.
# If you are running this outside the docker image you will have to change this path to your local cross section path.
openmc.config['cross_sections'] = Path.home() / 'nuclear_data' / 'cross_sections.xml'

# %%
# MATERIALS

breeder_material = openmc.Material()   # Pb84.2Li15.8
breeder_material.add_element('Pb', 84.2, percent_type='ao')
breeder_material.add_element('Li', 15.8, percent_type='ao', enrichment=7.0, enrichment_target='Li6', enrichment_type='ao')   # natural enrichment = 7% Li6
breeder_material.set_density('atom/b-cm', 3.2720171e-2)   # around 11 g/cm3

copper_material = openmc.Material()
copper_material.set_density('g/cm3', 8.5)
copper_material.add_element('Cu', 1.0)

eurofer_material = openmc.Material()
eurofer_material.set_density('g/cm3', 7.75)
eurofer_material.add_element('Fe', 89.067, percent_type='wo')

my_materials = openmc.Materials([breeder_material, eurofer_material, copper_material])


# GEOMETRY

# surfaces
central_sol_surface = openmc.ZCylinder(r=100)
central_shield_outer_surface = openmc.ZCylinder(r=110)
vessel_inner_surface = openmc.Sphere(r=500)
first_wall_outer_surface = openmc.Sphere(r=510)
breeder_blanket_outer_surface = openmc.Sphere(r=610, boundary_type='vacuum')

# cells
central_sol_region = -central_sol_surface & -breeder_blanket_outer_surface
central_sol_cell = openmc.Cell(region=central_sol_region)
central_sol_cell.fill = copper_material

central_shield_region = +central_sol_surface & -central_shield_outer_surface & -breeder_blanket_outer_surface
central_shield_cell = openmc.Cell(region=central_shield_region)
central_shield_cell.fill = eurofer_material

inner_vessel_region = -vessel_inner_surface & +central_shield_outer_surface
inner_vessel_cell = openmc.Cell(region=inner_vessel_region)
# no material set as default is vacuum

first_wall_region = -first_wall_outer_surface & +vessel_inner_surface
first_wall_cell = openmc.Cell(region=first_wall_region)
first_wall_cell.fill = eurofer_material

breeder_blanket_region = +first_wall_outer_surface & -breeder_blanket_outer_surface & +central_shield_outer_surface
breeder_blanket_cell = openmc.Cell(region=breeder_blanket_region)
breeder_blanket_cell.fill = breeder_material

my_geometry = openmc.Geometry([central_sol_cell, central_shield_cell, inner_vessel_cell, first_wall_cell, breeder_blanket_cell])

# %% [markdown]
# Making simulation settings and a cylindrical source

# %%
# Instantiate a Settings object
my_settings = openmc.Settings()
batches = 10
my_settings.batches = batches
my_settings.particles = 5000
my_settings.run_mode = 'fixed source'

# the distribution of radius is just a single value
radius = openmc.stats.Discrete([300], [1])

# the distribution of source z values is just a single value
z_values = openmc.stats.Discrete([0], [1])

# the distribution of source azimuthal angles values is a uniform distribution between 0 and 2 Pi
angle = openmc.stats.Uniform(a=0., b=2* 3.14159265359)

# Create a DT ring source
source = openmc.IndependentSource(
    space=openmc.stats.CylindricalIndependent(r=radius, phi=angle, z=z_values, origin=(0.0, 0.0, 0.0)),
    angle=openmc.stats.Isotropic(),
    energy=openmc.stats.muir(e0=14080000.0, m_rat=5.0, kt=20000.0)
)


my_settings.source = source

# %% [markdown]
# This code block creates a 3D regular mesh between two coordinates with a specified resolution in each axis.

# %%
# Create mesh which will be used for tally
mesh = openmc.RegularMesh().from_domain(
    my_geometry, # the corners of the mesh are being set automatically to surround the geometry
    dimension=10000 # 10000 voxels evenly distributed in each axis direction to create cube voxels
)

# %% [markdown]
# This code block creates two tallies on the mesh to record heating and tritium production.

# %%
my_tallies = openmc.Tallies()
# Create mesh filter for tally
mesh_filter = openmc.MeshFilter(mesh)

# Create flux mesh tally to score flux
mesh_tally_1 = openmc.Tally(name='tbr_on_mesh')
mesh_tally_1.filters = [mesh_filter]
mesh_tally_1.scores = ['(n,Xt)']  # where X is a wildcard
my_tallies.append(mesh_tally_1)

# Create flux mesh tally to score flux
mesh_tally_2 = openmc.Tally(name='heating_on_mesh')
mesh_tally_2.filters = [mesh_filter]
mesh_tally_2.scores = ['heating']
my_tallies.append(mesh_tally_2)

# %% [markdown]
# Now we make the model and plot the geometry with 100 samples of the neutron source shown as X points

# %%
model = openmc.Model(my_geometry, my_materials, my_settings, my_tallies)

model.plot(n_samples=100, pixels=400000, basis='xy', color_by='material')

# plane tolerance used as no points will be perfectly on the axis so this provides a tolerance for the plane
model.plot(n_samples=100, plane_tolerance=50, pixels=400000, basis='yz', color_by='material')

# %% [markdown]
# This next code block runs the simulation.

# %%
# deletes old statepoint and summary files
for f in Path('.').glob('s*.h5'):
    f.unlink(missing_ok=True)

# Run OpenMC!
sp_filename = model.run()

# %% [markdown]
# This code block runs a python function which extracts the mesh tally data from the statepoint.h5 file and saves it as a vtk file.

# %%
# loads up the output file from the simulation
with openmc.StatePoint(sp_filename) as statepoint:

    # extracts the mesh tally by name
    my_tbr_tally = statepoint.get_tally(name='tbr_on_mesh')

    # converts the tally result into a VTK file
    mesh.write_data_to_vtk(
        filename="tbr_tally_on_reg_mesh.vtk",
        datasets={"mean": my_tbr_tally.mean}  # the first "mean" is the name of the data set label inside the vtk file
    )

    # extracts the mesh tally by name
    my_heating_tally = statepoint.get_tally(name='heating_on_mesh')

    # converts the tally result into a VTK file
    # this time standard deviation error on the tally is added to the vtk file as another data set
    # the tally is also scaled from eV per source particle to Joules per source particle 1eV = 1.60218e-19J)
    # Try adding another scaling term to multiplying by the number of neutrons emitted per second would which would convert the units to Watts
    mesh.write_data_to_vtk(
        filename="heating_tally_on_reg_mesh.vtk",
        datasets={"mean": my_heating_tally.mean * 1.60218e-19, "std_dev": my_heating_tally.std_dev * 1.60218e-19}
    )

# %% [markdown]
# Now we will make a simple plot of the geometry with pyvista.

# %%
pv.set_jupyter_backend('html')
mesh = pv.read('heating_tally_on_reg_mesh.vtk')
mesh.set_active_scalars(name='mean')

# get the positive values from the mesh to avoid log10 of zero or negative numbers
positive_values = mesh['mean'][mesh['mean'] > 0]

log_mean = np.log10(np.clip(mesh['mean'], a_min=positive_values.min(), a_max=None))
mesh['log_mean'] = log_mean

# cut the mesh in half along the y-axis and hide the back half
clipped = mesh.clip(normal='y')

# threshold the mesh to only show values above a certain percentage of the maximum value
clipped_and_thresholded = clipped.threshold_percent(0.001)

# set the the color scale to be logarithmic
clipped_and_thresholded.set_active_scalars('log_mean')

clipped_and_thresholded.plot()

# %% [markdown]
# If you are running this in Docker you can click on the newly created vtk file in the file explorer to the left and download the vtk files onto your base computer and open them with a VTK file reader such as Paraview or Visit.
#
# Paraview or Visit can also be used to view the geometry file
#
# Paraview can be downloaded here: https://www.paraview.org/download/.
#
# Visit can be downloaded here: https://wci.llnl.gov/simulation/computer-codes/visit/downloads.

# %% [markdown]
# **Learning Outcomes for Part 2:**
#
# - Mesh tallies can be used in neutronics simulations to measure a variety of different reactions such as neutron absorption, tritium production and flux.
# - How neutrons are dissipated around the reactor.
#
# Now try replacing the regular mesh used for the tally filter with a Spherical mesh and see if the first wall heating is more accurately captured.
#
# ```python
# # SphericalMesh with 100 radial bins from r=0 to r=500 cm
# mesh = openmc.SphericalMesh(r_grid=np.linspace(0, 500, 100)).from_domain(
#     my_geometry, # the corners of the mesh are being set automatically to surround the geometry
#     dimension=[100, 100, 100] # 100 voxels in each axis direction (r, z, phi)
# )
# ```
