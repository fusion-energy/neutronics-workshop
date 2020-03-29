
import numpy as np
from skopt import gp_minimize
import plotly.graph_objects as go

from openmc_model import objective
# objective is a function that returns -1 the TBR value when provided with the Li6 enrichment as an argument


# This returns an scipy optimisation object
res_gp = gp_minimize(func=objective,
                     x0=[[0],[100]],  # specifying first simulation coordinates (these are the periphery of the parameter space)
                     y0=[0.15773, 0.92599],  # specifying results of first simulation coordinates
                     dimensions=[(0, 100)],  # as these are integers values the optimiers only tries integers
                     n_calls=12,
                     verbose=True)

print('Optimal Li6 enrichment = ', res_gp.x[0])
print('Maximum TBR = ', -res_gp.fun)

fig = go.Figure()


fig.add_trace(go.Scatter(name='All TBR values found',
                         x=[x[0] for x in res_gp.x_iters],
                         y=-res_gp.func_vals,
                         mode='markers'
                        )
             )


fig.add_trace(go.Scatter(name='Maximum TBR value found',
                         x=res_gp.x,
                         y=[-res_gp.fun],
                         mode='markers'
                        )
             )

fig.update_layout(title='Optimal Li6 enrichment',
                  xaxis={'title': 'Li6 enrichment percent'},
                  yaxis={'title': 'TBR'}
                 )

fig.show()