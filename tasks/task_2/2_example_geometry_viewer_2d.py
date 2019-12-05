#!/usr/bin/env python3

"""example_isotope_plot.py: plots few 2D views of a simple geometry ."""

__author__      = "Jonathan Shimwell"

import openmc
import matplotlib.pyplot as plt

mats = openmc.Materials()

natural_lead = openmc.Material(1, "natural_lead")
natural_lead.add_element('Pb', 1,'ao')
natural_lead.set_density('g/cm3', 11.34)
mats.append(natural_lead)


# natural_copper = openmc.Material(2, "natural_copper") #hint this is an example material you will need another one called natural_tungsten ,density is 19.3
# natural_copper.add_element('Cu', 1,'ao')
# natural_copper.set_density('g/cm3', 8.96)
# mats.append(natural_copper)


# sheild_material = openmc.Material(3, "mixed_tungsten_water")
# sheild_material.add_material(natural_tungsten, 0.9, 'ao')
# sheild_material.add_material(natural_copper, 0.1, 'ao')
# mats.append(sheild_material)


mats.export_to_xml()



#example surfaces
surface_sph1 = openmc.Sphere(r=500)
surface_sph2 = openmc.Sphere(r=600)

#add more surfaces here using https://openmc.readthedocs.io/en/stable/usersguide/geometry.html#surfaces-and-regions

volume_sph1 = +surface_sph1 & -surface_sph2 # above (+) surface_sph and below (-) surface_sph2


#example cell
cell_1 = openmc.Cell(region=volume_sph1)
cell_1.fill = natural_lead #assigning a material to a cell

#add more cells here

universe = openmc.Universe(cells=[cell_1]) #hint, this list will need to include the new cell

plt.show(universe.plot(width=(1200,1200),basis='xz',colors={cell_1: 'blue'}))
plt.show(universe.plot(width=(1200,1200),basis='xy',colors={cell_1: 'blue'}))
plt.show(universe.plot(width=(1200,1200),basis='yz',colors={cell_1: 'blue'}))

universe.plot(width=(1200,1200),basis='xz',colors={cell_1: 'blue'}).get_figure().savefig('xz_sphere.png')
universe.plot(width=(1200,1200),basis='xy',colors={cell_1: 'blue'}).get_figure().savefig('xy_sphere.png')
universe.plot(width=(1200,1200),basis='yz',colors={cell_1: 'blue'}).get_figure().savefig('yz_sphere.png')

geom = openmc.Geometry(universe)





