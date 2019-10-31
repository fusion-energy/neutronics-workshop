#!/usr/bin/env python3

"""simulation_results_plot.py: plots few 2D views of TBR and leakage."""

__author__      = "Jonathan Shimwell"


from plotly.offline import download_plotlyjs, plot
from plotly.graph_objs import Scatter, Layout, Scatter3d
import json
import pandas as pd
from pandas.io.json import json_normalize 
import openmc
import matplotlib
import matplotlib.cm
import numpy as np



with open('simulation_results500.json') as f:
    results = json.load(f)

# PLOTS RESULTS #

#results_df = pd.DataFrame(results)

results_df = json_normalize(data=results)


third_dimention = 'enrichment_fraction'#'thickness'
third_dimention = 'thickness'
color_by = 'thickness'

fill_color = 'rgba(229,229,229,0.9)'

for material_name in ['Li4SiO4','Li','Pb84.2Li15.8','F2Li2BeF2']:
    
    print('material_name',material_name)

    df_filtered_by_mat = results_df[results_df['breeder_material_name']==material_name]

    #norm = matplotlib.colors.Normalize(vmin=df_filtered_by_mat[color_by].max(),vmax=df_filtered_by_mat[color_by].min())
    #cmap = matplotlib.cm.get_cmap()

    traces={}
    for tally_name in ['vacuum_vessel_spectra']: #breeder_blanket_spectra
        

        
        traces[tally_name] = []
                 

        tallies = df_filtered_by_mat[tally_name+'.value']
        tallies_energy_groups = df_filtered_by_mat[tally_name+'.energy_groups']
        tallies_std_dev = df_filtered_by_mat[tally_name+'.std_dev']


        
        for lgroup_counter, (tally, tally_energy_groups, tally_std_dev,e,t,i,tbr,leak) in enumerate(zip(tallies,
                                                                                   tallies_energy_groups,
                                                                                   tallies_std_dev,
                                                                                   df_filtered_by_mat['enrichment_fraction'],
                                                                                   df_filtered_by_mat['thickness'],
                                                                                   df_filtered_by_mat['inner_radius'],
                                                                                   df_filtered_by_mat['tbr.value'],
                                                                                   df_filtered_by_mat['blanket_leakage.value'])):

            #print('        tally_std_dev',tally_std_dev)

            upper_tally_value = []
            lower_tally_value = []

            text_values = []
            for entry,error,energy in zip(tally,tally_std_dev,tally_energy_groups):
                upper_tally_value.append(entry+error)
                lower_tally_value.append(entry-error)
                #print(entry+error,entry,entry-error)
                text_values.append('(x) energy = '+str(energy)+'<br>'+
                                    '(y) neutrons ='+str(entry)+' per cm2 per source neutron<br>'+
                                    'Enrichment_fraction = '+str(e)+'<br>'+
                                    'Thickness = '+str(t)+'<br>'+
                                    'Inner_radius = '+str(i)+'<br>'+
                                    'TBR = '+str(tbr)+'<br>'+
                                    'Blanket leakage = '+str(leak)
                                    )
          

            #line_color = 'rgba'+str(cmap(norm(tally))) #based on the 14mev bin population
            #line_color = 'rgba'+str(cmap(norm(t))) #based on the thickness
            #line_color = 'rgba'+str(cmap(norm(e))) #based on the enrichment
            line_color = 'red'
            #print(line_color)

            traces[tally_name].append(Scatter3d(x=tally_energy_groups, 
                                    z=tally ,
                                    y=[t]*len(tally),
                                    mode = 'lines',
                                    hoverinfo='text',
                                    text=text_values,                       
                                    name = 'simulation '+str(lgroup_counter) ,                
                                    #error_y= {'array':tally_std_dev},
                                    line=dict(color=line_color,
                                              width=4),
                                    #fill='tonexty',
                                    #fillcolor=fill_color,
                                    #legendgroup=lgroup_counter
                                    )
                            )       


    if third_dimention == 'thickness':
        third_dimention_label = 'Thickness of '+material_name+' (cm)'
    else:
        third_dimention_label=third_dimention
        
    if traces[tally_name] != []:
        layout = {'title':tally_name.replace('_',' ').title()+' with '+material_name,
                  'font':dict(size=16),
                  'hovermode':'closest',
                  'showlegend':False,
                  'scene':{
                        'xaxis':{'title':'Energy eV',
                                'type':'linear'},
                        'zaxis':{'title':'Neutrons per cm2 per source neutron',
                                'type':'log'},
                        'yaxis':{'title':third_dimention_label,
                                'type':'linear',
                                'range':[df_filtered_by_mat[third_dimention].min(),df_filtered_by_mat[third_dimention].max()] }
                  }                                
                        
                 }


        xbuttons_list_of_dicts=[]
        xbuttons_list_of_dicts.append(dict(
                                        args=['scene.xaxis.type','log'],
                                        label='x axis log',
                                        method='relayout'
                                    )                                   
                                    )

        xbuttons_list_of_dicts.append(dict(
                                        args=['scene.xaxis.type','lin'],
                                        label='x axis lin',
                                        method='relayout'
                                    )                                   
                                    )                                     


        ybuttons_list_of_dicts=[]
        ybuttons_list_of_dicts.append(dict(
                                        args=['scene.yaxis.type','log'],
                                        label='y axis log',
                                        method='relayout'
                                    )                                   
                                    )

        ybuttons_list_of_dicts.append(dict(
                                        args=['scene.yaxis.type','lin'],
                                        label='y axis lin',
                                        method='relayout'
                                    )                                   
                                    )  

        zbuttons_list_of_dicts=[]
        zbuttons_list_of_dicts.append(dict(
                                        args=['scene.zaxis.type','log'],
                                        label='z axis log',
                                        method='relayout'
                                    )                                   
                                    )

        zbuttons_list_of_dicts.append(dict(
                                        args=['scene.zaxis.type','lin'],
                                        label='z axis lin',
                                        method='relayout'
                                    )                                   
                                    )                                      


        updatemenus=list([
            dict(
                buttons=list(xbuttons_list_of_dicts),
                direction = 'down',
                pad = {'r': 10, 't': 10},
                showactive = True,
                x = 0.1,
                xanchor = 'left',
                y = 1.1,
                yanchor = 'top' 
            ),
            dict(
                buttons=list(ybuttons_list_of_dicts),
                direction = 'down',
                pad = {'r': 10, 't': 10},
                showactive = True,
                x = 0.2,
                xanchor = 'left',
                y = 1.1,
                yanchor = 'top' 
            ),   
            dict(
                buttons=list(zbuttons_list_of_dicts),
                direction = 'down',
                pad = {'r': 10, 't': 10},
                showactive = True,
                x = 0.3,
                xanchor = 'left',
                y = 1.1,
                yanchor = 'top' 
            ),                        
        ])                                


        layout['updatemenus'] = updatemenus


        plot({'data':traces[tally_name],
                'layout':layout},
                filename=tally_name+'_for_'+material_name+'.html'
                )


