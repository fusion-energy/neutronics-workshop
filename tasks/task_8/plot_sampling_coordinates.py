#!/usr/bin/env python3

"""plot_simulation_results_3d.py: plots few 3d views of TBR for different materials."""


import json
import os

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def make_3d_plot(results_df,
    x_axis_name='blanket_breeder_li6_enrichment',
    y_axis_name="breeder_percent_in_breeder_plus_multiplier_ratio",
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

    fig.add_trace(
        go.Scatter(
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
    )
    return fig
