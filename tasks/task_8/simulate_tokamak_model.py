#!/usr/bin/env python3

""" simulate_model.py: obtains a few netronics parameters for a basic tokamak geometry ."""
""" run with python3 simulate_tokamak_model.py | tqdm >> /dev/null """
""" outputs results to a file called simulation_results.json """

__author__      = "Jonathan Shimwell"


import re 
import openmc
import os
import json
import numpy as np
from numpy import random
from tqdm import tqdm
import sys
import os
import matplotlib.pyplot as plt
from material_maker_functions import *


def make_breeder_materials(enrichment_fraction, breeder_material_name, temperature_in_C):

    #density data from http://aries.ucsd.edu/LIB/PROPS/PANOS/matintro.html

    natural_breeder_material = openmc.Material(name = "natural_breeder_material")
    breeder_material = openmc.Material(name = "breeder_material")

    element_numbers = get_element_numbers(breeder_material_name)
    elements = get_elements(breeder_material_name)

    for e, en in zip(elements, element_numbers):
        natural_breeder_material.add_element(e, en,'ao')

    for e, en in zip(elements, element_numbers):
        if e == 'Li':
            breeder_material.add_nuclide('Li6', en * enrichment_fraction, 'ao')
            breeder_material.add_nuclide('Li7', en * (1.0-enrichment_fraction), 'ao')  
        else:
            breeder_material.add_element(e, en,'ao')    

    density_of_natural_material_at_temperature = find_density_of_natural_material_at_temperature(breeder_material_name,temperature_in_C,natural_breeder_material)

    natural_breeder_material.set_density('g/cm3', density_of_natural_material_at_temperature)
    atom_densities_dict = natural_breeder_material.get_nuclide_atom_densities()
    atoms_per_barn_cm = sum([i[1] for i in atom_densities_dict.values()])

    breeder_material.set_density('atom/b-cm',atoms_per_barn_cm) 

    return breeder_material



