# %% [markdown]
# ---
# title: Structured mesh source
# ---

# %% [markdown]
# This example shows users how to make a mesh source using a cylindrical mesh and a source term for each voxel.
#
# This is a minimal example but a more realistic example could use the voxel location to look up properties of the plasma at each coordinate and customize the source energy and strength at each mesh voxel location

# %%
from pathlib import Path
import numpy as np
import openmc
from openmc_source_plotter import plot_source_position
# Setting the cross section path to the correct location in the docker image.
# If you are running this outside the docker image you will have to change this path to your local cross section path.
openmc.config['cross_sections'] = Path.home() / 'nuclear_data' / 'cross_sections.xml'

# %% [markdown]
# Making a minimal geometry

# %%
sphere_surf_1 = openmc.Sphere(r=2000)
sphere_cell_1 = openmc.Cell(region=-sphere_surf_1)

my_geometry = openmc.Geometry([sphere_cell_1])

# creating the mesh used for the mesh source
cylindrical_mesh = openmc.CylindricalMesh.from_domain(
    my_geometry, # the corners of the mesh are being set automatically to surround the geometry
    dimension=[10,10,10]
)

# empty list that will contain one source for each mesh voxel
all_sources = []
for i in cylindrical_mesh.indices:

    mesh_index = (i[0]-1, i[1]-1, i[2]-1)
    # this minimal example sets the same source for each voxel
    # to create a realistic plasma source the mesh centroid could be used to
    # find source strength, temperature and make a location specific source
    # a function could be called that returns the temperature and relative source
    # strength for each x,y,z or r, phi, z location
    # voxel centroid can be obtained like this
    # centroid = cylindrical_mesh.centroids[mesh_index]
    # voxel cylindrical_coords (z, phi, r) can be obtained like this
    cylindrical_coords = cylindrical_mesh.vertices_cylindrical[mesh_index]
    volume = cylindrical_mesh.volumes[mesh_index]
 
    # making a source for each voxel
    my_source = openmc.IndependentSource(
        energy=openmc.stats.Discrete([14.1e6], [1]),
        angle=openmc.stats.Isotropic(),
        strength=volume if cylindrical_coords[2] > 1000 else 0  # filtering out sources below radius of 1000
    )
    all_sources.append(my_source)

# creating the mesh source from the mesh and the list of sources
# the main difference between MeshSpatial (previous example) and MeshSource is that in
# MeshSpatial each mesh element has the same source with potentially a different
# strength while in MeshSource the elements can have a different source.
# Having a different source would allow a different energy distribution and therefore
# MeshSources are useful for shut down dose rate simulations where each active element
# results in a different photon emission
mesh_source = openmc.MeshSource(
    mesh=cylindrical_mesh,
    sources=np.array(all_sources).reshape(cylindrical_mesh.dimension)
)

# Update all element source strengths such that they sum to 1.0.
# this makes post processing the results easier if the total source strength is 1
mesh_source.normalize_source_strengths()

# %% [markdown]
# plotting the mesh source

# %%
plot = plot_source_position([mesh_source], n_samples=10000)
plot.show()
