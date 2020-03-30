
import json
import numpy as np
from skopt import gp_minimize
import plotly.graph_objects as go

from openmc_model import objective
# objective is a function that returns TBR value when provided with the Li6 enrichment as an argument

# Note, optimisation functions tend to minimise the value therefore there are a few negative signs in these scripts


# This call to gp_minimize is able to optimise black box functions involving noisy data
# The resulting res_gp is an scipy optimisation object that includes iterations, final value
res_gp = gp_minimize(func=objective,
                     dimensions=[(0., 100.)],
                     n_calls=10,
                     n_random_starts=1, # this is 10 by default but as this is a simple 1d problem without local minima we can reduce this
                     verbose=True)

print('Optimal Li6 enrichment = ', res_gp.x[0])
print('Maximum TBR = ', -res_gp.fun)



# The rest of this script is plotting the results
fig = go.Figure()

# plotting iterations of the optimisation  algorithum 
fig.add_trace(go.Scatter(name='All TBR values found',
                         x=[x[0] for x in res_gp.x_iters],
                         y=-res_gp.func_vals,
                         mode='markers'
                        )
             )

# plotting the maximum TBR found with the optimisation
fig.add_trace(go.Scatter(name='Maximum TBR value found',
                         x=res_gp.x,
                         y=[-res_gp.fun],
                         mode='markers'
                        )
             )


# plotting the previously calculated values
with open('enrichment_vs_tbr.json', 'r') as f: 
    data = json.load(f)
fig.add_trace(go.Scatter(name='Maximum TBR value found',
                         x=[i[0] for i in data],
                         y=[i[1] for i in data],
                         mode='lines'
                        )
             )

fig.update_layout(title='Optimal Li6 enrichment',
                  xaxis={'title': 'Li6 enrichment percent'},
                  yaxis={'title': 'TBR'}
                 )

fig.show()


# The optimser can be steered a bit but providing non random starting points (x0) 
# and optionally the values for these points(y0)
# Here is an example of how to 'help' the optimiser
# res_gp = gp_minimize(func=objective,
#                      dimensions=[(0., 100.)],  # these are integers values which reduces the number of options to try
#                      x0=[[0.],[100.]],  # specifying first simulation coordinates (these are the periphery of the parameter space)
#                      y0=[0.15773, 0.92599],  # specifying results of first simulation coordinates
#                      n_random_starts=0,  # setting this to 0 as well spaced starting points have been set
#                      n_calls=10,
#                      verbose=True)