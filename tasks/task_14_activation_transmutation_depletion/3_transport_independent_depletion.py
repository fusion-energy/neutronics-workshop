# This example performs a depletion simulation using the IndependentOperator
# instead of the CoupledOperator used in the first examples.

# This is an approximation so is less accurate but it is faster and might be
# still sufficiently accurate for your use case.

# More details on both Operators in the docs
# https://docs.openmc.org/en/stable/usersguide/depletion.html#transport-independent-depletion

import openmc
import openmc.deplete
import os

import math

# MATERIALS

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

# creates a 14MeV neutron point source
source = openmc.Source()
source.space = openmc.stats.Point((0, 0, 0))
source.angle = openmc.stats.Isotropic()
source.energy = openmc.stats.Discrete([14e6], [1])
source.particles = 'neutron'

# SETTINGS

# Instantiate a Settings object
settings = openmc.Settings()
settings.batches = 20
settings.inactive = 0
settings.particles = 1000
settings.source = source
settings.run_mode = 'fixed source'

model = openmc.model.Model(geometry, materials, settings)

# openmc.config['chain_file'] = '/nuclear_data/chain-nndc-b8.0.xml'
openmc.config['chain_file'] = 'chain-nndc-b8.0.xml'

# runs the simulation to generate one group microscopic cross sections
micro_xs = openmc.deplete.MicroXS.from_model(
    model,
    my_material,
    openmc.config['chain_file']
)
print('All the reaction rates within the material', micro_xs)

# This category of operator uses one-group microscopic cross sections to obtain transmutation reaction rates.
# The cross sections are pre-calculated, so there is no need for direct coupling between a transport-independent operator and a transport solver.
operator = openmc.deplete.IndependentOperator(
    materials=materials,
    micro_xs=micro_xs,
    chain_file=openmc.config['chain_file'],
    dilute_initial=0,  # set to zero to avoid adding small amounts of isotopes, defaults to adding small amounts of fissionable isotopes
    reduce_chain=True,  # reduced to only the isotopes present in depletable materials and their possible progeny
    reduce_chain_level=5,
)

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
integrator = openmc.deplete.PredictorIntegrator(
    operator=operator,
    timesteps=timesteps,
    source_rates=source_rates,
    timestep_units='s'
)

integrator.integrate()
print("Finalize depletion...")

results = openmc.deplete.ResultsList.from_hdf5("depletion_results.h5")

times, number_of_Ag110_atoms = results.get_atoms(my_material, 'Ag110')

for time, num in zip(times, number_of_Ag110_atoms):
    print(f" Time {time}s. Number of Ag110 atoms {num}")

import matplotlib.pyplot as plt

plt.plot(times, number_of_Ag110_atoms)
plt.show()
