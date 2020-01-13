#!/usr/bin/env python3

"""3_plot_neutron_birth_location.py: plots neutron birth locations."""

import openmc
import plotly.graph_objects as go

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
sett.particles = 1000
sett.particle = "neutron"
sett.run_mode = 'fixed source'


# creates a source object
source = openmc.Source()

#sets the source poition, direction and energy
source.space = openmc.stats.Point((0,0,0))
source.angle = openmc.stats.Isotropic()
source.energy = openmc.stats.Muir(e0=14080000.0, m_rat=5.0, kt=20000.0) #neutron energy = 14.08MeV, AMU for D + T = 5, temperature is 20KeV

sett.source = source

# Run OpenMC!
model = openmc.model.Model(geom, mats, sett)
model.run() 

sp = openmc.StatePoint('statepoint.'+str(batches)+'.h5')

print('birth location of first neutron =',sp.source['r'][0]) # these neutrons are all created

fig_coords = go.Figure()

text = ['Energy = '+str(i)+' eV' for i in sp.source['E']]

# plots 3d poisitons of particles coloured by energy

fig_coords.add_trace(go.Scatter3d(x=sp.source['r']['x'], 
                     y=sp.source['r']['y'],
                     z=sp.source['r']['z'],
                     hovertext= text,
                     text=text,
                     mode = 'markers',
                     marker={'size':2,'color':sp.source['E'],},
                    )
                  )
              

fig_coords.update_layout(title = 'Neutron production coordinates, coloured by energy')

fig_coords.write_html("particle_location.html")
try:
  fig_coords.write_html("/my_openmc_workshop/particle_location.html")
except FileNotFoundError:
  pass
  
fig_coords.show()
