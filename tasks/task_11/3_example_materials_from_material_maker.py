
import openmc 

from neutronics_material_maker import Material

# Some materials require arguments to correctly calculate material properties

# Water requires 'temperature' and 'pressure' arguments to be passed

# the following command creates a Material() object using the neutronics_material_maker
water = Material('H2O', temperature_in_C=25, pressure_in_Pa=100000) # atmospheric

# the following command converts Material() objects into neutronics materials which can be used in OpenMC
water_neutronics = water.neutronics_material
# this is equivalent to:
# water_neutronics = Material('H2O', temperature_in_C=25, pressure_in_Pa=100000).neutronics_material

print(type(water))
print(water)
print(type(water_neutronics))
print(water_neutronics)


# Some materials can also take arguments which adjust material properties

# Lithium Orthosilicate (Li4SiO4) can take arguments of 'enrichment_fraction' and 'packing_fraction'

default_Li4SiO4 = Material('Li4SiO4').neutronics_material 

# the following command creates Li4SiO4 with respect to the given arguments
enriched_and_packed_Li4SiO4 = Material('Li4SiO4', enrichment_fraction=0.6, packing_fraction=0.8).neutronics_material

print(type(default_Li4SiO4))
print(default_Li4SiO4)
print(type(enriched_and_packed_Li4SiO4))
print(enriched_and_packed_Li4SiO4)


# Neutronics materials can be inspected to extract material properties
# Densities are calculated for some materials using the CoolProp package

print('Water density = ' + water_neutronics.density)
print('Default Li4SiO4 density = ' + default_Li4SiO4.density)
print('Enriched and Packed Li4SiO4 density = ' + enriched_and_packed_Li4SiO4.density)
