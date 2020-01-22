
## <a name="task10"></a>Task 10 - Using CAD geometry

Google Colab Link: [Task_10](https://drive.google.com/open?id=1EM5xd9yC4JariHRQ2ftzY2v_HRHoTp9u)

Please allow 30 minutes for this task.

Expected outputs from this task are in the [presentation](https://slides.com/openmc_workshop/neutronics_workshop#/22).

Constructive solid geometry (CSG) has been used in all the previous tasks. This task demonstrates the use of CAD geometry usage within openmc.

The use of CAD geometry has several advantages compared to CSG.

- Geometry containing complex shapes including spline curves can be modeled. This is essential for some fusion reactor designs (e.g. stellerators). 

- Geometry created outside of neutronics (e.g. design offices) is created in a CAD format. Using the CAD geometry directly avoids the manual process of converting CAD geometry into CSG geometry which is a bottleneck in the design cycle.

- Simulation reults such as heating can be mapped directly into engineering models which also use CAD geometry. This is benifitial when integrating neutronics into the design cycle or coupling neutronics with thermal analysis.

- Visulisation of neutronics models can be performed with CAD software which is mature and feature rich.

This taks depends on [DAGMC](https://svalinn.github.io/DAGMC/) and [FreeCAD](https://www.freecadweb.org/) both of which are installed on this docker image. 

The geometry can be viewed in FreeCAD. Open up FreeCAD by typing ```freecad``` in the command line.

Once loaded select file open and select blanket.stp, firstwall.stp and poloidal_magnets.stp. This should show the 3D model within the FreeCAD viewer. Watch the video tutorial below to learn how to do this.

<p align="center"><a href="http://www.youtube.com/watch?feature=player_embedded&v=pyZXQg0AsJ4
" target="_blank"><img src="images/task10thumbnail.png" height="400" /></a></p>

If you have Trelis or Cubit installed (they can't be included on this Docker image) then try creating the DAGMC neutronics geometry using the command ```trelis make_faceted_geometry_with_materials```.

The trelis / cubit script will load up the stp files and combine them to create a faceted geometry that can be used in neutronics simulations. Feel free to explore the script and the coresponding json config file.

The next step is to open the OpenMC python script with the command ```coder example_CAD_simulation.py```.

Read throught the script and try to spot the differences between a CSG and CAD simulation script. You might notice that the materials are defined in the script but not assigned to volumes and that no geometry is made in the script. Also the settings object has an additional dagmc property

The material assignment is not required as this is perfomed when combining the stp files within the Trelis step. Trelis produces the dagmc.h5m file which contains geometry and each geometry is taged with a material name. These material names must be defined in the openmc script by it is not nessecary to assign them as this is taken care of by DAGMC.

Try running the script using the command ```python example_CAD_simulation.py```. This will run the simulation using the CAD geometry and produce the output results.

**Learning Outcomes**

- CAD geometry can be used to build complex models for use in neutronics simulations.