
#these commands can be run to complete this workshop task

# removes old mesh and faceted geometryfiles
rm *.h5m

trelis make_faceteted_neutronics_model.py

# this is the same command as above but it avoids loading up the GUI so it could be part of an automatic workflow
# trelis -batch -nographics make_faceteted_neutronics_model.py

make_watertight dagmc_notwatertight.h5m -o dagmc.h5m

# this makes a volume mesh of the geometry and saves it as a tet_mesh.exo file 
trelis make_unstructured_mesh.py

# this is the same command as above but it avoids loading up the GUI so it could be part of an automatic workflow
# trelis -batch -nographics make_unstructured_mesh.py

# this converts the tet_mesh.exo into a h5m file that can be used by OpenMC / Dagmc
mbconvert tet_mesh.exo tet_mesh.h5m

# this executes the simulations
python example_unstructured_mesh_simulation.py

# loads up the tet mesh heating tally for visualization
paraview tally_1.100.vtk
