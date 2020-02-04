
## <a name="task10"></a>Task 10 - Using CAD geometry

Google Colab Link: [Task_10](https://drive.google.com/open?id=1EM5xd9yC4JariHRQ2ftzY2v_HRHoTp9u)

Please allow 15 minutes for this task.

Expected outputs from this task are in the [presentation](https://slides.com/openmc_workshop/neutronics_workshop#/22).

Constructive solid geometry (CSG) has been used in all the previous tasks. This task demonstrates the use of CAD geometry usage within openmc.

The use of CAD geometry has several advantages compared to CSG.

- Geometry containing complex shapes including spline curves can be modeled. This is essential for some fusion reactor designs (e.g. stellerators). 

- Geometry created outside of neutronics (e.g. design offices) is typically created in a CAD format. Using the CAD geometry directly avoids the process (often manual) of converting CAD geometry into CSG geometry which can be a bottleneck in the design cycle.

- Simulation reults such as heating can be mapped directly into engineering models which also use CAD geometry. This is useful when integrating neutronics into the design cycle or coupling neutronics with thermal analysis.

- Visulisation of neutronics models can be performed with CAD software which is mature and feature rich.

- Void regions need to be defined in CSG and can be complex. The CAD based neutronics with DAGMC uses an implicit void which doesn't need to be defined by the user.

This task depends on [DAGMC](https://svalinn.github.io/DAGMC/), [FreeCAD](https://www.freecadweb.org/) and the OCC Faceter, all of which are installed on the workshop docker image. 

The geometry can be viewed in FreeCAD. Open up FreeCAD by typing ```freecad``` in the command line.

Once loaded select file open and select CAD files (blanket.stp, firstwall.stp and poloidal_magnets.stp). This should show the 3D model within the FreeCAD viewer. Watch the video tutorial below to learn how to do this.

<p align="center"><a href="http://www.youtube.com/watch?feature=player_embedded&v=pyZXQg0AsJ4
" target="_blank"><img src="images/task10thumbnail.png" height="400" /></a></p>

These CAD files can be converted into a neutronics geometry using the command ```steps2h5m```. This command also attaches material names to the geometry. The material names will need to have matching OpenMC material objects at the simulation stage. The ```steps2h5m``` requires three agruments, these are a json input file which lists the CAD files (stp files), the tolerance on the faceting and the output name of the resulting neutronics model (h5m format).


- Try opening the geometry_details.json file to see the CAD files used in this geometry and the material names assigned to them ```coder geometry_details.json```

- Try converting the STEP geometry into h5m files using the ```steps2h5m geometry_details.json 10 dagmc_notwatertight.h5m``` command.

The next command checks the geometry is watertight and that all the volumes are closed. This is required to prevent neutrons getting lost during the neutron transport stage.

- Try making the geometry watertight with the command ```make_watertight dagmc_notwatertight.h5m -o dagmc.h5m```

The example_CAD_simulation.py script is different to the previous CSG based OpenMC simulation scripts. Try to spot the differences between a CSG and CAD simulation scripts. You might notice that the materials are defined in the script but not assigned to volumes. Also the settings object has an additional dagmc property. Also notice there are no CSG surfaces or cells defined in the model.

The material assignment is not required as this is perfomed when combining the stp files within the Trelis step. Trelis produces the dagmc.h5m file which contains geometry and each geometry is taged with a material name. These material names must be defined in the openmc script by it is not nessecary to assign them as this is taken care of by DAGMC.

- Try open the OpenMC python script with the command ```coder example_CAD_simulation.py``` and find where the scripts refers to the dagmc.h5m model.


Try running the script using the command ```python example_CAD_simulation.py```. This will run the simulation using the CAD geometry and produce the output results.

**Learning Outcomes**

- CAD geometry can be used to build complex models with splines for use in neutronics simulations.
- CAD based neutronics has a number of advantages over CSG based neutronics.
