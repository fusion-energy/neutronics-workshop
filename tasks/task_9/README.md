
## <a name="task9"></a>Task 9 - Optimize a breeder blanket for tritium production

Google Colab Link: [Task_9](https://colab.research.google.com/drive/1Zak3lrQH6x2-As1vKskXtNmYs6mdRUgj)

Please allow 25 minutes for this task.

Expected outputs from this task are in the [presentation](https://slides.com/openmc_workshop/neutronics_workshop#/21).

The previous task sampled from the available parameters and used a brute force method of finding the optimal blanket composition. This task uses Gaussian processing to home in on the optimal solution and steer the sampling.

Open the following script which describes functions for constructing materials for use in simulations.

- ```material_maker_functions.py```

This task uses a [Gaussian process tool](https://github.com/C-bowman/inference_tools/blob/master/inference/gp_tools.py) developed by Chris Bowman to guide the simulations performed and optimize breeder blanket parameters for maximum TBR.

Take a look at the scripts below and try to understand how this works. Also try to understand how they use the material maker script to construct the model.

- ```lithium_enrichment_optimisation.py```

- ```lithium_enrichment_and_thickness_optimisation.py```. Note - This script does not currently work.

Initially, simulations are performed by sampling the parameter space of interest (according to the halton sequence) and the results fitted using Gaussian Regression. A further simulation is then performed using the parameters corresponding to max TBR as determined by the Gaussian fit. The simulation results are then fitted again, including this new point, and the process repeated. 

This iterative approach efficiently and accurately determines the point in the parameter space where TBR is maximum.

The output .gif shows how halton sampling is used to perform initial simulations before further simulations are informed by Gaussian interpolation.

<p align="center"><img src="tasks/task_9/images/output.gif" height="500"></p>

**Learning Outcomes**

- Halton sampling allows non-biased simulations to be performed over a parameter space.
- Data fitting can be used to optimise neutronics simulations.
