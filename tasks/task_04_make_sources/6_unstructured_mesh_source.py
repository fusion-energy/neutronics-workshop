# from cad_to_dagmc import CadToDagmc

# my_model = CadToDagmc()

# my_model.add_stp_file('plasma_simplified_180.step')   

# my_model.export_unstructured_mesh_file(filename="umesh.h5m", max_mesh_size=100, min_mesh_size=10)

# perhaps trimesh can get volumes
# import trimesh
# trimesh_mesh_object = trimesh.load_mesh('umesh.h5m')
# vertices = trimesh_mesh_object.vertices


import openmc

openmc.config['cross_sections'] = '/home/j/endf-b8.0-hdf5/endfb-viii.0-hdf5/cross_sections.xml'

umesh = openmc.UnstructuredMesh(filename="umesh.h5m",library='moab')

####

mesh_filter = openmc.MeshFilter(umesh)
tally = openmc.Tally(name="unstrucutred_mesh_tally")
tally.filters = [mesh_filter]
tally.scores = ["flux"]
tally.estimator = "tracklength"
my_tallies = openmc.Tallies([tally])

mat1 = openmc.Material()
mat1.add_nuclide("H1", 1, percent_type="ao")
mat1.set_density("g/cm3", 0.001)
my_materials = openmc.Materials([mat1])

surf1 = openmc.Sphere(r=50000, boundary_type="vacuum")
region1 = -surf1

cell1 = openmc.Cell(region=region1)
cell1.fill = mat1

my_geometry = openmc.Geometry([cell1])

my_settings = openmc.Settings()
my_settings.batches = 1
my_settings.inactive = 0
my_settings.particles = 1
my_settings.run_mode = "fixed source"

# Create a DT point source
my_source = openmc.IndependentSource()
my_source.space = openmc.stats.Point((0, 0, 0))
my_source.angle = openmc.stats.Isotropic()
my_source.energy = openmc.stats.Discrete([14e6], [1])
my_settings.source = my_source

model = openmc.model.Model(my_geometry, my_materials, my_settings, my_tallies)
sp_filename = model.run()

sp = openmc.StatePoint(sp_filename)

tally_result = sp.get_tally(name="unstrucutred_mesh_tally")

# normally with regular meshes I would get the mesh from the tally
# but with unstrucutred meshes the tally does not contain the mesh
# however we can get it from the statepoint file
# umesh = tally_result.find_filter(openmc.MeshFilter)
umesh_from_sp = sp.meshes[1]

# these trigger internal code in the mesh object so that its centroids and volumes become known.
# centroids and volumes are needed for the get_values and write_data_to_vtk steps
centroids = umesh_from_sp.centroids
mesh_vols = umesh_from_sp.volumes

#### end of code needed due to umesh not loading

all_sources = []
all_strengths = []
for volume, centroid in zip(centroids, mesh_vols):
    my_source = openmc.IndependentSource()
    my_source.angle = openmc.stats.Isotropic()
    # the energy could be based on location of centroid
    my_source.energy = openmc.stats.Discrete([14e6], [1])
    # the energy could be based on location of centroid and volume
    my_source.strength=1
    all_strengths.append(mesh_vols)

mesh_source = openmc.MeshSource(
    mesh=umesh,
    sources=all_sources,
)

mesh_source.normalize_source_strengths()

# https://github.com/fusion-energy/cad_to_dagmc/blob/main/examples/unstrucutred_volume_mesh/simulate_unstrucutred_volume_mesh_with_openmc.py