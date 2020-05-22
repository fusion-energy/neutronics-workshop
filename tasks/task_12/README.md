
This task creates neutronics geometry from CAD files and creates an unstrucutred mesh that is then used to score volumentic heating on the CAD geometry

Task 10 makes neutronics geometry from CAD using an opensource workflow. This task creates the same neutronics geometry in a different way by using Trelis. The use of Trelis also allows unstructed mesh / tet mesh to be created and overlayed on the neutronics geometry for scoring heating tallies.

The first stage is to install Trelis and then the DAGMC plugin , instucttions can be found [here](https://svalinn.github.io/DAGMC/install/plugin.html)

The second part is to make the neutroics geometry and h5 file. This can be skipped and you can move to the third part if you prefer to use the task 10 workflow then you can simply copy the task 10 geometry into this folder ```cp ../task_10/dagmc.h5 .``` .

- To create the h5 geometry file using Trelis run the following command from the terminal ```Trelis make_faceteted_geometry.py```. This will load the manifest.json which is used to find the the required step files and assign the material tags to the geometry. The script will export an h5m file.

- The h5m file then needs to make watertight with the following command ```make_watertight dagmc_notwatertight.h5m -o dagmc.h5m```

- Optionally a visulation can be made using mbconvert to make a vtk file and paraview to open the vtk file. ```make_watertight dagmc_notwatertight.h5m -o dagmc.vtk``` and the ```paraview dagmc.vtk```

The third part is to create the unstructured mesh using Trelis. To do this run the following command from the terminal ```trelis make_unstrucutred_mesh.py```. The script will export an cub file (Cubit file as Trelis is also known as Cubit in the US).

- The cub file can then be converted to a h5m file with the command line tool mbconvert. Try running the command ```mbconvert dagmc_notwatertight.cub dagmc_notwatertight.h5m```.

- h5m faceteted geometry file and the h5m unstructured mesh file can now be used in a neutronics simulation. Open up the openmc python script to see how these files are used in the simulations ```coder perform_openmc_simulation.py```.

- Run the openmc python script to using the command ```python perform_openmc_simulation.py```.

- Convert the openmc outputs into a vtk file for visulisation ```??? statepoint.10.h5 unstructured_mesh_tally.vtk```

- Open the vtk file using paraview and take a look at the heat distribution withing the blanket and the firstwall using slice and threshold operations. ```paraview unstructured_mesh_tally.vtk```. You might also want to create and then load into paraview a stl file of the geometry ```mbconvert dagmc.h5m dagmc.stl```.