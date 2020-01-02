#!/usr/bin/env python3

"""example_isotope_plot.py: plots cross sections for a couple of elements with natural abundance."""

__author__      = "Jonathan Shimwell"

import openmc
import plotly.graph_objects as go
from tqdm import tqdm
from openmc.data import atomic_weight

all_stable_elements = ['Ag', 'Al', 'Ar', 'As', 'Au', 'B', 'Ba', 'Be', 'Bi', 'Br', 'C', 'Ca', 'Cd', 'Ce', 'Cl', 'Co', 'Cr', 'Cs', 'Cu', 'Dy', 'Er', 'Eu', 'F', 'Fe', 'Ga', 'Gd', 'Ge', 'H', 'He', 'Hf', 'Hg', 'Ho', 'I', 'In', 'Ir', 'K', 'Kr', 'La', 'Li', 'Lu', 'Mg', 'Mn', 'Mo', 'N', 'Na', 'Nb', 'Nd', 'Ne', 'Ni', 'O', 'Os', 'P', 'Pa', 'Pb', 'Pd','Po', 'Pr', 'Pt', 'Rb', 'Re', 'Rh', 'Rn', 'Ru', 'S', 'Sb', 'Sc', 'Se', 'Si', 'Sm', 'Sn', 'Sr', 'Ta', 'Tb', 'Te', 'Th', 'Ti', 'Tl', 'Tm', 'U', 'V', 'W', 'Xe', 'Y', 'Yb', 'Zn', 'Zr']
Endf_MT_number = 16 # MT number 16 is (n,n2) reaction, MT 205 is (n,Xt). This number will need to be changed for this task


fig = go.Figure()
# this loop etracts the cross section and energy of reactions when they exist
for element_name in tqdm(all_stable_elements):

      element_object = openmc.Material() # this material defaults to a density of 1g/cm3

      try:
            element_object.add_element(element_name,1.0,percent_type='ao')
      except ValueError:
            print("The cross section files for the isotopes of ",element_name," don't exist")
            continue
      
      try:
            atomic_weight(element_name) 
      except ValueError:
            print('There are no natural isotopes of ',element_name)
            continue

      energy, cross_sections = openmc.calculate_cexs(element_object, 'material', [Endf_MT_number] )
      cross_section = cross_sections[0]
      if cross_section.sum() != 0.0:
            fig.add_trace(go.Scatter(x=energy, 
                              y=cross_section, 
                              mode = 'lines', 
                              name=element_name+' MT '+str(Endf_MT_number))
                        )
      else:
            print('Element ',element_name, ' has no cross section data for MT number', Endf_MT_number)



fig.update_layout(
      title = 'Element cross sections '+ str(Endf_MT_number),
      xaxis = {'title':'Energy (eV)',
               'range':(0,14.1e6)},
      yaxis = {'title':'Cross section (barns)'}
)


# this adds the dropdown box for log and lin axis selection
fig.update_layout(
    updatemenus=[
        go.layout.Updatemenu(
            buttons=list([
                dict(
                    args=[{"xaxis.type":'lin', "yaxis.type":'lin', 'yaxis.range':(0,14.1e6)}],
                    label="linear(x) , linear(y)",
                    method="relayout"
                ),
                dict(
                    args=[{"xaxis.type":'log', "yaxis.type":'log'}],
                    label="log(x) , log(y)",
                    method="relayout"
                ),
                dict(
                    args=[{"xaxis.type":'log', "yaxis.type":'lin', 'yaxis.range':(0,14.1e6)}],
                    label="log(x) , linear(y)",
                    method="relayout"
                ),
                dict(
                    args=[{"xaxis.type":'lin', "yaxis.type":'log'}],
                    label="linear(x) , log(y)",
                    method="relayout"
                )
            ]),
            pad={"r": 10, "t": 10},
            showactive=True,
            x=0.5,
            xanchor="left",
            y=1.1,
            yanchor="top"
        ),
    ]
)


fig.write_html("2_example_element_plot_"+str(Endf_MT_number)+".html")
fig.show()