#!/usr/bin/env python3

"""example_CAD_simulation.py: uses a dagmc.h5m file for the geometry."""

__author__      = "Jonathan Shimwell"

import openmc


#MATERIALS#

breeder_material = openmc.Material(1, "breeder_material") #Pb84.2Li15.8 with natural enrichment of Li6
enrichment_fraction = 0.90
breeder_material.add_element('Pb', 84.2,'ao')
breeder_material.add_nuclide('Li6', enrichment_fraction*15.8, 'ao')
breeder_material.add_nuclide('Li7', (1.0-enrichment_fraction)*15.8, 'ao')
breeder_material.set_density('atom/b-cm',3.2720171e-2) # around 11 g/cm3

copper = openmc.Material(name='magnet_material')
copper.set_density('g/cm3', 8.5)
copper.add_element('Cu', 1.0)

eurofer = openmc.Material(name='eurofer')
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


#GEOMETRY#

universe = openmc.Universe()
geom = openmc.Geometry(universe) # do i need this with DAGMC?




#SIMULATION SETTINGS#

# Instantiate a Settings object
sett = openmc.Settings()
batches = 10
sett.batches = batches
sett.inactive = 0
sett.particles = 500
sett.run_mode = 'fixed source'
sett.dagmc = True

# Create a DT point source
source = openmc.Source()
source.space = openmc.stats.Point((0,0,0))
source.angle = openmc.stats.Isotropic()
source.energy = openmc.stats.Discrete([14e6], [1])
sett.source = source


tallies = openmc.Tallies()

#added a cell tally for tritium production
cell_filter = openmc.CellFilter(1) #breeder_material is in cell number 1
tbr_tally = openmc.Tally(2,name='TBR')
tbr_tally.filters = [cell_filter]
tbr_tally.scores = ['(n,t)'] #or 205
tallies.append(tbr_tally)


# Run OpenMC!
model = openmc.model.Model(geom, mats, sett, tallies)
model.run()

# open the results file
sp = openmc.StatePoint('statepoint.'+str(batches)+'.h5')

# access the tally
tbr_tally = sp.get_tally(name='TBR')
df = tbr_tally.get_pandas_dataframe()

tbr_tally_result = df['mean'].sum()

print('The tritium breeding ratio was found, TBR = ',tbr_tally_result)

