#!/usr/bin/env python3

"""2_example_neutron_flux_tokamak.py: plots few 2D views of a simple tokamak geometry with neutron flux."""


import openmc
import os

# MATERIALS

breeder_material = openmc.Material(1, "PbLi")   # Pb84.2Li15.8
breeder_material.add_element('Pb', 84.2, percent_type='ao')
breeder_material.add_element('Li', 15.8, percent_type='ao', enrichment=7.0, enrichment_target='Li6', enrichment_type='ao')   # natural enrichment = 7% Li6
breeder_material.set_density('atom/b-cm', 3.2720171e-2)   # around 11 g/cm3

copper = openmc.Material(name='Copper')
copper.set_density('g/cm3', 8.5)
copper.add_element('Cu', 1.0)

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

mats = openmc.Materials([breeder_material, eurofer, copper])


# GEOMETRY

# surfaces
central_sol_surface = openmc.ZCylinder(r=100)
central_shield_outer_surface = openmc.ZCylinder(r=110)
vessel_inner_surface = openmc.Sphere(r=500)
first_wall_outer_surface = openmc.Sphere(r=510)
breeder_blanket_outer_surface = openmc.Sphere(r=610, boundary_type='vacuum')

# cells
central_sol_region = -central_sol_surface & -breeder_blanket_outer_surface
central_sol_cell = openmc.Cell(region=central_sol_region)
central_sol_cell.fill = copper

central_shield_region = +central_sol_surface & -central_shield_outer_surface & -breeder_blanket_outer_surface
central_shield_cell = openmc.Cell(region=central_shield_region)
central_shield_cell.fill = eurofer

inner_vessel_region = -vessel_inner_surface & +central_shield_outer_surface
inner_vessel_cell = openmc.Cell(region=inner_vessel_region)
# no material set as default is vacuum

first_wall_region = -first_wall_outer_surface & +vessel_inner_surface
first_wall_cell = openmc.Cell(region=first_wall_region)
first_wall_cell.fill = eurofer

breeder_blanket_region = +first_wall_outer_surface & -breeder_blanket_outer_surface & +central_shield_outer_surface
breeder_blanket_cell = openmc.Cell(region=breeder_blanket_region)
breeder_blanket_cell.fill = breeder_material

universe = openmc.Universe(cells=[central_sol_cell, central_shield_cell, inner_vessel_cell, first_wall_cell, breeder_blanket_cell])
geom = openmc.Geometry(universe)


# SIMULATION SETTINGS

# Instantiate a Settings object
sett = openmc.Settings()
batches = 4
sett.batches = batches
sett.inactive = 0
sett.particles = 5000
sett.run_mode = 'fixed source'

# Create a DT point source
source = openmc.Source()
mcnpsource = openmc.Source()
source.angle = openmc.stats.Isotropic()
source.energy = openmc.stats.Discrete([14e6], [1])
source.space = openmc.stats.Point((150, 150, 0))

sett.source = source

# Create 3d mesh which will be used for tally
mesh = openmc.RegularMesh()
mesh.dimension = [200, 100, 200]  # width, depth, height
mesh.lower_left = [-750, 0, -750]  # x,y,z coordinates
mesh.upper_right = [750, 750, 750]  # x,y,z coordinates


tallies = openmc.Tallies()
# Create mesh filter for tally
mesh_filter = openmc.MeshFilter(mesh)


# Create flux mesh tally to score flux
mesh_tally = openmc.Tally(name='tally_on_mesh')
mesh_tally.filters = [mesh_filter]
mesh_tally.scores = ['(n,Xt)']  # this can be changed to 'absorption' to show the impact of the center column
tallies.append(mesh_tally)


# Run OpenMC!
model = openmc.model.Model(geom, mats, sett, tallies)
model.run()

os.system('python openmc-statepoint-3d.py -i statepoint.'+str(batches)+'.h5 -t 1 -n tally_on_mesh -m 1 -o tally_on_mesh.vtk')
os.system('cp tally_on_mesh.vtk /my_openmc_workshop')
os.system('paraview tally_on_mesh.vtk')
