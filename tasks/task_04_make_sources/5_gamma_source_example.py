# %% [markdown]
# ---
# title: Gamma sources
# ---

# %% [markdown]
# OpenMC is also able to track gamma rays during a neutronics simulation.
#
# This task allows users to define a gamma point source and plot the energy distribution of the emitted gamma rays.
#
# The energy distribution will be different to Part 1 as the type of particle is different and we have discrete branching ratios for the gamma source.

# %% [markdown]
# First import OpenMC and configure the nuclear data path

# %%
import numpy as np

import openmc
from pathlib import Path
# Setting the cross section path to the correct location in the docker image.
# If you are running this outside the docker image you will have to change this path to your local cross section path.
openmc.config['cross_sections'] = Path.home() / 'nuclear_data' / 'cross_sections.xml'


# provides simple source plotting functions
# for more details here is a link to the package repository
# https://github.com/fusion-energy/openmc_source_plotter
from openmc_source_plotter import plot_source_energy

# %% [markdown]
# In this example we will define a gamma source similar to Co60.
#
# This is the decay scheme for Co60. The majoirty of the gamma emssion is via two high energy gamma rays (1.1732MeV and 1.3325MeV). Although there are [several other gamma emissions with low probabilites](http://www.nucleide.org/DDEP_WG/Nuclides/Co-60_tables.pdf) we will just model these two as 50:50 to keep the example simple.

# %% [markdown]
# ![decay routes](https://upload.wikimedia.org/wikipedia/commons/thumb/0/03/Cobalt-60m-decay.svg/1024px-Cobalt-60m-decay.svg.png)
#
# Image by Tubas-en - Own work, Public Domain, https://commons.wikimedia.org/w/index.php?curid=6330228

# %% [markdown]
# The following code block creates the gamma source using OpenMC and plots the energy distribution of a random sample of photons. Note how the particle type and energy distribution are defined.

# %%
# initializes a new source object
my_source = openmc.IndependentSource(
    # sets the location of the source to x=0 y=0 z=0
    space=openmc.stats.Point((0, 0, 0)),
    # sets the direction to isotropic
    angle=openmc.stats.Isotropic(),
    # sets the energy distribution to 50% 1.1MeV photons and 50% 1.3MeV photons
    energy=openmc.stats.Discrete([1.1732e6,1.3325e6], [0.5, 0.5]),
    particle='photon'
)

# %% [markdown]
# this next code block runs openmc and creates a file containing information on the initial particles. The energy information is the extracted and plotted.
#
# A few extra parameters are used here to specifiy the number of particles in the inital source and the energy bins of the histogram

# %%
# remove any other xml files so that openmc reads the correct xml files
for f in Path('.').glob('*.xml'):
    f.unlink(missing_ok=True)

# number_of_particles can be increased to sample more particles and the histogram resoluton can be changed
plot_source_energy(
    this=my_source,
    n_samples=1000,
    energy_bins=np.linspace(0, 2e6, 100)
)

# this time we are setting the number of energy bins for the plot

# %% [markdown]
# As the sampling is random the two peaks might not be equal sizes, despite the source having a 50:50 distribution.
#
# You can increase the ```number_of_particles``` in the last code block to sample more particles.

# %% [markdown]
# **Learning Outcomes for Part 4:**
# - OpenMC can also be used to define gamma sources for neutronics simulations.
