# This example has a sphere of water showing how to increase the depth of
# neutron transport through the water.
# First a simulation with no weight windows is shown
# Weight windows are found from the flux values obtained with the first simulation
# Secondly a simulation with weight windows is performed to find new flux values deeper into the water sphere
# Another set of weight windows is made from the second flux simulation
# The weight window value as a function of depth is plotted to show how these improve with each simulation iteration



import openmc
import numpy as np
import matplotlib.pyplot as plt
import openmc.lib

# materials
mat_water = openmc.Material()
mat_water.add_element("H", 1)
mat_water.add_element("O", 2)
mat_water.set_density("g/cm3", 1.0)

my_materials = openmc.Materials([mat_water])

# surfaces
outer_surface = openmc.Sphere(r=500, boundary_type="vacuum")

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
source.particle = "neutron"

my_settings = openmc.Settings()
my_settings.run_mode = "fixed source"
my_settings.source = source
my_settings.particles = 100
my_settings.batches = 5

# tally
# mesh = openmc.RegularMesh().from_domain(my_geometry)
mesh = openmc.SphericalMesh()
mesh.r_grid = np.linspace(0, outer_surface.r, 100)

mesh_filter = openmc.MeshFilter(mesh)

flux_tally = openmc.Tally(name="flux tally")
flux_tally.filters = [mesh_filter]
flux_tally.scores = ["flux"]

# adds the mesh tally to the model
my_tallies = openmc.Tallies()
my_tallies.append(flux_tally)

# model
model = openmc.model.Model(my_geometry, my_materials, my_settings, my_tallies)

# analogy running without weight windows
model.run()

with openmc.StatePoint(f'statepoint.{my_settings.batches}.h5') as sp:
    flux_tally = sp.get_tally(id=1)


model.export_to_xml()

openmc.lib.init()

tally = openmc.lib.tallies[1]

wws = openmc.lib.WeightWindows.from_tally(tally)

openmc.lib.run()

wws.update_weight_windows_magic(tally)
openmc.lib.settings.weight_windows_on = True
openmc.lib.run()

with openmc.StatePoint(f'statepoint.{my_settings.batches}.h5') as sp:
    ww_flux_tally = sp.get_tally(id=1)

# openmc.lib.finalize()


# plt.plot(
#     mesh.r_grid[1:],
#     ww_flux_tally.mean.flatten(),
#     label="flux tally ww",
#     color="red"
# )

# plt.plot(
#     mesh.r_grid[1:],
#     flux_tally.mean.flatten(),
#     label="flux tally no ww",
#     color="blue"
# )

# plt.legend()
# plt.yscale("log")
# plt.xlabel("Radius [cm]")
# plt.ylabel("Flux")
# plt.show()


    # # plot weight window against distance for the first and second set of weight windows made
    # plt.plot(
    #     mesh.r_grid[1:],
    #     weight_windows.lower_ww_bounds.flatten(),
    #     label="lower ww bounds",
    #     color="red",
    # )
    # plt.plot(
    #     mesh.r_grid[1:],
    #     weight_windows.upper_ww_bounds.flatten(),
    #     label="lower up bounds",
    #     color="lightcoral",
    # )
    # plt.plot(
    #     mesh.r_grid[1:],
    #     weight_windows_2.lower_ww_bounds.flatten(),
    #     label="lower ww bounds iteration 2",
    #     color="blue",
    # )
    # plt.plot(
    #     mesh.r_grid[1:],
    #     weight_windows_2.upper_ww_bounds.flatten(),
    #     label="lower up bounds iteration 2",
    #     color="cornflowerblue",
    # )
    # plt.legend()
    # plt.xlabel("Radius [cm]")
    # plt.ylabel("weight window bound value")
    # plt.show()
