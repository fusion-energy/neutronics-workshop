
import adaptive
from skopt.utils import dump

from openmc_model import objective

# Optimisation for 1D example
learner = adaptive.SKOptLearner(objective,
                                dimensions=[(0., 100.)],
                                base_estimator="GP",
                                acq_func="gp_hedge",
                                acq_optimizer="lbfgs",
                               )
runner = adaptive.Runner(learner, ntasks=1, goal=lambda l: l.npoints > 40)

runner.ioloop.run_until_complete(runner.task)

dump(runner.learner, 'saved_optimisation_1d.dat')
