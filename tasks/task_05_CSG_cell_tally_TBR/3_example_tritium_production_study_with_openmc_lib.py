"""
This script performs many simulations to find Tritium Breeding Ratio (TBR)
as a function of lithium 6 enrichment while only loading the nuclear data for
the nuclides just once.

As the simulation for TBR is quick and the loading of nuclear data is a relatively
large part of the process this saves a significant amount of time.
Using just the standard openmc python API one would have to load the same
nuclear data for each simulation.

openmc.lib provides Python bindings to the C/C++ API so we can have fine grain
control of the loading of the data, accessing the tallies and changing materials.
"""

import openmc


# make some python materials
breeder_material = openmc.Material(material_id = 12)  # Pb84.2Li15.8
breeder_material.add_element('Pb', 84.2)
breeder_material.add_element('Li', 15.8)
breeder_material.set_density('g/cm3', 11.)

steel = openmc.Material(material_id = 6)
steel.set_density('g/cm3', 7.75)
steel.add_element('Fe', 0.95)
steel.add_element('C', 0.05)

my_materials = openmc.Materials([breeder_material, steel])

# surfaces
vessel_inner = openmc.Sphere(r=500)
first_wall_outer_surface = openmc.Sphere(r=510)
breeder_blanket_outer_surface = openmc.Sphere(r=610, boundary_type='vacuum')


# cells
inner_vessel_region = -vessel_inner
inner_vessel_cell = openmc.Cell(region=inner_vessel_region)

first_wall_region = -first_wall_outer_surface & +vessel_inner
first_wall_cell = openmc.Cell(region=first_wall_region)
first_wall_cell.fill = steel

breeder_blanket_region = +first_wall_outer_surface & -breeder_blanket_outer_surface
breeder_blanket_cell = openmc.Cell(region=breeder_blanket_region)
breeder_blanket_cell.fill = breeder_material

my_geometry = openmc.Geometry([inner_vessel_cell, first_wall_cell, breeder_blanket_cell])


# SIMULATION SETTINGS
my_settings = openmc.Settings()
my_settings.batches = 10  # this is minimum number of batches that will be run
my_settings.trigger_active = True
my_settings.trigger_max_batches =  100  # this is maximum number of batches that will be run
my_settings.inactive = 0
my_settings.particles = 1000
my_settings.run_mode = 'fixed source'

source = openmc.IndependentSource()
source.space = openmc.stats.Point((0, 0, 0))
source.angle = openmc.stats.Isotropic()
source.energy = openmc.stats.Discrete([14e6], [1])
my_settings.source = source

# TALLIES

cell_filter = openmc.CellFilter(breeder_blanket_cell)
tbr_tally = openmc.Tally(name='TBR', tally_id=42)
tbr_tally.filters = [cell_filter]
tbr_tally.scores = ['(n,Xt)']  # Where X is a wildcard character, this catches any tritium production
my_tallies = openmc.Tallies([tbr_tally])

# RUN OPENMC
model = openmc.model.Model(my_geometry, my_materials, my_settings, my_tallies)

model.export_to_model_xml()

import openmc.lib
openmc.lib.init()

# run the simulation once and get the tally result
openmc.lib.run()
tally = openmc.lib.tallies[42]
print('tally result {tally.mean} with std. dev. {tally.std_dev}')

results=[]
enrichments = [0.0001, 0.25, 0.50, 0.75, 0.9999]
# now we will run the simulation 5 times
for enrichment in enrichments:  # percentage enrichment from 0% Li6 to 100% Li6

    # resets the tally to 0 so we don't combine result with previous simulation
    openmc.lib.hard_reset()

    # we modify the python material object here,
    # this helps get the new densities when updating the openmc.lib material
    breeder_material.remove_element('Li')
    breeder_material.add_nuclide('Li6', 15.8 * enrichment)
    breeder_material.add_nuclide('Li7', 15.8 * (1.-enrichment))

    # get the breeder material nuclides and densities in atom/b-cm
    new_composition = breeder_material.get_nuclide_atom_densities()

    nuclides = list(new_composition.keys())
    densities = list(new_composition.values())

    # get the openmc.lib material object that we want to change
    lib_breeder_material=openmc.lib.materials[breeder_material.id]
    # print the current nuclides and densities of the openmc.lib material
    print(f'old nuclides {lib_breeder_material.nuclides}') # List of nuclides in the material
    print(f'old nuclides {lib_breeder_material.densities}') # Array of densities in atom/b-cm
    # set the openmc.lib material object densities and nuclides to the updated values
    lib_breeder_material.set_densities(densities=densities, nuclides=nuclides)
    # print the new nuclides and densities of the openmc.lib material
    print(f'new nuclides {lib_breeder_material.nuclides}') # List of nuclides in the material
    print(f'new nuclides {lib_breeder_material.densities}') # Array of densities in atom/b-cm

    # run a simulation
    openmc.lib.run()

    # get the tally result for the TBR tally
    tally = openmc.lib.tallies[42]

    print('tally result {tally.mean} with std. dev. {tally.std_dev}')
    
    # append the tally to the results for plotting later
    results.append(tally.mean.flatten()[0])

# close down openmc lib interface
openmc.lib.finalize()

# plotting results
import plotly.graph_objects as go

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=enrichments,
        y=results,
        mode='lines',
    )
)

fig.update_layout(
    title="TBR as a function of Li6 enrichment",
    xaxis_title="Li6 enrichment (%)",
    yaxis_title="TBR"
)

fig.show()
