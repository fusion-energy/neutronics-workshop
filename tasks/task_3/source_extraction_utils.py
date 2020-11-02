#!/usr/bin/env python3

"""Provides utilities for creating h5 files containing itintal source
information and then plotting that information"""

import xml.etree.ElementTree as ET

import h5py
import openmc
import plotly.graph_objects as go
import numpy as np


def make_inital_source(
    energy=openmc.stats.Discrete([14e6], [1]),
    number_of_particles=2000):
    """Accepts different energy distirbutions and creates an intial
    source file for the simulation. Example arguments for energy
    are openmc.stats.Discrete([14e6], [1]),
    openmc.stats.Watt(a=988000.0, b=2.249e-06) and
    openmc.stats.Muir(e0=14080000.0, m_rat=5.0, kt=20000.0)
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

    # creates an isotropic point source
    source = openmc.Source()
    source.space = openmc.stats.Point((0, 0, 0))
    source.angle = openmc.stats.Isotropic()

    # sets the energy of neutrons decided by the function arguments
    source.energy = energy

    sett.source = source

    model = openmc.model.Model(geom, mats, sett)

    model.export_to_xml()

    # this just adds write_initial_source == True to the settings.xml
    tree = ET.parse("settings.xml")
    root = tree.getroot()
    elem = ET.SubElement(root, "write_initial_source")
    elem.text = "true"
    tree.write("settings.xml")

    # Run OpenMC!
    # this will crash hence the try except loop, but it writes the inital source.h5
    try:
        openmc.run()
    except:
        pass

    return "initial_source.h5"


def plot_energy_from_initial_source(
        energy_bins=np.linspace(0, 20e6, 50),
        input_filename='initial_source.h5'):
    """makes a plot of the energ distribution of the source"""

    f = h5py.File(input_filename,'r')
    dset = f['source_bank']

    e_values = []

    for particle in dset:
        # different attributes can be obtained here
        # xyz is [0][0], [0][1], [0][2]
        # dir is [1][0], [1][1], [1][2]
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
        name='neutron direction',
        )
    ) 

    fig.update_layout(
          title='neutron energy',
          xaxis={'title': 'Energy (eV)'},
          yaxis={'title': 'Probability'}
    )
    fig.show()
    return fig
