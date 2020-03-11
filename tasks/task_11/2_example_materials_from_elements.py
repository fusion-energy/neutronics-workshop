
import openmc

# Making water from elements

water_from_elements = openmc.Material(name='water_from_elements')
water_from_elements.add_element('H', 2.0, percent_type='ao')
water_from_elements.add_element('O', 1.0, percent_type='ao')
water_from_elements.set_density('g/cm3', 0.99821)

print(water_from_elements)



# Making Li4SiO4 from elements

# add Li4SiO4 here

# Li4SiO4_from_elements = openmc.Material(name='Li4SiO4_from_elements')
# Li4SiO4_from_elements.add_element.....
# Li4SiO4_from_elements.set_density.....
# print(Li4SiO4_from_elements)



# Making enriched Li4SiO4 from elements

enriched_Li4SiO4_from_elements = openmc.Material(name='enriched_Li4SiO4_from_elements')
enriched_Li4SiO4_from_elements.add_element('Li', 4.0, percent_type='ao', enrichment=60, enrichment_target='Li6', enrichment_type='ao')
enriched_Li4SiO4_from_elements.add_element('Si', 1.0, percent_type='ao')
enriched_Li4SiO4_from_elements.add_element('O', 4.0, percent_type='ao')
enriched_Li4SiO4_from_elements.set_density('g/cm3', 2.32)  # this would actually be lower than 2.32 g/cm3 but this would need calculating

# print(enriched_Li4SiO4_isotope_element)