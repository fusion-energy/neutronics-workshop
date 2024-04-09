# This example makes use of a DAGMC unstructured tet mesh to produce a source with a MeshSource .
import numpy as np

# this section loads a CAD step file and creates an unstrucutred DAGMC tet mesh
# the resulting mesh file (umesh.mesh) is already included in the repo
# so this creation from step file is included for completeness but can be skipped
from cad_to_dagmc import CadToDagmc
cad = CadToDagmc()
cad.add_stp_file('plasma_simplified_180.step')   
cad.export_unstructured_mesh_file(filename="umesh.h5m", max_mesh_size=100, min_mesh_size=10)


import openmc

# setting the nuclear data path to the correct location in the docker image
openmc.config['cross_sections'] = '/nuclear_data/cross_sections.xml'

umesh = openmc.UnstructuredMesh(filename="umesh.h5m",library='moab')

surf1 = openmc.Sphere(r=50000, boundary_type="vacuum")
region1 = -surf1

cell1 = openmc.Cell(region=region1)

my_geometry = openmc.Geometry([cell1])

# empty list that will contain one source for each mesh voxel
all_sources = []
for i in range(1104):

    # making a source for each voxel
    my_source = openmc.IndependentSource()
    # making two different energy sources to make the sources different
    if i > 500:
        my_source.energy = openmc.stats.Discrete([2.1e6], [1])
    else:
        my_source.energy = openmc.stats.Discrete([14.1e6], [1])
    my_source.angle = openmc.stats.Isotropic()
    my_source.strength = 1
    all_sources.append(my_source)

# creating the mesh source from the mesh and the list of sources
# the main difference between MeshSpatial (previous example) and MeshSource is that in
# MeshSpatial each mesh element has the same source with potentially a different
# strength while in MeshSource the elements can have a different source.
# Having a different source would allow a different energy distribution and therefore
# MeshSources are useful for shut down dose rate simulations where each active element
# results in a different photon emission
mesh_source = openmc.MeshSource(
    mesh=umesh,
    sources=np.array(all_sources)
)

# Update all element source strengths such that they sum to 1.0.
# this makes post processing the results easier if the total source strength is 1
mesh_source.normalize_source_strengths()

my_settings = openmc.Settings()
my_settings.batches = 10
my_settings.particles = 1000
my_settings.run_mode = "fixed source"
my_settings.source = mesh_source

model = openmc.model.Model(my_geometry, None, my_settings )

model.run()


# plotting the mesh source
from openmc_source_plotter import plot_source_position
plot = plot_source_position([mesh_source], n_samples=10000)
plot.show()
plot.save('meshsource.html')