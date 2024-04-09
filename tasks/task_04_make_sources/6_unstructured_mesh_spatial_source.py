# This example makes use of a DAGMC unstructured tet mesh to produce a source with
# a MeshSpatial distribution.


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

my_source = openmc.IndependentSource()
my_source.angle = openmc.stats.Isotropic()
my_source.energy = openmc.stats.Discrete([14e6], [1])
# link to docs for MeshSpatial
# https://docs.openmc.org/en/latest/pythonapi/generated/openmc.stats.MeshSpatial.html
# allows us to apply the same source to each element in the mesh. The source can be varied in terms of strength
my_source.space = openmc.stats.MeshSpatial(
    mesh=umesh,
    #we set the strengths to sum to 1 to make post processing easier.
    # in a more accurate plasma source the strength could be adjusted based on the source position.
    strengths=[1/1104]*1104,
    volume_normalized=False
)

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