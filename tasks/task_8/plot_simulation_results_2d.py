#!/usr/bin/env python3

"""simulation_results_plot.py: plots few 2D views of TBR and leakage."""

__author__      = "Jonathan Shimwell"


# from plotly.offline import download_plotlyjs, plot
# from plotly.graph_objs import Scatter, Layout
import plotly.graph_objects as go
import json
import pandas as pd
from pandas.io.json import json_normalize 

with open('simulation_results.json') as f:
    results = json.load(f)

# PLOTS RESULTS #

#results_df = pd.DataFrame(results)

results_df = json_normalize(data=results)

for tally_name in ['TBR']: #other tallies such as DPA or leakage can be added here
      
      text_values = {}

      for material_name in ['F2Li2BeF2','Li','Pb84.2Li15.8','Li4SiO4']:

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


      traces={}
      for x_axis_name in ['enrichment_fraction','inner_radius','thickness']:
            traces[x_axis_name] = []

            for material_name in ['F2Li2BeF2','Li','Pb84.2Li15.8','Li4SiO4']:

                  df_filtered_by_mat = results_df[results_df['breeder_material_name']==material_name]

                  tally = df_filtered_by_mat[tally_name+'.value']
                  tally_std_dev = df_filtered_by_mat[tally_name+'.std_dev']

                  
                  
                  traces[x_axis_name].append(go.Scatter(x=df_filtered_by_mat[x_axis_name], 
                                          y= tally,
                                          mode = 'markers',
                                          hoverinfo='text' ,
                                          text=text_values[material_name],                       
                                          name = material_name,                
                                          error_y= {'array':tally_std_dev},
                                          )
                                    )
      fig = go.Figure()
      # if len(text_value)>0:
      for x_axis_name in ['enrichment_fraction','thickness']:

            fig.update_layout(
                  title = tally_name+' and '+x_axis_name,
                  hovermode = 'closest',
                  xaxis = {'title':x_axis_name},
                  yaxis = {'title':tally_name}
            )

            for trace in traces[x_axis_name]:
                  fig.add_trace(trace)

            fig.write_html(tally_name+'_vs_'+x_axis_name+'.html')
            try:
                  fig.write_html('/my_openmc_workshop/'+tally_name+'_vs_'+x_axis_name+'.html')
            except NotADirectoryError:
                  pass

            fig.show()


