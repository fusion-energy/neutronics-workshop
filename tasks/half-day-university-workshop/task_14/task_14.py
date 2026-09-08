# %% [markdown]
# ---
# title: 2D mesh tallies
# ---

# %% [markdown]
# So far we have seen that neutron and photon interactions can be tallied on surfaces or cells, but what if we want to tally neutron behaviour throughout a geometry? (rather than the integrated neutron behaviour over a surface or cell).
#
# A mesh tally allows a visual inspection of the neutron behaviour spatially throughout the geometry.
#
# The geometry is subdivided into many rectangles and the neutron behaviour is recorded (tallied) by the simulation in each of the small rectangles.
#
# This can form a 2D slice of the neutron interactions throughout the model.
#
# This task allows users to create a simple geometry from a few different materials and plot the results of a 2D regular mesh tally applied to the geometry.
#
# First import packages needed and configure the OpenMC nuclear data path

# %%
import matplotlib.pyplot as plt
import openmc
from pathlib import Path
# Setting the cross section path to the correct location in the docker image.
# If you are running this outside the docker image you will have to change this path to your local cross section path.
openmc.config['cross_sections'] = Path.home() / 'nuclear_data' / 'cross_sections.xml'

# %% [markdown]
# This code block defines the model materials.

# %%
# creates two materials, one is a neutron multiplier (lead) and the other a tritium breeder (lithium)

breeder_material = openmc.Material() 
breeder_material.add_element('Li', 1, percent_type='ao')
breeder_material.set_density('g/cm3', 2.0)

multiplier_material = openmc.Material() 
multiplier_material.add_element('Pb', 1, percent_type='ao')
multiplier_material.set_density('g/cm3', 11.0)

my_materials = openmc.Materials([breeder_material, multiplier_material])

# %% [markdown]
# This code block defines the model geometry.

# %%
# surfaces
sph1 = openmc.Sphere(r=50)
sph2 = openmc.Sphere(r=90, boundary_type='vacuum')
plane1 = openmc.XPlane(20)

# cells fileld with materials
breeder_cell = openmc.Cell(region=+sph1 & -sph2 & -plane1)
breeder_cell.fill = breeder_material

multiplier_cell = openmc.Cell(region=+sph1 & -sph2 & +plane1)
multiplier_cell.fill = multiplier_material

# cell not filled with material (void cell)
inner_vacuum_cell = openmc.Cell(region=-sph1)

my_geometry = openmc.Geometry([inner_vacuum_cell, breeder_cell, multiplier_cell])

# %% [markdown]
# This code block makes the model source and settings

# %%
# SETTINGS

# Instantiate a Settings object
my_settings = openmc.Settings()
my_settings.batches = 100
my_settings.inactive = 0
my_settings.particles = 50
my_settings.run_mode = 'fixed source'

# creates a 14MeV point source
my_source = openmc.IndependentSource(
    space=openmc.stats.Point((0, 0, 0)),
    angle=openmc.stats.Isotropic(),
    energy=openmc.stats.Discrete([14e6], [1]),
    particle="neutron"
)
my_settings.source = my_source

# %% [markdown]
# This next code block makes the mesh and tally
#
# Notice how a 2D mesh is achieved by creating a 3D mesh with a thickness of one mesh cell in one dimension. This will make it easier to plot later

# %%
# Create mesh which will be used for tally
mesh = openmc.RegularMesh().from_domain(
    my_geometry, # the corners of the mesh are being set automatically to surround the geometry
    dimension=[100, 1, 100] # only 1 cell in the Y dimension
)


# Create mesh filter for tally
mesh_filter = openmc.MeshFilter(mesh)
mesh_tally = openmc.Tally(name='tallies_on_mesh')
mesh_tally.filters = [mesh_filter]
mesh_tally.scores = ['flux', 'absorption', '(n,2n)']  # you can have multiple scores on a single tally, this is more memory efficient that having new tallies each score
my_tallies = openmc.Tallies([mesh_tally])

# %% [markdown]
# Combining the geometry, materials, settings and tallies to create a neutronics model

# %%
model = openmc.Model(my_geometry, my_materials, my_settings, my_tallies)

# %% [markdown]
# The next code block performs the simulation which tallies neutron flux on the mesh, and loads the results for inspection.

# %%
# deletes old files
Path('summary.h5').unlink(missing_ok=True)
for f in Path('.').glob('statepoint.*.h5'):
    f.unlink(missing_ok=True)

# runs the simulation
output_filename = model.run()

# open the results file
results = openmc.StatePoint(output_filename)

