#!/usr/bin/env python3

"""example_isotope_plot.py: plots few 2D views of a simple tokamak geometry with neutron flux."""

__author__      = "Jonathan Shimwell"

import openmc
import matplotlib.pyplot as plt
import os

#MATERIALS#

breeder_material = openmc.Material(1, "PbLi") #Pb84.2Li15.8 with natural enrichment of Li6
enrichment_fraction = 0.50
breeder_material.add_element('Pb', 84.2,'ao')
breeder_material.add_nuclide('Li6', enrichment_fraction*15.8, 'ao')
breeder_material.add_nuclide('Li7', (1.0-enrichment_fraction)*15.8, 'ao')
breeder_material.set_density('atom/b-cm',3.2720171e-2) # around 11 g/cm3

copper = openmc.Material(name='Copper')
copper.set_density('g/cm3', 8.5)
copper.add_element('Cu', 1.0)

eurofer = openmc.Material(name='EUROFER97')
eurofer.set_density('g/cm3', 7.75)
eurofer.add_element('Fe', 89.067, percent_type='wo')
eurofer.add_element('C', 0.11, percent_type='wo')
eurofer.add_element('Mn', 0.4, percent_type='wo')
eurofer.add_element('Cr', 9.0, percent_type='wo')
eurofer.add_element('Ta', 0.12, percent_type='wo')
eurofer.add_element('W', 1.1, percent_type='wo')
eurofer.add_element('N', 0.003, percent_type='wo')
eurofer.add_element('V', 0.2, percent_type='wo')

mats = openmc.Materials([breeder_material, eurofer, copper])
mats.export_to_xml()


#GEOMETRY#

#surfaces
central_sol_surface = openmc.ZCylinder(r=100)
central_shield_outer_surface = openmc.ZCylinder(r=110)
vessel_inner = openmc.Sphere(r=500)
first_wall_outer_surface = openmc.Sphere(r=510)
breeder_blanket_outer_surface = openmc.Sphere(r=610,boundary_type='vacuum')

#cells

central_sol_region = -central_sol_surface & -breeder_blanket_outer_surface
central_sol_cell = openmc.Cell(region=central_sol_region) 
central_sol_cell.fill = copper

central_shield_region = +central_sol_surface & -central_shield_outer_surface & -breeder_blanket_outer_surface
central_shield_cell = openmc.Cell(region=central_shield_region) 
central_shield_cell.fill = eurofer

inner_vessel_region = -vessel_inner & + central_shield_outer_surface
inner_vessel_cell = openmc.Cell(region=inner_vessel_region) 

first_wall_region = -first_wall_outer_surface & +vessel_inner
first_wall_cell = openmc.Cell(region=first_wall_region) 
first_wall_cell.fill = eurofer

breeder_blanket_region = +first_wall_outer_surface & -breeder_blanket_outer_surface & +central_shield_outer_surface
breeder_blanket_cell = openmc.Cell(region=breeder_blanket_region) 
breeder_blanket_cell.fill = breeder_material

universe = openmc.Universe(cells=[central_sol_cell,central_shield_cell,inner_vessel_cell,first_wall_cell, breeder_blanket_cell])
geom = openmc.Geometry(universe)

geom.export_to_xml()

sphere = openmc.Sphere(r=10.0)
cell = openmc.Cell(region=-sphere)
vol_calc = openmc.VolumeCalculation(domains=[cell], samples=1000000)

# cell_vol_calc = openmc.VolumeCalculation([breeder_blanket_cell], 10000)

#SIMULATION SETTINGS#

# Instantiate a Settings object
sett = openmc.Settings()
batches = 2
sett.batches = batches
sett.inactive = 1
sett.particles = 50
sett.run_mode = 'fixed source'

# Create a DT point source
source = openmc.Source()
source.space = openmc.stats.Point((300,0,0))
source.angle = openmc.stats.Isotropic()
source.energy = openmc.stats.Discrete([14e6], [1])
sett.source = source
sett.volume_calculations 
sett.export_to_xml()


openmc.calculate_volumes()

#openmc.run()