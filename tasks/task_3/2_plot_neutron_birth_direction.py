#!/usr/bin/env python3

"""2_plot_neutron_birth_direction.py: plots neutron birth direction."""

__author__      = "Jonathan Shimwell"

import openmc
import plotly.graph_objects as go
from plotly.figure_factory import create_quiver

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
print('direction of first neutron =',sp.source['u'][0]) # these neutrons are all created

# plot the neutron birth locations and trajectory using a cone plot

fig_directions = go.Figure()

fig_directions.add_trace({
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
    "sizeref":30,
    "showscale":False,
})

fig_directions.update_layout(title = 'Neutron initial directions coloured by direction',
                                hovermode = 'closest')

fig_directions.write_html("3d_plot_cones.html")
try:
    fig_directions.write_html("/my_openmc_workshop/3d_plot_cones.html")
except FileNotFoundError:
    pass

fig_directions.show()