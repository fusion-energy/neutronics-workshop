#!/usr/bin/env python3

"""Provides utilities for creating h5 files containing itintal source
information and then plotting that information"""

import xml.etree.ElementTree as ET

import h5py
import openmc
import plotly.graph_objects as go
import numpy as np


def create_inital_particles(source, number_of_particles=2000):
    """Accepts an openmc source and creates an inital_source.h5 that can be
    used to find intial xyz, direction and energy of the partice source 
    """

    # MATERIALS

    # no real materials are needed for finding the source
    mats = openmc.Materials([])

    # GEOMETRY

    # just a minimal geometry
    outer_surface = openmc.Sphere(r=100, boundary_type='vacuum')
    cell = openmc.Cell(region=-outer_surface)
    universe = openmc.Universe(cells=[cell])
    geom = openmc.Geometry(universe)


    # SIMULATION SETTINGS
    
    # Instantiate a Settings object
    sett = openmc.Settings()
    sett.run_mode = "eigenvalue" # this will fail but it will write the inital_source.h5 file first
    sett.particles = number_of_particles
    sett.batches = 1
    sett.inactive = 0
    sett.write_initial_source = True

    sett.source = source

    model = openmc.model.Model(geom, mats, sett)

    model.export_to_xml()

    # this just adds write_initial_source == True to the settings.xml
    tree = ET.parse("settings.xml")
    root = tree.getroot()
    elem = ET.SubElement(root, "write_initial_source")
    elem.text = "true"
    tree.write("settings.xml")

    # This will crash hence the try except loop, but it writes the inital_source.h5
    try:
        openmc.run(output=False)
    except:
        pass

    return "initial_source.h5"


def plot_energy_from_initial_source(
        energy_bins=np.linspace(0, 20e6, 50),
        input_filename='initial_source.h5'):
    """makes a plot of the energy distribution of the source"""

    f = h5py.File(input_filename,'r')
    dset = f['source_bank']

    e_values = []

    for particle in dset:
        e_values.append(particle[2])

    # Calculate pdf for source energies
    probability, bin_edges = np.histogram(e_values, energy_bins, density=True)
    fig = go.Figure()

    # Plot source energy histogram
    fig.add_trace(go.Scatter(
        x=energy_bins[:-1],
        y=probability*np.diff(energy_bins),
        line={'shape': 'hv'},
        hoverinfo='text',
        name='particle direction',
        )
    ) 

    fig.update_layout(
          title='Particle energy',
          xaxis={'title': 'Energy (eV)'},
          yaxis={'title': 'Probability'}
    )

    return fig


def plot_postion_from_initial_source(input_filename='initial_source.h5'):
    """makes a plot of the inital creation locations of the particle source"""

    f = h5py.File(input_filename,'r')
    dset = f['source_bank']

    e_values = []
    x_values = []
    y_values = []
    z_values = []

    for particle in dset:
        x_values.append(particle[0][0])
        y_values.append(particle[0][1])
        z_values.append(particle[0][2])
        e_values.append(particle[2])
    
    text = ['Energy = '+str(i)+' eV' for i in e_values]

    fig = go.Figure()

    fig.add_trace(go.Scatter3d(
        x=x_values,
        y=y_values,
        z=z_values,
        hovertext=text,
        text=text,
        mode='markers',
        marker={'size': 2,
                'color': e_values,
               }
            )
        )

    fig.update_layout(title='Particle production coordinates - coloured by energy')

    return fig

def plot_direction_from_initial_source(input_filename='initial_source.h5'):
    """makes a plot of the inital creation directions of the particle source"""

    f = h5py.File(input_filename,'r')
    dset = f['source_bank']

    x_values = []
    y_values = []
    z_values = []
    x_dir = []
    y_dir = []
    z_dir = []

    for particle in dset:
        x_values.append(particle[0][0])
        y_values.append(particle[0][1])
        z_values.append(particle[0][2])
        x_dir.append(particle[1][0])
        y_dir.append(particle[1][1])
        z_dir.append(particle[1][2])


    fig = go.Figure()

    fig.add_trace({
        'type': 'cone',
        'cauto': False,
        'x': x_values,
        'y': y_values,
        'z': z_values,
        'u': x_dir,
        'v': y_dir,
        'w': z_dir,
        'cmin': 0,
        'cmax': 1,
        "anchor": "tail",
        "colorscale": 'Viridis',
        "hoverinfo": "u+v+w+norm",
        "sizemode": "absolute",
        "sizeref": 30,
        "showscale": False,
    })

    fig.update_layout(title='Particle initial directions')

    return fig
