
## <a name="task8"></a>Task 8 - Techniques for sampling parameter space

Google Colab Link: [Task_8](insert google colab link)

Please allow 25 minutes for this task.

Expected outputs from this task are in the [presentation](insert presentation list).

The aim of this task is to explore sampling techniques for performing simulations across a parameter space of interest.
A parameter space may be surveyed for several reasons. In the context of tritium breeding, this may be to measure the impact of a parameter on tritium breeding.

There are many ways to sample a parameter space, but some provide significant advantages to others.

In this task, we will use a simple ICF model (a sphere with a first wall), and perform simulations to measure the impact of varying lithium 6 enrichment and the breeder to multiplier fraction on TBR. Take a look at the ```openmc_model.py``` script to see the specific details of the model.

Using this model, simulations will be performed by varying blanket enrichment between 0 and 100%, and breeder percent in breeder plus multiplier volumes between 0 and 100%. These ranges define the 'parameter space' over which simulations are performed. We will demonstrate a variety of sampling techniques to sample the parameter space and discuss the advantages and disadvantages of each.

# Random Sampling

The easiest way to sample a parameter space is to use random sampling, where values are chosen at random from the parameter space.

Take a look at the ```1_simulate_with_random_sample.py``` script, which defines input parameters for the model defined in the ```openmc_model.py``` script. This script calculates TBR for given values of enrichment and breeder to multiplier ratios. Try to understand how the values of enrichment and breeder to multiplier ratios are randomly varied.

Run the script using the command ```python3 1_simulate_with_random_sample.py```, using the -n flag to specify the number of simulations. The results of the simulations are saved in the 'outputs' folder of the task directory.

The task folder also contains a script called ```plot_sampling_coordinates.py``` which plots TBR as a function of breeder to multiplier ratio and enrichment for each sampling method. Run this script to plot the results of the random simulations. This should look similar to the plot below.

<p align="center"><img src="https://user-images.githubusercontent.com/56687624/90138378-d3eeb900-dd6e-11ea-9d00-4615d5050c18.png" height="400"></p>

As shown, the simulations have been performed randomly across the parameter space of enrichment and breeder to multiplier ratio.

The main advantage of random sampling is that it is an 'unbiased' sampling technique, meaning simulations are performed across the entire parameter space at the same rate. This means that all simulations contribute to the overall data trend and additional simulations can be easily performed to increase accuracy.

However, random sampling is an inefficient sampling technique as it leads to point clusters and voids across the parameter space. Some simulations are performed with very similar input parameters,but some areas of parameter space are sparsely sampled. This is inefficient because some simulations provide little additional information about the overall trend and their computational time would be better spent sampling sparsely-sampled areas.

Overall, random sampling is a simple technique for performing unbiased simulations over a parameter space, however, its poor spatial distribution of sample points makes it a highly inefficient technique.

# Grid Sampling

Another sampling technique is 'grid sampling', where samples are taken at regular grid intervals across the parameter space, as shown below. This is an example of 'biased sampling' as the samples are performed in order according to the grid. An example of this is shown below.

<p align="center"><img src="https://user-images.githubusercontent.com/56687624/90138394-d8b36d00-dd6e-11ea-8e0f-04df9cb06b36.gif" height="250"></p>

Open the ```2_simulate_with_grid_sample.py``` script and try to understand how a grid of enrichment and breeder to multiplier ratios values defines the input parameters for the simulations; also note the order in which these simulations are performed.

Run the ```2_simulate_with_grid_sample.py``` script with the -n flag to specify the number of simulations and plot the results using the ```plot_sampling_coordinates.py``` script. Two graphs should be plotted showing the results for both random and grid simulations. Compare the two sampling methods.

<p align="center"><img src="https://user-images.githubusercontent.com/56687624/90138402-dc46f400-dd6e-11ea-8af4-8cde0d7969c5.png" height="400"></p>

As shown, grid sampling has a better spatial distribution of sample points than random sampling. 

Grid sampling maximises the spatial distribution of sample points across a parameter space by avoiding point clustering and, therefore, maximises the amount of useful information obtained from each simulation. As a result, grid sampling is a highly efficient sampling technique for covering a parameter space.

However, as simulations are performed in order according to the defined grid, they are biased towards the first parameter values in the grid. For example, ```2_simulate_with_grid_sample.py``` performs simulations with enrichment = 0 for all blanket breeder percents before enrichment is changed. This means that all simulations across the grid must be performed before a data trend across the entire parameter space can be observed.
This is the main disadvantage of grid sampling as more simulations than are necessary may be performed, and it is difficult to efficiently add sample points to the existing data without performing a complete new grid search 'in-between' the existing data points. On the other hand, random sampling is unbiased meaning the data trend across the parameter space can be observed with a small number of simulations and additional sample points can be added easily.

