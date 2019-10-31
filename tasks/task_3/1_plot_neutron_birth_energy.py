#!/usr/bin/env python3

"""example_isotope_plot.py: plots 3D model with neutron tracks."""

__author__      = "Jonathan Shimwell"

import openmc
# import matplotlib.pyplot as plt
from plotly.offline import download_plotlyjs, plot
from plotly.graph_objs import Scatter, Layout, Histogram , Bar, Scatter3d
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
sett.particles = 600
sett.particle = "neutron"
sett.run_mode = 'fixed source'



# creates an isotropic point source
source = openmc.Source()
source.space = openmc.stats.Point((0,0,0))
source.angle = openmc.stats.Isotropic()

# sets the energy of neutrons to 14MeV (monoenergetic)
source.energy = openmc.stats.Discrete([14e6], [1])

# sets the energy of neutrons to a fission energy distribution
#source.energy = openmc.stats.Watt(a=988000.0, b=2.249e-06)

# sets the energy of neutrons to a fusion energy distribution, energy is 14.08MeV, atomic mass for D + T = 5, temperature is 20KeV
#source.energy = openmc.stats.Muir(e0=14080000.0, m_rat=5.0, kt=20000.0) 

sett.source = source


# Run OpenMC!
model = openmc.model.Model(geom, mats, sett)
model.run() 

sp = openmc.StatePoint('statepoint.'+str(batches)+'.h5')

print('energy of neutrons =',sp.source['E']) # these neutrons are all created

energy_bins = np.linspace(0,20e6,50)

print('energy_bins',energy_bins)

# Calculate pdf for source energies
probability, bin_edges = np.histogram(sp.source['E'], energy_bins, density=True)


# Plot source energy histogram
traces=[Scatter(x=energy_bins[:-1], 
                       y=probability*np.diff(energy_bins),
                       line={'shape':'hv'},
                       hoverinfo='text' ,                       
                       name = 'neutron direction',                
                      )
              ] 

layout = {'title':'neutron energy',
             'hovermode':'closest',
             'xaxis':{'title':'Energy (eV)'},
             'yaxis':{'title':'Probability'},
            }

plot({'data':traces,
      'layout':layout},
      filename='particle_energy_histogram.html'
      )



text = ['Energy = '+str(i)+' eV' for i in sp.source['E']]

# plots 3d poisitons of particles coloured by energy
traces=[Scatter3d(x=sp.source['xyz'][:,0], 
                  y=sp.source['xyz'][:,1],
                  z=sp.source['xyz'][:,2],
                  hovertext= text,
                  text=text,
                  mode = 'markers',
                  marker={'size':2,'color':sp.source['E'],},
                  )]

layout = {'title':'Neutron production coordinates, coloured by energy',
            'hovermode':'closest'}

plot({'data':traces,
      'layout':layout},
      filename='3d_scatter_plot.html')


