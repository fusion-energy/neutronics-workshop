# %% [markdown]
# ---
# title: Visualising Particle Tracks
# ---

# %% [markdown]
# When running neutronics simulations we may want to track how particles travel through the defined geometry.
#
# This task allows users to generate particle track files that can be opened and viewed alongside the 3D geometry.

# %% [markdown]
# First import OpenMC and configure the nuclear data path

# %%
import openmc
from pathlib import Path
# Setting the cross section path to the correct location in the docker image.
# If you are running this outside the docker image you will have to change this path to your local cross section path.
openmc.config['cross_sections'] = Path.home() / 'nuclear_data' / 'cross_sections.xml'

# %% [markdown]
# This first code block makes a geometry with hemispheres. One side is a moderator (H2O) and the other is a material that is quite transparent to neutrons (zirconium).
#
# Because of the different neutronic properties of the materials, we expect neutrons to track differently through the two materials. We can visualise this using OpenMC.

# %%
# MATERIALS
mats = openmc.Materials()

moderating_material = openmc.Material(42, "water")  # water contains hydrogen which is a good neutron moderator, note the ID number is 42, we need this later
moderating_material.add_element('H', 2, 'ao')  # Note, 'percent_type=' does not have to be written to specify 'ao' or 'wo'
moderating_material.add_element('O', 1, 'ao')
moderating_material.set_density('g/cm3', 1.0)
mats.append(moderating_material)

transparent_material = openmc.Material(82, "zirconium")  # one of the more transparent materials, note the ID number is 42, we need this later
transparent_material.add_element('Zr', 1, 'ao')
transparent_material.set_density('g/cm3', 2)  # lower density to make it even more transparent
mats.append(transparent_material)


# GEOMETRY
sph0 = openmc.Sphere(r=400)
sph1 = openmc.Sphere(r=600, boundary_type='vacuum')
flat_surf = openmc.YPlane(y0=0)

simple_moderator_cell = openmc.Cell(region=+sph0 & -sph1 & +flat_surf)
simple_moderator_cell.fill = moderating_material

simple_transparent_cell = openmc.Cell(region=+sph0 & -sph1 & -flat_surf)
simple_transparent_cell.fill = transparent_material

vaccum_cell = openmc.Cell(region=-sph0)

geom = openmc.Geometry([simple_moderator_cell, simple_transparent_cell, vaccum_cell])


# SIMULATION SETTINGS

# Instantiate a Settings object
sett = openmc.Settings()
batches = 1
sett.batches = batches
sett.inactive = 0
sett.particles = 10  # Note that only 10 particles are simulated, otherwise we make too many files
sett.particle = "neutron"
sett.run_mode = 'fixed source'

# creates a 14MeV point source
source = openmc.IndependentSource(
    space=openmc.stats.Point((0, 0, 0)),
    angle=openmc.stats.Isotropic(),
    energy=openmc.stats.Discrete([14e6], [1])
)

# source.file = 'source_1000_particles.h5'
sett.source = source

# %% [markdown]
# This is the new part covered by this task. The running of OpenMC in track mode.

# %%
# Run OpenMC!
model = openmc.Model(geom, mats, sett)
model.run(tracks=True)  # this creates h5 files that contain track information

# %% [markdown]
# Loading the track output file and plotting the results

# %%
tracks = openmc.Tracks('tracks.h5')

# %% [markdown]
# Makes a quick 3D plot of the tracks.

# %%
tracks.plot()

# %% [markdown]
# This exports the tracks.h5 files to vtk / vtp files which can be opened with Paraview to show the tracks in 3d.

# %%
tracks.write_to_vtk('tracks.vtp')

# %% [markdown]
# Cycles through each of the tracks printing information on each track

# %%
# gets the first track from the 10 tracks. This is 10 because we simulated 10 particles
track = tracks[0]

# get the primary particle track from this particle
one_particle = track.particle_tracks[0]

# prints out the x position, y position, z position, x direction, y direction, z direction, energy, weight (varience reduction is off), cell id and material id
print(one_particle.states)

# Notice the energy starts at 14MeV and decreases with each collision

# %% [markdown]
# Filtering of tracks is also easy with the built in filter method.
#
# There are 10 tracks in total as we simulated just 10 particles.
#
# However we can filter these 10 particles to look at the ones that interacted with water then we could inspect the properties of tracks in certain materials.

# %%
tracks_in_zirconium_material = tracks.filter(state_filter=lambda s:s['material_id'] == 82)
# writing a separate vtk file for the tracks that go through the zirconium material 
tracks_in_zirconium_material.write_to_vtk('tracks_in_zirconium_material.vtp')

tracks_in_water_material = tracks.filter(state_filter=lambda s:s['material_id'] == 42)
# writing a separate vtk file for the tracks that go through the water material 
tracks_in_water_material.write_to_vtk('tracks_in_water_material.vtp')

print(f'{len(tracks_in_water_material)} tracks in water and {len(tracks_in_zirconium_material)}')

# %% [markdown]
# This next code block might be familiar from task 3. Here, we are converting the geometry into a 3D version which can be viewed. This will provide a nice background for the tracks so we know where are relative to the materials.
#
# If you were working with CAD geometry you could load up STL files or use mbconvert to convert a dagmc.h5m to a VTK file.
#
# Mesh tallies (in VTK format) as you can visualize the geometry together with the source in Paraview

# %%
vox_plot = openmc.VoxelPlot()

vox_plot.width = (1300., 1300., 1300.)
vox_plot.pixels = (100, 100, 100)
vox_plot.filename = 'plot_3d'
vox_plot.color_by = 'material'
vox_plot.colors = {moderating_material: 'blue', transparent_material: 'red'}
plots = openmc.Plots([vox_plot])
plots.export_to_xml()

openmc.plot_geometry()

# this reads in the h54 voxel file and writes it to a vti file
vox_plot.to_vtk(output='voxel_plot.vti')

# %%
import pyvista as pv

pv.set_jupyter_backend('html')

# Load voxel mesh
mesh = pv.read('voxel_plot.vti')
mesh.set_active_scalars(name='id')

nonzero = mesh.threshold(0.5)   # removes the surounding void

# Load tracks
tracks = pv.read('tracks_0.vtp')

# Plot
p = pv.Plotter()

# Semi-transparent voxels
p.add_mesh(
    nonzero, 
    scalars='id',  
    categories=True,
    cmap='Set2',
    opacity=0.3,  # lower = more see-through
)

p.add_mesh(
    tracks,
    color="red",
    line_width=3,
)

p.show()

# %% [markdown]
# Right mouse click on the vtp files in the file explorer to download the vtk file to your base computer and open it with a VTK file reader such as Paraview or Visit.
#
# Paraview can be downloaded here: https://www.paraview.org/download/.
# Visit can be downloaded here https://wci.llnl.gov/simulation/computer-codes/visit/downloads.

# %% [markdown]
# **Learning Outcomes for Part 3:**
#
# - Particle tracks through geometry can be tracked in OpenMC and visualised in programs such as Paraview and Visit.
