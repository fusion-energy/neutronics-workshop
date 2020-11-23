
import ghalton
import numpy as np
import plotly.graph_objects as go
from skopt import gp_minimize
from skopt.utils import load
import pandas as pd

from openmc_model import objective
# loads up the optimisation data
res = load('saved_optimisation_2d.dat')

print('Optimal breeder_percent_in_breeder_plus_multiplier_ratio = ', res.x[0])
print('Optimal Li6 enrichment = ', res.x[1])
print('Maximum TBR = ', -res.fun)

# Loads true data for comparison
data = pd.read_json('2d_tbr_values.json')
x_data=data['breeder_percent_in_breeder_plus_multiplier']
y_data=data['blanket_breeder_li6_enrichment']
z_data=data['tbr']


fig = go.Figure()

fig.add_trace(go.Scatter3d(name='TBR values found during optimisation',
                         x=[x[0] for x in res.x_iters],
                         y=[x[1] for x in res.x_iters],
                         z=-res.func_vals,
                         mode='markers'
                        )
             )

fig.add_trace(go.Scatter3d(name='True values',
                         x=x_data,
                         y=y_data,
                         z=z_data,
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

fig.update_layout(title='Optimal Li6 enrichment and breeder percent in breeder plus multiplier',
                  scene={'yaxis': {'title': 'Li6 enrichment percent'},
                         'zaxis': {'title': 'breeder percent in breeder plus multiplier'},
                         'zaxis': {'title': 'TBR'}
                        }
                 )

fig.write_html("2d_optimization_graph_scatter.html")
try:
    fig.write_html("/my_openmc_workshop/2d_optimization_graph_scatter.html")
except (FileNotFoundError, NotADirectoryError):  # for both inside and outside docker container
    pass

fig.show()
