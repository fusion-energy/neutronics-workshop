#!/usr/bin/env python3

"""example_isotope_plot.py: plots few 2D views of a simple tokamak geometry with neutron flux."""

__author__      = "Jonathan Shimwell"

import openmc
import matplotlib.pyplot as plt
import os

#MATERIALS#

breeder_material = openmc.Material(1, "Lithium") 
breeder_material.set_density('g/cm3', 2.)
breeder_material.add_element('Li', 1., 'ao')

firstwall_material = openmc.Material(name='Iron')
firstwall_material.set_density('g/cm3', 7.75)
firstwall_material.add_element('Fe', 1., percent_type='wo')

mats = openmc.Materials([breeder_material, firstwall_material])


#GEOMETRY#

#surfaces
vessel_inner = openmc.Sphere(r=500)
first_wall_outer_surface = openmc.Sphere(r=510)
breeder_blanket_outer_surface = openmc.Sphere(r=610,boundary_type='vacuum')

#cells
inner_vessel_region = -vessel_inner
inner_vessel_cell = openmc.Cell(region=inner_vessel_region) 
# filled with void by default

first_wall_region = -first_wall_outer_surface & +vessel_inner
first_wall_cell = openmc.Cell(region=first_wall_region) 
first_wall_cell.fill = firstwall_material

breeder_blanket_region = +first_wall_outer_surface & -breeder_blanket_outer_surface
breeder_blanket_cell = openmc.Cell(region=breeder_blanket_region) 
breeder_blanket_cell.fill = breeder_material

universe = openmc.Universe(cells=[inner_vessel_cell,first_wall_cell, breeder_blanket_cell])
geom = openmc.Geometry(universe)




#SIMULATION SETTINGS#

# Instantiate a Settings object
sett = openmc.Settings()
batches = 2
sett.batches = batches
sett.inactive = 0
sett.particles = 5000
sett.run_mode = 'fixed source'

# Create a DT point source
source = openmc.Source()
source.space = openmc.stats.Point((300,0,0))
source.angle = openmc.stats.Isotropic()
source.energy = openmc.stats.Discrete([14e6], [1])
sett.source = source


tallies = openmc.Tallies()

#added a cell tally for tritium production
cell_filter = openmc.CellFilter(first_wall_cell)
reaction_tally = openmc.Tally(name='DPA')
reaction_tally.filters = [cell_filter]
reaction_tally.scores = ['444']
tallies.append(reaction_tally)


# Run OpenMC!
model = openmc.model.Model(geom, mats, sett, tallies)
model.run()

# open the results file
sp = openmc.StatePoint('statepoint.'+str(batches)+'.h5')

# access the tally
tally = sp.get_tally(name='DPA')

df = tally.get_pandas_dataframe()

tally_result = df['mean'].sum()
tally_std_dev = df['std. dev.'].sum()


print('Displacement damage = ',tally_result)
print('error on the DPA tally is ',tally_std_dev)
