#!/usr/bin/env python3

"""example_isotope_plot.py: plots few 2D views of a simple tokamak geometry with neutron flux."""

__author__      = "Jonathan Shimwell"

import openmc
import matplotlib.pyplot as plt
import os

def test_volume(uo2):
    """Test adding volume information from a volume calculation."""
    # Create model with nested spheres
    model = openmc.model.Model()
    model.materials.append(uo2)
    inner = openmc.Sphere(r=1.)
    outer = openmc.Sphere(r=2., boundary_type='vacuum')
    c1 = openmc.Cell(fill=uo2, region=-inner)
    c2 = openmc.Cell(region=+inner & -outer)
    u = openmc.Universe(cells=[c1, c2])
    model.geometry.root_universe = u
    model.settings.particles = 100
    model.settings.batches = 10
    model.settings.run_mode = 'fixed source'
    model.settings.source = openmc.Source(space=openmc.stats.Point())

    ll, ur = model.geometry.bounding_box
    
    model.settings.volume_calculations

    for domain in (c1, uo2, u):
        # Run stochastic volume calculation
        volume_calc = openmc.VolumeCalculation(
            domains=[domain], samples=1000, lower_left=ll, upper_right=ur)
        model.settings.volume_calculations = [volume_calc]
        model.export_to_xml()
        openmc.calculate_volumes()

        # Load results and add volume information
        volume_calc.load_results('volume_1.h5')
        model.geometry.add_volume_information(volume_calc)

        # get_nuclide_densities relies on volume information
        nucs = set(domain.get_nuclide_densities())



copper = openmc.Material(name='Copper')
copper.set_density('g/cm3', 8.5)
copper.add_element('Cu', 1.0)

test_volume(copper)