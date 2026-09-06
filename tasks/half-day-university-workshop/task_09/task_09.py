# %% [markdown]
# ---
# title: Plasma source plotting
# ---

# %% [markdown]
# As show in Part 1, OpenMC can be used to create point sources with different energy distributions. However, there are other ways to create neutron sources for use in neutronics simulations.
#
# This task allows users to plot the energy, position and initial directions of a parametric plasma source.
#
# This task makes use of the openmc-plasma-source package.

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
from openmc_source_plotter import plot_source_direction, plot_source_position

# %% [markdown]
# This first code block creates a neutron source using the PlasmaSource class from the parametric_plasma_source package. The properties of the source are controlled by the input parameters.

# %%
from openmc_plasma_source import tokamak_source

my_sources = tokamak_source(
    elongation=1.557,
    ion_density_centre=1.09e20,
    ion_density_peaking_factor=1,
    ion_density_pedestal=1.09e20,
    ion_density_separatrix=3e19,
    ion_temperature_centre=45.9,
    ion_temperature_peaking_factor=8.06,
    ion_temperature_pedestal=6.09,
    ion_temperature_separatrix=0.1,
    major_radius=9.06,
    minor_radius=2.92258,
    pedestal_radius=0.8 * 2.92258,
    mode="H",
    shafranov_factor=0.44789,
    triangularity=0.270,
    ion_temperature_beta=6,
    start_angle=0,  # toroidal start angle in radians
    rotation_angle=2 * 3.14,  # toroidal extent in radians
) # returns an openmc MeshSource

# %% [markdown]
# Makes a simple model for the sources.

# %%
settings = openmc.Settings()
settings.particles = 1
settings.batches = 1
settings.source = my_sources
materials = openmc.Materials()
sph = openmc.Sphere(r=1000000, boundary_type="vacuum")
cell = openmc.Cell(region=-sph)
geometry = openmc.Geometry([cell])
model = openmc.Model(geometry, materials, settings)

# %% [markdown]
# This code block then plots the birth location of each neutron, coloured by neutron birth energy.

# %%
plot = plot_source_position(this=model, n_samples=2000)
plot.show()

# %% [markdown]
# We can also plot the birth direction of each neutron.

# %%
plot = plot_source_direction(this=model, n_samples=500)
plot.show()

# %% [markdown]
# **Learning Outcomes for Part 2:**
#
# - Plasma sources can be defined using the parametric_plasma_source package.
