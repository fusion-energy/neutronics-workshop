import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.interpolate import griddata
from scipy.interpolate import Rbf
from tqdm import tqdm

# loads simulation output files
list_files = []
for path in Path("outputs").rglob("*.json"):
    list_files.append(path)
resultdict = []
for filename in tqdm(list_files):
    with open(filename, "r") as inputjson:
        resultdict.append(json.load(inputjson))
results_df = pd.DataFrame(resultdict)

# aranging the 4 plots on one canvas
row_col_coords = [[1, 1], [1, 2], [2, 1], [2, 2], [3,1]]
sampling_methods = ["random", "grid", "halton", "adaptive"]#, "combined"]
fig = make_subplots(rows=2, cols=2, subplot_titles=(sampling_methods))

# addes a contour plot with scatter points for each of the 4 sampling methods
for sample, coords in zip(sampling_methods, row_col_coords):
    # if sample == "combined":
    #     filtered_results_df = results_df
    # else:
    filtered_results_df = results_df[results_df["sample"] == sample]
    if len(filtered_results_df) > 1:

        # obtains x, y, z value from pandas dataframe
        x = filtered_results_df["blanket_breeder_li6_enrichment"]
        y = filtered_results_df["breeder_percent_in_breeder_plus_multiplier_ratio"]
        z = filtered_results_df["tbr"]

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
            row=coords[0],
            col=coords[1]
        )

        # scatter plot showing simulation coordinates
        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode="markers",
                name=sample,
                # hovertext=[xval +'<br>' + yval + '<br>' + zval for xval, yval, zval in zip(x, y ,z)],
                hoverinfo="text",
                showlegend=False,
                marker={"color": "red", "size": 8},
            ),
            row=coords[0],
            col=coords[1],
        )

fig.update_xaxes(title_text="Li6 enrichment percent")
fig.update_yaxes(title_text="Breeder percent in breeder plus multiplier volume")

fig.show()

fig.write_html("interpolated_results.html")
try:
    fig.write_html("/my_openmc_workshop/interpolated_results.html")
except (FileNotFoundError, NotADirectoryError):
    pass