# %% [markdown]
# This code block filters the results to show the neutron flux recorded by the mesh tally.
#
# Notice that neutrons are produced and emitted isotopically from a point source.
#
# There is a slight increase in flux within the neutron multiplier.

# %%
# access the flux tally
my_tally = results.get_tally(scores=['flux'])
my_slice = my_tally.get_slice(scores=['flux'])
my_slice.mean.shape = (mesh.dimension[0], mesh.dimension[2]) # setting the resolution to the mesh dimensions

fig, ax1 = plt.subplots(figsize=(6, 4))

# when plotting the 2d data, added the extent is required.
# otherwise the plot uses the index of the 2d data arrays
# as the x y axis
plot_1 = ax1.imshow(X=my_slice.mean, extent=mesh.bounding_box.extent['xz'])

ax2 = my_geometry.plot(
    outline='only',
    extent=my_geometry.bounding_box.extent['xz'],
    axes=ax1,  # Use the same axis as ax1
    pixels=10_000_000,  #avoids rounded corners on outline

)
ax2.set_xlim(ax1.get_xlim())
ax2.set_ylim(ax1.get_ylim())
ax2.set_aspect(ax1.get_aspect())  # Match aspect ratio

plt.show()

# %% [markdown]
# This code block filters the results to show the neutron absorption recorded by the mesh tally.

# %%
# access the absorption tally
my_tally = results.get_tally(scores=['absorption'])
my_slice = my_tally.get_slice(scores=['absorption'])
my_slice.mean.shape = (mesh.dimension[0], mesh.dimension[2])

fig, ax1 = plt.subplots(figsize=(6, 4))

# when plotting the 2d data, added the extent is required.
# otherwise the plot uses the index of the 2d data arrays
# as the x y axis
plot_1 = ax1.imshow(X=my_slice.mean, extent=mesh.bounding_box.extent['xz'])

ax2 = my_geometry.plot(
    outline='only',
    extent=my_geometry.bounding_box.extent['xz'],
    axes=ax1,  # Use the same axis as ax1
    pixels=10_000_000,  #avoids rounded corners on outline

)
ax2.set_xlim(ax1.get_xlim())
ax2.set_ylim(ax1.get_ylim())
ax2.set_aspect(ax1.get_aspect())  # Match aspect ratio

plt.show()
# notice that neutrons are being absorpted on the left hand side of the model

# %% [markdown]
# This code block filters the results to show the neutron multiplication recorded by the mesh tally.
#
# notice that neutrons are being multiplied on the right hand side of the model where the lead material is

# %%
# access the neutron multiplication tally
my_tally = results.get_tally(scores=['(n,2n)'])
my_slice = my_tally.get_slice(scores=['(n,2n)'])
my_slice.mean.shape = (mesh.dimension[0], mesh.dimension[2])

fig, ax1 = plt.subplots(figsize=(6, 4))

# when plotting the 2d data, added the extent is required.
# otherwise the plot uses the index of the 2d data arrays
# as the x y axis
plot_1 = ax1.imshow(X=my_slice.mean, extent=mesh.bounding_box.extent['xz'])

ax2 = my_geometry.plot(
    outline='only',
    extent=my_geometry.bounding_box.extent['xz'],
    axes=ax1,  # Use the same axis as ax1
    pixels=10_000_000,  #avoids rounded corners on outline

)
ax2.set_xlim(ax1.get_xlim())
ax2.set_ylim(ax1.get_ylim())
ax2.set_aspect(ax1.get_aspect())  # Match aspect ratio

plt.show()

# closes the results file now that the last tally has been read from it.
# The first cell of this task deletes the old statepoint files and
# Windows does not allow a file that is still open to be deleted
results.close()

# %%
# Bonus information
# The 2D mesh tally is currently recording all interactions in the 3rd dimension (z).
# The diagrams are showing the xy plane and all interactions in the z direction.
# However one can also change the mesh to take a central slice of with a 1cm thickness in the following way.
# The tally takes a little longer to converge as less neutrons are interacting in the tally region.

# Create mesh which will be used for tally, manually setting the left and right corners, the plotting will also need adapting.
mesh = openmc.RegularMesh()
mesh.dimension = [100, 1, 100] # only one entry in the Y direction
mesh.lower_left = [-200, -0.5, -200] # Y thickness is now smaller
mesh.upper_right = [200, 0.5, 200] # Y thickness is now smaller

# %% [markdown]
# **Learning Outcomes for Part 1:**
#
# - Mesh tallies can be used to visualise neutron interactions spatially throughout geometry.
