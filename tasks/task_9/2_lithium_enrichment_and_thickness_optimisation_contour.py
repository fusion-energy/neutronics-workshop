
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
with open('enrichment_thickness_vs_tbr.json', 'r') as f: 
    data = json.load(f)



x_data=[i[0] for i in data]
y_data=[i[1] for i in data]
z_data=[i[-1] for i in data]


fig = go.Figure()

GP_for_sample = make_gp(
    x=x_data,
    y=y_data,
    z=z_data,
    # z_e=list(filtered_results_df["TBR_std_dev"]),
)

sample_data = prepare_grid_data(
    GP=GP_for_sample,
    x=x_data,
    y=y_data,
    z=z_data,
    # z_e=filtered_results_df["TBR_std_dev"],
)

fig.add_trace(make_2d_surface_trace(**sample_data, min_z=0, max_z=1.7)
#         row=row,
#         col=col)
)

fig.add_trace(
    go.Scatter(
        x=x_data,
        y=y_data,
        mode="markers",
        name='sample',
        hovertext=z_data,
        hoverinfo="text",
        showlegend=False,
        marker={"color": "red", "size": 8},
    )
)

fig.show()


with open('sdf.json', 'r') as f: 
    data = json.load(f)
