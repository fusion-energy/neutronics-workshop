import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.interpolate import griddata
from scipy.interpolate import Rbf
from tqdm import tqdm

def plot_interpolated_results(results_df,
    x_axis_name='blanket_breeder_li6_enrichment',
    y_axis_name='breeder_percent_in_breeder_plus_multiplier_ratio',
    z_axis_name='tbr'):

    fig = go.Figure()
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
        fig.add_trace(
            go.Contour(
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
                ),
            ),
        )

        # scatter plot showing simulation coordinates
        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode="markers",
                # hovertext=[xval +'<br>' + yval + '<br>' + zval for xval, yval, zval in zip(x, y ,z)],
                hoverinfo="text",
                text=text_value,
                showlegend=False,
                marker={"color": "red", "size": 8},
            ),
        )

        return fig

