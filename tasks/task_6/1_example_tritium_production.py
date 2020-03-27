#!/usr/bin/env python3

"""example_tritium_production.py: plots few 2D views of a simple tokamak geometry with neutron flux."""

__author__ = "Jonathan Shimwell"

import openmc
import json
import os

# MATERIALS

breeder_material = openmc.Material(1, "PbLi")  # Pb84.2Li15.8
breeder_material.add_element('Pb', 84.2, percent_type='ao')
breeder_material.add_element('Li', 15.8, percent_type='ao', enrichment=50.0, enrichment_target='Li6', enrichment_type='ao')  # 50% enriched
breeder_material.set_density('atom/b-cm', 3.2720171e-2)  # around 11 g/cm3


steel = openmc.Material(name='steel')
steel.set_density('g/cm3', 7.75)
steel.add_element('Fe', 0.95, percent_type='wo')
steel.add_element('C', 0.05, percent_type='wo')

mats = openmc.Materials([breeder_material, steel])


# GEOMETRY

# surfaces
vessel_inner = openmc.Sphere(r=500)
first_wall_outer_surface = openmc.Sphere(r=510)
breeder_blanket_outer_surface = openmc.Sphere(r=610, boundary_type='vacuum')


# cells
inner_vessel_region = -vessel_inner
inner_vessel_cell = openmc.Cell(region=inner_vessel_region)

first_wall_region = -first_wall_outer_surface & +vessel_inner
first_wall_cell = openmc.Cell(region=first_wall_region)
first_wall_cell.fill = steel

breeder_blanket_region = +first_wall_outer_surface & -breeder_blanket_outer_surface
breeder_blanket_cell = openmc.Cell(region=breeder_blanket_region)
breeder_blanket_cell.fill = breeder_material

universe = openmc.Universe(cells=[inner_vessel_cell, first_wall_cell, breeder_blanket_cell])
geom = openmc.Geometry(universe)


# SIMULATION SETTINGS

# Instantiate a Settings object
sett = openmc.Settings()
batches = 2
sett.batches = batches
sett.inactive = 0
sett.particles = 5000
sett.run_mode = 'fixed source'

# Create a DT point source
source = openmc.Source()
source.space = openmc.stats.Point((0, 0, 0))
source.angle = openmc.stats.Isotropic()
source.energy = openmc.stats.Discrete([14e6], [1])
sett.source = source


tallies = openmc.Tallies()

# added a cell tally for tritium production
cell_filter = openmc.CellFilter(breeder_blanket_cell)
tbr_tally = openmc.Tally(name='TBR')
tbr_tally.filters = [cell_filter]
tbr_tally.scores = ['(n,Xt)']  # MT 205 is the (n,Xt) reaction where X is a wildcard, if MT 105 or (n,t) then some tritium production will be missed, for example (n,nt) which happens in Li7 would be missed
tallies.append(tbr_tally)


# Run OpenMC!
model = openmc.model.Model(geom, mats, sett, tallies)
model.run()

# open the results file
sp = openmc.StatePoint('statepoint.'+str(batches)+'.h5')

# access the tally using pandas dataframes
tbr_tally = sp.get_tally(name='TBR')
df = tbr_tally.get_pandas_dataframe()

tbr_tally_result = df['mean'].sum()
tbr_tally_std_dev = df['std. dev.'].sum()

# print results
print('The tritium breeding ratio was found, TBR = ', tbr_tally_result)
print('error on the tbr tally is ', tbr_tally_std_dev)

# output results to json file
json_output = {'TBR': tbr_tally_result,
               'TBR_std_dev': tbr_tally_std_dev}
with open('simulation_results.json', 'w') as file_object:
    json.dump(json_output, file_object, indent=2)
os.system('cp simulation_results.json /my_openmc_workshop')
