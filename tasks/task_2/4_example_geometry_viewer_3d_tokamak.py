#!/usr/bin/env python3

"""example_isotope_plot.py: plots few 2D views of a simple tokamak geometry ."""

__author__      = "Jonathan Shimwell"

import openmc
import matplotlib.pyplot as plt
import os

mats = openmc.Materials()

copper = openmc.Material(name='Copper')
copper.set_density('g/cm3', 8.5)
copper.add_element('Cu', 1.0)
mats.append(copper)

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
mats.append(eurofer)

breeder_material = openmc.Material(name='breeder_material')
breeder_material.set_density('g/cm3', 9.1)
breeder_material.add_element('Pb', 84.2, percent_type='ao')
breeder_material.add_element('Li', 15.8, percent_type='ao')
mats.append(breeder_material)

mats.export_to_xml()

#define all the surfaces
central_sol_surface = openmc.ZCylinder(r=100)
central_shield_outer_surface = openmc.ZCylinder(r=110,boundary_type='vacuum')
vessel_inner = openmc.Sphere(r=500,boundary_type='vacuum')
first_wall_outer_surface = openmc.Sphere(r=510)
breeder_blanket_outer_surface = openmc.Sphere(r=610)


#define the cells
central_sol_region = -central_sol_surface & -breeder_blanket_outer_surface
central_sol_cell = openmc.Cell(region=central_sol_region) 
central_sol_cell.fill = copper

central_shield_region = +central_sol_surface & -central_shield_outer_surface & -breeder_blanket_outer_surface
central_shield_cell = openmc.Cell(region=central_shield_region) 
central_shield_cell.fill = eurofer

first_wall_region = -first_wall_outer_surface & +vessel_inner & +central_shield_outer_surface
first_wall_cell = openmc.Cell(region=first_wall_region) 
first_wall_cell.fill = eurofer

breeder_blanket_region = +first_wall_outer_surface & -breeder_blanket_outer_surface & +central_shield_outer_surface
breeder_blanket_cell = openmc.Cell(region=breeder_blanket_region) 
breeder_blanket_cell.fill = breeder_material

universe = openmc.Universe(cells=[central_sol_cell,central_shield_cell,first_wall_cell, breeder_blanket_cell])

geom = openmc.Geometry(universe)

geom.export_to_xml()


# makes the 3d "cube" style geometry 
vox_plot = openmc.Plot()
vox_plot.type = 'voxel'
vox_plot.width = (1500., 1500., 1500.)
vox_plot.pixels = (200, 200, 200)
vox_plot.filename = 'plot_3d_tokamak'
vox_plot.color_by = 'material'
#vox_plot.colors = {copper: 'blue'}  # materials can be coloured using this command
plots = openmc.Plots([vox_plot])
plots.export_to_xml()

openmc.plot_geometry()

# this converts the h5 file to a vti
os.system('openmc-voxel-to-vtk plot_3d_tokamak.h5 -o plot_3d_tokamak.vti')
os.system('paraview plot_3d_tokamak.vti')  # or visit might work better
