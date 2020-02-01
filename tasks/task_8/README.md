
## <a name="task8"></a>Task 8 - Survey breeder blanket designs for tritium production

Google Colab Link: [Task_8](https://colab.research.google.com/drive/1fDOBm2YMojXVtucPQQ9XSjFqtzMibvjD)

Please allow 25 minutes for this task.

Expected outputs from this task are in the [presentation](https://slides.com/openmc_workshop/neutronics_workshop/#/20).

This task is more open ended - the aim is to find the impact of lithium 6 enrichment and blanket thickness on the TBR for different breeder materials.

There are several candidate breeder materials including a lithium ceramic (Li4SiO4), Flibe, Lithium lead (eutectic) and pure lithium. Each material can have it's Li6 content enriched and the blanket thickness varied and these have an impact on the TBR.

Examine the ```1_simulate_with_random_selection.py``` file and try to understand how the model is created and particularly how the simulation parameters are saved in a json file with a unique ID.

- Currently the input parameters for Li6 enrichment and blanket thickness are randomly sampled so you might want to change this to speed up the search.

Run the script to perform simulations. There are two scripts to help you analyse the results.

- ```2_plot_simulation_results_2d.py``` will allow you to see the impact of changing either the Li6 enrichment or the blanket thickness on TBR. This will need running with an argument which is used to filter the simulation data. ```python 2_plot_simulation_results_2d.py --sample random```

- ```3_plot_simulation_results_3d.py``` will allow you to see the combined impact of changing the Li6 enrichment and the blanket thickness on TBR. This will need running with an argument which is used to filter the simulation data. ```python 3_plot_simulation_results_3d.py --sample random```

For 200 simulations, the 2D plots should look similar to the plots below.

<p align="center"><img src="images/TBR_vs_enrichment_fraction.png" height="500"></p>

<p align="center"><img src="images/TBR_vs_thickness.png" height="500"></p>

For 525 simulations, the 3D plots should look similar to the example plot shown below.

<p align="center"><img src="images/TBR_vs_thickness_vs_enrichment_fraction_lithium.png" height="500"></p>

Using random sampling to cover the parameter space is inefficient. Halton sampling is one method that is able to cover the parameter space more effiicently.

- Try using Halton sampling to explore the parameter space with the following command ```python 4_simulate_with_halton_sample.py```

- Try replotting the graphs to see how the parameter space has been more efficiently covered. ```python 2_plot_simulation_results_2d.py --sample halton``` and ```python 3_plot_simulation_results_3d.py --sample halton```

**Learning Outcomes**

- A simple parameter study that makes use of unique ID's for each simulation.
- Some candiate breeder materials can meet the TBR requirment with a thinner blanket.
- Increasing the thickness of blanket or lthium 6 enrichment tend to increase the TBR but not for all materials.
- Random slection of parameters is not an efficient way of covering the search space or finding the optimal.