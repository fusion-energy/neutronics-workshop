
import json
from pathlib import Path

import ghalton
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.interpolate import griddata
from skopt import gp_minimize
from skopt.utils import load
from tqdm import tqdm

from inference.gp_tools import GpRegressor, RationalQuadratic
from openmc_model import objective
from scipy.interpolate import Rbf



res = load('saved_optimisation_2d.dat')

print('Optimal Li6 enrichment = ', res.x[0])
print('Optimal breeder percent in breeder plus multiplier = ', res.x[1])
print('Maximum TBR = ', -res.fun)

# Loads precomputed true data values for comparison
data = pd.read_json('2d_tbr_values.json')
x=list(data['breeder_percent_in_breeder_plus_multiplier'])
y=list(data['blanket_breeder_li6_enrichment'])
z=list(data['tbr'])

# creates a grid and interploates values on it
xi = np.linspace(0, 100, 100)
yi = np.linspace(0, 100, 100)
zi = griddata((x, y), z, (xi[None,:], yi[:,None]), method='linear')


fig = go.Figure()

# plots interpolated values as colour map plot
fig.add_trace(trace = go.Contour(
                z=zi,
                x=yi,
                y=xi,
        colorscale="Viridis",
        opacity=0.9,
        line=dict(width=0, smoothing=0.85),
        contours=dict(
            showlines=False,
            showlabels=False,
            size=0,
            labelfont=dict(size=15,),
        ),
    ))

fig.add_trace(go.Scatter(name='TBR values found during optimisation',
                         x=[x[0] for x in res.x_iters][30:],
                         y=[x[1] for x in res.x_iters][30:],
                         hovertext=-res.func_vals,
                         hoverinfo="text",
                         marker={"size": 8},
                         mode='markers'
                        )
             )

# The optimiser has intial points that are randomly selected over the parameter space
fig.add_trace(go.Scatter(name='Random starting points',
                         x=[x[0] for x in res.x_iters][0:30],
                         y=[x[1] for x in res.x_iters][0:30],
                         hovertext=-res.func_vals[0:30],
                         hoverinfo="text",
                         marker={"size": 8},
                         mode='markers'
                        )
             )

# This add the final optimal value found during the optimisation as a seperate scatter point on the graph
fig.add_trace(go.Scatter(name='Maximum TBR value found',
                         x=[res.x[0]],
                         y=[res.x[1]],
                         hovertext=[-res.fun],
                         hoverinfo="text",
                         marker={"size": 8},
                         mode='markers'
                        )
             )

fig.update_layout(title='',
                  xaxis={'title': 'breeder percent in breeder plus multiplier', 'range':(-1, 101)},
                  yaxis={'title': 'blanket breeder li6 enrichment', 'range':(-1, 101)},
                  legend_orientation="h"
                 )


fig.write_html("2d_optimization_graph_contour.html")
try:
    fig.write_html("/my_openmc_workshop/2d_optimization_graph_contour.html")
except (FileNotFoundError, NotADirectoryError):  # for both inside and outside docker container
    pass

fig.show()
