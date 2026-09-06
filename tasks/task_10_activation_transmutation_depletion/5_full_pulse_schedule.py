# %% [markdown]
# ---
# title: Full pulse schedule depletion simulation
# ---

# %% [markdown]
# This example performs a depletion/transmutation/activation simulation
#
# The simulation has been accelerated by making use of the IndependentOperator instead of the CoupledOperator.
#
# This is an approximation so is less accurate but it is much faster.
#
# This approach performs just a single transport simulation and obtains reactions rates once and assumes that they remain constant.
#
# If the materials don't change significantly during the irradiation this is a reasonable approximation.
#
# Fission fuel pins would perhaps require the full CoupledOperator while the majority of fusion simulations are suitable for the IndependentOperator
#
# More details on both Operators in the docs
# https://docs.openmc.org/en/stable/usersguide/depletion.html#transport-independent-depletion

# %%
import matplotlib.pyplot as plt
import openmc
import openmc.deplete
import math
from pathlib import Path
# Setting the cross section path to the correct location in the docker image.
# If you are running this outside the docker image you will have to change this path to your local cross section path.
openmc.config['cross_sections'] = Path.home() / 'nuclear_data' / 'cross_sections.xml'
# This chain file was downloaded using the download_endf_chain script that is included in the openmc_data package https://github.com/openmc-data-storage/openmc_data
# this file tells openmc the decay paths between isotopes including probabilities of different routes and half lives
# To download this xml file you can run these commands
# pip install openmc_data
# download_endf_chain -d nuclear_data -r b8.0
openmc.config['chain_file'] = Path.home() / 'nuclear_data' / 'chain-endf-b8.0.xml'

# remove any old files
Path('model.xml').unlink(missing_ok=True)
Path('materials.xml').unlink(missing_ok=True)
Path('geometry.xml').unlink(missing_ok=True)
Path('settings.xml').unlink(missing_ok=True)

# %% [markdown]
# Creates a simple material which we will deplete

# %%
my_material = openmc.Material(material_id=1) 
my_material.add_element('Ag', 1, percent_type='ao')
my_material.set_density('g/cm3', 10.49)

# %% [markdown]
# As we are doing a depletion simulation we must set the material volume and the .depletion to True

# %%
sphere_radius = 100
volume_of_sphere = (4/3) * math.pi * math.pow(sphere_radius, 3)
my_material.volume = volume_of_sphere  # a volume is needed so openmc can find the number of atoms in the cell/material
my_material.depletable = True  # depletable = True is needed to tell openmc to update the material with each time step
materials = openmc.Materials([my_material])

# %% [markdown]
# makes a simple sphere surface and cell

# %%
sph1 = openmc.Sphere(r=sphere_radius, boundary_type='vacuum')
shield_cell = openmc.Cell(region=-sph1)
shield_cell.fill = my_material
geometry = openmc.Geometry([shield_cell])

# %% [markdown]
# creates a simple point source

# %%
source = openmc.IndependentSource(
    space=openmc.stats.Point((0, 0, 0)),
    angle=openmc.stats.Isotropic(),
    energy=openmc.stats.Discrete([14e6], [1]),
    particle='neutron'
)

# %% [markdown]
# defines the simulation settings

# %%
settings = openmc.Settings()
settings.batches = 10
settings.inactive = 0
settings.particles = 1000
settings.source = source
settings.run_mode = 'fixed source'

# %% [markdown]
# builds the model combining the materials, geometry and settings into one object

# %%
model = openmc.Model(geometry, materials, settings)

# %% [markdown]
# this does perform particle transport but just to get the flux and micro xs

# %%
flux_in_each_group, micro_xs = openmc.deplete.get_microxs_and_flux(
    model=model,
    domains=[shield_cell],
    chain_file=openmc.config['chain_file'],
)

# %% [markdown]
# constructing the operator, note we pass in the flux and micro xs calculated earlier

# %%
operator = openmc.deplete.IndependentOperator(
    materials=materials,
    fluxes=[i[0] for i in flux_in_each_group],
    micros=micro_xs,
    reduce_chain_level=5,
    normalization_mode="source-rate"
)

# %% [markdown]
# We define timesteps together with the source rate to make it clearer

# %%
timesteps_and_source_rates = [
    (24, 1e20),
    (24, 1e20),
    (24, 1e20),
    (24, 1e20),
    (24, 1e20),  # should saturate Ag110 here as it has been irradiated for over 5 halflives
    (24, 1e20),
    (24, 1e20),
    (24, 1e20),
    (24, 1e20),
    (24, 0),
    (24, 0),
    (24, 0),
    (24, 0),
    (24, 0),
    (24, 0),
    (24, 0),
    (24, 0),
    (24, 0),
    (24, 0),
    (24, 0),
]

# Uses list Python comprehension to get the timesteps and source_rates separately
timesteps = [item[0] for item in timesteps_and_source_rates]
source_rates = [item[1] for item in timesteps_and_source_rates]

# %% [markdown]
# construct the integrator

# %%
integrator = openmc.deplete.PredictorIntegrator(
    operator=operator,
    timesteps=timesteps,
    source_rates=source_rates,
    timestep_units='s'
)

# %% [markdown]
# this runs the depltion calculations for the timesteps

# %%
integrator.integrate()

# %% [markdown]
# Loads up the results

# %%
results = openmc.deplete.Results("depletion_results.h5")

# %% [markdown]
# Gets the material from the 2nd timestep and shows the composition

# %%
second_time_step = results[2]
second_time_step.get_material('1')

# %% [markdown]
# prints the atoms of Ag110 in a table for reach time step

# %%
times, number_of_Ag110_atoms = results.get_atoms(my_material, 'Ag110')
for time, num in zip(times, number_of_Ag110_atoms):
    print(f" Time {time}s. Number of Ag110 atoms {num}")

# %%
# plots the number of atoms as a function of time

# %%
plt.plot(times, number_of_Ag110_atoms)
plt.xlabel('Time [s]')
plt.ylabel('Number of Ag110 atoms')
plt.show()
