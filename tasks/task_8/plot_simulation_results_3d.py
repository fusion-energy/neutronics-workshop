#!/usr/bin/env python3

"""simulation_results_plot.py: plots few 2D views of TBR and leakage."""

__author__      = "Jonathan Shimwell"


import json
import pandas as pd
from pandas.io.json import json_normalize 
import numpy as np
import plotly.graph_objects as go

with open('simulation_results.json') as f:
    results = json.load(f)

# PLOTS RESULTS #

# results_df = pd.DataFrame(results)

results_df = json_normalize(data=results)

all_materials = ['F2Li2BeF2','Li','Pb84.2Li15.8','Li4SiO4']

'TBR with'

for tally_name in ['TBR']:
    #tally_name_error = tally_name+'_st_dev'

    text_values = {}

    for material_name in all_materials:

        df_filtered_by_mat = results_df[results_df['breeder_material_name']==material_name]

        text_value = []
        for e,t,i,tbr, leak in zip(df_filtered_by_mat['enrichment_fraction'],
                            df_filtered_by_mat['thickness'],
                            df_filtered_by_mat['inner_radius'],
                            df_filtered_by_mat['TBR.value'],
                            df_filtered_by_mat['vessel_leakage.value']):
                text_value.append('TBR =' +str(tbr)+'<br>'+
                                'Vessel leakage =' +str(leak)+'<br>'+
                                'enrichment fraction ='+str(e) +'<br>'+
                                'thickness ='+str(t) +'<br>'+
                                'inner radius ='+str(i)                                            
                                )
        text_values[material_name] = text_value             

    x_axis_name = 'enrichment_fraction'
    y_axis_name = 'thickness'
    z_axis_name = 'TBR.value'

    traces=[]
    for material_name in all_materials:

        df_filtered_by_mat = results_df[results_df['breeder_material_name']==material_name]

        traces.append(go.Scatter3d(x=list(df_filtered_by_mat[x_axis_name]), 
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

    fig = go.Figure()

    fig.update_layout(
        title = 'Select a breeder material:',
        hovermode = 'closest',
        scene = {'xaxis':{'title':" ".join(x_axis_name.title().split('_'))},
                 'yaxis':{'title':" ".join(y_axis_name.title().split('_'))},
                 'zaxis':{'title':" ".join(z_axis_name.title().split('_'))}
                 }
    )
                    

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
            x = 0.14,
            xanchor = 'left',
            y = 1.1,
            yanchor = 'top' 
        ),
    ])

    # annotations = list([
    #     dict(text='Breeder material:', x=0, y=3, yref='paper', align='left', showarrow=False)
    # ])
    fig.update_layout(updatemenus=updatemenus)
                    #   annotations=annotations)

    for trace in traces:
        fig.add_trace(trace)

    fig.write_html(tally_name+'_for_different_materials.html')
    try:
        fig.write_html('/my_openmc_workshop/'+tally_name+'_for_different_materials.html')
    except (FileNotFoundError, NotADirectoryError):
        pass

    fig.show()

