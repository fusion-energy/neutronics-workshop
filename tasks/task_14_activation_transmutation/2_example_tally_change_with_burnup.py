import openmc
import openmc.deplete
import matplotlib.pyplot as plt
import math

lithium_orthosilicate_radius = 250

# MATERIALS

mats = openmc.Materials()

# makes a simple material from Iron
shielding_material = openmc.Material(name="shielding_material") 
shielding_material.add_elements_from_formula('Li4SiO4')
shielding_material.set_density('g/cm3', 2.5)
shielding_material.volume = (4/3) * math.pi * lithium_orthosilicate_radius**3
shielding_material.depletable = True

materials = openmc.Materials([shielding_material])
materials.export_to_xml()


# GEOMETRY

# surfaces
sph1 = openmc.Sphere(r=lithium_orthosilicate_radius, boundary_type='vacuum')

# cells
shield_cell = openmc.Cell(region=-sph1)
shield_cell.fill = shielding_material
shield_cell.volume = (4/3) * math.pi * sph1.r**3

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

# added a cell tally for tritium production
cell_filter = openmc.CellFilter(shield_cell)
tbr_tally = openmc.Tally(name='TBR')
tbr_tally.filters = [cell_filter]
tbr_tally.scores = ['(n,Xt)']  # Where X is a wildcard character, this catches any tritium production
tallies.append(tbr_tally)


# run python generate_endf71_chain.py from the openmc-dev/data repo
chain_filename = '/home/jshim/data-shimwell/depletion/chain_endfb71.xml'
chain = openmc.deplete.Chain.from_xml(chain_filename)

geometry.export_to_xml()
settings.export_to_xml()
tallies.export_to_xml()  # running in depletion mode doesn't write out the tallies file
materials.export_to_xml()
model = openmc.model.Model(geometry, materials, settings, tallies)

operator = openmc.deplete.Operator(model, chain_filename)


time_steps = [365*24*60*60] * 5 # 5 steps of 5 years in seconds
source_rates = [1e9]*5 # 1GW


integrator = openmc.deplete.PredictorIntegrator(operator, time_steps, source_rates)

integrator.integrate()

for counter in [0,1,2,3,4,5]:
    sp = openmc.StatePoint(f'openmc_simulation_n{counter}.h5')
    tbr_tally = sp.get_tally(name='TBR')
    print(tbr_tally.mean, tbr_tally.std_dev)
