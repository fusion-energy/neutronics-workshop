

## <a name="task3"></a>This task is currently not working as source points are no longer included in the openmc statepoint file for fixed source problems.

## <a name="task3"></a>Task 3 - Visualizing neutron tracks

Google Colab Link: [Task_3](https://colab.research.google.com/drive/1kOFp9s3utX0o2D7llXXJ6pyyrvK_V-Nz)

Please allow 20 minutes for this task.

Expected outputs from this task are also in the [presentation](https://slides.com/openmc_workshop/neutronics_workshop/#/15).

When OpenMC runs, a statepoint (output) file is produced which contains information about the neutron source, tally results and additional information. This task focuses on extracting neutron source information from the statepoint file, while tasks 4, 5 and 6 focus on extracting other information from the statepoint file.

The ```1_plot_neutron_birth_energy.py``` file shows you how to access the statepoint file created during the simulation. In this example the birth energy of all the simulated neutrons is extracted. A plot of the energy distribution can be produced by running the script.

```python 1_plot_neutron_birth_energy.py```

The script will produce a plot of a mono-energetic energy source of 14 MeV neutrons, as shown below.

<p align="center"><img src="https://user-images.githubusercontent.com/56687624/90137797-051ab980-dd6e-11ea-842c-eaa0f3c02f5a.png" height="500"></p>

There are actually three different energy distributions available in the ```1_plot_neutron_birth_energy.py``` script (14 MeV monenergetic, Watt fission distribution, Muir fusion distribution).

- Try plotting the Watt and Muir spectra and compare them to the mono-energetic neutron source.

- Try changing the Muir plasma temperature from 20 KeV to 40 KeV.

In the next example the initial neutron birth locations and neutron trajectories for a very basic neutron point source are plotted. Again, this information is accessed from the statepoint file.

- Try running ```python 2_plot_neutron_birth_location.py``` to produce a plot of neutron birth  locations, the output should look similar to the plot shown below.

- Try running ```python 3_plot_neutron_birth_direction.py``` to produce a plot of neutron directions, the output should look similar to the plot shown below.

<p align="center">
<img src="https://user-images.githubusercontent.com/56687624/90137835-149a0280-dd6e-11ea-8fdc-6d154ed4240a.png" height="300">
<img src="https://user-images.githubusercontent.com/56687624/90137842-1663c600-dd6e-11ea-8f1f-98cbd75fc647.png" height="300">
</p>

<p align="center"><i>Left = Neutron birth locations, Right = Neutron initial directions</i></p>

Now open the next example source plotting script ```4_plot_neutron_birth_locations_plasma.py```. Look for the part in the script where the source is defined - you should notice that an external source library is used. The ```source_sampling.so``` file is a precompiled plasma source file containing neutron positions, energies and directions for a given plasma source. This file is in the task_3 directory.

- Try running ```python 4_plot_neutron_birth_location_plasma.py``` to produce a plot of neutron birth locations for a more realistic plasma source. The output should look similar to the plot shown below.

- Try running ```python 5_plot_neutron_birth_direction_plasma.py``` to produce a plot of birth neutron directions for a more realistic plasma source. The output should look similar to the plot shown below.

<p align="center">
<img src="https://user-images.githubusercontent.com/56687624/90137862-1cf23d80-dd6e-11ea-9a67-eb0e0399dded.png" height="300">
<img src="https://user-images.githubusercontent.com/56687624/90137867-1e236a80-dd6e-11ea-9fd1-8358c5785164.png" height="300">
</p>

<p align="center"><i>Left = Neutron birth locations, Right = Neutron initial directions</i></p>

OpenMC is also able to track particles as they pass through model geometries. Open the ```6_example_neutron_tracks.py``` script and notice that it contains ```model.run(tracks=True)```. This argument results in the creation of a h5 file for each neutron simulated which contains particle track information. 

The next example script defines a model of a hollow sphere made of two materials and a 14 MeV point source at the geometry centre.

- Try running ```python 6_example_neutron_tracks.py``` which simulates neutron movement through the geometry and produces particle h5 files from which neutron tracks can be visualized with the geometry.

**Instructions:** Watch the video below to learn how to load the geometry file, open the track files and slice the geometry such that the neutron tracks can be visualised. (Instructions with screenshots can also be found in the [presentation](https://slides.com/openmc_workshop/neutronics_workshop/#/15/4)).

<p align="center"><a href="http://www.youtube.com/watch?feature=player_embedded&v=uHTXw6Dza-Y
" target="_blank"><img src="https://user-images.githubusercontent.com/56687624/90137884-254a7880-dd6e-11ea-8850-e45a8e05fd1b.png" height="400" /></a></p>

- Looking at the tracks can you tell which material is water and which is zirconium?

**Learning Outcomes**

- How to access information on the particle positions, energy and direction from the simulation.
- How to visualize particle tracks through the geometry.