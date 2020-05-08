
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


def make_2d_surface_trace(gp_mu, x_gp, y_gp, min_z, max_z):
    gp_mu_folded = np.reshape(gp_mu, (len(x_gp), len(y_gp))).T
    trace = go.Contour(
        z=gp_mu_folded,
        x=x_gp,
        y=y_gp,
        colorscale="Viridis",
        opacity=0.9,
        line=dict(width=1, smoothing=0.85),
        #     visible=visiblabilty,
        contours=dict(
            showlines=False,
            showlabels=False,
            coloring="heatmap",
            start=min_z,
            end=max_z,
            size=0.05,
            labelfont=dict(size=15,),
        ),
    )
    return trace



def make_gp(x, y, z, z_e=None):

    my_cov = RationalQuadratic()

    coords = list(zip(x, y))
    if z_e is None:
        GP = GpRegressor(coords, z, kernel=my_cov)
    else:
        GP = GpRegressor(coords, z, y_err=z_e, kernel=my_cov)

    return GP


def prepare_grid_data(GP, x, y, z, z_e=None):

    x_gp = np.linspace(start=min(x), stop=max(x), num=int(len(x) * 0.5))
    y_gp = np.linspace(start=min(y), stop=max(y), num=int(len(y) * 0.5))

    coords_gp = [(i, j) for i in x_gp for j in y_gp]
    gp_mu, gp_sigma = GP(coords_gp)

    return {"gp_mu": gp_mu, "x_gp": x_gp, "y_gp": y_gp}


res = load('saved_optimisation_2d.dat')

print('Optimal Li6 enrichment = ', res.x[0])
print('Optimal thickness = ', res.x[1])
print('Maximum TBR = ', -res.fun)

# Loads true data for comparison
data = pd.read_json('2d_tbr_values.json')
x_data=data['enrichment']
y_data=data['thickness']
z_data=data['tbr']
# z_data_error=data['TBR_std_dev']


fig = go.Figure()

GP_for_sample = make_gp(
    x=x_data,
    y=y_data,
    z=z_data,
    # z_e=z_data_error,
)

sample_data = prepare_grid_data(
    GP=GP_for_sample,
    x=x_data,
    y=y_data,
    z=z_data,
    # z_e=z_data_error,
)

fig.add_trace(make_2d_surface_trace(**sample_data, min_z=0, max_z=1.7))

fig.add_trace(go.Scatter(name='All TBR values found',
                         x=[x[0] for x in res.x_iters],
                         y=[x[1] for x in res.x_iters],
                         hovertext=-res.func_vals,
                         hoverinfo="text",
                         marker={"size": 8},
                         mode='markers'
                        )
             )

fig.add_trace(go.Scatter(name='Starting points',
                         x=[x[0] for x in res.x_iters][0:30],
                         y=[x[1] for x in res.x_iters][0:30],
                         hovertext=-res.func_vals[0:30],
                         hoverinfo="text",
                         marker={"size": 8},
                         mode='markers'
                        )
             )

fig.add_trace(go.Scatter(name='True values',
                         x=x_data,
                         y=y_data,
                         hovertext=z_data,
                         hoverinfo="text",
                         marker={"size": 8},
                         mode='markers'
                        )
             )

fig.add_trace(go.Scatter(name='Maximum TBR value found',
                         x=[res.x[0]],
                         y=[res.x[1]],
                         hovertext=[-res.fun],
                         hoverinfo="text",
                         marker={"size": 8},
                         mode='markers'
                        )
             )

fig.write_html("2d_optimization_graph_contour.html")
try:
    fig.write_html("/my_openmc_workshop/2d_optimization_graph_contour.html")
except (FileNotFoundError, NotADirectoryError):  # for both inside and outside docker container
    pass

fig.show()
