#!/usr/bin/env python3

""" simulate_model.py: obtains a few netronics parameters for a basic sphere geometry ."""
""" run with python3 simulate_sphere_model.py | tqdm >> /dev/null """
""" outputs results to a file called simulation_results.json """

__author__      = "Jonathan Shimwell"

import openmc
import os
import json
import numpy as np
from numpy import random
import re 
from tqdm import tqdm
from inference.gp_tools import GpOptimiser
# from inference.gp_tools import GpOptimiser
from neutronics_material_maker import Material
from numpy import sin, cos, linspace, array, meshgrid
import matplotlib.pyplot as plt
import matplotlib as mpl
import ghalton




def make_materials_geometry_tallies(enrichment_fraction_list,batches = 2, inner_radius = 500, thickness = 100, breeder_material_name = 'Li', temperature_in_C = 500):
    if isinstance(enrichment_fraction_list,list):
        enrichment_fraction = enrichment_fraction_list[0]
    else:
        enrichment_fraction = enrichment_fraction_list
    print('simulating ',batches,enrichment_fraction,inner_radius,thickness,breeder_material_name)
    
    #MATERIALS from library of materials in neutronics_material_maker package
    breeder_material = Material(material_name = breeder_material_name,
                                enrichment_fraction = enrichment_fraction,
                                temperature_in_C = temperature_in_C).neutronics_material

    eurofer = Material(material_name = 'eurofer').neutronics_material

    mats = openmc.Materials([breeder_material, eurofer])

    #GEOMETRY#

    breeder_blanket_inner_surface = openmc.Sphere(r=inner_radius)
    breeder_blanket_outer_surface = openmc.Sphere(r=inner_radius+thickness)

    vessel_inner_surface = openmc.Sphere(r=inner_radius+thickness+10)
    vessel_outer_surface = openmc.Sphere(r=inner_radius+thickness+20,boundary_type='vacuum')

    breeder_blanket_region = -breeder_blanket_outer_surface & +breeder_blanket_inner_surface
    breeder_blanket_cell = openmc.Cell(region=breeder_blanket_region) 
    breeder_blanket_cell.fill = breeder_material
    breeder_blanket_cell.name = 'breeder_blanket'

    inner_void_region = -breeder_blanket_inner_surface 
    inner_void_cell = openmc.Cell(region=inner_void_region) 
    inner_void_cell.name = 'inner_void'

    vessel_region = +vessel_inner_surface & -vessel_outer_surface
    vessel_cell = openmc.Cell(region=vessel_region) 
    vessel_cell.name = 'vessel'
    vessel_cell.fill = eurofer

    blanket_vessel_gap_region = -vessel_inner_surface & + breeder_blanket_outer_surface
    blanket_vessel_gap_cell = openmc.Cell(region=blanket_vessel_gap_region) 
    blanket_vessel_gap_cell.name = 'blanket_vessel_gap'    

    universe = openmc.Universe(cells=[inner_void_cell, 
                                      breeder_blanket_cell,
                                      blanket_vessel_gap_cell,
                                      vessel_cell])

    geom = openmc.Geometry(universe)

    #SIMULATION SETTINGS#

    sett = openmc.Settings()
    # batches = 3 # this is parsed as an argument
    sett.batches = batches
    sett.inactive = 20
    sett.particles = 5000
    sett.run_mode = 'fixed source'

    source = openmc.Source()
    source.space = openmc.stats.Point((0,0,0))
    source.angle = openmc.stats.Isotropic()
    source.energy = openmc.stats.Muir(e0=14080000.0, m_rat=5.0, kt=20000.0) #neutron energy = 14.08MeV, AMU for D + T = 5, temperature is 20KeV
    sett.source = source

    #TALLIES#

    tallies = openmc.Tallies()

    # define filters
    cell_filter_breeder = openmc.CellFilter(breeder_blanket_cell)
    cell_filter_vessel = openmc.CellFilter(vessel_cell)
    particle_filter = openmc.ParticleFilter('neutron') #1 is neutron, 2 is photon
    surface_filter_rear_blanket = openmc.SurfaceFilter(breeder_blanket_outer_surface)
    surface_filter_rear_vessel = openmc.SurfaceFilter(vessel_outer_surface)
    energy_bins = openmc.mgxs.GROUP_STRUCTURES['VITAMIN-J-175']
    energy_filter = openmc.EnergyFilter(energy_bins)
    
    tally = openmc.Tally(name='TBR')
    tally.filters = [cell_filter_breeder]
    tally.scores = ['205'] # MT 205 is the (n,Xt) reaction where X is a wildcard, if MT 105 or (n,t) then some tritium production will be missed, for example (n,nt) which happens in Li7 would be missed
    tallies.append(tally)

    tally = openmc.Tally(name='blanket_leakage')
    tally.filters = [surface_filter_rear_blanket]
    tally.scores = ['current']
    tallies.append(tally)

    tally = openmc.Tally(name='vessel_leakage')
    tally.filters = [surface_filter_rear_vessel]
    tally.scores = ['current']
    tallies.append(tally)

    tally = openmc.Tally(name='breeder_blanket_spectra')
    tally.filters = [cell_filter_breeder, energy_filter]
    tally.scores = ['flux']
    tallies.append(tally)

    tally = openmc.Tally(name='vacuum_vessel_spectra')
    tally.filters = [cell_filter_vessel, energy_filter]
    tally.scores = ['flux']
    tallies.append(tally)

    tally = openmc.Tally(name='DPA')
    tally.filters = [cell_filter_vessel]
    tally.scores = ['444']
    tallies.append(tally)
 

    #RUN OPENMC #
    model = openmc.model.Model(geom, mats, sett, tallies)
    model.run()

    sp = openmc.StatePoint('statepoint.'+str(batches)+'.h5')

    json_output = {'enrichment_fraction': enrichment_fraction,
                   'inner_radius': inner_radius,
                   'thickness': thickness,
                   'breeder_material_name': breeder_material_name,
                   'temperature_in_C': temperature_in_C}

    tallies_to_retrieve = ['TBR', 'DPA', 'blanket_leakage', 'vessel_leakage']
    for tally_name in tallies_to_retrieve:
        tally = sp.get_tally(name=tally_name)
        
        df = tally.get_pandas_dataframe()
    
        tally_result = df['mean'].sum()
        tally_std_dev = df['std. dev.'].sum()

        json_output[tally_name] = {'value': tally_result,
                                   'std_dev': tally_std_dev}

    spectra_tallies_to_retrieve = ['breeder_blanket_spectra', 'vacuum_vessel_spectra']
    for spectra_name in spectra_tallies_to_retrieve:
        spectra_tally = sp.get_tally(name=spectra_name)
        spectra_tally_result = [entry[0][0] for entry in spectra_tally.mean]
        spectra_tally_std_dev = [entry[0][0] for entry in spectra_tally.std_dev]

        json_output[spectra_name] = {'value': spectra_tally_result,
                                     'std_dev': spectra_tally_std_dev,
                                     'energy_groups': list(energy_bins)}


    return json_output


