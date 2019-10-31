#!/usr/bin/env python3

"""example_isotope_plot.py: plots cross sections for a couple of isotopes."""

__author__      = "Jonathan Shimwell"

import openmc
from plotly import __version__
from plotly.offline import download_plotlyjs, plot
from plotly.graph_objs import Scatter, Layout
import matplotlib.pyplot as plt
import re






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

def make_materials(enrichment_fraction, breeder_material_name, temperature_in_C):

    #density data from http://aries.ucsd.edu/LIB/PROPS/PANOS/matintro.html

    natural_breeder_material = openmc.Material(2, "natural_breeder_material")
    breeder_material = openmc.Material(1, breeder_material_name)

    element_numbers = get_element_numbers(breeder_material_name)
    elements = get_elements(breeder_material_name)

    for e, en in zip(elements, element_numbers):
        natural_breeder_material.add_element(e, en,'ao')
    print('natural_breeder_material',natural_breeder_material)

    for e, en in zip(elements, element_numbers):
        if e == 'Li':
            breeder_material.add_nuclide('Li6', en * enrichment_fraction, 'ao')
            breeder_material.add_nuclide('Li7', en * (1.0-enrichment_fraction), 'ao')  
        else:
            breeder_material.add_element(e, en,'ao')    

    if breeder_material_name == 'Pb84.2Li15.8':
        #Pb84.2Li15.8 is the eutectic ratio, this could be a varible

        density_of_natural_material_at_temperature = 99.90*(0.1-16.8e-6*temperature_in_C) #valid for in the range 240-350 C. source http://aries.ucsd.edu/LIB/PROPS/PANOS/lipb.html

    if breeder_material_name == 'F2Li2BeF2':
        #Li2BeF4 made from 2(FLi):BeF2 is the eutectic ratio, this could be a varible

        density_of_natural_material_at_temperature = 2.214 - 4.2e-4 * temperature_in_C # source http://aries.ucsd.edu/LIB/MEETINGS/0103-TRANSMUT/gohar/Gohar-present.pdf

    if breeder_material_name == 'Li':

        density_of_natural_material_at_temperature = 0.515 - 1.01e-4 * (temperature_in_C - 200) # valid between 200 - 1600 C source http://aries.ucsd.edu/LIB/PROPS/PANOS/li.html

    if breeder_material_name == 'Li4SiO4':

      density_of_natural_material_at_temperature = calculate_crystal_structure_density(breeder_material,14,1.1543e-21)



    natural_breeder_material.set_density('g/cm3', density_of_natural_material_at_temperature)
    atom_densities_dict = natural_breeder_material.get_nuclide_atom_densities()
    atoms_per_barn_cm = sum([i[1] for i in atom_densities_dict.values()])



    breeder_material.set_density('atom/b-cm',atoms_per_barn_cm) 

    mats = openmc.Materials([breeder_material])
    print(breeder_material)
    return breeder_material



def generate_material_trace(mat,Endf_MT_number):
      if type(Endf_MT_number) == int:
            Endf_MT_number = [Endf_MT_number]
      Energy, data = openmc.calculate_cexs(mat, 'material', Endf_MT_number )
      cross_section = data[0]

      trace1= Scatter(x=Energy, 
                y=cross_section, 
                mode = 'lines', 
                name=mat.name + ' MT '+str(Endf_MT_number[0]) )
      return trace1


traces = []

mat_Li = make_materials(0.6, 'Li', 500)
traces.append(generate_material_trace(mat_Li,4))

mat_Pb84Li15 = make_materials(0.6, 'Pb84.2Li15.8', 500)
traces.append(generate_material_trace(mat_Pb84Li15,4))

mat_F2Li2BeF2 = make_materials(0.6, 'F2Li2BeF2', 500)
traces.append(generate_material_trace(mat_F2Li2BeF2,4))

mat_Li4SiO4 = make_materials(0.6, 'Li4SiO4', 500)
traces.append(generate_material_trace(mat_Li4SiO4,4))

mat_Li = make_materials(0.6, 'Li', 500)
traces.append(generate_material_trace(mat_Li,1))

mat_Pb84Li15 = make_materials(0.6, 'Pb84.2Li15.8', 500)
traces.append(generate_material_trace(mat_Pb84Li15,1))

mat_F2Li2BeF2 = make_materials(0.6, 'F2Li2BeF2', 500)
traces.append(generate_material_trace(mat_F2Li2BeF2,1))

mat_Li4SiO4 = make_materials(0.6, 'Li4SiO4', 500)
traces.append(generate_material_trace(mat_Li4SiO4,1))


mat_Li = make_materials(0.6, 'Li', 500)
traces.append(generate_material_trace(mat_Li,205))

mat_Pb84Li15 = make_materials(0.6, 'Pb84.2Li15.8', 500)
traces.append(generate_material_trace(mat_Pb84Li15,205))

mat_F2Li2BeF2 = make_materials(0.6, 'F2Li2BeF2', 500)
traces.append(generate_material_trace(mat_F2Li2BeF2,205))

mat_Li4SiO4 = make_materials(0.6, 'Li4SiO4', 500)
traces.append(generate_material_trace(mat_Li4SiO4,205))





layout = {'title':'Element cross sections',
          'xaxis':{'title':'Energy (eV)',
                   #'range':(1e-10,14.1e6), 
                   'type':'log'
                  },
          'yaxis':{'title':'Macroscopic Cross Section (1/cm2)',
                   'type':'log'
                  },
         }

plot({'data':traces,
      'layout':layout})




