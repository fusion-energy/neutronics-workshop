
# spectra_tally.mean
# normalised_spectra = spectra_tally.mean / sum(spectra_tally.mean)

# normalised_spectra is probability of each enegry , sum of normalised_spectra = 1



import openmc

# MATERIALS

# Due to the hydrogen content water is a very good neutron moderator
my_material = openmc.Material()
my_material.add_element('H', 1, percent_type='ao')
my_material.add_element('O', 2, percent_type='ao')
my_material.set_density('g/cm3', 1)

my_materials = openmc.Materials([my_material])


# GEOMETRY

# surfaces
outer_surface = openmc.Sphere(r=500, boundary_type='vacuum')

# cells
cell_1 = openmc.Cell(region=-outer_surface)
cell_1.fill = my_material

my_geometry = openmc.Geometry([cell_1])


# SIMULATION SETTINGS

# Instantiate a Settings object
my_settings = openmc.Settings()
my_settings.batches = 10
my_settings.particles = 10000
my_settings.run_mode = 'fixed source'

# Create a DT point source
my_source = openmc.Source()
my_source.space = openmc.stats.Point((0, 0, 0))
my_source.angle = openmc.stats.Isotropic()
my_source.energy = openmc.stats.Discrete([14e6], [1])
my_settings.source = my_source

#creates an empty tally object
my_tallies = openmc.Tallies()

# sets up filters for the tallies
neutron_particle_filter = openmc.ParticleFilter(['neutron'])

# creates an array of 300 linear spaced energy bins from 0MeV to 15MeV
# our source is 14MeV so this should capture all the neutron energies in the simulation
# there is a disadvantage of using a linear group structure which is covered in part 2 of this task
import numpy as np
energy_filter = openmc.EnergyFilter(np.linspace(0, 15e6, 300))

# setup the filters for the cell tally
cell_filter = openmc.CellFilter(cell_1) 

# create the tally
cell_spectra_tally = openmc.Tally(name='cell_spectra_tally')
cell_spectra_tally.scores = ['flux']
cell_spectra_tally.filters = [cell_filter, neutron_particle_filter, energy_filter]
my_tallies.append(cell_spectra_tally)

# combine all the required parts to make a model
model = openmc.model.Model(my_geometry, my_materials, my_settings, my_tallies)

# remove old files and runs OpenMC

results_filename = model.run()

# open the results file
results = openmc.StatePoint(results_filename)

#extracts the tally values from the simulation results
cell_tally = results.get_tally(name='cell_spectra_tally')

# flattens the ndarray into a 1d array
flux = cell_tally.mean.flatten()

spectrum_probability = flux / sum(flux)

proberbility_per_ev = spectrum_probability / np.diff(energy_filter.bins).flatten()

tab = openmc.stats.Tabular(
    x = energy_filter.bins,
    p=proberbility_per_ev,
    interpolation='histogram'
)

energy_filter.tabular(cell_tally.mean.flatten())

source = openmc.Source()
source.energy = tab
