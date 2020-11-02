#!/usr/bin/env python3

"""makes a 3d plot of neutron direction"""


from random import random
import plotly.graph_objects as go

from parametric_plasma_source import PlasmaSource

my_plasma = PlasmaSource(
    elongation=1.557,
    ion_density_origin=1.09e20,
    ion_density_peaking_factor=1,
    ion_density_pedestal=1.09e20,
    ion_density_separatrix=3e19,
    ion_temperature_origin=45.9,
    ion_temperature_peaking_factor=8.06,
    ion_temperature_pedestal=6.09,
    ion_temperature_separatrix=0.1,
    major_radius=906.0,
    minor_radius=292.258,
    pedestal_radius=0.8 * 292.258,
    plasma_id=1,
    shafranov_shift=44.789,
    triangularity=0.270,
    ion_temperature_beta=6
)

x_locations, y_locations, z_locations, x_directions, y_directions, z_directions, energies = ([] for i in range(7))

fig = go.Figure()

for x in range(500):
    sample = my_plasma.sample([random(), random(), random(), random(), random(), random(), random(), random()])
    x_locations.append(sample[0])
    y_locations.append(sample[1])
    z_locations.append(sample[2])
    x_directions.append(sample[3])
    y_directions.append(sample[4])
    z_directions.append(sample[5])
    energies.append(sample[6])

fig.add_trace({
    'type': 'cone',
    'cauto': False,
    'x': x_locations,
    'y': y_locations,
    'z': z_locations,
    'u': x_directions,
    'v': y_directions,
    'w': z_directions,
    'cmin': 0,
    'cmax': 1,
    "anchor": "tail",
    "colorscale": "Viridis",
    "hoverinfo": "u+v+w+norm",
    "sizemode": "absolute",
    "sizeref": 3,
    "showscale": False
})

fig.update_layout(
    title='Neutron initial directions coloured by direction',
    hovermode='closest'
)

fig.show()
