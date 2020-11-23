
import openmc
from openmc.data import *  # this imports the NATURAL_ABUNDANCE dictionary


# Making water from isotopes

# specify material object
water_from_isotopes = openmc.Material(name='water_from_isotopes')

# add isotopes to material object
water_from_isotopes.add_nuclide('H1', 2.0*NATURAL_ABUNDANCE['H1'], percent_type='ao')
water_from_isotopes.add_nuclide('H2', 2.0*NATURAL_ABUNDANCE['H2'], percent_type='ao')
water_from_isotopes.add_nuclide('O16', NATURAL_ABUNDANCE['O16'], percent_type='ao')
water_from_isotopes.add_nuclide('O17', NATURAL_ABUNDANCE['O17'], percent_type='ao')
water_from_isotopes.add_nuclide('O18', NATURAL_ABUNDANCE['O18'], percent_type='ao')

# set material density
water_from_isotopes.set_density('g/cm3', 0.99821)

print(water_from_isotopes)


# Making Li4SiO4 from isotopes

# add Li4SiO4 here

# Li4SiO4_from_isotopes = openmc.Material(name='Li4SiO4_from_isotopes')
# Li4SiO4_from_isotopes.add_nuclide......
# Li4SiO4_from_isotopes.set_density......
# print(Li4SiO4_from_isotopes)


# Making enriched Li4SiO4 from isotopes

enrichment_fraction = 0.6

enriched_Li4SiO4_isotope = openmc.Material(name='enriched_Li4SiO4_isotope')
enriched_Li4SiO4_isotope.add_nuclide('Li6', 4.0*enrichment_fraction, percent_type='ao')
enriched_Li4SiO4_isotope.add_nuclide('Li7', 4.0*(1-enrichment_fraction), percent_type='ao')
enriched_Li4SiO4_isotope.add_nuclide('Si28', NATURAL_ABUNDANCE['Si28'], percent_type='ao')
enriched_Li4SiO4_isotope.add_nuclide('Si29', NATURAL_ABUNDANCE['Si29'], percent_type='ao')
enriched_Li4SiO4_isotope.add_nuclide('Si30', NATURAL_ABUNDANCE['Si30'], percent_type='ao')
enriched_Li4SiO4_isotope.add_nuclide('O16', 4.0*NATURAL_ABUNDANCE['O16'], percent_type='ao')
enriched_Li4SiO4_isotope.add_nuclide('O17', 4.0*NATURAL_ABUNDANCE['O17'], percent_type='ao')
enriched_Li4SiO4_isotope.add_nuclide('O18', 4.0*NATURAL_ABUNDANCE['O18'], percent_type='ao')
enriched_Li4SiO4_isotope.set_density('g/cm3', 2.32)  # this would be lower than 2.32 but this would need calculating

# print(enriched_Li4SiO4_isotope)
