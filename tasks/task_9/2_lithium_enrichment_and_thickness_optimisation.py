#!/usr/bin/env python3

""" simulate_model.py: obtains a few netronics parameters for a basic sphere geometry ."""
""" run with python3 simulate_sphere_model.py | tqdm >> /dev/null """
""" outputs results to a file called simulation_results.json """

__author__ = "Jonathan Shimwell"

import openmc
import os
import json
import numpy as np
from numpy import random
import re
from tqdm import tqdm
from gp_tools import GpOptimiser
# from inference.gp_tools import GpOptimiser
from numpy import sin, cos, linspace, array, meshgrid
import matplotlib.pyplot as plt
import matplotlib as mpl
import ghalton
from neutronics_material_maker import Material


def make_materials_geometry_tallies(v):
    enrichment_fraction, thickness = v
    inner_radius = 500
    breeder_material_name = 'Li'
    temperature_in_C = 500

    print('simulating enrichment,', enrichment_fraction, 'thickness ', thickness)

    # MATERIALS from library of materials in neutronics_material_maker package
    breeder_material = Material(material_name=breeder_material_name,
                                enrichment_fraction=enrichment_fraction,
                                temperature_in_C=temperature_in_C).neutronics_material

    eurofer = Material(material_name='eurofer').neutronics_material

    mats = openmc.Materials([breeder_material, eurofer])

    # GEOMETRY

    breeder_blanket_inner_surface = openmc.Sphere(r=inner_radius)
    breeder_blanket_outer_surface = openmc.Sphere(r=inner_radius+thickness)

    vessel_inner_surface = openmc.Sphere(r=inner_radius+thickness+10)
    vessel_outer_surface = openmc.Sphere(r=inner_radius+thickness+20, boundary_type='vacuum')

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

    blanket_vessel_gap_region = -vessel_inner_surface & +breeder_blanket_outer_surface
    blanket_vessel_gap_cell = openmc.Cell(region=blanket_vessel_gap_region)
    blanket_vessel_gap_cell.name = 'blanket_vessel_gap'

    universe = openmc.Universe(cells=[inner_void_cell,
                                      breeder_blanket_cell,
                                      blanket_vessel_gap_cell,
                                      vessel_cell])

    geom = openmc.Geometry(universe)

    # SIMULATION SETTINGS

    sett = openmc.Settings()
    # batches = 3 # this is parsed as an argument
    sett.batches = batches
    sett.inactive = 0
    sett.particles = 500
    sett.run_mode = 'fixed source'

    source = openmc.Source()
    source.space = openmc.stats.Point((0, 0, 0))
    source.angle = openmc.stats.Isotropic()
    source.energy = openmc.stats.Muir(e0=14080000.0, m_rat=5.0, kt=20000.0)  # neutron energy = 14.08MeV, AMU for D + T = 5, temperature is 20KeV
    sett.source = source

    # TALLIES

    tallies = openmc.Tallies()

    # define filters
    cell_filter_breeder = openmc.CellFilter(breeder_blanket_cell)
    cell_filter_vessel = openmc.CellFilter(vessel_cell)
    particle_filter = openmc.ParticleFilter([1])  # 1 is neutron, 2 is photon
    surface_filter_rear_blanket = openmc.SurfaceFilter(breeder_blanket_outer_surface)
    surface_filter_rear_vessel = openmc.SurfaceFilter(vessel_outer_surface)
    energy_bins = openmc.mgxs.GROUP_STRUCTURES['VITAMIN-J-175']
    energy_filter = openmc.EnergyFilter(energy_bins)

    tally = openmc.Tally(name='TBR')
    tally.filters = [cell_filter_breeder, particle_filter]
    tally.scores = ['(n,Xt)']  # MT 205 is the (n,Xt) reaction where X is a wildcard, if MT 105 or (n,t) then some tritium production will be missed, for example (n,nt) which happens in Li7 would be missed
    tallies.append(tally)

    # RUN OPENMC
    model = openmc.model.Model(geom, mats, sett, tallies)
    model.run()

    sp = openmc.StatePoint('statepoint.'+str(batches)+'.h5')

    json_output = {'enrichment_fraction': enrichment_fraction,
                   'inner_radius': inner_radius,
                   'thickness': thickness,
                   'breeder_material_name': breeder_material_name,
                   'temperature_in_C': temperature_in_C}

    tally = sp.get_tally(name='TBR')

    df = tally.get_pandas_dataframe()

    json_output['TBR'] = df['mean'].sum()
    json_output['TBR_std_dev'] = df['std. dev.'].sum()

    return json_output


