import openmc
import os
from spectrum_plotter import plot_spectrum_from_tally


# MATERIALS

# creates a single material
mats = openmc.Materials()
 
shielding_material = openmc.Material(name="breeder") 
shielding_material.add_nuclide('Fe56', 1, percent_type='ao')
shielding_material.set_density('g/cm3', 7)

mats = [shielding_material]


# GEOMETRY

# surfaces
sph1 = openmc.Sphere(r=250, boundary_type='vacuum')

# cells
shield_cell = openmc.Cell(region=-sph1)
shield_cell.fill = shielding_material

universe = openmc.Universe(cells=[shield_cell])

geom = openmc.Geometry(universe)


# creates a 14MeV neutron point source
source = openmc.Source()
source.space = openmc.stats.Point((0, 0, 0))
source.angle = openmc.stats.Isotropic()
source.energy = openmc.stats.Discrete([14e6], [1])
source.particles = 'neutron'

# SETTINGS

# Instantiate a Settings object
sett = openmc.Settings()
sett.batches = 100
sett.inactive = 0
sett.particles = 500
sett.source = source
sett.run_mode = 'fixed source'


#creates an empty tally object
tallies = openmc.Tallies()


# setup the filters for the surface tally
# detects neutrons (not photons)
neutron_particle_filter = openmc.ParticleFilter(['neutron'])
# detects when particles across the surface
front_surface_filter = openmc.SurfaceFilter(sph1)
energy_filter = openmc.EnergyFilter.from_group_structure('CCFE-709')


front_surface_spectra_tally = openmc.Tally(name='front_surface_spectra_tally')
front_surface_spectra_tally.scores = ['current']
front_surface_spectra_tally.filters = [front_surface_filter, neutron_particle_filter, energy_filter]
tallies.append(front_surface_spectra_tally)


# combines the geometry, materials, settings and tallies to create a neutronics model
model = openmc.model.Model(geom, mats, sett, tallies)

# deletes old files
try:
    os.remove('summary.h5')
    os.remove('statepoint.*.h5')
except OSError:
    pass


# runs the simulation without weight windows
output_filename = model.run()

# open the results file
results = openmc.StatePoint(output_filename)
my_analogy_tally = results.get_tally(name="front_surface_spectra_tally")



# Create mesh which will be used for the weight windows
my_ww_mesh = openmc.RegularMesh()

my_ww_mesh.dimension = [25, 25, 25]
my_ww_mesh.lower_left = [-120, -120, -120]  # physical limits (corners) of the mesh
my_ww_mesh.upper_right = [120, 120, 120]

# imports values for weight windows
from weight_window_values import upper_ww_bounds, lower_ww_bounds


# docs for ww are here
# https://docs.openmc.org/en/latest/_modules/openmc/weight_windows.html?highlight=weight%20windows
ww = openmc.WeightWindows(
    mesh=my_ww_mesh,
    upper_ww_bounds=upper_ww_bounds,
    lower_ww_bounds=lower_ww_bounds,
    particle_type='neutron',
    energy_bins=(0.0, 100_000_000.),  # applies this weight window to neutrons of within a large energy range (basically all neutrons in the simulation)
    survival_ratio=5
)
# sets the weight windows define to be used in the simulation
sett.weight_windows = ww

# deletes old files
try:
    os.remove('summary.h5')
except OSError:
    pass

# as each particle history is now longer due to the splitting that occurs with
# weight windows. Running the same number of batches would therefore take more
# time. To make a fair comparison the batch has been reduce to 20 as this takes
# a similar amount of time as 100 without weight windows
sett.batches=20

# combines the geometry, materials, settings and tallies to create a neutronics model
model = openmc.model.Model(geom, mats, sett, tallies)

# runs the simulation with weight windows
output_ww_filename = model.run()

# open the results file
ww_results = openmc.StatePoint(output_ww_filename)
my_weight_window_tally = ww_results.get_tally(name="front_surface_spectra_tally")


# this function plots the neutron spectrum and requires spectrum_plotter to be installed
# pip install spectrum_plotter
test_plot = plot_spectrum_from_tally(
    spectrum={"analogy": my_analogy_tally, 'my_weight_window_tally': my_weight_window_tally},
    x_label="Energy [MeV]",
    y_label="Current [n/source_particle]",
    x_scale="log",
    y_scale="log",
    title="example plot 1",
    required_units="neutron / source_particle",
    plotting_package="plotly",
    filename="example_spectra_from_tally_matplotlib.html",
)

# loads up the plot in a webbrowser
test_plot.show()