def example_plot_1d(GP):
    M = 500
    x_gp = linspace(*bounds[0],M)
    mu, sig = GP(x_gp)
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, gridspec_kw={'height_ratios': [1, 3, 1]}, figsize = (10,8))
    plt.subplots_adjust(hspace=0)

    ax1.plot(evaluations, max_values, marker = 'o', ls = 'solid', c = 'orange', label = 'optimum value', zorder = 5)
    #ax1.plot([2,12], [max(y_func), max(y_func)], ls = 'dashed', label = 'actual max', c = 'black')
    ax1.set_xlabel('Simulations')
    ax1.set_xlim([0,len(evaluations)])
    #ax1.set_ylim([max(y)-0.3, max(y_func)+0.3])
    ax1.xaxis.set_label_position('top')
    ax1.yaxis.set_label_position('right')
    ax1.xaxis.tick_top()
    ax1.set_yticks([])
    ax1.legend(loc=4)

    
    ax2.errorbar(GP.x, GP.y, marker='o', yerr=GP.y_err, ftm=None, linestyle='', c = 'green', label = 'Simulation (Halton sample selection)', zorder = 5)
    if len(GP.y) > number_of_samples:
        ax2.errorbar(GP.x[number_of_samples:], GP.y[number_of_samples:], marker='o', yerr=GP.y_err[number_of_samples:], ftm=None, linestyle='', c = 'red', label = 'Simulation (Gaussian process selection)', zorder = 6)
    # ax2.plot(GP.x, GP.y, marker='o', c = 'red', label = 'observations', zorder = 5)
    #ax2.plot(GP.x, GP.y, 'o', c = 'red', label = 'observations', zorder = 5)
    #ax2.plot(x_gp, y_func, lw = 1.5, c = 'red', ls = 'dashed', label = 'actual function')
    ax2.plot(x_gp, mu, lw = 2, c = 'blue', label = 'GP prediction')
    ax2.fill_between(x_gp, (mu-2*sig), y2=(mu+2*sig), color = 'blue', alpha = 0.15, label = '95% confidence interval')
    # ax2.set_ylim([min(mu-2*sig),max(mu+2*sig)])
    ax2.set_ylim([0.8,2.0])
    ax2.set_xlim(*GP.bounds)
    ax2.set_ylabel('TBR')
    ax2.set_xticks([])
    ax2.legend(loc=2)

    aq = array([abs(GP.expected_improvement(array([k]))) for k in x_gp])
    ax3.plot(x_gp, 0.9*aq/max(aq), c = 'green', label = 'acquisition function')
    ax3.set_yticks([])
    ax3.set_xlabel('Li6 enrichment')
    ax3.legend(loc=1)

    print('plotting ',GP.x, GP.y, GP.y_err)
    # plt.show()
    plt.savefig(str(len(GP.y)).zfill(4)+'.png')


