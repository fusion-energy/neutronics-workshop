from cad_to_dagmc import CadToDagmc

my_model = CadToDagmc()

my_model.add_stp_file('plasma_simplified_180.step')   

my_model.export_unstructured_mesh_file(filename="umesh.h5m", max_mesh_size=10, min_mesh_size=1)



openmc.MeshSource(

# https://github.com/fusion-energy/cad_to_dagmc/blob/main/examples/unstrucutred_volume_mesh/simulate_unstrucutred_volume_mesh_with_openmc.py