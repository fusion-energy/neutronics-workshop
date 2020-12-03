
import json

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from skopt.acquisition import gaussian_ei
from skopt.utils import load

from openmc_model import objective

# Note, optimisation functions tend to minimise the value therefore there are a few negative signs in these scripts


# Loads true data for comparison
data = pd.read_json('1d_tbr_values.json')

x_data=data['breeder_percent_in_breeder_plus_multiplier']
fx=-data['tbr']

res = load('saved_optimisation_1d.dat')

fig = go.Figure()

# Plot samples from optimsation points
fig.add_trace(go.Scatter(x = [i[0] for i in res.Xi],
                         y = [-i for i in res.yi],
                         name="Samples from optimisation",
                         mode='markers',
                         marker=dict(color='red', size=10)
                        )
                )

# Plot true function.
fig.add_trace(go.Scatter(name="True value (unknown)",
                          x = x_data,
                          y = [-i for i in fx],
                          mode='lines',
                          line = {'shape': 'spline'},
                          marker=dict(color='green')
                         )
              )

fig.update_layout(title='Optimal breeder percent in breeder plus multiplier',
                  xaxis={'title': 'breeder percent in breeder plus multiplier', 'range': [0, 100]},
                  yaxis={'title': 'TBR', 'range': [0.1, 2]}
                 )


print('Maximum TBR of ', -res.yi[-1], 'found with a breeder percent in breeder plus multiplier of ', res.Xi[-1])


fig.write_html("1d_optimization_graph.html")
try:
    fig.write_html("/my_openmc_workshop/1d_optimization_graph.html")
except (FileNotFoundError, NotADirectoryError):  # for both inside and outside docker container
    pass

fig.show()
