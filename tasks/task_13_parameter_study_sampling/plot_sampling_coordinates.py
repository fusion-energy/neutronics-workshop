#!/usr/bin/env python3

"""plot_simulation_results_3d.py: plots few 3d views of TBR for different materials."""


import json
import os

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def plot_simulation_results(results_df,
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