def make_geometry_tallies(batches,nps,enrichment_fraction,inner_radius,thickness,breeder_material_name,temperature_in_C):
    #print('simulating ',batches,enrichment_fraction,inner_radius,thickness,breeder_material_name)

    #MATERIALS#
    breeder_material = make_breeder_materials(enrichment_fraction,breeder_material_name,temperature_in_C)
    eurofer = make_eurofer()
    copper  = make_copper()
    mats = openmc.Materials([breeder_material,eurofer, copper])
    mats.export_to_xml('materials.xml')


    #GEOMETRY#

    central_sol_surface = openmc.ZCylinder(r=100)
    central_shield_outer_surface = openmc.ZCylinder(r=110)
    first_wall_inner_surface = openmc.Sphere(r=inner_radius)
    first_wall_outer_surface = openmc.Sphere(r=inner_radius+10)
    breeder_blanket_outer_surface = openmc.Sphere(r=inner_radius+10.0+thickness)
    vessel_outer_surface = openmc.Sphere(r=inner_radius+10.0+thickness+10.0,boundary_type='vacuum')
    
    central_sol_region = -central_sol_surface & -breeder_blanket_outer_surface
    central_sol_cell = openmc.Cell(region=central_sol_region) 
    central_sol_cell.fill = copper

    central_shield_region = +central_sol_surface & -central_shield_outer_surface & -breeder_blanket_outer_surface
    central_shield_cell = openmc.Cell(region=central_shield_region) 
    central_shield_cell.fill = eurofer

    inner_void_region = -first_wall_inner_surface & +central_shield_outer_surface
    inner_void_cell = openmc.Cell(region=inner_void_region) 
    inner_void_cell.name = 'inner_void'

    first_wall_region = -first_wall_outer_surface & +first_wall_inner_surface & +central_shield_outer_surface
    first_wall_cell = openmc.Cell(region=first_wall_region) 
    first_wall_cell.fill = eurofer

    breeder_blanket_region = +first_wall_outer_surface & -breeder_blanket_outer_surface & +central_shield_outer_surface
    breeder_blanket_cell = openmc.Cell(region=breeder_blanket_region) 
    breeder_blanket_cell.fill = breeder_material

    vessel_region = +breeder_blanket_outer_surface & -vessel_outer_surface
    vessel_cell = openmc.Cell(region=vessel_region) 
    vessel_cell.name = 'vessel'
    vessel_cell.fill = eurofer

    universe = openmc.Universe(cells=[central_sol_cell,
                                      central_shield_cell,
                                      inner_void_cell,
                                      first_wall_cell, 
                                      breeder_blanket_cell,
                                      vessel_cell])

    #plt.show(universe.plot(width=(1500,1500),basis='xz'))


    geom = openmc.Geometry(universe)
    # geom.export_to_xml('geometry.xml')

    #SIMULATION SETTINGS#

    sett = openmc.Settings()
    sett.batches = batches
    sett.inactive = 1
    sett.particles = nps
    sett.run_mode = 'fixed source'

    source = openmc.Source()
    source.space = openmc.stats.Point((150,0,0))
    source.angle = openmc.stats.Isotropic()
    #source.energy = openmc.stats.Discrete([14.08e6], [1])
    source.energy = openmc.stats.Muir(e0=14080000.0, m_rat=5.0, kt=20000.0) #neutron energy = 14.08MeV, AMU for D + T = 5, temperature is 20KeV
    sett.source = source

    sett.export_to_xml('settings.xml')


    #tally filters
    particle_filter = openmc.ParticleFilter('neutron')
    cell_filter_breeder = openmc.CellFilter(breeder_blanket_cell)
    cell_filter_vessel = openmc.CellFilter(vessel_cell)
    surface_filter_front = openmc.SurfaceFilter(first_wall_inner_surface)
    surface_filter_rear = openmc.SurfaceFilter(breeder_blanket_outer_surface)
    energy_bins = openmc.mgxs.GROUP_STRUCTURES['VITAMIN-J-175']   
    energy_filter = openmc.EnergyFilter(energy_bins)

    #TALLIES#
    tallies = openmc.Tallies()

    tally = openmc.Tally(name='TBR')
    tally.filters = [cell_filter_breeder,particle_filter]
    tally.scores = ['205']
    tallies.append(tally)

    tally = openmc.Tally(name='blanket_leakage')
    tally.filters = [surface_filter_rear,particle_filter]
    tally.scores = ['current']
    tallies.append(tally)

    tally = openmc.Tally(name='vessel_leakage')
    tally.filters = [surface_filter_rear,particle_filter]
    tally.scores = ['current']
    tallies.append(tally)    

    tally = openmc.Tally(name='rear_neutron_spectra')
    tally.filters = [surface_filter_rear,particle_filter,energy_filter]
    tally.scores = ['flux']
    tallies.append(tally)

    tally = openmc.Tally(name='front_neutron_spectra')
    tally.filters = [surface_filter_front,particle_filter,energy_filter]
    tally.scores = ['flux']
    tallies.append(tally)

    tally = openmc.Tally(name='breeder_blanket_spectra')
    tally.filters = [cell_filter_breeder,particle_filter,energy_filter]
    tally.scores = ['flux']
    tallies.append(tally)    

    tally = openmc.Tally(name='vacuum_vessel_spectra')
    tally.filters = [cell_filter_vessel,particle_filter,energy_filter]
    tally.scores = ['flux']
    tallies.append(tally)        

    tally = openmc.Tally(name='DPA')
    tally.filters = [cell_filter_vessel,particle_filter]
    tally.scores = ['444']
    tallies.append(tally)    


    #RUN OPENMC #
    model = openmc.model.Model(geom, mats, sett, tallies)
    
    model.run()


    #RETRIEVING TALLY RESULTS

    sp = openmc.StatePoint('statepoint.'+str(batches)+'.h5')
    
    json_output= {'enrichment_fraction':enrichment_fraction,
                  'inner_radius':inner_radius,
                  'thickness':thickness,
                  'breeder_material_name':breeder_material_name,
                  'temperature_in_C':temperature_in_C}

    tallies_to_retrieve = ['TBR', 'DPA', 'blanket_leakage', 'vessel_leakage']
    for tally_name in tallies_to_retrieve:
        tally = sp.get_tally(name=tally_name)
        
        df = tally.get_pandas_dataframe()
    
        tally_result = df['mean'].sum()
        tally_std_dev = df['std. dev.'].sum()

        json_output[tally_name] = {'value': tally_result,
                                   'std_dev':tally_std_dev}

    spectra_tallies_to_retrieve = ['front_neutron_spectra', 'breeder_blanket_spectra', 'vacuum_vessel_spectra', 'rear_neutron_spectra']
    for spectra_name in spectra_tallies_to_retrieve:
        spectra_tally = sp.get_tally(name=spectra_name)
        spectra_tally_result = [entry[0][0] for entry in spectra_tally.mean] 
        spectra_tally_std_dev = [entry[0][0] for entry in spectra_tally.std_dev] 

        json_output[spectra_name] = {'value': spectra_tally_result,
                                     'std_dev':spectra_tally_std_dev,
                                     'energy_groups':list(energy_bins)}

    return json_output



results = []
num_simulations = 5 # this value will need to be changed

for i in tqdm(range(0,num_simulations)):
    breeder_material_name = random.choice(['Li4SiO4', 'F2Li2BeF2', 'Li', 'Pb84.2Li15.8'])
    enrichment_fraction = random.uniform(0, 1)
    thickness = random.uniform(1, 500)
    result = make_geometry_tallies(batches=2,
                                   nps=1000, # this value will need to be increased
                                   enrichment_fraction=enrichment_fraction,
                                   inner_radius=500,
                                   thickness=thickness,
                                   breeder_material_name = breeder_material_name, 
                                   temperature_in_C=500
                                   )
    results.append(result)

output_filename = 'simulation_results.json'
with open(output_filename, mode='w', encoding='utf-8') as f:
    json.dump(results, f)




