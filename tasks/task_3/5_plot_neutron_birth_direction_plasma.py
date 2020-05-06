#!/usr/bin/env python3

"""5_plot_neutron_birth_direction_plasma.py : makes a 3d plot of neutron direction"""

import numpy as np
import plotly.graph_objects as go
from plotly.figure_factory import create_quiver

import openmc

from parametric_plasma_source import Plasma


# MATERIALS

mats = openmc.Materials([])


# GEOMETRY

sph1 = openmc.Sphere(r=1000, boundary_type='vacuum')

simple_moderator_cell = openmc.Cell(region=-sph1)

universe = openmc.Universe(cells=[simple_moderator_cell])

geom = openmc.Geometry(universe)


# SIMULATION SETTINGS

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
# this creates a neutron distribution with the shape of a tokamak plasma
my_plasma = Plasma(elongation=2.9,
                   minor_radius=1.118,
                   major_radius=1.9,
                   triangularity = 0.55)
# there are other parameters that can be set for the plasma, but we can use the defaults for now
my_plasma.export_plasma_source('my_custom_plasma_source.so')
# sets the source poition, direction and energy with predefined plasma parameters (see source_sampling.cpp)
source.library = './my_custom_plasma_source.so'
sett.source = source


# Run OpenMC!
model = openmc.model.Model(geom, mats, sett)
statepoint_filename = model.run()

sp = openmc.StatePoint(statepoint_filename)

print('direction of first neutron =', sp.source['u'][0])  # these neutrons are all created

fig_directions = go.Figure()

# plot the neutron birth locations and trajectory
fig_directions.add_trace({
    'type': 'cone',
    'cauto': False,
    'x': sp.source['r']['x'],
    'y': sp.source['r']['y'],
    'z': sp.source['r']['z'],
    'u': sp.source['u']['x'],
    'v': sp.source['u']['y'],
    'w': sp.source['u']['z'],
    'cmin': 0,
    'cmax': 1,
    "anchor": "tail",
    "colorscale": 'Viridis',
    "hoverinfo": "u+v+w+norm",
    "sizemode": "absolute",
    "sizeref": 3,
    "showscale": False,
})

fig_directions.update_layout(title='Neutron initial directions coloured by direction',
                             hovermode='closest')


fig_directions.write_html("plasma_particle_direction.html")
try:
    fig_directions.write_html("/my_openmc_workshop/plasma_particle_direction.html")
except (FileNotFoundError, NotADirectoryError):  # for both inside and outside docker container
    pass

fig_directions.show()
