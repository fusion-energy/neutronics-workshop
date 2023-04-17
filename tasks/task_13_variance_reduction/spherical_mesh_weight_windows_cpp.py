# This example has a sphere of concrete showing how to increase the depth of
# neutron transport through the concrete.
# First a simulation with no weight windows is shown
# Weight windows are found from the flux values obtained with the first simulation
# Secondly a simulation with weight windows is performed to find new flux values deeper into the concrete sphere
# Another set of weight windows is made from the second flux simulation
# The weight window value as a function of depth is plotted to show how these improve with each simulation iteration

import openmc
import numpy as np
import matplotlib.pyplot as plt


# materials
mat_concrete = openmc.Material()
mat_concrete.add_element("H",0.168759)
mat_concrete.add_element("C",0.001416)
mat_concrete.add_element("O",0.562524)
mat_concrete.add_element("Na",0.011838)
mat_concrete.add_element("Mg",0.0014)
mat_concrete.add_element("Al",0.021354)
mat_concrete.add_element("Si",0.204115)
mat_concrete.add_element("K",0.005656)
mat_concrete.add_element("Ca",0.018674)
mat_concrete.add_element("Fe",0.00426)
mat_concrete.set_density("g/cm3", 2.3)

my_materials = openmc.Materials([mat_concrete])

# surfaces
outer_surface = openmc.Sphere(r=500, boundary_type="vacuum")

# regions
region_1 = -outer_surface

# cells
cell_1 = openmc.Cell(region=region_1)
cell_1.fill = mat_concrete

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
my_settings.particles = 10000
my_settings.batches = 10

# tally
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
output_file = model.run(cwd="no_ww")




import openmc.lib

model.export_to_xml()

with openmc.lib.run_in_memory():

    openmc.lib.reset()  # clears tallies

    tally = openmc.lib.tallies[1]
    wws = openmc.lib.WeightWindows.from_tally(tally)

    openmc.lib.run()

    wws.update_magic(tally)  # tally now has meaning information
    openmc.lib.settings.weight_windows_on = True

    # second run
    openmc.lib.run()

# # plot flux against distance
# plt.plot(
#     mesh.r_grid[1:], flux_tally.mean.flatten(), label="flux tally no ww", color="red"
# )
# plt.legend()
# plt.yscale("log")
# plt.xlabel("Radius [cm]")
# plt.ylabel("Flux")
# plt.show()


# # plot weight window against distance
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
# plt.legend()
# plt.xlabel("Radius [cm]")
# plt.ylabel("weight window bound value")
# plt.show()

# model.settings.weight_windows = weight_windows
# # model update by assigning the weight windows found.

# output_file = model.run(cwd="initial_ww")

# with openmc.StatePoint(output_file) as sp:
#     flux_tally_with_ww = sp.get_tally(id=flux_tally.id)
#     # weight windows from flux
#     weight_windows_2 = sp.generate_wws(tally=flux_tally_with_ww, rel_err_tol=0.7)[0]


# # plot flux with and with out weight windows against distance
# plt.plot(
#     mesh.r_grid[1:], flux_tally.mean.flatten(), label="flux tally no ww", color="red"
# )
# plt.plot(
#     mesh.r_grid[1:],
#     flux_tally_with_ww.mean.flatten(),
#     label="flux tally with ww",
#     color="blue",
# )
# plt.legend()
# plt.yscale("log")
# plt.xlabel("Radius [cm]")
# plt.ylabel("Flux")
# plt.show()

# # plot weight window against distance for the firstand second set of weight windows made
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
