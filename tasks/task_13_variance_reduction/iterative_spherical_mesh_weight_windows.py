# This example has a sphere of water showing how to increase the depth of
# neutron transport through the water.
# A series of simulations are performed that iteratively improve the weight window values
# The resulting neutron flux can be observed to propagate further through the geometry 

import openmc
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from pathlib import Path


# materials
mat_water = openmc.Material()
mat_water.add_element("H", 1)
mat_water.add_element("O", 2)
mat_water.set_density("g/cm3", 1.0)

my_materials = openmc.Materials([mat_water])

# surfaces
outer_surface = openmc.Sphere(r=1000, boundary_type="vacuum")

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

import openmc_weight_window_generator
# import adds generate_wws_magic_method method to the model class

model = openmc.Model(my_geometry, my_materials, my_settings, my_tallies)


all_wws = model.generate_wws_magic_method(
    tally=flux_tally, iterations=5, max_split=2, output_dir="magic_ww", rel_err_tol=0.99
)

# plots the flux as a function of radius for each iteration
output_files = [Path("magic_ww") / str(c) / f"statepoint.{my_settings.batches}.h5" for c in range(1, 6)]
fig = go.Figure()
for i, output_file in enumerate(output_files):
    with openmc.StatePoint(output_file) as sp:
        flux_tally = sp.get_tally(name="flux tally")
    fig.add_trace(
        go.Scatter(
            x=mesh.r_grid[1:], y=flux_tally.mean.flatten(), name=f"flux tally, iteration {i+1}"
        )
    )
fig.update_yaxes(type="log")
fig.update_layout(xaxis_title="Radius [cm]", yaxis_title="Flux")
fig.show()

# plots the lower bound of the the weight window values as a function of radius for each iteration
fig = go.Figure()
for i, weight_windows in enumerate(all_wws):
    fig.add_trace(
        go.Scatter(
            x=mesh.r_grid[1:],
            y=weight_windows[0].lower_ww_bounds.flatten(),
            name=f"lower ww bounds, iteration {i+1}",
        )
    )
fig.update_layout(xaxis_title="Radius [cm]", yaxis_title="weight window bound value")
fig.show()
