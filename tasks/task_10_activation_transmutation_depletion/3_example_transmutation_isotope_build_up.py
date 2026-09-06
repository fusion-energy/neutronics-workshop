# %% [markdown]
# ---
# title: Nuclide Build Up During Depletion Simulation
# ---

# %% [markdown]
# This example simulates the build up of activation products within a material under neutron irradiation. The subsequent decay of unstable isotopes is also simulated.

# %% [markdown]
# This first cell imports the packages needed, note the extra import openmc.deplete import

# %%
# remove any old files
from pathlib import Path
for f in Path('.').glob('*.xml'):
    f.unlink(missing_ok=True)

import math
import openmc
import openmc.deplete
# Setting the cross section path to the correct location in the docker image.
# If you are running this outside the docker image you will have to change this path to your local cross section path.
openmc.config['cross_sections'] = Path.home() / 'nuclear_data' / 'cross_sections.xml'
# the chain file was downloaded with
# pip install openmc_data
# download_endf_chain -r b8.0
openmc.config['chain_file'] = Path.home() / 'nuclear_data' / 'chain-endf-b8.0.xml'

# %% [markdown]
# This section creates the geometry and the cells.
# Note that it necessary to set the volume of the material or cell.
# This is so that the depletion code can find the number of atoms within the cell given the material composition, material density and volume.

# %%
# MATERIALS
openmc.reset_auto_ids()  # automatically assign unique ID numbers to objects

# makes a simple material from Silver
my_material = openmc.Material() 
my_material.add_element('Ag', 1, percent_type='ao')
my_material.set_density('g/cm3', 10.49)


sphere_radius = 100
volume_of_sphere = (4/3) * math.pi * math.pow(sphere_radius, 3)
my_material.volume = volume_of_sphere  # a volume is needed so openmc can find the number of atoms in the cell/material
my_material.depletable = True  # depletable = True is needed to tell openmc to update the material with each time step

materials = openmc.Materials([my_material])
materials.export_to_xml()


# GEOMETRY

# surfaces
sph1 = openmc.Sphere(r=sphere_radius, boundary_type='vacuum')

# cells, makes a simple sphere cell
shield_cell = openmc.Cell(region=-sph1)
shield_cell.fill = my_material

# sets the geometry to the universe that contains just the one cell
geometry = openmc.Geometry([shield_cell])

# %% [markdown]
# This section defines the neutron source term to use and the settings

# %%
# creates a 14MeV neutron point source
source = openmc.IndependentSource(
    space=openmc.stats.Point((0, 0, 0)),
    angle=openmc.stats.Isotropic(),
    energy=openmc.stats.Discrete([14e6], [1]),
    particle='neutron'
)

# SETTINGS

# Instantiate a Settings object
settings = openmc.Settings()
settings.batches = 2
settings.inactive = 0
settings.particles = 10000
settings.source = source
settings.run_mode = 'fixed source'

model = openmc.Model(geometry, materials, settings)

# %% [markdown]
# This is the depletion specific part of the model setup.
#
# This section specifies the chain file, this tells openmc the decay paths between isotopes including probabilities of different routes and half lives

# %% [markdown]
# This next stage sets the time steps and corresponding source rates for the irradiation schedule.
#
# An output file will be produced with showing the material composition at every time step.
#
# We are irradiating the Silver for multiple half lives to show build up and saturation
#
# Saturation happens when decay is = to creation of the particular isotope
#
# Ag110 half life is 24 seconds so it will start to become saturated after 120 seconds
#
# Ag108 half life is 145 seconds so it will not be saturated

# %%
# We define timesteps together with the source rate to make it clearer
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


# PredictorIntegrator has been selected as the depletion operator for this example as it is a fast first order Integrator
# OpenMC offers several time-integration algorithms https://docs.openmc.org/en/stable/pythonapi/deplete.html#primary-api\n",
# CF4Integrator should normally be selected as it appears to be the most accurate https://dspace.mit.edu/handle/1721.1/113721\n",

model.deplete(
    method="predictor",  # predictor is a simple but quick method
    operator_kwargs={
        "normalization_mode": "source-rate",  # needed as this is a fixed source simulation
        "chain_file": openmc.config['chain_file'],
        "reduce_chain_level": 5,
    },
    timesteps=timesteps,
    source_rates=source_rates,
)

# %% [markdown]
# This next section starts the depletion simulation and produces the output files

# %% [markdown]
# This section extracts the results of the depletion simulation from the h5 file and gets the amount of Ag110 in the material at each of the time steps

# %%
results = openmc.deplete.ResultsList.from_hdf5("depletion_results.h5")

times, number_of_Ag110_atoms = results.get_atoms(my_material, 'Ag110')

for time, num in zip(times, number_of_Ag110_atoms):
    print(f" Time {time}s. Number of Ag110 atoms {num}")

# %% [markdown]
# In addition to Ag110 other atoms get created. This section plots the number of nuclides in the material excluding the original nuclides in the unirradiated material

# %%
import openmc_depletion_plotter
# this package provides convenient plotting methods for depletion simulations like this one
# more details here https://github.com/fusion-energy/openmc_depletion_plotter

results.plot_atoms_vs_time(excluded_material=my_material)

# %% [markdown]
# Not all nuclides are unstable and the unstable ones have a different half life. This next plot shows the specific activity (activity per unit mass) as a function of time.
#
# This is useful for identifying a suitable waste repository for activated waste.

# %%
results.plot_activity_vs_time()
