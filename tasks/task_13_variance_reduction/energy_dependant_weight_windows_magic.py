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
import plotly.graph_objects as go


# materials
mat_water = openmc.Material()
mat_water.add_element('H', 1)
mat_water.add_element('O', 2)
mat_water.set_density('g/cm3', 1.)

my_materials = openmc.Materials([mat_water])

# surfaces
outer_surface = openmc.Sphere(r=200, boundary_type='vacuum')

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
mesh.r_grid = np.linspace(0, outer_surface.r, 100)

mesh_filter = openmc.MeshFilter(mesh)

flux_tally = openmc.Tally(name='flux tally')
flux_tally.filters = [mesh_filter]
flux_tally.scores = ['flux']

# adds the mesh tally to the model
my_tallies = openmc.Tallies()
my_tallies.append(flux_tally)

# model
import openmc_weight_window_generator
model = openmc.Model(my_geometry, my_materials, my_settings, my_tallies)



all_wws = model.generate_wws_magic_method(
    tally=flux_tally,
    iterations=5,
    max_split=2,
    output_dir='magic_ww',
    rel_err_tol=0.99
)

# for i, weight_windows in enumerate(all_wws):
#     plt.plot(mesh.r_grid[1:], weight_windows[0].lower_ww_bounds.flatten(), label=f'lower_ww_bounds {i}')
#     # plt.plot(mesh.r_grid[1:], weight_windows[0].upper_ww_bounds.flatten(), label='lower_up_bounds')
# plt.yscale("log")
# plt.xlabel("Radius [cm]")
# plt.ylabel("Weignt window bound")
# plt.legend()
# plt.show()
fig = go.Figure()
for i, weight_windows in enumerate(all_wws):
    fig.add_trace(
        go.Scatter(x=mesh.r_grid[1:], y=weight_windows[0].lower_ww_bounds.flatten(), name=f'lower_ww_bounds {i}')
    )
fig.show()