## <a name="task4"></a>Task 4 - Finding neutron interactions with mesh tallies

Google Colab link: [Task_4](https://colab.research.google.com/drive/1TVgCaEU_GAnJziNuyDFEvDfFYLU-fQaJ)

Please allow 15 minutes for this task.

Expected outputs from this task are also in the [presentation](https://slides.com/openmc_workshop/neutronics_workshop/#/16).

OpenMC uses 'tallies' to measure parameters such as particle flux, absorption and other interactions, to obtain useful information from the simulation. Tallies can be recorded on model cells, surfaces or on a superimposed mesh. In this task mesh tallies will be produced and visualized.  The example script contains a simple hollow sphere geometry of a single material, a 14 MeV point source.

- Try opening the example script ```coder 1_example_neutron_flux.py```and identify the mesh tally which measures neutron flux. 

- Try running the example script ```python 1_example_neutron_flux.py```

You should see plots of the simple sphere geometry and the isotropic point source, as shown below. The colour map shows the neutron flux, as tallied by the mesh, which is seen to reduce as one moves away from the point source.

<p align="center">
<img src="https://user-images.githubusercontent.com/56687624/90137942-36938500-dd6e-11ea-8b51-5593c522aa9f.png" height="300">
<img src="https://user-images.githubusercontent.com/56687624/90137945-37c4b200-dd6e-11ea-8393-c25f4c1f1b93.png" height="300">
</p>

<p align="center"><i>Left = Geometry Plot, Right = Flux Plot</i></p>

- Try changing the "flux" tally to an "absorption" tally and re-run the simulation.

The next example script is the ```2_example_neutron_flux_tokamak.py``` file which measures tritium production on a mesh in a simple tokamak geometry. 

The model still has a point source but now it is located at x=150 y=150 z=0. The tritium production mesh tally is now 3D and is displayed in 3D using paraview.

- Try running the script with the following command ```python 2_example_neutron_flux_tokamak.py``` and use the log scale within Paraview to show the tritium production more clearly. Watch the video below to learn how to do this.

<p align="center"><a href="http://www.youtube.com/watch?feature=player_embedded&v=be3G3ceQSWU
" target="_blank"><img src="https://user-images.githubusercontent.com/56687624/90137972-3dba9300-dd6e-11ea-9663-108518bc7033.png" height="400" /></a></p>

Further instructions can also be found in the [presentation](https://slides.com/openmc_workshop/neutronics_workshop#/16/1).

- Try changing the mesh tally from (n,Xt) to absorption to see the impact of the center column.

This should produce a 3D view of the mesh tally similar to the plots shown below.

<p align="center">
<img src="https://user-images.githubusercontent.com/56687624/90137982-3f845680-dd6e-11ea-8074-6c1e8e946dda.png" height="300">
<img src="https://user-images.githubusercontent.com/56687624/90137986-414e1a00-dd6e-11ea-9551-15b84ba9b63e.png" height="300">
</p>

<p align="center"><i>Left = Tritium production, Right = Neutron absorption</i></p>

OpenMC has a plotter which was first introduced in task 2 to view geometry can also be used for viewing mesh tallies. 

- Try running the OpenMC plotter using the ```openmc-plotter``` command and visualize the geometry.

- Try visualizing the mesh tally within the openmc-plotter by using the menus. Select data -> open statepoint and then select the "tally_on_mesh" tally within the tally dock.

**Learning Outcomes**

- How mesh tallies can be used in neutronics simulations to measure a variety of different reactions such as neutron absorption, tritium production and flux. 
- How neutrons are dissipated around the reactor.

**Next task:** [Task 5 - Finding the neutron and photon spectra - 15 minutes](https://github.com/ukaea/openmc_workshop/tree/master/tasks/task_5)