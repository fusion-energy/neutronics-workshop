#!/usr/bin/env python3

"""plots different neutron bith directions"""

import openmc
from source_extraction_utils import create_inital_particles, plot_direction_from_initial_source

# creates an isotropic point source with monoenergetic 14MeV neutrons
source = openmc.Source()
source.space = openmc.stats.Point((0, 0, 0))
source.angle = openmc.stats.Isotropic()
source.energy = openmc.stats.Discrete([14e6], [1])

create_inital_particles(source)
plot_direction_from_initial_source()
