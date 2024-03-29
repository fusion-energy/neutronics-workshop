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
my_source.space = openmc.stats.Point((0, 0, 0))
my_source.angle = openmc.stats.Isotropic()
my_source.energy = openmc.stats.Discrete([14e6], [1])

all_sources = [my_source] * 1767
mesh_source = openmc.MeshSource(
    mesh=umesh,
    sources=all_sources,
)

my_settings = openmc.Settings()
my_settings.batches = 1
my_settings.particles = 1
my_settings.run_mode = "fixed source"
my_settings.source = mesh_source

model = openmc.model.Model(my_geometry, None, my_settings )
model.export_to_model_xml()

openmc.lib.init()
# umesh_full = openmc.lib.meshes[umesh.id]
# openmc.lib.UnstructuredMesh()


# all_sources = []
# all_strengths = []
# for volume, centroid in zip(centroids, mesh_vols):
#     my_source = openmc.IndependentSource()
#     my_source.angle = openmc.stats.Isotropic()
#     # the energy could be based on location of centroid
#     my_source.energy = openmc.stats.Discrete([14e6], [1])
#     # the energy could be based on location of centroid and volume
#     my_source.strength=1
#     all_strengths.append(mesh_vols)

# mesh_source = openmc.MeshSource(
#     mesh=umesh,
#     sources=all_sources,
# )

# mesh_source.normalize_source_strengths()

# # https://github.com/fusion-energy/cad_to_dagmc/blob/main/examples/unstrucutred_volume_mesh/simulate_unstrucutred_volume_mesh_with_openmc.py