os.system('rm *.png')
sequencer = ghalton.Halton(1)
number_of_samples = 10
x = sequencer.get(number_of_samples)
x = [item for sublist in x for item in sublist]

bounds = [(0.0,1.0)]
#x = array([])
y = []
y_errors = []

max_values = []
evaluations = []

all_results = []

for filename_counter, coords in enumerate(x):
    
    results = make_materials_geometry_tallies(enrichment_fraction_list=coords ,batches = 2, inner_radius = 500, thickness = 100, breeder_material_name = 'Li', temperature_in_C = 500)
    
    all_results.append(results)     

    y.append(results['TBR']['value'])
    
    y_errors.append(0.1)#results['TBR']['std_dev'] * 2)

    print('x from HS',x[0:filename_counter+1])
    print('y from HS',y)
    print('y_errors  from HS',y_errors)
    print('bounds',bounds)
    

    if filename_counter >0:
        GP = GpOptimiser(x[0:filename_counter+1],y,y_err=y_errors,bounds=bounds)
        max_values.append(max(GP.y))
        evaluations.append(len(GP.y))
        example_plot_1d(GP)



for i in range(number_of_samples,number_of_samples+10):
    # plot the current state of the optimisation
    example_plot_1d(GP)

    # request the proposed evaluation
    new_x = GP.search_for_maximum()

    # evaluate the new point
    new_result = make_materials_geometry_tallies(enrichment_fraction_list = new_x ,batches = 2, inner_radius = 500, thickness = 100, breeder_material_name = 'Li', temperature_in_C = 500)
    all_results.append(results)  
    
    new_y = new_result['TBR']['value']
    new_y_error = new_result['TBR']['std_dev'] * 2

    print('x from loop',new_x)
    print('y from loop',new_y)
    print('new_y_error from loop',new_y_error)

    # update the gaussian process with the new information
    GP.add_evaluation(new_x, new_y, new_y_err=new_y_error)

    # track the optimum value for plotting
    max_values.append(max(GP.y))
    evaluations.append(len(GP.y))

os.system('convert *.png output.gif')

os.system('eog -f output.gif')

os.system('cp output.gif /my_openmc_workshop')



with open('simulation_results.json', 'w') as file_object:
    json.dump(all_results.append(results)  , file_object, indent=2)
       



