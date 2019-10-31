#!/usr/bin/env python3

""" material_maker_functions.py: obtains a few material values such as density, chemical present etc ."""

__author__      = "Jonathan Shimwell"

import re
import openmc

def calculate_crystal_structure_density(material,atoms_per_unit_cell,volume_of_unit_cell_cm3):
      molar_mass = material.average_molar_mass*len(material.nuclides)
      atomic_mass_unit_in_g = 1.660539040e-24
      density_g_per_cm3 = molar_mass * atomic_mass_unit_in_g * atoms_per_unit_cell / volume_of_unit_cell_cm3
      #print('density =',density_g_per_cm3)
      return density_g_per_cm3

def read_chem_eq(chemical_equation):
        return [a for a in re.split(r'([A-Z][a-z]*)', chemical_equation) if a]

def get_elements(chemical_equation):
        chemical_equation_chopped_up = read_chem_eq(chemical_equation)
        list_elements = []

        for counter in range(0, len(chemical_equation_chopped_up)):
            if chemical_equation_chopped_up[counter].isalpha():
                element_symbol = chemical_equation_chopped_up[counter]
                list_elements.append(element_symbol)
        return list_elements

def get_element_numbers(chemical_equation):
        chemical_equation_chopped_up = read_chem_eq(chemical_equation)
        list_of_fractions = []

        for counter in range(0, len(chemical_equation_chopped_up)):
            if chemical_equation_chopped_up[counter].isalpha():
                if counter == len(chemical_equation_chopped_up)-1:
                    list_of_fractions.append(1.0)
                elif not (chemical_equation_chopped_up[counter + 1]).isalpha():
                    list_of_fractions.append(float(chemical_equation_chopped_up[counter + 1]))
                else:
                    list_of_fractions.append(1.0)
        return list_of_fractions

def find_density_of_natural_material_at_temperature(breeder_material_name,temperature_in_C,natural_breeder_material):

    if breeder_material_name == 'Pb84.2Li15.8':
        #Pb84.2Li15.8 is the eutectic ratio, this could be a varible

        return 99.90*(0.1-16.8e-6*temperature_in_C) #valid for in the range 240-350 C. source http://aries.ucsd.edu/LIB/PROPS/PANOS/lipb.html

    if breeder_material_name == 'F2Li2BeF2':
        #Li2BeF4 made from 2(FLi):BeF2 is the eutectic ratio, this could be a varible

        return 2.214 - 4.2e-4 * temperature_in_C # source http://aries.ucsd.edu/LIB/MEETINGS/0103-TRANSMUT/gohar/Gohar-present.pdf

    if breeder_material_name == 'Li':

        return 0.515 - 1.01e-4 * (temperature_in_C - 200) # valid between 200 - 1600 C source http://aries.ucsd.edu/LIB/PROPS/PANOS/li.html

    if breeder_material_name == 'Li4SiO4':

        return calculate_crystal_structure_density(natural_breeder_material,14,1.1543e-21)

def make_copper():  

    copper = openmc.Material(name='Copper')
    copper.set_density('g/cm3', 8.5)
    copper.add_element('Cu', 1.0)
  
    return copper  

def make_eurofer():  

    eurofer = openmc.Material(name='EUROFER97')
    eurofer.set_density('g/cm3', 7.75)
    eurofer.add_element('Fe', 89.067, percent_type='wo')
    #eurofer.add_element('C', 0.11, percent_type='wo')
    eurofer.add_element('Mn', 0.4, percent_type='wo')
    eurofer.add_element('Cr', 9.0, percent_type='wo')
    eurofer.add_element('Ta', 0.12, percent_type='wo')
    eurofer.add_element('W', 1.1, percent_type='wo')
    eurofer.add_element('N', 0.003, percent_type='wo')
    eurofer.add_element('V', 0.2, percent_type='wo')
   
    return eurofer  
        
