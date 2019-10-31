#!/usr/bin/env python3

"""simulation_results_plot.py: plots few 2D views of TBR and leakage."""

__author__      = "Jonathan Shimwell"


from plotly.offline import download_plotlyjs, plot
from plotly.graph_objs import Scatter, Layout
import json
import pandas as pd
from pandas.io.json import json_normalize 
import openmc
import matplotlib
import matplotlib.cm
import numpy as np



with open('simulation_results_tokamak.json') as f:
    results = json.load(f)

# PLOTS RESULTS #

#results_df = pd.DataFrame(results)

results_df = json_normalize(data=results)




fill_color = 'rgba(229,229,229,0.9)'

for material_name in ['F2Li2BeF2','Li','Pb84.2Li15.8','Li4SiO4']:
    
    print('material_name',material_name)

    df_filtered_by_mat = results_df[results_df['breeder_material_name']==material_name]

    #get color map for lines
    max_vals,min_vals=[],[]
    for spec in df_filtered_by_mat['vacuum_vessel_spectra.value']:
        max_vals.append(spec[-8])
        min_vals.append(spec[-8])
    upper_color_value = max(max_vals)
    lower_color_value = min(min_vals)
    print(lower_color_value,upper_color_value)
    norm = matplotlib.colors.Normalize(vmin=lower_color_value,vmax=upper_color_value)
    cmap = matplotlib.cm.get_cmap()

    traces={}
    for tally_name in ['vacuum_vessel_spectra']: #'neutron_spectra_front_surface','neutron_spectra_breeder_cell'
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
          
                   
            traces[tally_name].append(Scatter(x=tally_energy_groups, 
                                    y=upper_tally_value ,
                                    mode = 'lines',
                                    hoverinfo='text' ,
                                    text=[],                       
                                    name = 'upper',                
                                    #error_y= {'array':tally_std_dev},
                                    line=dict(shape='hv',color=fill_color),
                                    #fill='tonext'
                                    fillcolor=fill_color,
                                    showlegend=False,
                                    legendgroup=lgroup_counter
                                    )
                            )

            traces[tally_name].append(Scatter(x=tally_energy_groups, 
                                    y=lower_tally_value ,
                                    mode = 'lines',
                                    hoverinfo='text' ,
                                    text=text_values,                       
                                    name = 'lower',                
                                    #error_y= {'array':tally_std_dev},
                                    line=dict(shape='hv',color=fill_color),
                                    fill='tonexty',
                                    fillcolor=fill_color,
                                    showlegend=False,
                                    legendgroup=lgroup_counter
                                    )
                            )      


            line_color = 'rgba'+str(cmap(norm(tally[-8])))
            print(line_color)

            traces[tally_name].append(Scatter(x=tally_energy_groups, 
                                    y=tally ,
                                    mode = 'lines',
                                    hoverinfo='text' ,
                                    text=[],                       
                                    name = 'simulation '+str(lgroup_counter) ,                
                                    #error_y= {'array':tally_std_dev},
                                    line=dict(shape='hv',color=line_color),
                                    fill='tonexty',
                                    fillcolor=fill_color,
                                    legendgroup=lgroup_counter
                                    )
                            )       





    if traces[tally_name] != []:
        layout = {'title':tally_name+' and '+material_name,
                    'hovermode':'closest',
                    'xaxis':{'title':'Energy eV',
                             'type':'log'},
                    'yaxis':{'title':'Neutrons per cm2 per source neutron',
                             'type':'log'},
                    }


        xbuttons_list_of_dicts=[]
        xbuttons_list_of_dicts.append(dict(
                                        args=['xaxis.type','log'],
                                        label='x axis log',
                                        method='relayout'
                                    )                                   
                                    )

        xbuttons_list_of_dicts.append(dict(
                                        args=['xaxis.type','lin'],
                                        label='x axis lin',
                                        method='relayout'
                                    )                                   
                                    )                                     


        ybuttons_list_of_dicts=[]
        ybuttons_list_of_dicts.append(dict(
                                        args=['yaxis.type','log'],
                                        label='y axis log',
                                        method='relayout'
                                    )                                   
                                    )

        ybuttons_list_of_dicts.append(dict(
                                        args=['yaxis.type','lin'],
                                        label='y axis lin',
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
        ])                                


        layout['updatemenus'] = updatemenus


        plot({'data':traces[tally_name],
                'layout':layout},
                filename=tally_name+'_for_'+material_name+'.html'
                )


