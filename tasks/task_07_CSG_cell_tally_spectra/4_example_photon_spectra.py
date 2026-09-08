# %% [markdown]
# ---
# title: Plotting photon and neutron energy spectra in a cell with a energy group structure
# ---

# %% [markdown]
# This example creates a simple sphere of tungsten with a neutron source inside.
#
# Neutrons generate photons as they travel through the material.
#
# Photon transport is enabled so these photons can be tracked tallied and plotted
#
# Photon flux is averaged across the cell and plotted as a function of energy.

# %% [markdown]
# First import OpenMC and configure the nuclear data path

# %%
import matplotlib.pyplot as plt
import openmc
from pathlib import Path
# Setting the cross section path to the correct location in the docker image.
# If you are running this outside the docker image you will have to change this path to your local cross section path.
openmc.config['cross_sections'] = Path.home() / 'nuclear_data' / 'cross_sections.xml'

# %% [markdown]
# This section creates a simple material, geometry and settings. This model is used in both the photon current tally and photon flux tally.

# %%
# MATERIALS

# Tungsten is a very good photon shield, partly due to its high Z number and electrons
my_material = openmc.Material()
my_material.add_element('W', 1, percent_type='ao')
my_material.set_density('g/cm3', 19)

my_materials = openmc.Materials([my_material])

# GEOMETRY

# surfaces
outer_surface = openmc.Sphere(r=100, boundary_type='vacuum')

# cells
blanket_cell = openmc.Cell(region=-outer_surface)
blanket_cell.fill = my_material

my_geometry = openmc.Geometry([blanket_cell])


# SIMULATION SETTINGS

# Instantiate a Settings object
my_settings = openmc.Settings()
my_settings.batches = 10
my_settings.particles = 1000
my_settings.run_mode = 'fixed source'
my_settings.photon_transport = True  # This line is required to switch on photons tracking, other wise the photons created by the neutrons are not tracked


# Create a DT point source
source = openmc.IndependentSource(
    space=openmc.stats.Point((0, 0, 0)),
    angle=openmc.stats.Isotropic(),
    energy=openmc.stats.Discrete([14e6], [1]),
# neutron is the default source.particle value so this line is not actually necessary for the simulation.
# However it is added for clarity.
# This simulation has a neutron source and those neutrons generate photons via interactions with the material.
# The resulting photons energy spectrum is tallied, but the units are still per source netron.
    particle='neutron'
)
my_settings.source = source

# %% [markdown]
# This section section adds a tally for the average photon flux across a cell.

# %%
#creates an empty tally object
my_tallies = openmc.Tallies()

# sets up filters for the tallies
particle_filter = openmc.ParticleFilter(['photon'])  # note the use of photons here, otherwise all particles are tallied
energy_filter = openmc.EnergyFilter.from_group_structure('VITAMIN-J-175')

# setup the filters for the cell tally
cell_filter = openmc.CellFilter(blanket_cell) 

# create the tally
cell_spectra_tally = openmc.Tally(name='cell_photon_spectra_tally')
cell_spectra_tally.scores = ['flux']
cell_spectra_tally.filters = [cell_filter, particle_filter, energy_filter]
my_tallies.append(cell_spectra_tally)

# %% [markdown]
# This section runs the simulation.

# %%
# combine all the required parts to make a model
model = openmc.Model(my_geometry, my_materials, my_settings, my_tallies)

# remove old files and runs OpenMC
for f in Path('.').glob('*.h5'):
    f.unlink(missing_ok=True)
results_filename = model.run()

# %% [markdown]
# This section extracts the cell tally data from the results file and plots photon flux across the cell.

# %%
# open the results file
with openmc.StatePoint(results_filename) as results:

    #extracts the tally values from the simulation results
    cell_tally = results.get_tally(name='cell_photon_spectra_tally')

    # flattens the ndarray into a 1d array for plotting
    openmc_flux = cell_tally.mean.flatten()

    volume_of_cell = 4188790 # cell is 100cm radius sphere, this volume is in units of cm3
    reactor_power = 500e6  # in units of watts
    energy_of_each_fusion_reaction = 17.5e6 * 2.8e-18  # eV converted to Joules
    neutrons_per_second = reactor_power / energy_of_each_fusion_reaction

    flux = (openmc_flux / volume_of_cell) * neutrons_per_second # divide by cell volume and then multiply by source strength


    plt.figure()
     # trim the last energy filter bin edge to make the number of x and y values the same
    plt.step(energy_filter.values[:-1], flux)
plt.yscale('log')
plt.xscale('log')
plt.ylabel('Flux [photons/cm2-s]')
plt.xlabel('Energy [eV]')
plt.show()

# %% [markdown]
# - In this simulation we used the VITAMIN-J-175 energy group structure to tally photons in energy bins.
# - There are several group structures built into OpenMC.
# - The VITAMIN-J-175, CCFE-709 and UKAEA-1102 structures are popular in fusion energy as they include 14MeV in the range.
# - OpenMC source code with other group structures can be found here: https://github.com/openmc-dev/openmc/blob/develop/openmc/mgxs/__init__.py.

# %% [markdown]
# **Learning Outcomes for Part 2:**
#
# - OpenMC can perform coupled neutron-photon simulations where photons are created from neutron interactions.
# - Photon spectra can be tallied in OpenMC using flux or current tallies, and energy bins.
