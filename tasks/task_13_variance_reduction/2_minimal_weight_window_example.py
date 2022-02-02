import openmc
import matplotlib.pyplot as plt

# MATERIALS

# creates a single material
mats = openmc.Materials()
 
shielding_material = openmc.Material(name="breeder") 
shielding_material.add_nuclide('Fe56', 1, percent_type='ao')
shielding_material.set_density('g/cm3', 7)

mats = [shielding_material]



# GEOMETRY

# surfaces
sph1 = openmc.Sphere(r=200, boundary_type='vacuum')

# cells
shield_cell = openmc.Cell(region=-sph1)
shield_cell.fill = shielding_material

universe = openmc.Universe(cells=[shield_cell])

geom = openmc.Geometry(universe)

# Create mesh which will be used for tally and weight window
my_ww_mesh = openmc.RegularMesh()
mesh_height = 10  # number of mesh elements in the Y direction
mesh_width = 10  # number of mesh elements in the X direction
my_ww_mesh.dimension = [mesh_width, 1, mesh_height] # only 1 cell in the Y dimension
my_ww_mesh.lower_left = [-100, -100, -100]  # physical limits (corners) of the mesh
my_ww_mesh.upper_right = [100, 100, 100]




lower_ww_bounds=[]
upper_ww_bounds=[]
for mesh_element in range(1,  (mesh_height * mesh_width)+1):
    if mesh_element > (mesh_height * mesh_width) *0.5:
        lower_ww_bounds.append(0.001)
        upper_ww_bounds.append(0.7)
    else:
        lower_ww_bounds.append(-1)
        upper_ww_bounds.append(-1)


# docs on ww https://docs.openmc.org/en/latest/_modules/openmc/weight_windows.html?highlight=weight%20windows
ww = openmc.WeightWindows(
    mesh =my_ww_mesh,
    upper_ww_bounds=upper_ww_bounds,
    lower_ww_bounds=lower_ww_bounds,
    particle_type='neutron',
    energy_bins=(0.0, 100_000_000.0),  # applies this weight window to neutrons of within a large energy range (basically all neutrons in the simulation)
    survival_ratio=5
)


# creates a 14MeV point source
source = openmc.Source()
source.space = openmc.stats.Point((0, 0, 0))
source.angle = openmc.stats.Isotropic()
source.energy = openmc.stats.Discrete([14e6], [1])

# SETTINGS

# Instantiate a Settings object
sett = openmc.Settings()
sett.batches = 100
sett.inactive = 0
sett.particles = 500
sett.source = source
sett.run_mode = 'fixed source'
sett.weight_windows = ww




#creates an empty tally object
tallies = openmc.Tallies()


# sets up filters for the tallies
neutron_particle_filter = openmc.ParticleFilter(['neutron'])
energy_bins = openmc.mgxs.GROUP_STRUCTURES['CCFE-709']
energy_filter = openmc.EnergyFilter(energy_bins)

# setup the filters for the surface tally
front_surface_filter = openmc.SurfaceFilter(sph1)
# detects when particles across the surface

front_surface_spectra_tally = openmc.Tally(name='front_surface_spectra_tally')
front_surface_spectra_tally.scores = ['current']
front_surface_spectra_tally.filters = [front_surface_filter, neutron_particle_filter, energy_filter]
tallies.append(front_surface_spectra_tally)


# combines the geometry, materials, settings and tallies to create a neutronics model
model = openmc.model.Model(geom, mats, sett, tallies)

# plt.show(universe.plot(width=(180, 180), basis='xz'))

# # deletes old files
# !rm summary.h5
# !rm statepoint.*.h5

# runs the simulation
output_filename = model.run()

# open the results file
results = openmc.StatePoint(output_filename)
my_tally = results.get_tally(name="front_surface_spectra_tally")

from spectrum_plotter import plot_spectrum_from_tally

test_plot = plot_spectrum_from_tally(
    spectrum={"neutron spectra": my_tally},
    volume=1,
    x_label="Energy [MeV]",
    y_label="Flux [n/cm^2s]",
    x_scale="linear",
    y_scale="linear",
    title="example plot 1",
    filename="example_spectra_from_tally_matplotlib.png",
)