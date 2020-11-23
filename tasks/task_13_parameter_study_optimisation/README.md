
## This task is currently under development and may not work

## <a name="task9"></a>Task 9 - Optimize a breeder blanket for tritium production

Please allow 25 plus minutes for this task depending on the computational power available.

The previous task sampled from the available parameters and aimed to cover the parameter space efficiently. This task uses  Scikit-opt Gaussian Processing to home in on the optimal solution. In optimisation algorithms it is common to see a combination of exploration and exploitation to find the optimal value.

The first stage of the optimisation is to 

Open the first file and try to identify the initial sample points, the optimisation section and the part where the code saves the output as a file.

- ```code get_optimised_values_1d.py```

Then run this optimisation script, it should save a .dat file which contains all the simulations sampled along the route.

- ```python get_optimised_values_1d.py```

We can compare the results with previously calculated results to see how the optimiser did. A series of TBR results have previously be calculated using ```python get_true_values_1d.py``` and saved to a json file. A plot of the optimisation which loads the true results (1d_tbr_values.json file) and the optimisation samples and initial samples (saved_optimisation_1d.dat file) can now be made.

Try plotting the graph and using the interactive scroll bar to see how the optimiser samples points 

- ```python 1_plot_1d_optimisation.py.py```

The same techniques can be applied to N dimensional problems but the number of simulations required increases. The next example is a 2D dimensional problem where the optimal breeder to multiplier ratio and enrichment are being found. Open the optimisation script to identify the differences in the bounds of the 1d and 2d problem.

- ```meld get_optimised_values_2d.py```

Then run this optimisation script, it should save a .dat file which contains all the simulations sampled along the route.

- ```python get_optimised_values_2d.py```

Again we can compare the results with the true results to see how the optimiser did. The a grid of TBR results have previously be calculated using ```python get_true_values_2d.py``` and saved to a json file. A plot of the optimisation which loads the true results (2d_tbr_values.json file) and the optimisation samples and inital samples (saved_optimisation_2d.dat file) can now be made.

There are currently two graphs to view these results, try both and let me know which you prefer

- ```python 2_plot_2d_optimisation_contour.py```

- ```python 2_plot_2d_optimisation_scatter.py```



**Learning Outcomes**

Introduction to a methods of optimising a neutronics results in 1d and 2d.
Appreciation that for high dimensional space approaches to reduce the amount of sampling are needed.
Understand that there are several factors that can be changed to increase the TBR

**Next task:** [Task 10 - Using CAD geometry - 30 minutes](https://github.com/ukaea/openmc_workshop/tree/master/tasks/task_10)