
## <a name="task8"></a>Task 8 - Techniques for sampling parameter space

Google Colab Link: [Task_8](insert google colab link)

Please allow 25 minutes for this task.

Expected outputs from this task are in the [presentation](insert presentation list).

The aim of this task is to explore sampling techniques for performing simulations across a parameter space of interest.
A parameter space may be surveyed for a number of reasons. In the context of tritum breeding, simulations may be performed across a parameter space to determine the impact of that parameter on tritum breeding.

There are many ways to sample a parameter space, but some provide significant advantages to others.

In this task, we will use a simple tokamak model consisting of a central solenoid and shield, and a surrounding breeder blanket. As shown below.

Using this model, we will perform simulations to determine the impact of changing the enrichment and thickness of the blanket cell on TBR.
To do this, we will vary enrichment between 0 and 1, and thickness between 1cm and 500cm. This is our 'parameter space', which we will sample in a variety of different ways to perform simulations, and demonstrate the advantages and disadvantages of each.

# Random Sampling

The easiest way to sample a parameter space is to use random sampling. 

Open the ```1_simulate_with_random_sample.py``` file and try to understand how the values for enrichment and thickness are randomly varied.

Run the script to perform simulations. 

The task folder also contains a script called ```plot_sampling_coordinates.py```. Running this script will produce plots showing how TBR varies as a function of thickness and enrichment.

Run this script to see how the simulation settings have been randomly sampled from the parameter space.
This should look similar to the plot shown below.

As you can see, randomly sampling the values of enrichment and thickness means simulations are performed across the parameter space of interest.
An advantage of using random sampling is that results are obtained across the entire parameter space (i.e. perform simulations across the whole space instead of it being ordered - you know what i mean. We can just run more random simulations and add them to our existing data set with no problem), but the points themselves do not have the best spatial distribution.
(each simulation contributes to the overall trend)
As you can see, some points are very close together meaning some simulations have been performed with very similar input parameters. Therefore, some simulations provide very little additional information about the overall trend across the parameter space. This wastes computational time and is, therefore, very inefficient.

Overall, although random sampling allows an easy way to perform simulations over a parameter space, the poor spatial distribution of results means that it is an inefficient way of performing simulations.

# Grid Sampling

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