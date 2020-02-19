
import openmc
from openmc.data import *

# Making water from isotopes

water_isotope = openmc.Material(name='water_isotope')
water_isotope.add_nuclide('H1', 2.0*NATURAL_ABUNDANCE['H1'], percent_type='ao')
water_isotope.add_nuclide('H2', 2.0*NATURAL_ABUNDANCE['H2'], percent_type='ao')
water_isotope.add_nuclide('O16', NATURAL_ABUNDANCE['O16'], percent_type='ao')
water_isotope.add_nuclide('O17', NATURAL_ABUNDANCE['O17'], percent_type='ao')
water_isotope.add_nuclide('O18', NATURAL_ABUNDANCE['O18'], percent_type='ao')
water_isotope.set_density('g/cm3', 0.99821)

# Making Li4SiO4 from isotopes

Li4SiO4_isotope = openmc.Material(name='Li4SiO4_isotope')
Li4SiO4_isotope.add_nuclide('Li6', 4.0*NATURAL_ABUNDANCE['Li6'], percent_type='ao')
Li4SiO4_isotope.add_nuclide('Li7', 4.0*NATURAL_ABUNDANCE['Li7'], percent_type='ao')
Li4SiO4_isotope.add_nuclide('Si28', NATURAL_ABUNDANCE['Si28'], percent_type='ao')
Li4SiO4_isotope.add_nuclide('Si29', NATURAL_ABUNDANCE['Si29'], percent_type='ao')
Li4SiO4_isotope.add_nuclide('Si30', NATURAL_ABUNDANCE['Si30'], percent_type='ao')
Li4SiO4_isotope.add_nuclide('O16', 4.0*NATURAL_ABUNDANCE['O16'], percent_type='ao')
Li4SiO4_isotope.add_nuclide('O17', 4.0*NATURAL_ABUNDANCE['O17'], percent_type='ao')
Li4SiO4_isotope.add_nuclide('O18', 4.0*NATURAL_ABUNDANCE['O18'], percent_type='ao')
Li4SiO4_isotope.set_density('g/cm3', 2.32)

print(type(water_isotope))
print(water_isotope)
print(type(Li4SiO4_isotope))
print(Li4SiO4_isotope)


# Making enriched Li4SiO4 from isotopes

# enrichment_fraction = 0.6

# enriched_Li4SiO4_isotope = openmc.Material(name='enriched_Li4SiO4_isotope')
# enriched_Li4SiO4_isotope.add_nuclide('Li6', 4.0*enrichment_fraction, percent_type='ao')
# enriched_Li4SiO4_isotope.add_nuclide('Li7', 4.0*(1-enrichment_fraction), percent_type='ao')
# enriched_Li4SiO4_isotope.add_nuclide('Si28', NATURAL_ABUNDANCE['Si28'], percent_type='ao')
# enriched_Li4SiO4_isotope.add_nuclide('Si29', NATURAL_ABUNDANCE['Si29'], percent_type='ao')
# enriched_Li4SiO4_isotope.add_nuclide('Si30', NATURAL_ABUNDANCE['Si30'], percent_type='ao')
# enriched_Li4SiO4_isotope.add_nuclide('O16', 4.0*NATURAL_ABUNDANCE['O16'], percent_type='ao')
# enriched_Li4SiO4_isotope.add_nuclide('O17', 4.0*NATURAL_ABUNDANCE['O17'], percent_type='ao')
# enriched_Li4SiO4_isotope.add_nuclide('O18', 4.0*NATURAL_ABUNDANCE['O18'], percent_type='ao')
# enriched_Li4SiO4_isotope.set_density('g/cm3', 2.32)

# print(type(enriched_Li4SiO4_isotope))
# print(enriched_Li4SiO4_isotope)