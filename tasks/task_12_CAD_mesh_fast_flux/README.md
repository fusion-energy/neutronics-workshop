
## This task is currently under development and may not work

## </a>Task 12 - Unstructured mesh on CAD geometry

Please allow 20 minutes for this task.

Expected outputs from this task are in the [presentation](https://slides.com/openmc_workshop/neutronics_workshop#/13).

This task creates neutronics geometry from CAD files and creates an unstrucutred mesh that is then used to score volumentic heating on the CAD geometry.

Task 10 also makes a faceted neutronics geometry from a CAD geometry. The difference between task 10 and this task is that task 10 used an open source workflow while this task uses proprietary software (Trelis). Adittionally this task creates an unstructed mesh / tet mesh which is overlayed on the neutronics geometry for scoring heating tallies.

The first stage is to install Trelis and then the DAGMC plugin, instructions can be found [here](https://svalinn.github.io/DAGMC/install/plugin.html)

- To create the h5 geometry file using Trelis run the following command from the terminal ```trelis make_faceteted_neutronics_model.py```. This will load the manifest.json which is used to find the the required step files and assign the material tags to the geometry. The script will export an h5m file. This command can also be run in batch mode as which avoids launching the GUI  ```trelis -batch -nographics make_faceteted_neutronics_model.py``` which might work better in a docker enviroment.

- The h5m file then needs to make watertight with the following command ```make_watertight dagmc_notwatertight.h5m -o dagmc.h5m```

The next stage is to create the unstructured mesh using Trelis. To do this run the following command from the terminal ```trelis make_unstructured_mesh.py```. This script also loads the manifest.json file which is used to decide which volumes to load and mesh. The script will export an cub file (Cubit file as Trelis is also known as Cubit in the US). The command can also be run without the GUI using the -batch and -batch -nographics options ```trelis -batch -nographics make_unstructured_mesh.py```

- The cub file can then be converted to a h5m file with the command line tool mbconvert. Try running the command ```mbconvert tet_mesh.exo tet_mesh.h5m```.

- h5m faceteted geometry file and the h5m unstructured mesh file can now be used in a neutronics simulation. Open up the openmc python script to see how these files are used in the simulations ```coder example_unstructured_mesh_simulation.py``` . This script should look similar if you have completed task 10, look for the additional line where the tet mesh is loading into the model. Also another difference to find is in the arguments passed to the model.run() part of the script.

- Run the openmc python script to using the command ```python example_unstructured_mesh_simulation.py```. This should produce a vtk file of the unstrucutred mesh tally.

- Open the vtk file using paraview and take a look at the heat distribution withing the blanket and the firstwall using slice and threshold operations ```paraview tally_1.100.vtk```.

Optinal extras

- You might also want to create and then load into paraview a stl file of the geometry ```mbconvert dagmc.h5m dagmc.stl```.

- You can change the mesh size by opening up the manifest.json file and reducing the size number in the mesh dictionary entry. Warning, this can significantly increase the duration of the simulations and meshing time.

- Open up the run_all.sh and learn how to perform the model creation and simulations without the Trelis GUI. This is useful for automated workflows

- There are two tutorials on the OpenMC website that were very helpful when making this example. If you want to try more advanced features take a look at (example 1)[https://docs.openmc.org/en/latest/examples/unstructured-mesh-part-i.html] and (example 2)[https://docs.openmc.org/en/latest/examples/unstructured-mesh-part-ii.html]
