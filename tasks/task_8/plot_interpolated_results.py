import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.interpolate import griddata
from tqdm import tqdm

from inference.gp_tools import GpRegressor, RationalQuadratic


def load_data(path_to_json="outputs"):
    list_files = []
    for path in Path(path_to_json).rglob("*.json"):
        list_files.append(path)
    # list_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
    resultdict = []
    for filename in tqdm(list_files):
        with open(filename, "r") as inputjson:
            resultdict.append(json.load(inputjson))
    results_df = pd.DataFrame(resultdict)
    return results_df


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


results_df = load_data()

sampling_methods = ["random", "grid", "halton", "adaptive"]
fig = make_subplots(rows=2, cols=2, subplot_titles=(sampling_methods))


row_col_coords = [[1, 1], [1, 2], [2, 1], [2, 2]]

for sample, coords in zip(sampling_methods, row_col_coords):
    filtered_results_df = results_df[results_df["sample"] == sample]
    if len(filtered_results_df) > 1:
        row = coords[0]
        col = coords[1]

        GP_for_sample = make_gp(
            x=filtered_results_df["enrichment"],
            y=filtered_results_df["thickness"],
            z=filtered_results_df["TBR"],
            #z_e=list(filtered_results_df["TBR_std_dev"]),
        )
        sample_data = prepare_grid_data(
            GP=GP_for_sample,
            x=filtered_results_df["enrichment"],
            y=filtered_results_df["thickness"],
            z=filtered_results_df["TBR"],
            #z_e=filtered_results_df["TBR_std_dev"],
        )

        max_z_for_all = max(sample_data["gp_mu"])

        fig.add_trace(make_2d_surface_trace(**sample_data, min_z=0, max_z=max_z_for_all),
            row=row,
            col=col)

        fig.add_trace(
            go.Scatter(
                x=filtered_results_df["enrichment"],
                y=filtered_results_df["thickness"],
                mode="markers",
                name=sample,
                hovertext=filtered_results_df["TBR"],
                hoverinfo="text",
                showlegend=False,
                marker={"color": "red", "size": 8},
            ),
            row=row,
            col=col,
        )

    # x = filtered_results_df["enrichment"]
    # y = filtered_results_df["thickness"]
    # z = filtered_results_df["TBR"]

    # xi = np.linspace(0, 100, 75)
    # yi = np.linspace(0, 500, 75)

    # zi = griddata((x, y), z, (xi[None, :], yi[:, None]), method="cubic")

    # fig.add_trace(
    #     go.Contour(z=zi, x=xi, y=yi), row=row, col=col,
    # )


fig.update_xaxes(title_text="Li6 enrichment percent")
fig.update_yaxes(title_text="blanket thickness (cm)")

fig.show()

fig.write_html("interpolated_results.html")
try:
    fig.write_html("/my_openmc_workshop/interpolated_results.html")
except (FileNotFoundError, NotADirectoryError):
    pass
