#!/usr/bin/env python3

"""1_example_neutron_flux.py: plots few 2D views of a simple tokamak geometry with neutron flux."""


import openmc
import matplotlib.pyplot as plt
import os

#MATERIALS#
mats = openmc.Materials()

breeder_material = openmc.Material(1, "PbLi") #Pb84.2Li15.8 with natural enrichment of Li6
enrichment_fraction = 0.07 #change the enrichment upto 1.0
breeder_material.add_element('Pb', 84.2,'ao')
breeder_material.add_nuclide('Li6', enrichment_fraction*15.8, 'ao')
breeder_material.add_nuclide('Li7', (1.0-enrichment_fraction)*15.8, 'ao')
breeder_material.set_density('g/cm3',11.0)
mats.append(breeder_material)


#GEOMETRY#


sph1 = openmc.Sphere(r=50)
sph2 = openmc.Sphere(r=80, boundary_type = 'vacuum')
sph3 = +sph1 & -sph2 

breeder_blanket_cell = openmc.Cell(region=sph3)
breeder_blanket_cell.fill = breeder_material

inner_vacuum_cell = openmc.Cell(region=-sph1)

universe = openmc.Universe(cells=[inner_vacuum_cell,breeder_blanket_cell]) 

geom = openmc.Geometry(universe)



#SIMULATION SETTINGS#

# Instantiate a Settings object
sett = openmc.Settings()
batches = 2
sett.batches = batches
sett.inactive = 0
sett.particles = 5000
sett.particle = "neutron"
sett.run_mode = 'fixed source'

# creates a 14MeV point source
source = openmc.Source()
source.space = openmc.stats.Point((0,0,0))
source.angle = openmc.stats.Isotropic()
source.energy = openmc.stats.Discrete([14e6], [1])
sett.source = source


# Create mesh which will be used for tally
mesh = openmc.RegularMesh()
mesh_height=200
mesh_width = mesh_height
mesh.dimension = [mesh_width, mesh_height]
mesh.lower_left = [-200, -200]
mesh.upper_right = [200, 200]


tallies = openmc.Tallies()
# Create mesh filter for tally
mesh_filter = openmc.MeshFilter(mesh)
# Create mesh tally to score flux
mesh_tally = openmc.Tally(1,name='tallies_on_mesh')
mesh_tally.filters = [mesh_filter]
mesh_tally.scores = ['flux'] # change flux to absorption
tallies.append(mesh_tally)


# Run OpenMC!
model = openmc.model.Model(geom, mats, sett, tallies)
model.run()


# open the results file
sp = openmc.StatePoint('statepoint.'+str(batches)+'.h5')

# access the flux tally
flux_tally = sp.get_tally(scores=['flux'])  # change flux to absorption
flux_slice = flux_tally.get_slice(scores=['flux']) # change flux to absorption
flux_slice.mean.shape = (mesh_width, mesh_height)

fig = plt.subplot()

fig.imshow(flux_slice.mean).get_figure().savefig('flux_plot.png')
universe.plot(width=(180,180),basis='xz').get_figure().savefig('universe_plot.png')

try:
    fig.imshow(flux_slice.mean).get_figure().savefig('/my_openmc_workshop/flux_plot.png')
    universe.plot(width=(180,180),basis='xz').get_figure().savefig('/my_openmc_workshop/universe_plot.png')
except (FileNotFoundError, NotADirectoryError):   # for both inside and outside docker container
    pass


plt.show(fig.imshow(flux_slice.mean))
plt.show(universe.plot(width=(180,180),basis='xz'))
