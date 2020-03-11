#!/usr/bin/env python3

"""1_find_dpa.py: Calculates the neutron damage via a 444 MT reaction tally."""

import openmc
import json


#MATERIALS#

firstwall_material = openmc.Material(name='Iron')
firstwall_material.set_density('g/cm3', 7.75)
firstwall_material.add_element('Fe', 1.0, percent_type='wo')

breeder_material = openmc.Material(name="Lithium") 
breeder_material.set_density('g/cm3', 2.0)
breeder_material.add_element('Li', 1.0, percent_type='ao')

mats = openmc.Materials([firstwall_material, breeder_material])


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
batches = 10
sett.batches = batches
sett.inactive = 0
sett.particles = 10000
sett.run_mode = 'fixed source'

# Create a DT point source
source = openmc.Source()
source.space = openmc.stats.Point((0,0,0))
source.angle = openmc.stats.Isotropic()
source.energy = openmc.stats.Discrete([14e6], [1])
sett.source = source


tallies = openmc.Tallies()

# added a cell tally for tritium production
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

damage_energy_in_ev = df['mean'].sum()


print('Damage energy depositied per source neutron = ',damage_energy_in_ev, 'eV\n')

print('Two times the threshold energy of 40eV is needed to displace an atom')
displacements_per_source_neutron = damage_energy_in_ev / (2*40)
print('Displacements per source neutron = ', displacements_per_source_neutron, '\n')

print('Assuming about 80% remains after 20% recombine to original lattice locations')
displacements_per_source_neutron_with_recombination = displacements_per_source_neutron*0.8
print('Displacements per source neutron after recombination = ', displacements_per_source_neutron_with_recombination, '\n')

fusion_power = 3e9 # units Watts
energy_per_fusion_reaction = 17.6e6 # units eV
eV_to_Joules = 1.60218e-19 # multiplication factor to convert eV to Joules
number_of_neutrons_per_second = fusion_power/ (energy_per_fusion_reaction*eV_to_Joules)
print('Number of neutrons per second', number_of_neutrons_per_second, '\n')

number_of_neutrons_per_year = number_of_neutrons_per_second * 60*60*24*365.25
print('Number of neutrons per full power year ', number_of_neutrons_per_year)

displacements_for_all_atoms = number_of_neutrons_per_year * displacements_per_source_neutron_with_recombination
print('displacements for all atoms in the volume ', displacements_for_all_atoms, '\n')

print('Now the number of atoms in the volume must be found to find displacements per atom (DPA)')

json_output = {'Damage energy in eV': damage_energy_in_ev,
               'Total number of displacements': displacements_for_all_atoms}

with open('1_find_dpa_results.json', 'w') as file_object:
    json.dump(json_output, file_object, indent=2)
