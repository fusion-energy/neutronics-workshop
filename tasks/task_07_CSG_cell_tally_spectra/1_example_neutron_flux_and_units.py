# %% [markdown]
# ---
# title: Neutron flux and units
# ---

# %% [markdown]
# This example creates a simple sphere of water and tallies neutron flux averaged across a cell.

# %% [markdown]
# First import OpenMC and configure the nuclear data path

# %%
import openmc
from pathlib import Path
# Setting the cross section path to the correct location in the docker image.
# If you are running this outside the docker image you will have to change this path to your local cross section path.
openmc.config['cross_sections'] = Path.home() / 'nuclear_data' / 'cross_sections.xml'

# %% [markdown]
# This section creates a simple material, geometry and settings. This model is used in both the neutron current tally and the neutron flux tally.

# %%
# MATERIALS

# Due to the hydrogen content water is a very good neutron moderator
my_material = openmc.Material()
my_material.add_element('H', 1, percent_type='ao')
my_material.add_element('O', 2, percent_type='ao')
my_material.set_density('g/cm3', 1)

my_materials = openmc.Materials([my_material])


# GEOMETRY

# surfaces
outer_surface = openmc.Sphere(r=500, boundary_type='vacuum')

# cells
cell_1 = openmc.Cell(region=-outer_surface)
cell_1.fill = my_material
# we will need this volume later to convert the flux units
cell_1.volume = 5.24e8  # using (4/3)pi * r^3

my_geometry = openmc.Geometry([cell_1])


# SIMULATION SETTINGS

# Instantiate a Settings object
my_settings = openmc.Settings()
my_settings.batches = 10
my_settings.particles = 1000
my_settings.run_mode = 'fixed source'

# Create a DT point source
my_source = openmc.IndependentSource(
    space=openmc.stats.Point((0, 0, 0)),
    angle=openmc.stats.Isotropic(),
    energy=openmc.stats.Discrete([14e6], [1])
)
my_settings.source = my_source

# %% [markdown]
# This section section adds a tally for the average neutron flux across a cell.

# %%
# sets up filters for the tallies
neutron_particle_filter = openmc.ParticleFilter(['neutron'])

# setup the filters for the cell tally
cell_filter = openmc.CellFilter(cell_1) 

# create the tally
cell_spectra_tally = openmc.Tally(name='cell_flux_tally')
cell_spectra_tally.scores = ['flux']
cell_spectra_tally.filters = [cell_filter, neutron_particle_filter]
my_tallies = openmc.Tallies([cell_spectra_tally])

# %% [markdown]
# This section adds two surface current tallies - one on the inner sphere surface and one on the outer sphere surface.

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
# This section extracts the cell tally data from the results file and plots neutron flux across the cell. Selecting log-log scale will allow you to see a distribution of thermal neutrons.

# %%
# open the results file
with openmc.StatePoint(results_filename) as results:

    #extracts the tally values from the simulation results
    cell_tally = results.get_tally(name='cell_flux_tally')

    # flattens the ndarray into a 1d array
    openmc_flux = cell_tally.mean.flatten()

# %% [markdown]
# Discussion on results and units of flux
#
# Openmc like most of other neutronics codes accumulates track lengths within cell volumes, i.e the length that a neutron travels in a material.
#
# A track length has units of centimeters (cm).
#
# Neutronics codes typically make use of cm instead of the SI base unit for length of meters, this is partly historical and partly due to the format of nuclear data files.
#
# A flux score on a cell in OpenMC therefore returns the average length that neutrons travel through the cell.
#
# As we have simulated many neutrons we can get an average result and as we have batches we can get a standard deviation on that result.
#
# OpenMC returns a flux tally in units of "neutron cm per source neutron"
#
# To convert this into more common units of flux "neutrons per cm2 per second" we must first divide by the volume.
#
# As this is a cell tally we divide by the cell volume, if this was a mesh tally we would divide by the voxel volume.
#
# This gives us units of "neutrons per cm2 per source neutron".
#
# In a fixed source simulation (not an fission eigenvalue simulation) we can then scale the result by the number of neutrons per second that the source emits.
#
# To find the number of neutrons you would typically know the power of the fusion reactor in watts.
#
# Assuming we are using DT fuel then we know that each neutron resulted in 17.6MeV or 2.8e-18Joules of energy.
#
# Therefore the neutrons per second is power in watts / 2.8e-18. For a 500MW fusion power reactor we would get 500e6/2.8e-18=1.785e+26 neutrons per second
#
# So our source strength is 1.785e+26 and we multiply out flux by this to get units of "neutrons per cm2 per second"
#
# For ICF (Inertial Confinement Fusion) you might use units of per shot instead of per second

# %%
volume_of_cell = 5.24e8 # in units of cm3
reactor_power = 500e6  # in units of watts
energy_of_each_fusion_reaction = 17.5e6 * 1.60218e-19  # eV converted to Joules
neutrons_per_second = reactor_power / energy_of_each_fusion_reaction
flux = (openmc_flux / volume_of_cell) * neutrons_per_second # divide by cell volume and then multiply by source strength


print(f'neutron flux = {flux} neutrons per cm2 per second')

# %% [markdown]
# **Learning Outcomes for Part 1:**
#
# - Neutron flux in found in units of "neutron cm per source neutron" but can be converted to "neutrons per cm2 per second"
