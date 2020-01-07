#!/usr/bin/env python3

"""2_example_photon_spectra_tokamak.py: plots photon spectra."""

import openmc
import plotly.graph_objects as go

#MATERIALS#

breeder_material = openmc.Material(1, "PbLi") #Pb84.2Li15.8 with natural enrichment of Li6
enrichment_fraction = 0.97
breeder_material.add_element('Pb', 84.2,'ao')
breeder_material.add_nuclide('Li6', enrichment_fraction*15.8, 'ao')
breeder_material.add_nuclide('Li7', (1.0-enrichment_fraction)*15.8, 'ao')
breeder_material.set_density('atom/b-cm',3.2720171e-2) # around 11 g/cm3

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


#GEOMETRY#

#surfaces
central_sol_surface = openmc.ZCylinder(r=100)
central_shield_outer_surface = openmc.ZCylinder(r=110)
vessel_inner = openmc.Sphere(r=500)
first_wall_outer_surface = openmc.Sphere(r=510)
breeder_blanket_outer_surface = openmc.Sphere(r=610,boundary_type='vacuum')

#cells

central_sol_region = -central_sol_surface & -breeder_blanket_outer_surface
central_sol_cell = openmc.Cell(region=central_sol_region) 
central_sol_cell.fill = copper

central_shield_region = +central_sol_surface & -central_shield_outer_surface & -breeder_blanket_outer_surface
central_shield_cell = openmc.Cell(region=central_shield_region) 
central_shield_cell.fill = eurofer

inner_vessel_region = -vessel_inner & + central_shield_outer_surface
inner_vessel_cell = openmc.Cell(region=inner_vessel_region) 

first_wall_region = -first_wall_outer_surface & +vessel_inner
first_wall_cell = openmc.Cell(region=first_wall_region) 
first_wall_cell.fill = eurofer

breeder_blanket_region = +first_wall_outer_surface & -breeder_blanket_outer_surface & +central_shield_outer_surface
breeder_blanket_cell = openmc.Cell(region=breeder_blanket_region) 
breeder_blanket_cell.fill = breeder_material

universe = openmc.Universe(cells=[central_sol_cell,central_shield_cell,inner_vessel_cell,first_wall_cell, breeder_blanket_cell])
geom = openmc.Geometry(universe)




#SIMULATION SETTINGS#

# Instantiate a Settings object
sett = openmc.Settings()
batches = 2
sett.batches = batches
sett.inactive = 0
sett.particles = 7000
sett.run_mode = 'fixed source'

# Create a DT point source
source = openmc.Source()
source.space = openmc.stats.Point((150,0,0))
source.angle = openmc.stats.Isotropic()
source.energy = openmc.stats.Discrete([14e6], [1])
sett.source = source
sett.photon_transport = True # This line is required to switch on photons tracking

#setup the tallies
tallies = openmc.Tallies()

photon_particle_filter = openmc.ParticleFilter(['photon']) # This line adds a particle filter for photons
neutron_particle_filter = openmc.ParticleFilter(['neutron'])
cell_filter = openmc.CellFilter(breeder_blanket_cell)
energy_bins = openmc.mgxs.GROUP_STRUCTURES['VITAMIN-J-175']   
energy_filter = openmc.EnergyFilter(energy_bins)

spectra_tally = openmc.Tally(name='breeder_blanket_neutron_spectra')
spectra_tally.filters = [cell_filter,neutron_particle_filter,energy_filter]
spectra_tally.scores = ['flux']
tallies.append(spectra_tally)  

spectra_tally = openmc.Tally(name='breeder_blanket_photon_spectra')
spectra_tally.filters = [cell_filter,photon_particle_filter,energy_filter]
spectra_tally.scores = ['flux']
tallies.append(spectra_tally)  



# Run OpenMC!
model = openmc.model.Model(geom, mats, sett, tallies)
model.run()

# open the results file
sp = openmc.StatePoint('statepoint.'+str(batches)+'.h5')


spectra_tally = sp.get_tally(name='breeder_blanket_neutron_spectra') 
df = spectra_tally.get_pandas_dataframe()
spectra_tally_result = df['mean']


fig = go.Figure()


fig.add_trace(go.Scatter(x=energy_bins, 
                      y=spectra_tally_result,
                      name='breeder_blanket_neutron_spectra',
                      line=dict(shape='hv')
                     )
              )


spectra_tally = sp.get_tally(name='breeder_blanket_photon_spectra') 
df = spectra_tally.get_pandas_dataframe()
spectra_tally_result = df['mean']


fig.add_trace(go.Scatter(x=energy_bins, 
                      y=spectra_tally_result,
                      name='breeder_blanket_photon_spectra',
                      line=dict(shape='hv')
                     )
              )


fig.update_layout(
      title = 'Photon and neutron energy spectra',
      xaxis = {'title':'Energy (eV)'},
      yaxis = {'title':'Photons / neutrons per cm2 per source neutron',
               'type':'log'
              }
)


fig.write_html("tokamak_photon_spectra.html")
try:
       fig.write_html("/my_openmc_workshop/tokamak_photon_spectra.html")
except NotADirectoryError:
       pass

fig.show()