Overall, grid sampling is a more efficient sampling technique than random sampling, but its bias towards initial parameter values makes it unsuitable for most applications. Instead, we tend to use more advanced 'quasi-random' or 'adaptive' techniques to improve sampling efficiency.

# Halton Sampling

Halton sampling is a quasi-random sampling technique based on the [halton sequence](link). Using a [quasi-random number sequence](link) based on coprime numbers, halton sampling allows an entire parameter space to be sampled both efficiently and with a element of random nature. Like random sampling, halton sampling allows data trends across the parameter space to be observed with a small number of samples, but distributes the sample points more efficiently throughout the parameter space.

Open the ```3_simulate_with_halton_sample.py``` script and try to understand how the halton sequence is used to generate inputs for the simulation.

Run this script and plot the results. The graph produced should look similar to the plot below.

<p align="center"><img src="https://user-images.githubusercontent.com/56687624/90138407-dd782100-dd6e-11ea-905b-0b1617b48d3a.png" height="400"></p>

As you can see, the sample points have a much better spatial distribution across the parameter space than random sampling.

The main advantage of halton sampling is that it allows the efficient sampling of an entire parameter space. Sample points are not clustered meaning each simulation provides a large amount of additional information about the overall data trend, and its quasi-random nature means additional samples can be added efficiently.
However, the main disadvantage of halton sampling is that it still surveys the entire parameter space of interest. This can lead to the excessive sampling of 'flat' regions of the parameter space, i.e. areas where there is little variation in the overall trend, resulting in inefficiency. 

Overall, halton sampling is better than random and grid sampling as it provides good spatial distribution and allows more samples to be added easily and efficiently. Ideally, however, we want to avoid over-sampling flat regions of the parameter space to further improve efficiency and reduce the number of simulations required. This is where 'adaptive' sampling is advantageous.

# Adaptive Sampling

Adaptive sampling is a sampling technique which uses data fitting to decide where in the parameter space to sample next. By fitting the data from samples that have already been taken, the overall data trend across the parameter space can be roughly predicted and an informed choice on where to sample the parameter space next can be made. Regions in the parameter space where the data trend is relatively flat do not have to be sampled as densely as rapidly changing regions. By allowing sample points to be chosen based on the data trend, computational time can be focused on the most important parts of the data trend.

Open the ```4_simulate_with_adaptive_sample.py``` script and try to understand how 'adaptive' python module is used to adaptively sample the parameter space. Simulations begin by sampling the limits of the parameter space (i.e. (enrichment, breeder percentage) = (0, 100), (100, 0), (0, 100), (100, 100)) and then fitting these points to predict where TBR is varying most rapidly across the parameter space. A sample is then taken at this point and the process repeated. There are many ways to fit existing data points during adaptive sampling, however, this particular example uses [gaussian process regression](link). 

Run this script and plot the results. The graph produced should look similar to the plot below.

<p align="center"><img src="https://user-images.githubusercontent.com/56687624/90138409-dea94e00-dd6e-11ea-8424-bc4e46855eae.png" height="400"></p>

As mentioned, the most important parts of a data trend are (usually) the regions where the data is changing as a function of parameter values. In our example, these are the regions where TBR is changing as a function of enrichment and breeder percentage. I.e. we do not want to excessively sample regions where TBR changes negligibly as a function of enrichment and breeder percentage.
As shown, the parameter space is densely sampled in regions where TBR is changing most rapidly, and sparsely sampled in regions where TBR is changing negligibly.

The main advantage of adaptive sampling is that it is the most efficient technique for sampling a parameter space with an unknown distribution. By iteratively fitting the data and performing additional simulations we can determine an accurate distribution across the parameter space with fewer simulations than any other sampling technique.
It is not a perfect solution, however, because over-sampling could still take place if we don't specify when to stop sampling. I.e. we would calculate the data fit and stop when we reach an acceptable uncertainty. Also could miss areas which have less prominent trends? I.e we don't get the whole picture across the whole parameter space.

Overall, adaptive sampling allows computational time to be focused on the most important parts of a distribution and is a highly efficient way of sampling a parameter space and, therefore, performing simulations.

To more accuratly cover this parameter space more than the default 40 samples would be required.


Possible Learning Outcomes:
- The optimal breeder percent in breeder plus multiplier volume changes for different amounts of lithium enrichment.
- Increasing the lthium 6 enrichment tends to increase the TBR.
- Random slection of parameters is not an efficient way of covering the search space or finding the optimal.