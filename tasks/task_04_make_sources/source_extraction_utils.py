#!/usr/bin/env python3

"""Provides utilities for creating h5 files containing initial source
information and then plotting that information"""

import xml.etree.ElementTree as ET

import h5py
import numpy as np
import openmc
import plotly.graph_objects as go


def create_initial_particles(source, number_of_particles=2000, openmc_exec='openmc'):
    """Accepts an openmc source and creates an initial_source.h5 that can be
    used to find initial xyz, direction and energy of the partice source
    """

    # no real materials are needed for finding the source
    mats = openmc.Materials([])

    # just a minimal geometry
    outer_surface = openmc.Sphere(r=100, boundary_type="vacuum")
    cell = openmc.Cell(region=-outer_surface)
    universe = openmc.Universe(cells=[cell])
    geom = openmc.Geometry(universe)

    # Instantiate a Settings object
    settings = openmc.Settings()
    settings.run_mode = ("fixed source")
    settings.particles = number_of_particles
    settings.batches = 1
    settings.inactive = 0
    settings.write_initial_source = True
    settings.source = source

    model = openmc.model.Model(geom, mats, settings)

    model.export_to_xml()

    # openmc.run(openmc_exec='/home/jshimwell/openmc/build/bin/openmc_0.11.0')
    # when using conda install openmc==0.11.0 then the dir for the executable is
    # '/home/jshimwell/miniconda3/envs/openmc_0_11_0/bin/openmc'
    openmc.run(openmc_exec=openmc_exec)


def plot_energy_from_initial_source(
    energy_bins=np.linspace(0, 20e6, 50),
    input_filename: str = "initial_source.h5"
):
    """makes a plot of the energy distribution of the source"""

    f = h5py.File(input_filename, "r")
    dset = f["source_bank"]

    e_values = []

    for particle in dset:
        e_values.append(particle[2])

    # Calculate pdf for source energies
    probability, bin_edges = np.histogram(e_values, energy_bins, density=True)
    fig = go.Figure()

    # Plot source energy histogram
    fig.add_trace(
        go.Scatter(
            x=energy_bins[:-1],
            y=probability * np.diff(energy_bins),
            line={"shape": "hv"},
            hoverinfo="text",
            name="particle direction",
        )
    )

    fig.update_layout(
        title="Particle energy",
        xaxis={"title": "Energy (eV)"},
        yaxis={"title": "Probability"},
    )

    return fig


def plot_postion_from_initial_source(input_filename="initial_source.h5"):
    """makes a plot of the initial creation locations of the particle source"""

    f = h5py.File(input_filename, "r")
    dset = f["source_bank"]

    e_values = []
    x_values = []
    y_values = []
    z_values = []

    for particle in dset:
        x_values.append(particle[0][0])
        y_values.append(particle[0][1])
        z_values.append(particle[0][2])
        e_values.append(particle[2])

    text = ["Energy = " + str(i) + " eV" for i in e_values]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter3d(
            x=x_values,
            y=y_values,
            z=z_values,
            hovertext=text,
            text=text,
            mode="markers",
            marker={
                "size": 2,
                "color": e_values,
            },
        )
    )

    fig.update_layout(title="Particle production coordinates - coloured by energy")

    return fig


def plot_direction_from_initial_source(input_filename="initial_source.h5"):
    """makes a plot of the initial creation directions of the particle source"""

    f = h5py.File(input_filename, "r")
    dset = f["source_bank"]

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

    fig.add_trace(
        {
            "type": "cone",
            "cauto": False,
            "x": x_values,
            "y": y_values,
            "z": z_values,
            "u": x_dir,
            "v": y_dir,
            "w": z_dir,
            "cmin": 0,
            "cmax": 1,
            "anchor": "tail",
            "colorscale": "Viridis",
            "hoverinfo": "u+v+w+norm",
            "sizemode": "absolute",
            "sizeref": 30,
            "showscale": False,
        }
    )

    fig.update_layout(title="Particle initial directions")

    return fig
