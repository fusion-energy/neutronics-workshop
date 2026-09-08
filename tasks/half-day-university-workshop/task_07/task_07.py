# %% [markdown]
# ---
# title: Point source plotting
# ---

# %% [markdown]
# To perform a neutronics simulation a neutron source must also be defined.
#
# This task allows users to make a simple OpenMC point source and plot its energy, position and initial directions.

# %% [markdown]
# First import OpenMC and configure the nuclear data path

# %%
import openmc
from pathlib import Path
# Setting the cross section path to the correct location in the docker image.
# If you are running this outside the docker image you will have to change this path to your local cross section path.
openmc.config['cross_sections'] = Path.home() / 'nuclear_data' / 'cross_sections.xml'

# provides simple source plotting functions
# for more details here is a link to the package repository
# https://github.com/fusion-energy/openmc_source_plotter
from openmc_source_plotter import plot_source_energy, plot_source_position, plot_source_direction

# %% [markdown]
# This first code block creates an isotropic point source with 14 MeV monoenergetic neutrons.

# %%
# initialises a new source object
my_source = openmc.IndependentSource(
    # sets the location of the source to x=0 y=0 z=0
    space=openmc.stats.Point((0, 0, 0)),
    # sets the direction to isotropic
    angle=openmc.stats.Isotropic(),
    # sets the energy distribution to a delta function at 14 MeV
    # openmc.stats.Discrete([14e6], [1]) places 100% probability at exactly 14 MeV — no spread
    energy=openmc.stats.Discrete([14e6], [1])
)

# %% [markdown]
# this next code block runs openmc and creates a file containing information on the initial particles. The energy information is the extracted and plotted

# %%
plot_source_energy(my_source)

# %% [markdown]
# The next code block creates an isotropic point source with a fission energy distribution.

# %%
# Documentation on the Watt distribution is here
# https://docs.openmc.org/en/stable/pythonapi/generated/openmc.data.WattEnergy.html
my_source_2 = openmc.IndependentSource(
    space=openmc.stats.Point((0, 0, 0)),
    angle=openmc.stats.Isotropic(),
    energy=openmc.stats.Watt(a=988000.0, b=2.249e-06)
)

plot_source_energy(my_source_2)

# %% [markdown]
# This code block creates an isotropic point source with a fusion energy distribution.

# %%
# Documentation on the Muir distribution is here
# https://docs.openmc.org/en/stable/pythonapi/generated/openmc.stats.muir.html
my_source_3 = openmc.IndependentSource(
    space=openmc.stats.Point((0, 0, 0)),
    angle=openmc.stats.Isotropic(),
    energy=openmc.stats.muir(e0=14080000.0, m_rat=5.0, kt=20000.0)
)

plot_source_energy(my_source_3)

# %% [markdown]
# The following code block plots the birth location of the neutrons from a 14 MeV monoenergetic point source.

# %%
# Creates an isotropic point source with monoenergetic 14MeV neutrons
my_source_4 = openmc.IndependentSource(
    space=openmc.stats.Point((0, 0, 0)),
    angle=openmc.stats.Isotropic(),
    energy=openmc.stats.Discrete([14e6], [1])
)

plot_source_position(my_source_4)

# %% [markdown]
# Finally, the following code block plots the birth direction of the neutrons from the same source.

# %%
# Creates an isotropic point source with monoenergetic 14MeV neutrons
my_source_5 = openmc.IndependentSource(
    space=openmc.stats.Point((0, 0, 0)),
    angle=openmc.stats.Isotropic(),
    energy=openmc.stats.Discrete([14e6], [1])
)

plot_source_direction(my_source_5)

# %% [markdown]
# For convenience a plasma source package has been made that wraps openmc.IndependentSource and provides easy creation of point (and other) fusion sources.
# https://github.com/fusion-energy/openmc-plasma-source/ you could try plotting the energy this source

# %% [markdown]
# **Learning Outcomes for Part 1:**
#
# - OpenMC can be used to create neutron point sources with different energy distributions.
