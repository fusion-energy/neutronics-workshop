# %% [markdown]
# ---
# title: Tally Value Change During Depletion Simulation
# ---

# %% [markdown]
# This example simulates the variation of a tally response as a function of time. This particular tally is the tritium breeding ratio and this tends to decrease over time as the lithium gets burnt up by neutron irradiation.

# %% [markdown]
# First import OpenMC and configure the nuclear data paths

# %%
import openmc
import openmc.deplete
import math
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
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

# %%
# MATERIALS

mats = openmc.Materials()

# makes a simple material from Iron
breeding_material = openmc.Material() 
breeding_material.add_elements_from_formula('Li4SiO4')
breeding_material.set_density('g/cm3', 2.5)

lithium_orthosilicate_radius = 250
breeding_material.volume = (4/3) * math.pi * lithium_orthosilicate_radius**3 # a volume is needed so openmc can find the number of atoms in the cell/material
breeding_material.depletable = True  # depletable = True is needed to tell openmc to update the material with each time step

materials = openmc.Materials([breeding_material])

# GEOMETRY

# surfaces
sph1 = openmc.Sphere(r=lithium_orthosilicate_radius, boundary_type='vacuum')

# cells
shield_cell = openmc.Cell(region=-sph1)
shield_cell.fill = breeding_material
shield_cell.volume = (4/3) * math.pi * sph1.r**3

geometry = openmc.Geometry([shield_cell])

# %% [markdown]
# This section defines the neutron source term to use and the settings

# %%
# creates a 14MeV neutron point source
source = openmc.IndependentSource(
    space=openmc.stats.Point((0, 0, 0)),
    energy=openmc.stats.Discrete([14e6], [1]),
    particle='neutron'
)

# SETTINGS

# Instantiate a Settings object
settings = openmc.Settings()
settings.batches = 2
settings.particles = 5000
settings.source = source
settings.run_mode = 'fixed source'


tallies = openmc.Tallies()

# added a cell tally for tritium production
cell_filter = openmc.CellFilter(shield_cell)
tbr_tally = openmc.Tally(name='TBR')
tbr_tally.filters = [cell_filter]
tbr_tally.scores = ['H3-production']  # could use any score https://docs.openmc.org/en/stable/usersguide/tallies.html#id2
tallies.append(tbr_tally)

geometry.export_to_xml()
settings.export_to_xml()
tallies.export_to_xml()
materials.export_to_xml()
model = openmc.Model(geometry, materials, settings, tallies)

# %% [markdown]
# This is the depltion specific part of the model setup.
# Here we:
#
#     specify the chain file, this tells openmc the decay paths between isotopes including probabilities of different routes and half lives
#     
#     set the time steps and corresponding source rates 

# %%
operator = openmc.deplete.CoupledOperator(
    model=model,
    normalization_mode="source-rate",  # set for fixed source simulation, otherwise defaults to fission simulation
    reduce_chain_level=5
)

seconds_in_a_year=[365*24*60*60]
time_steps = seconds_in_a_year * 5 # 5 steps of 1 year in seconds
source_rates = [1e9]*5 # 1e9 neutrons per second for the full 5 years

integrator = openmc.deplete.PredictorIntegrator(operator, time_steps, source_rates)

integrator.integrate(write_rates=True)  # setting write_rates set to True so that rates are included in the depletion file

# %% [markdown]
# Access the TBR tally at each depletion time step, to observe the TBR decreasing as a function of time the simulation needs to be run with around 50000 particles

# %%
for counter in [0,1,2,3,4,5]:
    with openmc.StatePoint(f'openmc_simulation_n{counter}.h5') as sp:
        tbr_tally = sp.get_tally(name='TBR')
        print(f'depletion step {counter} TBR={tbr_tally.mean.sum()}')

# %% [markdown]
# Certain reations are also available in the depletion results file. 
#
# For example you can access the rate of n,gamma reactions at each time step

# %%
results = openmc.deplete.Results("depletion_results.h5")

times, number_of_n_gamma_reactions = results.get_reaction_rate(breeding_material, 'Li6', '(n,gamma)')

# %% [markdown]
# Then we can plot the changing reaction rate as a function of time steps

# %%
plt.plot(times/seconds_in_a_year, number_of_n_gamma_reactions)
plt.xlabel('time [years]')
plt.ylabel('Reaction rate')
plt.show()

# %% [markdown]
# This example shows how to simulate a reaction rate tally as a function of time as the materials are depleted the tally value changes.
#
# This is relevant for tritium breeding which tends to decrease as Li6 is burnt up
# Interestingly neutron shields also get slightly worse as neutron absorbing nuclei are depleted
#
# The material depletion is more relevant for power producing reactors where the neutron flux is higher than experimental reactors.
