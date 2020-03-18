from PIL import Image
from paramak import SphericalReactor
from neutronics_material_maker import MultiMaterial, Material
import numpy as np
import json
from pathlib import Path
import os
from tqdm import tqdm
import pandas as pd
from pathlib import Path
from inference.gp_tools import GpRegressor, RationalQuadratic


import plotly.graph_objects as go
from plotly.subplots import make_subplots

def load_data(path_to_json = "outputs"):
        list_files = []
        for path in Path(path_to_json).rglob('*.json'):
                list_files.append(path)
        # list_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
        resultdict = []
        for filename in tqdm(list_files):
                with open(filename, "r") as inputjson:
                        resultdict.append(json.load(inputjson))
        print(resultdict)
        results_df = pd.DataFrame(resultdict)
        print(results_df)
        return results_df


def make_2d_surface_trace(gp_mu,x_gp,y_gp,min_z,max_z):
        gp_mu_folded = np.reshape(gp_mu,(len(x_gp),len(y_gp))).T
        trace = go.Contour(
            z=gp_mu_folded,
            x=x_gp,
            y=y_gp,
            colorscale='Viridis',
            opacity=0.9,
            line= dict(width=1,smoothing=0.85),
        #     visible=visiblabilty,
            contours=dict(
                showlines=False,
                showlabels=False,
                coloring= "heatmap",
                start=min_z,
                end=max_z,
                size=0.05,
                        labelfont=dict(
                            size=15,
                        ),
                )
        )
        return trace

my_cov = RationalQuadratic()

def make_gp(x,y,z,z_e=None):

    coords = list(zip(x,y))
    if z_e == None:
        GP = GpRegressor(coords, z, kernel=my_cov)
    else:
        GP = GpRegressor(coords, z, y_err=z_e, kernel=my_cov)

    return GP


def prepare_grid_data(GP, x,y,z,z_e=None):
    

    x_gp = np.linspace(start=min(x), stop=max(x), num=int(len(x)*0.5))
    y_gp = np.linspace(start=min(y), stop=max(y), num=int(len(y)*0.5))

    coords_gp = [ (i,j) for i in x_gp for j in y_gp ]
    gp_mu, gp_sigma = GP(coords_gp)

    return {'gp_mu': gp_mu, 'x_gp': x_gp, 'y_gp': y_gp}


data = load_data()

fig = go.Figure()

GP_Li4SiO4 = make_gp(x = data[(data['breeder_material_name']=='Li4SiO4')]['enrichment'], 
             y = data[(data['breeder_material_name']=='Li4SiO4')]['thickness'], 
             z = data[(data['breeder_material_name']=='Li4SiO4')]['TBR'],
             z_e= list(data[(data['breeder_material_name']=='Li4SiO4')]['TBR_std_dev'])
             )

Li4SiO4_data = prepare_grid_data(GP=GP_Li4SiO4,
                             x = data[(data['breeder_material_name']=='Li4SiO4')]['enrichment'], 
                             y = data[(data['breeder_material_name']=='Li4SiO4')]['thickness'], 
                             z = data[(data['breeder_material_name']=='Li4SiO4')]['TBR'],
                             z_e= data[(data['breeder_material_name']=='Li4SiO4')]['TBR_std_dev']
                             )

max_z_for_all = max(Li4SiO4_data['gp_mu'])

fig.add_trace(make_2d_surface_trace(**Li4SiO4_data, min_z = 0, max_z=max_z_for_all))


fig.add_trace(go.Scatter(x=data[(data['breeder_material_name']=='Li4SiO4')]['enrichment'],
                         y=data[(data['breeder_material_name']=='Li4SiO4')]['thickness'],
                         mode = 'markers',
                         name='Li4SiO4',
                         hovertext=data[(data['breeder_material_name']=='Li4SiO4')]['TBR'],
                         hoverinfo="text",
                         showlegend=False
                         )
              )



fig.update_layout(
    title={'text': "TBR for different enrichments and blanket thicknesses"}
)

fig.update_xaxes(title_text="Li6 enrichment percent")
fig.update_xaxes(title_text="blanket thickness (cm)")

fig.show()
# # fig.write_html('tet.html')