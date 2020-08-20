#!/usr/bin/env python3

"""4_plot_neutron_birth_location_plasma.py plots neutron birth locations."""

import plotly.graph_objects as go

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
sp_filename = model.run()

sp = openmc.StatePoint(sp_filename)

print('birth location of first neutron =', sp.source['r'][0])  # these neutrons are all created

fig_coords = go.Figure()

text = ['Energy = '+str(i)+' eV' for i in sp.source['E']]

# plots 3d poisitons of particles coloured by energy

fig_coords.add_trace(go.Scatter3d(x=sp.source['r']['x'],
                                  y=sp.source['r']['y'],
                                  z=sp.source['r']['z'],
                                  hovertext=text,
                                  text=text,
                                  mode='markers',
                                  marker={'size': 1.,
                                          'color': sp.source['E']
                                  }
                    )
                  )

fig_coords.update_layout(title='Neutron production coordinates, coloured by energy')

fig_coords.write_html("plasma_particle_location.html")
try:
    fig_coords.write_html("/my_openmc_workshop/plasma_particle_location.html")
except (FileNotFoundError, NotADirectoryError):  # for both inside and outside docker container
    pass

fig_coords.show()
