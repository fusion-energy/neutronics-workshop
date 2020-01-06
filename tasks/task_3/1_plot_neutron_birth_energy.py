#!/usr/bin/env python3

"""1_plot_neutron_birth_energy.py: plots 3D model with neutron tracks."""

__author__      = "Jonathan Shimwell"

import openmc
import plotly.graph_objects as go
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

fig_energy = go.Figure()

# Plot source energy histogram
fig_energy.add_trace(go.Scatter(x=energy_bins[:-1], 
                       y=probability*np.diff(energy_bins),
                       line={'shape':'hv'},
                       hoverinfo='text' ,                       
                       name = 'neutron direction',                
                      )
              ) 


fig_energy.update_layout(
      title = 'neutron energy',
      xaxis = {'title':'Energy (eV)'},
      yaxis = {'title':'Probability'}
)


fig_energy.write_html("particle_energy_histogram.html")
fig_energy.show()