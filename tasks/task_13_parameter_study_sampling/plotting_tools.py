
import os
import json

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from plotly.subplots import make_subplots
from scipy.interpolate import griddata
from scipy.interpolate import Rbf


def read_in_data(path_to_json="outputs"):
    # reads all json files into pandas dataframe
    list_files = [
        pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith(".json")
    ]
    resultdict = []
    for filename in list_files:
        with open(os.path.join(path_to_json, filename), "r") as inputjson:
            resultdict.append(json.load(inputjson))
    results_df = pd.DataFrame(resultdict)
    return results_df


def plot_simulation_results(results_df,
    x_axis_name='blanket_breeder_li6_enrichment',
    y_axis_name="breeder_percent_in_breeder_plus_multiplier_ratio",
    z_axis_name='tbr'):

    text_value = []
    for e, r, tbr in zip(results_df[x_axis_name], results_df[y_axis_name], results_df[z_axis_name]):

        text_value.append(
            "TBR ="
            + str(tbr)
            + "<br>"
            + "Li6 enrichment ="
            + str(e)
            + "<br>"
            + "breeder percent in breeder + multiplier ="
            + str(r)
            + "<br>"
    )

    trace = go.Scatter(
                x=list(results_df[x_axis_name]),
                y=list(results_df[y_axis_name]),
                # z=list(results_df[z_axis_name]),
                mode="markers",
                name="TBR in HCPB blanket",
                showlegend=False,
                hoverinfo="text",
                text=text_value,
                marker={
                    "color": list(results_df[z_axis_name]),
                    "colorscale": "Viridis",
                    "size": 8,
                },
            )

    return trace


def plot_interpolated_results(results_df,
    x_axis_name='blanket_breeder_li6_enrichment',
    y_axis_name='breeder_percent_in_breeder_plus_multiplier_ratio',
    z_axis_name='tbr'):

    traces = []

    text_value = []
    for e, r, tbr in zip(results_df[x_axis_name], results_df[y_axis_name], results_df[z_axis_name]):

        text_value.append(
            "TBR ="
            + str(tbr)
            + "<br>"
            + "Li6 enrichment ="
            + str(e)
            + "<br>"
            + "breeder percent in breeder + multiplier ="
            + str(r)
            + "<br>"
        )

    if len(results_df) > 1:

        # obtains x, y, z value from pandas dataframe
        x = results_df["blanket_breeder_li6_enrichment"]
        y = results_df["breeder_percent_in_breeder_plus_multiplier_ratio"]
        z = results_df["tbr"]

        xi = np.linspace(0, 100, 100)
        yi = np.linspace(0, 100, 100)

        # griddata can be used instead of r basis functions to z values using cubic or linear interpolation. 
        # This also works but don't predict outside of the sample space to the edges of the parameter space
        zi = griddata((x, y), z, (xi[None,:], yi[:,None]), method='cubic')

        # Uses radial basis function to obtain interpolated values
        # See https://docs.scipy.org/doc/scipy/reference/tutorial/interpolate.html for more details
        # XI, YI = np.meshgrid(xi, yi)
        # rbf = Rbf(x, y, z, epsilon=2)
        # zi = rbf(XI, YI)

        # contour plot showing interpoloated TBR values
        traces.append(go.Contour(
                        z=zi,
                        x=xi,
                        y=yi,
                        colorscale="Viridis",
                        opacity=0.9,
                        line=dict(width=1, smoothing=0.85),
                        contours=dict(
                            showlines=False,
                            showlabels=False,
                            coloring="heatmap",
                            start=min(z),
                            end=max(z),
                            size=0.,
                            labelfont=dict(size=15,),
                        )
                    )
        )

        traces.append(go.Scatter(
                        x=x,
                        y=y,
                        mode="markers",
                        hoverinfo="text",
                        showlegend=False,
                        marker={"color": "red", "size": 8},
                    )
        )

        return traces