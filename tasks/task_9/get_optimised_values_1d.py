
import json

import adaptive
from skopt import gp_minimize
from skopt.utils import dump

from openmc_model import objective

# Optimisation for 1D EXAMPLE

# Uses adaptive sampling methods from task 8 to obtain starting points for the optimiser
learner = adaptive.Learner1D(objective, bounds=(0, 100))
runner = adaptive.Runner(learner, ntasks=1, goal=lambda l: l.npoints > 7)
runner.ioloop.run_until_complete(runner.task)


# Gaussian Processes based optimisation that returns an SciPy optimisation object
res = gp_minimize(objective,          # the function to minimize
                  [(0., 100.)],       # the bounds on each dimension of x
                  n_calls=30,         # the number of evaluations of f
                  n_random_starts=0,  # the number of random initialization points
                  verbose=True,
                  x0=[[i] for i in list(learner.data.keys())], # initial data from the adaptive sampling method
                  y0=list(learner.data.values()) # initial data from the adaptive sampling method
                  )

# Saves the optimisation simulation reults to a file
dump(res, 'saved_optimisation_1d.dat')