# Cross section plotter

import openmc
from plotly import __version__
from plotly.offline import download_plotlyjs, plot
from plotly.graph_objs import Scatter, Layout

import json
import pandas as pd 
from pandas.io.json import json_normalize
import numpy as np


# Materials

# Beryllium
beryllium = openmc.Material()
beryllium.set_density('g/cm3', 1.848)
beryllium.add_element('Be', 1.0)


# Uranium-235
uranium235 = openmc.Material()
uranium235.set_density('g/cm3', 19.3)
uranium235.add_nuclide('U235', 1.0)


# Carbon - Reactor grade
carbon_reactor_grade = openmc.Material()
carbon_reactor_grade.add_element('B', 0.000001, percent_type='wo')
carbon_reactor_grade.add_element('C', 0.999999, percent_type='wo')
carbon_reactor_grade.set_density('g/cm3', 1.70)


# Tungsten
tungsten = openmc.Material()
tungsten.set_density('g/cm3', 19.3)
tungsten.add_element('W', 1.0)


Endf_MT16_number = [16]     # (n,2n)
Endf_MT2_number = [2]       # (n, elastic scatter)
Endf_MT18_number = [18]     # (n,fission)
Endf_MT102_number = [102]   # (n,gamma)


energy_beryllium, data = openmc.calculate_cexs(beryllium, 'material', Endf_MT16_number)
cross_section_beryllium = data[0]

energy_uranium, data = openmc.calculate_cexs(uranium235, 'material', Endf_MT18_number)
cross_section_uranium = data[0]

energy_carbon, data = openmc.calculate_cexs(carbon_reactor_grade, 'material', Endf_MT2_number)
cross_section_carbon = data[0]

energy_tungsten, data = openmc.calculate_cexs(tungsten, 'material', Endf_MT102_number)
cross_section_tungsten = data[0]


traces = []

traces.append(Scatter(x=energy_beryllium,
                      y=cross_section_beryllium,
                      mode='lines',
                      name='Beryllium (n,2n)'))

traces.append(Scatter(x=energy_uranium,
                      y=cross_section_uranium,
                      mode='lines',
                      name='Uranium-235 (n,fission)'))

traces.append(Scatter(x=energy_carbon,
                      y=cross_section_carbon,
                      mode='lines',
                      name='Carbon (n,elastic)'))

traces.append(Scatter(x=energy_tungsten,
                      y=cross_section_tungsten,
                      mode='lines',
                      name='Tungsten (n,gamma)'))


layout1 = Layout(
    title='Interaction cross-sections for different elements and interactions',
    xaxis=dict(title='Energy (eV)',
               range=[0, 10000000]),
    yaxis={'title':'Macroscopic Cross-Section (1/cm)',
           'type':'log'})

layout2 = Layout(
    title='Interaction cross-sections for different elements and interactions',
    xaxis=dict(title='Energy (eV)',
               range=[0, 10000000]),
    yaxis=dict(title='Macroscopic Cross-Section (1/cm)',
               range=[0,0.6],))


plot({'data':traces,
      'layout':layout1},
      filename='elemental_cross_sections_logarithmic.html')

plot({'data':traces,
      'layout':layout2},
      filename='elemental_cross_sections.html')