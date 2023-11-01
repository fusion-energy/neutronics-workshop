# This example performs a depletion simulation using the IndependentOperator
# instead of the CoupledOperator used in the first examples.

# This is an approximation so is less accurate but it is faster and might be
# still sufficiently accurate for your use case.

# More details on both Operators in the docs
# https://docs.openmc.org/en/stable/usersguide/depletion.html#transport-independent-depletion

import openmc
import openmc.deplete
import math
import matplotlib.pyplot as plt
#openmc.config['chain_file']=/home/j/openmc_data/chain-endf-b8.0.xml
#openmc.config['cross_sections']=/home/j/nndc-b8.0-hdf5/endfb-viii.0-hdf5/cross_sections.xml
my_material = openmc.Material() 
my_material.add_element('Ag', 1, percent_type='ao')
my_material.set_density('g/cm3', 10.49)
sphere_radius = 100
volume_of_sphere = (4/3) * math.pi * math.pow(sphere_radius, 3)
my_material.volume = volume_of_sphere  # a volume is needed so openmc can find the number of atoms in the cell/material
my_material.depletable = True  # depletable = True is needed to tell openmc to update the material with each time step
materials = openmc.Materials([my_material])
sph1 = openmc.Sphere(r=sphere_radius, boundary_type='vacuum')
shield_cell = openmc.Cell(region=-sph1)
shield_cell.fill = my_material
geometry = openmc.Geometry([shield_cell])
source = openmc.IndependentSource()
source.space = openmc.stats.Point((0, 0, 0))
source.angle = openmc.stats.Isotropic()
source.energy = openmc.stats.Discrete([14e6], [1])
source.particles = 'neutron'
settings = openmc.Settings()
settings.batches = 10
settings.inactive = 0
settings.particles = 1000
settings.source = source
settings.run_mode = 'fixed source'
model = openmc.model.Model(geometry, materials, settings)
# this does perform transport but just to get the flux, the flux could also be input in the energy group format (ccfe 709 used here)
flux_in_each_group, micro_xs = openmc.deplete.get_microxs_and_flux(
    model=model,
    domains=[shield_cell],
    energies='CCFE-709',
)
plt.title('neutron flux spectra')
plt.plot(openmc.mgxs.GROUP_STRUCTURES['CCFE-709'][:-1], flux_in_each_group[0])
plt.xscale('log')
plt.yscale('log')
plt.show()
operator = openmc.deplete.IndependentOperator(
    materials=materials,
    fluxes=flux_in_each_group,
    micros=micro_xs,
    reduce_chain=True,  # reduced to only the isotopes present in depletable materials and their possible progeny
    reduce_chain_level=5,
    normalization_mode="source-rate"
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

integrator = openmc.deplete.PredictorIntegrator(
    operator=operator,
    timesteps=timesteps,
    source_rates=source_rates,
    timestep_units='s'
)
integrator.integrate()
results = openmc.deplete.ResultsList.from_hdf5("depletion_results.h5")
times, number_of_Ag110_atoms = results.get_atoms(my_material, 'Ag110')
for time, num in zip(times, number_of_Ag110_atoms):
    print(f" Time {time}s. Number of Ag110 atoms {num}")
plt.cla()
plt.clf()
plt.plot(times, number_of_Ag110_atoms)
plt.show()
