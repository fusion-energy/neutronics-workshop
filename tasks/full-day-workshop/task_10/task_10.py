# %% [markdown]
# ---
# title: Ring source plotting
# ---

# %% [markdown]
# This task shows users how to make a simple ring source in OpenMC and plot the position of source particles.

# %% [markdown]
# We will make use of the CylindricalIndependent source as described in the docs
# https://docs.openmc.org/en/stable/pythonapi/generated/openmc.stats.CylindricalIndependent.html
#
# The CylindricalIndependent source can make makes a ring shaped source with the corect inputs.
# - The r value (distribution of radius values)
# - The phi value (distribution of azimuthal angle values)
# - The z value (distribution of z values on the z axis)
#
# Each of these inputs must be a univariate probability disitribution.

# %% [markdown]
# OpenMC has several built in distributions for popular distributions such as Normal, Maxwell and others.
#
# See the full list here https://docs.openmc.org/en/stable/pythonapi/stats.html#univariate-probability-distributions
#
# In this example we are going to make use of the Uniform disitrbution by feel free to tinker with the differnt distributions an make your own source.

# %% [markdown]
# First import OpenMC and configure the nuclear data path

# %%
import openmc
from pathlib import Path
# Setting the cross section path to the correct location in the docker image.
# If you are running this outside the docker image you will have to change this path to your local cross section path.
openmc.config['cross_sections'] = Path.home() / 'nuclear_data' / 'cross_sections.xml'

# This package provides simple source plotting functions
# for more details here is a link to the package repository
# https://github.com/fusion-energy/openmc_source_plotter
from openmc_source_plotter import plot_source_position

# %%
# the distribution of radius is just a single value
radius = openmc.stats.Discrete([10], [1])

# the distribution of source z values is just a single value
z_values = openmc.stats.Discrete([0], [1])

# the distribution of source azimuthal angles values is a uniform distribution between 0 and 2 Pi
angle = openmc.stats.Uniform(a=0., b=2* 3.14159265359)

# initialises a new ring source using the three distributions and a radius
my_source = openmc.IndependentSource(
    space=openmc.stats.CylindricalIndependent(r=radius, phi=angle, z=z_values, origin=(0.0, 0.0, 0.0)),
    angle=openmc.stats.Isotropic(),
    energy=openmc.stats.muir(e0=14080000.0, m_rat=5.0, kt=20000.0)
)

# %% [markdown]
# this next code block runs openmc and creates a file containing information on the initial particles. The position information is the extracted and plotted

# %%
plot_source_position(my_source)

# %% [markdown]
# This is closer to looking like a plasma compared to a point source but the distribution of spatial distribution can be improved in the next task

# %%
# these plotting methods can also be run if you are interested in energy or direction
# they will need importing from the openmc_source_plotter package
# plot_source_energy(my_source)
# plot_source_direction(my_source)

# %% [markdown]
# For convenience a plasma source package has been made that wraps openmc.IndependentSource and provides easy creation of ring (and other) fusion sources.
# https://github.com/fusion-energy/openmc-plasma-source you could try plotting the position of this source
