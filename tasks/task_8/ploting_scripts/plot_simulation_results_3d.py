#!/usr/bin/env python3

"""simulation_results_plot.py: plots few 2D views of TBR and leakage."""

__author__      = "Jonathan Shimwell"


from plotly.offline import download_plotlyjs, plot
from plotly.graph_objs import Scatter3d, Layout, Scatter
import json
import pandas as pd
from pandas.io.json import json_normalize 
import numpy as np

with open('simulation_results_tokamak.json') as f:
    results = json.load(f)

# PLOTS RESULTS #

# results_df = pd.DataFrame(results)

results_df = json_normalize(data=results)

all_materials = ['F2Li2BeF2','Li','Pb84.2Li15.8','Li4SiO4']



for tally_name in ['tbr']:
    #tally_name_error = tally_name+'_st_dev'

    text_values = {}

    for material_name in all_materials:

        df_filtered_by_mat = results_df[results_df['breeder_material_name']==material_name]

        text_value = []
        for e,t,i,tbr, leak in zip(df_filtered_by_mat['enrichment_fraction'],
                            df_filtered_by_mat['thickness'],
                            df_filtered_by_mat['inner_radius'],
                            df_filtered_by_mat['tbr.value'],
                            df_filtered_by_mat['vessel_leakage.value']):
                text_value.append('TBR =' +str(tbr)+'<br>'+
                                'Leakage =' +str(leak)+'<br>'+
                                'enrichment fraction ='+str(e) +'<br>'+
                                'thickness ='+str(t) +'<br>'+
                                'inner radius ='+str(i)                                            
                                )
        text_values[material_name] = text_value             

    x_axis_name = 'enrichment_fraction'
    y_axis_name = 'thickness'
    z_axis_name = 'inner_radius'

    traces=[]
    for material_name in all_materials:

        df_filtered_by_mat = results_df[results_df['breeder_material_name']==material_name]

        traces.append(Scatter3d(x=list(df_filtered_by_mat[x_axis_name]), 
                                y=list(df_filtered_by_mat[y_axis_name]),
                                z=list(df_filtered_by_mat[z_axis_name]),
                                mode = 'markers',
                                name = material_name,
                                hoverinfo='text' ,
                                text=text_values[material_name],
                                visible=False,
                                marker={'color':list(df_filtered_by_mat[tally_name+'.value']),
                                        'colorscale':'Viridis',
                                        'size':2,
                                        'colorbar':{'title':tally_name,
                                                    'tickvals':np.linspace(start=min(list(df_filtered_by_mat[tally_name+'.value'])),stop=max(list(df_filtered_by_mat[tally_name+'.value'])),num=10)
                                                        }
                                        }
        ))
                    



    layout = {'title':'Select a material',
            'hovermode':'closest',
            'scene':{'xaxis':{'title':" ".join(x_axis_name.title().split('_'))},
                    'yaxis':{'title':" ".join(y_axis_name.title().split('_'))},
                    'zaxis':{'title':" ".join(z_axis_name.title().split('_'))}
            }
            }


    buttons_list_of_dicts = []

    for v, material in enumerate(all_materials):
        vis_list = []
        for i in range(len(all_materials)):
            if i == v:
                vis_list.append(True)    
            else:
                vis_list.append(False)

        buttons_list_of_dicts.append(dict(
                                        args=[{'visible': vis_list},
                                                {'title':tally_name+' with '+material}
                                                ],
                                        label=material,
                                        method='update'
                                    ))  
    print(buttons_list_of_dicts)   


    updatemenus=list([
        dict(
            buttons=list(buttons_list_of_dicts),
            direction = 'down',
            pad = {'r': 10, 't': 10},
            showactive = True,
            x = 0.1,
            xanchor = 'left',
            y = 1.1,
            yanchor = 'top' 
        ),
    ])

    annotations = list([
        dict(text='Breeder material:', x=0, y=1.085, yref='paper', align='left', showarrow=False)
    ])
    layout['updatemenus'] = updatemenus
    layout['annotations'] = annotations


    plot({'data':traces,
        'layout':layout},
        filename=tally_name+'_for_different_materials.html')