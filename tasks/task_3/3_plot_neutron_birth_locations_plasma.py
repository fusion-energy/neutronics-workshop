#!/usr/bin/env python3

"""example_isotope_plot.py: plots neutron birth locations and directions."""

__author__      = "Jonathan Shimwell"

import openmc
# import matplotlib.pyplot as plt
from plotly.offline import download_plotlyjs, plot
from plotly.graph_objs import Scatter, Layout, Histogram , Bar
from plotly.figure_factory import create_quiver

import os
import numpy as np

#MATERIALS#

mats = openmc.Materials([])


#GEOMETRY#

sph1 = openmc.Sphere(r=1000, boundary_type = 'vacuum')

simple_moderator_cell = openmc.Cell(region= -sph1 )

universe = openmc.Universe(cells=[simple_moderator_cell]) 

geom = openmc.Geometry(universe)



#SIMULATION SETTINGS#

# Instantiate a Settings object
sett = openmc.Settings()
batches = 2
sett.batches = batches
sett.inactive = 0
sett.particles = 3000
sett.particle = "neutron"
sett.run_mode = 'fixed source'


# creates a source object
source = openmc.Source()

#sets the source poition, direction and energy with predefined plasma parameters (see source_sampling.cpp)
source._source_library = 'source_sampling.so'

sett.source = source


# Run OpenMC!
model = openmc.model.Model(geom, mats, sett)
model.run() 

sp = openmc.StatePoint('statepoint.'+str(batches)+'.h5')

print('birth location of first neutron =',sp.source['r'][0]) # these neutrons are all created
print('direction of first neutron =',sp.source['u'][0]) # these neutrons are all created


# plot the neutron birth locations and trajectory
traces =[{
    'type': 'cone',
    'cauto' : False,
    'x':sp.source['r']['x'],
    'y':sp.source['r']['y'],
    'z':sp.source['r']['z'],
    'u':sp.source['u']['x'],
    'v':sp.source['u']['y'],
    'w':sp.source['u']['z'],
    'cmin':0,'cmax':1,
    "anchor": "tail",
    "colorscale": 'Viridis',
    "hoverinfo": "u+v+w+norm",
    "sizemode":"absolute",
    "sizeref":3,
    "showscale":False,
    }]

layout = {'title':'Neutron initial directions coloured by direction',
        'hovermode':'closest'}

plot({'data':traces,
    'layout':layout},
    filename='3d_plasma_cones.html')


traces =[{
    'type': 'scatter3d',
    # 'cauto' : False,
    'x':sp.source['r']['x'],
    'y':sp.source['r']['y'],
    'z':sp.source['r']['z'],
    'mode':'markers',
    'marker':{'size':1,
              'color':sp.source['E'],
              'colorscale':'Viridis',
              'colorbar':{'title':'Neutron energy in eV'}}
    }]

layout = {'title':'Neutron initial birth location coloured by energy',
        'hovermode':'closest'}

plot({'data':traces,
    'layout':layout},
    filename='3d_plasma_scatter.html')
