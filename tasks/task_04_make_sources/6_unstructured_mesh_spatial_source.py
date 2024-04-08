# This example makes use of a DAGMC unstructured tet mesh to produce a source with
# a MeshSpatial distribution.

from cad_to_dagmc import CadToDagmc

my_model = CadToDagmc()

my_model.add_stp_file('plasma_simplified_180.step')   
# import gmsh
# gmsh.initialize()

gmshm = my_model.export_unstructured_mesh_file(filename="umesh.h5m", max_mesh_size=100, min_mesh_size=10)

# perhaps trimesh can get volumes
# import trimesh
# trimesh_mesh_object = trimesh.load_mesh('umesh.h5m')
# vertices = trimesh_mesh_object.vertices


import openmc
import openmc.lib

openmc.config['cross_sections'] = '/home/j/endf-b8.0-hdf5/endfb-viii.0-hdf5/cross_sections.xml'

umesh = openmc.UnstructuredMesh(filename="umesh.h5m",library='moab')

surf1 = openmc.Sphere(r=50000, boundary_type="vacuum")
region1 = -surf1

cell1 = openmc.Cell(region=region1)

my_geometry = openmc.Geometry([cell1])

my_source = openmc.IndependentSource()
my_source.angle = openmc.stats.Isotropic()
my_source.energy = openmc.stats.Discrete([14e6], [1])
# link to docs for MeshSpatial
# https://docs.openmc.org/en/latest/pythonapi/generated/openmc.stats.MeshSpatial.html
# the main difference between MeshSpatial and MeshSource is that in MeshSpatial
# each mesh element has the same source with potentially a different strength
# while in MeshSource the elements can have a different source.
# Having a different source would allow a different energy distribution and therefore
# MeshSources are useful for shut down dose rate simulations where each active element
# results in a different photon emission
my_source.space = openmc.stats.MeshSpatial(
    mesh=umesh,
    strengths=[1]*1104, # in a more detailed version the strength could be adjusted based on the source position.
    volume_normalized=False
)
my_source.strength=1

my_settings = openmc.Settings()
my_settings.batches = 10
my_settings.particles = 1000
my_settings.run_mode = "fixed source"
my_settings.source = my_source

model = openmc.model.Model(my_geometry, None, my_settings )

model.run()


# plotting the mesh source
from openmc_source_plotter import plot_source_position
plot = plot_source_position([my_source], n_samples=10000)
plot.show()