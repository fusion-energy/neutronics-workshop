
import re

import openmc
from openmc.data import ATOMIC_NUMBER, ATOMIC_SYMBOL
from openmc.deplete.chain import REACTIONS

# creates a material
material = openmc.Material()
material.add_element('Fe', 1)
material.set_density('g/cm3', 7.7)
materials = openmc.Materials([material])

# creates a geometry
surface = openmc.Sphere(r=500, boundary_type='vacuum')
cell = openmc.Cell(region=-surface)
cell.fill = material
geometry = openmc.Geometry([cell])

# creates simulation settings
settings = openmc.Settings()
settings.batches = 10
settings.inactive = 0
settings.particles = 500
settings.run_mode = 'fixed source'

# Create a DT point source
my_source = openmc.IndependentSource()
my_source.energy = openmc.stats.Discrete([14e6], [1])
settings.source = my_source

# gets all the possible reactions like (n,2n), (n,p), (n,2a) etc
reactions = list(REACTIONS.keys())

# makes a tally for every nuclide in the material and every reaction
rr_tally = openmc.Tally(name='RR')
rr_tally.nuclides = material.get_nuclides()
rr_tally.scores = reactions
tallies = openmc.Tallies([rr_tally])

# builds the model and runs it
model = openmc.model.Model(geometry, materials, settings, tallies)
sp_filename = model.run()

# gets the simulation results
sp = openmc.StatePoint(sp_filename)

# gets the tally
tbr_tally = sp.get_tally(name='RR')

# converts to a pandas dataframe for easy manipulation
df = tbr_tally.get_pandas_dataframe()
# sorts the reactions from highest to lowest
df = df.sort_values('mean', ascending=False)

# this loop goes through the reactions getting the reaction rate (mean) for each
# nuclide (nuclide) and each reaction (score)
print('Reaction rates per source neutron')
for index, row in df.iterrows():
    if row['mean']!= 0.:
        score = row['score']
        nuclide = row['nuclide']

        # gets the reaction change in terms of delta atomic number (dA)
        # and delta mass number (dZ). This is a tuple for example (n,2n) is
        # (-1, 0) because the atomic number decrease by one and the mass number
        # stays the same
        dAdZ = REACTIONS[score].dadz

        # gets the element symbol from the nuclide name for example Fe from Fe56
        element_symbol = re.split('(\d+)', nuclide)[0]
        # gets the Z number from the nuclide name for example 56 from Fe56
        Z_number = int(re.split('(\d+)', nuclide)[1])

        # looks up the atomic number from the element symbol
        A_number = ATOMIC_NUMBER[element_symbol]

        # increases the atomic and mass numbers according to the delta values
        new_Z = Z_number + dAdZ[1]
        new_A = A_number + dAdZ[0]

        # gets the element symbol of the potentially new element
        new_element_symbol = ATOMIC_SYMBOL[new_A]

        # prints all the transmutations and the reaction rates
        print(f"{element_symbol}{Z_number} -> {score} -> {new_element_symbol}{new_Z} per source neutron {row['mean']}")
