
## <a name="task2"></a>Task 2 - Building and visualizing the model geometry

Google Colab Link: [Task_2](https://colab.research.google.com/drive/17o94Go2_pQLHrrkcM_2K-asvKrSsMbtx)

Please allow 25 minutes for this task.

Expected outputs from this task are also in the [presentation](https://slides.com/openmc_workshop/neutronics_workshop/#/14).

OpenMC can provide both 2D and 3D visualizations of the Constructive Solid Geometry ([CSG](https://en.wikipedia.org/wiki/Constructive_solid_geometry)) of a model.

There are two methods for producing 2D slice views of model geometries. This can be done via a Python Matplotlib (```1_example_geometry_viewer_2d.py```) or via the production of xml files, again with Python (```2_example_geometry_viewer_2d_xml_version.py```). The first option is simpler to understand and use while the second option is slightly faster for complex geometries, we will use the simpler option in this workshop.

- Try understanding the example code ```coder 1_example_geometry_viewer_2d.py```

- Try running the example code ```python 1_example_geometry_viewer_2d.py```

Views of the model geometry from XY, YZ and XZ planes should appear one after the other.

<p align="center"><img src="https://user-images.githubusercontent.com/56687624/90137554-b2d99880-dd6d-11ea-87fe-3db437987b11.png" height="210"></p>

As the geometry is a spherical shell centred at the origin, its views in each plane are identical.

Edit the script and try adding a first wall and centre column to the model using the OpenMC [simple examples](https://openmc.readthedocs.io/en/stable/examples/pincell.html#Defining-Geometry) and the [documentation](https://openmc.readthedocs.io/en/stable/usersguide/geometry.html) for CSG operations.

- Try adding a 20cm thick first wall to the hollow sphere.

- Try assigning the eurofer material to the first wall - specification provided below. (Eurofer density = 7.75 g/cm3)

<p align="center"><img src="https://user-images.githubusercontent.com/56687624/90137636-d13f9400-dd6d-11ea-9faa-53a47eb3feaa.png"></p>

- Try adding a centre column using a [ZCylinder](https://openmc.readthedocs.io/en/stable/pythonapi/generated/openmc.ZCylinder.html) surface with a 100cm radius. This must also be cut at the top and bottom by the firstwall sphere surface.

- Try creating a material from pure copper and assign it to the centre column.

- Colour the geometry plots by material - see the [documentation](https://openmc.readthedocs.io/en/stable/usersguide/plots.html) for an example.

By the time you have added the extra components, your geometry should look similar to the geometry contained within the next example script.

```coder 3_example_geometry_viewer_2d_tokamak.py```

```python 3_example_geometry_viewer_2d_tokamak.py```

Run this script to produce views of the tokamak model from different planes, as shown below, and compare these to the geometry produced by your edited script.

<p align="center">
<img src="https://user-images.githubusercontent.com/56687624/90137577-bbca6a00-dd6d-11ea-9cc3-7cc8f4b6a8e4.png" height="210">
<img src="https://user-images.githubusercontent.com/56687624/90137583-bcfb9700-dd6d-11ea-86d3-fc3a7ae60152.png" height="210">
<img src="https://user-images.githubusercontent.com/56687624/90137587-be2cc400-dd6d-11ea-8812-5bde721e41df.png" height="210">
</p>

<p align="center"><i>Left = XY plane, Middle = XZ plane, Right = YZ plane</i></p>

The next script shows how a simple geometry can be viewed in 3D using paraview. This converts the geometry into a block.

```coder 4_example_geometry_viewer_3d_tokamak.py```

```python 4_example_geometry_viewer_3d_tokamak.py```

Paraview should load up when the script completes, however, no geometry will be visible. Watch the video below to learn how to view geometry in Paraview.

<p align="center"><a href="http://www.youtube.com/watch?feature=player_embedded&v=VWjQ-iHcaxA
" target="_blank"><img src="https://user-images.githubusercontent.com/56687624/90137604-c258e180-dd6d-11ea-8917-bc20437937f0.png" height="400" /></a></p>

**Instructions:** To make the geometry visible click the "Apply" button and also the small eyeball icon on the left hand side. Then select "id" and "surface" in the dropdown menus to view the geometry. The threshold and slice operations can then be used to view specific parts of the geometry. (Instructions with screenshots are also provided in the [presentation](https://slides.com/openmc_workshop/neutronics_workshop/#/14/1)).

- Try using the threshold operation to remove the vacuum cell. Set the threshold to 0 then click the "Apply" button.

OpenMC has a plotter which can also be used for viewing 3D geometry. This has been pre-installed in the Docker image. To use the OpenMC plotter it must be run from the folder containing the xml files which are created by the Python API. The OpenMC plotter repository has [more details](https://github.com/openmc-dev/plotter) on how to use the application.

- Try running the OpenMC plotter using the ```openmc-plotter``` command and visualize the geometry.

**Learning Outcomes**

- Construction of simple Constructive Solid Geometry (CSG) geometry.
- Visualisation of models using 2D slices.
- Visualisation of models using 3D cube geometry.

**Next task:** [Task 3 - Visualizing neutron tracks - 20 minutes](https://github.com/ukaea/openmc_workshop/tree/master/tasks/task_3)