def example_plot_1d(GP):
    M = 500
    x_gp = linspace(*bounds[0], M)
    mu, sig = GP(x_gp)
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, gridspec_kw={'height_ratios': [1, 3, 1]}, figsize=(10, 8))
    plt.subplots_adjust(hspace=0)

    ax1.plot(evaluations, max_values, marker='o', ls='solid', c='orange', label='optimum value', zorder=5)
    # ax1.plot([2,12], [max(y_func), max(y_func)], ls='dashed', label='actual max', c='black')
    ax1.set_xlabel('Simulations')
    ax1.set_xlim([0, len(evaluations)])
    # ax1.set_ylim([max(y)-0.3, max(y_func)+0.3])
    ax1.xaxis.set_label_position('top')
    ax1.yaxis.set_label_position('right')
    ax1.xaxis.tick_top()
    ax1.set_yticks([])
    ax1.legend(loc=4)

    ax2.errorbar(GP.x, GP.y, marker='o', yerr=GP.y_err, ftm=None, linestyle='', c='green', label='Simulation (Halton sample selection)', zorder=5)
    if len(GP.y) > number_of_samples:
        ax2.errorbar(GP.x[number_of_samples:], GP.y[number_of_samples:], marker='o', yerr=GP.y_err[number_of_samples:], ftm=None, linestyle='', c='red', label='Simulation (Gaussian process selection)', zorder=6)
    # ax2.plot(GP.x, GP.y, marker='o', c='red', label='observations', zorder=5)
    # ax2.plot(GP.x, GP.y, 'o', c='red', label='observations', zorder=5)
    # ax2.plot(x_gp, y_func, lw=1.5, c='red', ls='dashed', label='actual function')
    ax2.plot(x_gp, mu, lw=2, c='blue', label='GP prediction')
    ax2.fill_between(x_gp, (mu-2*sig), y2=(mu+2*sig), color='blue', alpha=0.15, label='95% confidence interval')
    # ax2.set_ylim([min(mu-2*sig),max(mu+2*sig)])
    ax2.set_ylim([0.8, 2.0])
    ax2.set_xlim(*GP.bounds)
    ax2.set_ylabel('TBR')
    ax2.set_xticks([])
    ax2.legend(loc=2)

    aq = array([abs(GP.expected_improvement(array([k]))) for k in x_gp])
    ax3.plot(x_gp, 0.9*aq/max(aq), c='green', label='acquisition function')
    ax3.set_yticks([])
    ax3.set_xlabel('Li6 enrichment')
    ax3.legend(loc=1)

    print('plotting ', GP.x, GP.y, GP.y_err)
    # plt.show()
    plt.savefig(str(len(GP.y)).zfill(4)+'.png')


def example_plot_2d(GP):
    fig, (ax1, ax2) = plt.subplots(2, 1, gridspec_kw={'height_ratios': [1, 3]}, figsize=(10, 8))
    plt.subplots_adjust(hspace=0)

    ax1.plot(evaluations, max_values, marker='o', ls='solid', c='orange', label='optimum value', zorder=5)
    ax1.plot([5, 30], [z_func.max(), z_func.max()], ls='dashed', label='actual max', c='black')
    ax1.set_xlabel('function evaluations')
    # ax1.set_xlim([5, 30])
    # ax1.set_ylim([max(y) - 0.3, z_func.max() + 0.3])
    # ax1.xaxis.set_label_position('top')
    # ax1.yaxis.set_label_position('right')
    # ax1.xaxis.tick_top()
    # ax1.set_yticks([])
    # ax1.legend(loc=4)

    ax2.contour(*mesh, z_func, 40)
    ax2.plot([i[0] for i in GP.x], [i[1] for i in GP.x], 'D', c='red', markeredgecolor='black')
    plt.show()


os.system('rm *.png')
sequencer = ghalton.Halton(2)
number_of_samples = 10
x = sequencer.get(number_of_samples)
x = [[i[0], i[1] * 100] for i in x]

bounds = [(0.0, 1.0), (0, 100)]

N = 80
x = linspace(*bounds[0], N)
y = linspace(*bounds[1], N)
mesh = meshgrid(x, y)


y = []
y_errors = []

max_values = []
evaluations = []

all_results = []

for filename_counter, coords in enumerate(zip(x, y)):

    results = make_materials_geometry_tallies(coords[0], coords[1])

    all_results.append(results)

    y.append(results['TBR'])
    y_errors.append(results['TBR_std_dev'] * 2)

    print('x from HS', x[0: filename_counter+1])
    print('y from HS', y)
    print('y_errors  from HS', y_errors)

    # if filename_counter >0:
    #     GP = GpOptimiser(x[0:filename_counter+1], y, y_err=y_errors,bounds=bounds)
    #     max_values.append(max(GP.y))
    #     evaluations.append(len(GP.y))
    #     example_plot_2d(GP)


for i in range(number_of_samples, number_of_samples+10):
    # plot the current state of the optimisation

    # request the proposed evaluation
    new_x = GP.search_for_maximum()[0]

    # evaluate the new point
    new_result = make_materials_geometry_tallies(new_x)
    all_results.append(results)

    y.append(results['TBR'])
    y_errors.append(results['TBR_std_dev'] * 2)

    print('x from loop', new_x)
    print('y from loop', new_y)
    print('new_y_error from loop', new_y_error)

    # update the gaussian process with the new information
    GP.add_evaluation(new_x, new_y, new_y_err=new_y_error)

    # track the optimum value for plotting
    max_values.append(max(GP.y))
    evaluations.append(len(GP.y))

    example_plot_2d(GP)

os.system('convert *.png output.gif')

os.system('eog -f output.gif')


with open('simulation_results.json', 'w') as file_object:
    json.dump(all_results.append(results), file_object, indent=2)
