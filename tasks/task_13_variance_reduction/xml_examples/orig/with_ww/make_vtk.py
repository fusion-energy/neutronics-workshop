from openmc_mesh_tally_to_vtk import write_mesh_tally_to_vtk
import openmc

# assumes you have a statepoint file from the OpenMC simulation
statepoint = openmc.StatePoint('statepoint.2.h5')

print(statepoint.tallies)

# assumes the statepoint file has a RegularMesh tally with a certain name
my_tally = statepoint.get_tally(id=10)

# converts the tally result into a VTK file
write_mesh_tally_to_vtk(
    tally=my_tally,
    filename = "vtk_file_from_openmc_mesh.vtk",
)