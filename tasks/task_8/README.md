
## <a name="task8"></a>Task 8 - Techniques for sampling parameter space

Google Colab Link: [Task_8](insert google colab link)

Please allow 25 minutes for this task.

Expected outputs from this task are in the [presentation](insert presentation list).

The aim of this task is to explore sampling techniques for performing simulations across a parameter space of interest.
A parameter space may be surveyed for several reasons. In the context of tritium breeding, this may be to determine the impact of a parameter on tritium breeding.

There are many ways to sample a parameter space, but some provide significant advantages to others.

In this task, we will use a simple tokamak model consisting of a central solenoid and shield, and a surrounding breeder blanket. As shown below.

Using this model, we will perform simulations to determine the impact of changing the enrichment and thickness of the blanket cell on TBR.
To do this, we will vary enrichment between 0 and 1, and thickness between 1cm and 500cm. This is our 'parameter space', which we will sample to perform simulations and demonstrate the advantages and disadvantages of different sampling techniques.

# Random Sampling

The easiest way to sample a parameter space is to use random sampling, where values for each parameter are chosen at random.

Take a look at the ```1_simulate_with_random_sample.py``` script, which defines input parameters for the model defined in the ```openmc_model.py``` script. Try to understand how the values of enrichment and thickness are randomly varied.

Run the script using the command ```python3 1_simulate_with_random_sample.py```, using the -n flag to specify the number of simulations to perform. The results of the simulation are saved in the 'outputs' folder of the task folder.

The task folder also contains a script called ```plot_sampling_coordinates.py``` which plots TBR as a function of thickness and enrichment for each sampling method.

Run the script to show the results of the random simulations. This should look similar to the plot below.

INSERT IMAGE

As shown, the simulations have been performed randomly across the parameter space of enrichment and thickness.

The main advantage of random sampling is that it is an 'unbiased' sampling technique because simulations are performed across the entire parameter space at the same rate. This means that all simulations contribute to the overall data trend and additional simulations can be easily performed to increase precision.

However, random sampling is an inefficient way to sample a parameter space. As you can see, some points on the graph are very close together, meaning some simulations performed had very similar input parameters. This is inefficient because these simulations provide little information about the overall data trend and are, therefore, a waste of computational time. It would be better to 
having a better spatial distribution of simulation points would mean the same precision data could be obtained with a smaller number of simulations.

Overall, random sampling is an easy technique for performing unbiased simulations over a parameter space, however, its poor spatial distribution of sample points makes it an inefficient way of performing simulations.


# Grid Sampling

Another sampling technique is 'grid sampling', where samples are taken at regular grid intervals across the parameter space. This is an example of 'biased sampling' as the samples are ordered according to the grid.

Take a look at the ```2_simulate_with_grid_sample.py``` script and try to understand how a grid of enrichment and thickness values is defined as the input parameters for the simulations. Also note the order in which these simulations are performed. 

Run the ```2_simulate_with_grid_sample.py``` script with the -n flag to specify the number of simulations performed and plot the results using the ```plot_sampling_coordinates.py``` script. This should show the results of both the random simulations and the grid simulations on the same graph, similar to the graph shown below.

The main advantage of grid sampling is that it maximises the spatial distribution of sample points across the parameter space. As shown, 
Using grid sampling extracts the maximum amount of useful data from a number of simulations, maximising the efficiency.

This means that the maximum amount of 

However, a major disadvantage of grid sampling is that the simulations are performed in the order of the defined grid and are, therefore, biased towards the first parameter values.
This means that all simulations must be performed to obtain the overall data trend across the whole parameter space of interest. Not being able to see the overall data trend until all simulations have completed means that we may end up performing many more simulations that are actually needed.
Grid sampling also provides an additional problem in that it is hard to efficiently add further simulations to the existing data set. A whole new grid would need to be defined and simulated to completion, whereas any number of simulations based on random sampling techniques contribute to the trend as a whole.

Grid sampling is, therefore, not a good technique for sampling a parameter space. Instead, we 

As shown, the simulations performed 

The main advantage of grid sampling is that it maximises the spatial distribution of sample points across the parameter space. As shown, the parameter space of interest is covered by the s

SHOW A COMPARISON BETWEEN RANDOM AND GRID SAMPLING FOR THE SAME NUMBER OF POINTS.

As a result, the maximum amount of useful information is extracted from the smallest number of simulations.This maximises the spatial distribution of sample points across the parameter space meaning This is an example of a 'biased' sampling technique as the 

Instead of randomly sampling a parameter space, we can perform a 'grid sample'. This is where samples of the parameter space are taken in a regular grid

An alternative sampling technique is 'grid sampling', where samples of a parameter space are taken in a regular grid

Instead of randomly sampling a parameter space, we can perform a grid sample. This is where samples will be taken in a regular grid over the parameter space. This provides maximum spatial distribution of the points, meaning the maximum amount of useful information is extracted from the smallest number of simulations.

```2_simulate_with_grid_sample.py```

The problem with grid sampling, however, is that the simulations are performed in order.
This means there is a bias towards the first simulations and we need to wait for all simulations to be performed before an overall trend across the whole parameter space can be seen.
Also makes it difficult to perform additional simulations as you would have to track where the grid search has got up to.
Therefore, ideally, we would use a sampling technique that had elements of a random nature such that simualations are unbiased, but still have a good spatial distribution.

Run the script.
These outputs are saved in the same output folder as any previously run simulations, however, the output files contain a tag showing the sampling techique used to perform the simulation.
Running the plotting script again, the plotting script will now plot the results by grouping the results for each sampling technique separately.
Run this script to compare grid sampling and random sampling.


# Halton Sampling

Halton sampling is a sampling technique based on the halton sequence. This sequence is a quasi-random number sequence based on coprime numbers.
More information can be found here, but what is most important to know is that Halton sampling allows parameter space to be covered more efficiently.

```3_simulate_with_halton_sample.py```







Maybe use some of these
- Some candiate breeder materials can meet the TBR requirment with a thinner blanket.
- Increasing the thickness of blanket or lthium 6 enrichment tend to increase the TBR but not for all materials.
- Random slection of parameters is not an efficient way of covering the search space or finding the optimal.