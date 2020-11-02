#!/usr/bin/env python3

"""plots different neutron energy distrubutions"""

import openmc
from source_extraction_utils import create_inital_particles, plot_energy_from_initial_source

# creates an isotropic point source with monoenergetic 14MeV neutrons
source = openmc.Source()
source.space = openmc.stats.Point((0, 0, 0))
source.angle = openmc.stats.Isotropic()
source.energy = openmc.stats.Discrete([14e6], [1])

create_inital_particles(source)
plot_energy_from_initial_source(input_filename='initial_source.h5')


# creates an isotropic point source with a fission energy distribution
source = openmc.Source()
source.space = openmc.stats.Point((0, 0, 0))
source.angle = openmc.stats.Isotropic()
source.energy = openmc.stats.Watt(a=988000.0, b=2.249e-06)

create_inital_particles(source)
plot_energy_from_initial_source(input_filename='initial_source.h5')


# creates an isotropic point source with a fusion energy distribution
source = openmc.Source()
source.space = openmc.stats.Point((0, 0, 0))
source.angle = openmc.stats.Isotropic()
source.energy = openmc.stats.Muir(e0=14080000.0, m_rat=5.0, kt=20000.0)

create_inital_particles(source)
plot_energy_from_initial_source(input_filename='initial_source.h5')
