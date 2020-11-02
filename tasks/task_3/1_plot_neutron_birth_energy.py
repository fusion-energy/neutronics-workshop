#!/usr/bin/env python3

"""plots different neutron energy distrubutions"""

import openmc
from source_extraction_utils import make_inital_source, plot_energy_from_initial_source


# sets the energy of neutrons to monoenergetic 14MeV source
make_inital_source(energy=openmc.stats.Discrete([14e6], [1]))
plot_energy_from_initial_source(input_filename='initial_source.h5')

# sets the energy of neutrons to a fission energy distribution
make_inital_source(energy=openmc.stats.Watt(a=988000.0, b=2.249e-06))
plot_energy_from_initial_source(input_filename='initial_source.h5')

# sets the energy of neutrons to a fusion energy distribution, energy is 14.08MeV, atomic mass for D + T = 5, temperature is 20KeV
make_inital_source(energy=openmc.stats.Muir(e0=14080000.0, m_rat=5.0, kt=20000.0))
plot_energy_from_initial_source(input_filename='initial_source.h5')
