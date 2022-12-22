# This example has a sphere of water showing how to increase the depth of
# neutron transport through the water. 
# First a simulation with now weight windows is shown
# Secondly a simulation with weight windows is show
# Finally a simulation with energy dependant weight windows is show
# The weight window value as a function of depth is also plotted to show some
# insight into the weight window values obtained.

import openmc
import numpy as np
import matplotlib.pyplot as plt


# materials
mat_water = openmc.Material()
mat_water.add_element('H', 1)
mat_water.add_element('O', 2)
mat_water.set_density('g/cm3', 1.)

my_materials = openmc.Materials([mat_water])

# surfaces
outer_surface = openmc.Sphere(r=500, boundary_type='vacuum')

# regions
region_1 = -outer_surface

# cells
cell_1 = openmc.Cell(region=region_1)
cell_1.fill = mat_water

# settings
my_settings = openmc.Settings()

my_geometry = openmc.Geometry([cell_1])

source = openmc.Source()
source.space = openmc.stats.Point((0.0, 0.0, 0.0))
source.angle = openmc.stats.Isotropic()
source.energy = openmc.stats.Discrete([14e6], [1.0])
source.particle = 'neutron'

my_settings = openmc.Settings()
my_settings.run_mode = 'fixed source'
my_settings.source = source
my_settings.particles = 10000
my_settings.batches = 10

# tally
mesh = openmc.SphericalMesh()
mesh.r_grid = np.linspace(0, 500, 100)

mesh_filter = openmc.MeshFilter(mesh)

flux_tally = openmc.Tally(name='flux tally')
flux_tally.filters = [mesh_filter]
flux_tally.scores = ['flux']

# adds the mesh tally to the model
my_tallies = openmc.Tallies()
my_tallies.append(flux_tally)

# model
model = openmc.model.Model(my_geometry, my_materials, my_settings, my_tallies)
output_file = model.run(cwd='no_ww')

import openmc_weight_window_generator
# post process
with openmc.StatePoint(output_file) as sp:
    flux_tally = sp.get_tally(id=flux_tally.id)
    # weight windows from flux
    weight_windows = sp.generate_wws(tally=flux_tally, rel_err_tol=0.7)[0]


# plot flux against distance
plt.plot(mesh.r_grid[1:], flux_tally.mean.flatten(), label='flux')
plt.yscale("log")
plt.xlabel("Radius [cm]")
plt.ylabel("Flux")
plt.show()


# plot weight window against distance
plt.plot(mesh.r_grid[1:], weight_windows.lower_ww_bounds.flatten(), label='lower_ww_bounds')
plt.plot(mesh.r_grid[1:], weight_windows.upper_ww_bounds.flatten(), label='lower_up_bounds')
plt.xlabel("Radius [cm]")
plt.ylabel("bound value")
plt.show()

model.settings.weight_windows = weight_windows
# model update

output_file = model.run(cwd='initial_ww')

with openmc.StatePoint(output_file) as sp:
    flux_tally = sp.get_tally(id=flux_tally.id)
    # weight windows from flux
    weight_windows_2 = sp.generate_wws(tally=flux_tally, rel_err_tol=0.7)[0]


# plot flux against distance
plt.plot(mesh.r_grid[1:], flux_tally.mean.flatten(), label='flux')
plt.yscale("log")
plt.xlabel("Radius [cm]")
plt.ylabel("Flux")
plt.show()

# plot weight window against distance
plt.plot(mesh.r_grid[1:], weight_windows.lower_ww_bounds.flatten(), label='lower_ww_bounds')
plt.plot(mesh.r_grid[1:], weight_windows.upper_ww_bounds.flatten(), label='lower_up_bounds')
plt.plot(mesh.r_grid[1:], weight_windows_2.lower_ww_bounds.flatten(), label='lower_ww_bounds_2')
plt.plot(mesh.r_grid[1:], weight_windows_2.upper_ww_bounds.flatten(), label='lower_up_bounds_2')
plt.xlabel("Radius [cm]")
plt.ylabel("bound value")
plt.show()

# update plot flux against distance

# energy dependant weight window

# plot weight window against distance

# model update

# update plot flux against distance