import openmc
import openmc.deplete
import matplotlib.pyplot as plt
import math


iron_sphere_radius = 250

# MATERIALS

mats = openmc.Materials()

# makes a simple material from Iron
my_material = openmc.Material(name="my_material") 
my_material.add_nuclide('Co59', 1, percent_type='ao')
my_material.set_density('g/cm3', 7.7)
my_material.volume = (4/3) * math.pi * iron_sphere_radius**3
my_material.depletable = True

materials = openmc.Materials([my_material])
materials.export_to_xml()


# GEOMETRY

# surfaces
sph1 = openmc.Sphere(r=iron_sphere_radius, boundary_type='vacuum')

# cells, makes a simple sphere cell
shield_cell = openmc.Cell(region=-sph1)
shield_cell.fill = my_material
shield_cell.volume = (4/3) * math.pi * sph1.r**3

# sets the geometry to the universe that contains just the one cell
universe = openmc.Universe(cells=[shield_cell])
geometry = openmc.Geometry(universe)

# creates a 14MeV neutron point source
source = openmc.Source()
source.space = openmc.stats.Point((0, 0, 0))
source.angle = openmc.stats.Isotropic()
source.energy = openmc.stats.Discrete([14e6], [1])
source.particles = 'neutron'

# SETTINGS

# Instantiate a Settings object
settings = openmc.Settings()
settings.batches = 2
settings.inactive = 0
settings.particles = 500
settings.source = source
settings.run_mode = 'fixed source'


tallies = openmc.Tallies()
geometry.export_to_xml()
settings.export_to_xml()
# tallies.export_to_xml()  # running in depletion mode doesn't need the tallies to be writen out
materials.export_to_xml()
model = openmc.model.Model(geometry, materials, settings, tallies)

# This chain_endfb71 file was made with the run python generate_endf71_chain.py from the openmc-dev/data repo
# this tells openmc the decay paths between isotopes including proabilities of different routes and half lives
chain_filename = 'chain-nndc-b7.1.xml'
chain = openmc.deplete.Chain.from_xml(chain_filename)


operator = openmc.deplete.Operator(
    model=model,
    chain_file=chain_filename,
    normalization_mode="source-rate"
)

# 1e9 neutrons per second for 5 years then 5 years of no neutrons (shut down cooling time)
time_steps = [365*24*60*60] + [365*24*60*60] * 5
source_rates = [1e9] + [0] * 5
print(source_rates)
print(source_rates)
print(source_rates)
print(source_rates)
print(source_rates)

# CF4Integrator has been selected as the depletion operator for this example
# OpenMC offers several time-integration algorithms https://docs.openmc.org/en/stable/pythonapi/deplete.html#primary-api
# CF4Integrator was selected as it appears to be the most accurate https://dspace.mit.edu/handle/1721.1/113721
integrator = openmc.deplete.CF4Integrator(
    operator=operator, timesteps=time_steps,source_rates=source_rates
)

integrator.integrate()

results = openmc.deplete.ResultsList.from_hdf5("depletion_results.h5")

times, number_of_co60_atoms = results.get_atoms(my_material, 'Co60')

import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.plot(times, number_of_co60_atoms)

ax.set(xlabel='time (s)', ylabel='Number of atoms',
       title='Build up of atoms saturates when decay is equal to activation this occurs at circa 5 half lives')
ax.grid()
plt.savefig('atoms.png')
plt.show()