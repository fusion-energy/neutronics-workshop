#!/usr/bin/env python3

"""simulation_results_plot.py: plots few 2D views of TBR."""


import plotly.graph_objects as go
import json
import pandas as pd
import os
import argparse

def make_plot(x_axis_name,y_axis_name, y_axis_error_name):

      fig = go.Figure()

      text_values = {}

      for material_name in results_df['breeder_material_name'].unique():

            df_filtered_by_mat = results_df[results_df['breeder_material_name']==material_name]

            text_value = []
            for e,t,i,tbr in zip(df_filtered_by_mat['enrichment_fraction'],
                                          df_filtered_by_mat['thickness'],
                                          df_filtered_by_mat['inner_radius'],
                                          df_filtered_by_mat['TBR']):
                  text_value.append('TBR =' +str(tbr)+'<br>'+
                                    'enrichment fraction ='+str(e) +'<br>'+
                                    'thickness ='+str(t) +'<br>'+
                                    'inner radius ='+str(i)
                                    )

            text_values[material_name] = text_value

            tally = df_filtered_by_mat[y_axis_name]
            tally_std_dev = df_filtered_by_mat[y_axis_error_name]

            fig.add_trace(go.Scatter(x=df_filtered_by_mat[x_axis_name], 
                                    y= tally,
                                    mode = 'markers',
                                    hoverinfo='text' ,
                                    text=text_values[material_name],
                                    name = material_name,
                                    error_y= {'array':tally_std_dev},
                                    )
                              )

      fig.update_layout(
            title = y_axis_name+' vs '+x_axis_name + ', number of simulations = ' +str(len(results_df)),
            hovermode = 'closest',
            xaxis = {'title':x_axis_name},
            yaxis = {'title':y_axis_name}
      )

      fig.write_html(y_axis_name+'_vs_'+x_axis_name+'_'+args.samples+'.html')
      try:
            fig.write_html('/my_openmc_workshop/'+y_axis_name+'_vs_'+x_axis_name+'_'+args.samples+'.html')
      except (FileNotFoundError, NotADirectoryError):
            pass

      fig.show()


parser = argparse.ArgumentParser()
parser.add_argument('-s', 
                    '--samples', 
                    required=True,
                    choices=['random', 'halton'],
                    help='Choose the type of sampling to plot'
                    )
args = parser.parse_args()

#reads all json files into pandas dataframe
path_to_json = "outputs"
list_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
resultdict = []
for filename in list_files:
    with open(os.path.join(path_to_json, filename), "r") as inputjson:
        resultdict.append(json.load(inputjson))

results_df = pd.DataFrame(resultdict)
results_df = results_df[results_df['sample'] == args.samples]

make_plot(x_axis_name='enrichment_fraction',y_axis_name='TBR', y_axis_error_name='TBR_std_dev')
make_plot(x_axis_name='thickness',y_axis_name='TBR', y_axis_error_name='TBR_std_dev')
