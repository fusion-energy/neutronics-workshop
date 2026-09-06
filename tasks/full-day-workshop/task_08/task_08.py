# %% [markdown]
# ---
# title: 3D Geometry viewing
# ---

# %% [markdown]
# It is also possible to create a 3D representation of CSG geometry. The model is converted into a pixelated geometry which can resemble the style of geometry seen in the minecraft computer game.
#
# This is not an actual representation of the CSG geometry but more like a sample of the types of cells with 3D coordinates. CAD geometry is covered later and this gives us a method of seeing the 3D geometry more accurately.
#
# 3D pixelated geometry can still be useful for exploring the model; particularly if the resolution is high enough. However, this can be a memory intensive task.
#
# This task allows users to construct CSG geometry and view a 3D representation.

# %% [markdown]
# This first code block recreates the simple reactor geometry seen in Part 2, but also assigns materials to each cell.

# %% [markdown]
# First import OpenMC and configure the nuclear data path

# %%
import openmc
from pathlib import Path
# Setting the cross section path to the correct location in the docker image.
# If you are running this outside the docker image you will have to change this path to your local cross section path.
openmc.config['cross_sections'] = Path.home() / 'nuclear_data' / 'cross_sections.xml'

# %%
copper = openmc.Material()
copper.set_density('g/cm3', 8.5)
copper.add_element('Cu', 1.0)  # Note, percent_type does not have to be specified as material is 100% copper

iron = openmc.Material()
iron.set_density('g/cm3', 7.75)
iron.add_element('Fe', 1.0, percent_type='wo')

breeder_material = openmc.Material()
breeder_material.set_density('g/cm3', 0.5)
breeder_material.add_element('Li', 1, percent_type='ao')

mats = openmc.Materials([copper, iron, breeder_material])

mats.export_to_xml()

# define all the surfaces
central_sol_surface = openmc.ZCylinder(r=100)
central_shield_outer_surface = openmc.ZCylinder(r=110, boundary_type='vacuum')
vessel_inner = openmc.Sphere(r=500, boundary_type='vacuum')
first_wall_outer_surface = openmc.Sphere(r=510)
breeder_blanket_outer_surface = openmc.Sphere(r=610)


# define the cells
central_sol_region = -central_sol_surface & -breeder_blanket_outer_surface
central_sol_cell = openmc.Cell(region=central_sol_region)
central_sol_cell.fill = copper

central_shield_region = +central_sol_surface & -central_shield_outer_surface & -breeder_blanket_outer_surface
central_shield_cell = openmc.Cell(region=central_shield_region)
central_shield_cell.fill = iron

first_wall_region = -first_wall_outer_surface & +vessel_inner & +central_shield_outer_surface
first_wall_cell = openmc.Cell(region=first_wall_region)
first_wall_cell.fill = iron

breeder_blanket_region = +first_wall_outer_surface & -breeder_blanket_outer_surface & +central_shield_outer_surface
breeder_blanket_cell = openmc.Cell(region=breeder_blanket_region)
breeder_blanket_cell.fill = breeder_material

my_geometry = openmc.Geometry([central_sol_cell,central_shield_cell,first_wall_cell, breeder_blanket_cell])

my_geometry.export_to_xml()

# %% [markdown]
# The next code block runs OpenMC in plot mode and produces a vti file.
#
# Particles are not transported through the geometry in plot mode - it simply samples the geometry on the grid and makes a output vti file with the results.

# %%
# makes the 3d "cube" style geometry
vox_plot = openmc.VoxelPlot()

# makes sure the bounds of the plot include the whole geometry
vox_plot.width = my_geometry.bounding_box.width

# makes sure the voxel plot is centered at the center of the geometry
vox_plot.origin = my_geometry.bounding_box.center

# sets the pixels in each direction to be proportional to the size of the geometry in that direction
# Your computer RAM will limit the number of pixels you can set in each direction.
# The * 0.1 part of this line reduces the number of pixels in each direction to a reasonable amount but this could be increased if you want more resolution.
vox_plot.pixels = [int(w* 0.1) for w in my_geometry.bounding_box.width]

vox_plot.color_by = 'material'

vox_plot.to_vtk(output='voxel_plot.vti')

# %% [markdown]
# Now we will make a simple plot of the geometry with pyvista.

# %%
import pyvista as pv
pv.set_jupyter_backend('html')
mesh = pv.read('voxel_plot.vti')
mesh.set_active_scalars(name='id')

# cut the mesh in half along the y-axis and hide the back half
clipped = mesh.clip(normal='y')

# removed any ID values that are 0 or below, these are the void materials
nonzero = clipped.threshold(0.5)  # 0.5 excludes 0, keeps 1 and above

nonzero.plot()

# %% [markdown]
# If you are running this in Docker then right mouse click on the vti file in the file explorer to download the vti file onto your base computer and open it with a VTK file reader such as Paraview or Visit.
#
# Paraview or Visit can also be used to view the geometry file
#
# Paraview can be downloaded here: https://www.paraview.org/download/.
#
# Visit can be downloaded here: https://wci.llnl.gov/simulation/computer-codes/visit/downloads.

# %% [markdown]
# **Learning Outcomes for Part 3**
#
# - CSG models can be converted to vti files and viewed in 3D with tools such as Pyvista, Paraview or Visit.
