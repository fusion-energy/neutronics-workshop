# this example shows users how to make a mesh source using a cylindrical mesh and a source term for each voxel.

# this is a minimal example but a more realistic example could use the voxel location to look up properties
# of the plasma at each coordinate and customize the source energy and strength at each mesh voxel location

import openmc
import numpy as np

openmc.config['cross_sections'] = '/home/j/endf-b8.0-hdf5/endfb-viii.0-hdf5/cross_sections.xml'

# making a minimal geometry
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
    my_source = openmc.IndependentSource()
    my_source.energy = openmc.stats.Discrete([14.1e6], [1])
    my_source.angle = openmc.stats.Isotropic()
    if cylindrical_coords[2] > 1000: # filtering out sources below radius of 1000
        my_source.strength = volume # uniform source
    else:
        my_source.strength = 0
    all_sources.append(my_source)

# creating the mesh source from the mesh and the list of sources
mesh_source = openmc.MeshSource(
    mesh=cylindrical_mesh,
    sources=np.array(all_sources).reshape(cylindrical_mesh.dimension)
)

# Update all element source strengths such that they sum to 1.0.
# this makes post processing the results easier if the total source strength is 1
mesh_source.normalize_source_strengths()

# plotting the mesh source
from openmc_source_plotter import plot_source_position
plot = plot_source_position([mesh_source], n_samples=10000)
plot.show()
