
import ghalton
import numpy as np
import plotly.graph_objects as go
from skopt import gp_minimize
from skopt.utils import load

from openmc_model import objective

res = load('saved_optimisation_2d.dat')

print('Optimal Li6 enrichment = ', res.x[0])
print('Optimal thickness = ', res.x[1])
print('Maximum TBR = ', -res.fun)

fig = go.Figure()

fig.add_trace(go.Scatter3d(name='All TBR values found',
                         x=[x[0] for x in res.x_iters],
                         y=[x[1] for x in res.x_iters],
                         z=-res.func_vals,
                         mode='markers'
                        )
             )

fig.add_trace(go.Scatter3d(name='Starting points',
                         x=[x[0] for x in res.x_iters][0:30],
                         y=[x[1] for x in res.x_iters][0:30],
                         z=-res.func_vals[0:30],
                         mode='markers'
                        )
             )

fig.add_trace(go.Scatter3d(name='Maximum TBR value found',
                         x=[res.x[0]],
                         y=[res.x[1]],
                         z=[-res.fun],
                         mode='markers'
                        )
             )

fig.update_layout(title='Optimal Li6 enrichment and blanket thickness',
                  scene={'xaxis': {'title': 'Li6 enrichment percent'},
                         'yaxis': {'title': 'Blanket thickness'},
                         'zaxis': {'title': 'TBR'}
                        }
                 )

fig.show()
