#!/usr/bin/env python3

"""1_example_geometry_viewer_2d.py: plots few 2D views of a simple geometry ."""

import os
import openmc
import matplotlib.pyplot as plt

mats = openmc.Materials()

natural_lead = openmc.Material(1, "natural_lead")
natural_lead.add_element('Pb', 1, percent_type='ao')
natural_lead.set_density('g/cm3', 11.34)
mats.append(natural_lead)


# HINT: this is an example material made from copper
# natural_copper = openmc.Material(2, "natural_copper")
# natural_copper.add_element('Cu', 1, percent_type='ao')
# natural_copper.set_density('g/cm3', 8.96)
# mats.append(natural_copper)


mats.export_to_xml()


# example surfaces
surface_sph1 = openmc.Sphere(r=500)
surface_sph2 = openmc.Sphere(r=600)

# add more surfaces here using https://openmc.readthedocs.io/en/stable/usersguide/geometry.html#surfaces-and-regions
# for the first wall you will need another sphere
# for the center column you will need a cylinder

blanket_region = +surface_sph1 & -surface_sph2 # above (+) surface_sph and below (-) surface_sph2


# example cell
cell_1 = openmc.Cell(region=blanket_region)
cell_1.fill = natural_lead   # assigning a material to a cell

# add more cells here for the first wall and the center column

universe = openmc.Universe(cells=[cell_1])   # HINT: this list will need to include the new cell

# shows the plots
plt.show(universe.plot(width=(1200,1200),basis='xz',colors={cell_1: 'blue'}))
plt.show(universe.plot(width=(1200,1200),basis='xy',colors={cell_1: 'blue'}))
plt.show(universe.plot(width=(1200,1200),basis='yz',colors={cell_1: 'blue'}))

# saves the plots
universe.plot(width=(1200,1200),basis='xz',colors={cell_1: 'blue'}).get_figure().savefig('xz_sphere.png')
universe.plot(width=(1200,1200),basis='xy',colors={cell_1: 'blue'}).get_figure().savefig('xy_sphere.png')
universe.plot(width=(1200,1200),basis='yz',colors={cell_1: 'blue'}).get_figure().savefig('yz_sphere.png')

os.system('cp xz_sphere.png /my_openmc_workshop')
os.system('cp xy_sphere.png /my_openmc_workshop')
os.system('cp yz_sphere.png /my_openmc_workshop')

geom = openmc.Geometry(universe)
