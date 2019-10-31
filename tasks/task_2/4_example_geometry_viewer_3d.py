#!/usr/bin/env python3

"""example_isotope_plot.py: plots few 2D views of a simple tokamak geometry ."""

__author__      = "Jonathan Shimwell"

import openmc
import matplotlib.pyplot as plt
import os

mats = openmc.Materials()

natural_lead = openmc.Material(1, "natural_lead")
natural_lead.add_element('Pb', 1,'ao')
mats.append(natural_lead)

mats.export_to_xml()


#example surfaces
sph1 = openmc.Sphere(r=10)
sph2 = openmc.Sphere(r=20)

core_of_sphere = -sph1 # volume is below sph1
hollow_sphere = +sph1 & -sph2 # volume is above sph1 and below sph2

#hint, add cylindical surfaces here using https://openmc.readthedocs.io/en/stable/usersguide/geometry.html#surfaces-and-regions


#hint, this is an example cell, by default it is filled with a vacuum
cell1 = openmc.Cell(region=core_of_sphere)

cell2 = openmc.Cell(region=hollow_sphere)
cell2.fill = natural_lead




#add more cells here

universe = openmc.Universe(cells=[cell1, cell2]) #this list will need to include the new cell



geom = openmc.Geometry(universe)

geom.export_to_xml()

vox_plot = openmc.Plot()
vox_plot.type = 'voxel'
vox_plot.width = (40., 40., 40.)
vox_plot.pixels = (200, 200, 200)
vox_plot.filename = 'plot_3d'
vox_plot.color_by = 'material'
vox_plot.colors = {natural_lead: 'blue'}
plots = openmc.Plots([vox_plot])
plots.export_to_xml()

openmc.plot_geometry()

os.system('openmc-voxel-to-vtk plot_3d.h5 -o plot_3d.vti')
os.system('paraview plot_3d.vti') # or visit might work better
