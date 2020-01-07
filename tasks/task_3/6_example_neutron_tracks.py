#!/usr/bin/env python3

"""example_isotope_plot.py: plots 3D model with neutron tracks."""

__author__      = "Jonathan Shimwell"

import openmc
import matplotlib.pyplot as plt
import os

#MATERIALS#
mats = openmc.Materials()

moderating_material = openmc.Material(1, "water") # water contains hydrogen which is a good neutron moderator
moderating_material.add_element('H', 2,'ao')
moderating_material.add_element('O', 1,'ao')
moderating_material.set_density('g/cm3',1.0)
mats.append(moderating_material)

transparent_material = openmc.Material(2, "zirconium") # one of the more transparent materials
transparent_material.add_element('Zr', 1,'ao')
transparent_material.set_density('g/cm3',6.49)
mats.append(transparent_material)



#GEOMETRY#

sph0 = openmc.Sphere(r=50)
sph1 = openmc.Sphere(r=600, boundary_type = 'vacuum')
flat_surf = openmc.YPlane(y0=0)

simple_moderator_cell = openmc.Cell(region= +sph0 & -sph1 & +flat_surf)
simple_moderator_cell.fill = moderating_material

simple_transparent_cell = openmc.Cell(region= +sph0 & -sph1 & -flat_surf)
simple_transparent_cell.fill = transparent_material

vaccum_cell = openmc.Cell(region= -sph0)


universe = openmc.Universe(cells=[simple_moderator_cell,simple_transparent_cell,vaccum_cell]) 

geom = openmc.Geometry(universe)



#SIMULATION SETTINGS#

# Instantiate a Settings object
sett = openmc.Settings()
batches = 1
sett.batches = batches
sett.inactive = 0
sett.particles = 20
sett.particle = "neutron"
sett.track = (1,2,4)
sett.run_mode = 'fixed source'

# creates a 14MeV point source
source = openmc.Source()
source.space = openmc.stats.Point((0,0,0))
source.angle = openmc.stats.Isotropic()
source.energy = openmc.stats.Discrete([14e6], [1])

# source.file = 'source_1000_particles.h5'
sett.source = source


# Run OpenMC!
model = openmc.model.Model(geom, mats, sett)
model.run(tracks=True) # this creates h5 files with openmc-track-to-vtk

for i in range(1,11):
   print('converting h5 track file to vtpi')
   os.system('openmc-track-to-vtk track_1_1_'+str(i)+'.h5 -o track_1_1_'+str(i))

#os.system('paraview track_1_1_'+str(i)+'.pvtp')


vox_plot = openmc.Plot()
vox_plot.type = 'voxel'
vox_plot.width = (200., 200., 200.)
vox_plot.pixels = (100, 100, 100)
vox_plot.filename = 'plot_3d'
vox_plot.color_by = 'material'
vox_plot.colors = {moderating_material: 'blue',transparent_material: 'red'}
plots = openmc.Plots([vox_plot])
plots.export_to_xml()

openmc.plot_geometry()

os.system('openmc-voxel-to-vtk plot_3d.h5 -o plot_3d.vti')
os.system('cp plot_3d.vti /my_openmc_workshop')
os.system('cp *.vtp /my_openmc_workshop')
os.system('paraview plot_3d.vti') # visit might be preffered
