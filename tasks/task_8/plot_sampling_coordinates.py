#!/usr/bin/env python3

"""plot_simulation_results_3d.py: plots few 3d views of TBR for different materials."""


import json
import os

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def make_3d_plot(results_df, x_axis_name, y_axis_name, z_axis_name, row, col):

    text_value = []
    for e, r, tbr in zip(
        results_df["blanket_breeder_li6_enrichment"], results_df["breeder_percent_in_breeder_plus_multiplier_ratio"], results_df["tbr"]
    ):

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
        ),
        row=row,
        col=col,
    )

    fig.update_xaxes({"title": x_axis_name.replace('_',' ')}, row=row, col=col)
    fig.update_yaxes({"title": y_axis_name.replace('_',' ')}, row=row, col=col)
    # fig.update_zaxes({'title': z_axis_name}, row=row, col=col)


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


sampling_methods = ["random", "grid", "halton", "adaptive"]

fig = make_subplots(rows=2, cols=2, subplot_titles=(sampling_methods))

row_col_coords = [[1, 1], [1, 2], [2, 1], [2, 2]]
results_df = read_in_data()
for sample, coords in zip(sampling_methods, row_col_coords):
    filtered_results_df = results_df[results_df["sample"] == sample]

    make_3d_plot(
        filtered_results_df,
        x_axis_name="blanket_breeder_li6_enrichment",
        y_axis_name="breeder_percent_in_breeder_plus_multiplier_ratio",
        z_axis_name="tbr",
        row=coords[0],
        col=coords[1],
    )

fig.show()

fig.write_html("sampling_coords.html")
try:
    fig.write_html("/my_openmc_workshop/sampling_coords.html")
except (FileNotFoundError, NotADirectoryError):
    pass
