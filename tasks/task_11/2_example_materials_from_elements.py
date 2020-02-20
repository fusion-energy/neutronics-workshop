
import openmc

# Making water from elements

water_from_elements = openmc.Material(name='water_from_elements')
water_from_elements.add_element('H', 2.0, percent_type='ao')
water_from_elements.add_element('O', 1.0, percent_type='ao')
water_from_elements.set_density('g/cm3', 0.99821)

print(water_from_elements)


# Making Li4SiO4 from elements

Li4SiO4_from_elelmets = openmc.Material(name='Li4SiO4_from_elelmets')
Li4SiO4_from_elelmets.add_element('Li', 4.0, percent_type='ao')
Li4SiO4_from_elelmets.add_element('Si', 1.0, percent_type='ao')
Li4SiO4_from_elelmets.add_element('O', 4.0, percent_type='ao')
Li4SiO4_from_elelmets.set_density('g/cm3', 2.32)

print(Li4SiO4_from_elelmets)


# Making Li4SiO4 from isotopes and elements
# Remember, to make enriched Li4SiO4, we must still specify the Li isotopes

enrichment_fraction = 0.6

enriched_Li4SiO4_isotope_element = openmc.Material(name='enriched_Li4SiO4_isotope_element')
enriched_Li4SiO4_isotope_element.add_nuclide('Li6', 4.0*enrichment_fraction, percent_type='ao')
enriched_Li4SiO4_isotope_element.add_nuclide('Li7', 4.0*(1-enrichment_fraction), percent_type='ao')
enriched_Li4SiO4_isotope_element.add_element('Si', 1.0, percent_type='ao')
enriched_Li4SiO4_isotope_element.add_element('O', 4.0, percent_type='ao')
enriched_Li4SiO4_isotope_element.set_density('g/cm3', 2.32) # this would be lower than 2.32 but this would need calculating

print(enriched_Li4SiO4_isotope_element)