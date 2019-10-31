#!/usr/bin/env python3

"""example_isotope_plot.py: plots cross sections for a couple of isotopes."""

__author__      = "Jonathan Shimwell"

import openmc
from plotly import __version__
from plotly.offline import download_plotlyjs, plot
from plotly.graph_objs import Scatter, Layout


def calculate_crystal_structure_density(material,atoms_per_unit_cell,volume_of_unit_cell_cm3):
      molar_mass = material.average_molar_mass*len(material.nuclides)
      atomic_mass_unit_in_g = 1.660539040e-24
      density_g_per_cm3 = molar_mass * atomic_mass_unit_in_g * atoms_per_unit_cell / volume_of_unit_cell_cm3
      #print('density =',density_g_per_cm3)
      return density_g_per_cm3



natural_Li4SiO4 = openmc.Material()
natural_Li4SiO4.add_element('Li',4.0,percent_type='ao')
natural_Li4SiO4.add_element('Si',1.0,percent_type='ao')
natural_Li4SiO4.add_element('O',4.0,percent_type='ao')
natural_Li4SiO4.set_density('g/cm3',calculate_crystal_structure_density(natural_Li4SiO4,14,1.1543e-21))
print('natural_Li4SiO4 density',natural_Li4SiO4.density,natural_Li4SiO4.density_units)

enrichment_fraction=0.6
enriched_Li4SiO4 = openmc.Material()
enriched_Li4SiO4.add_nuclide('Li6',4.0*enrichment_fraction,percent_type='ao')
enriched_Li4SiO4.add_nuclide('Li7',4.0*(1-enrichment_fraction),percent_type='ao')
enriched_Li4SiO4.add_element('Si',1.0,percent_type='ao')
enriched_Li4SiO4.add_element('O',4.0,percent_type='ao')
enriched_Li4SiO4.set_density('g/cm3',calculate_crystal_structure_density(enriched_Li4SiO4,14,1.1543e-21))
print('enriched_Li4SiO4 density',enriched_Li4SiO4.density,enriched_Li4SiO4.density_units)

natural_Li2SiO3 = openmc.Material()
natural_Li2SiO3.add_element('Li',4.0,percent_type='ao')
natural_Li2SiO3.add_element('Si',1.0,percent_type='ao')
natural_Li2SiO3.add_element('O',4.0,percent_type='ao')
natural_Li2SiO3.set_density('g/cm3',calculate_crystal_structure_density(natural_Li2SiO3,4,0.23632e-21))
print('natural_Li2SiO3 density',natural_Li2SiO3.density,natural_Li2SiO3.density_units)

natural_Li2ZrO3 = openmc.Material()
natural_Li2ZrO3.add_element('Li',4.0,percent_type='ao')
natural_Li2ZrO3.add_element('Si',1.0,percent_type='ao')
natural_Li2ZrO3.add_element('O',4.0,percent_type='ao')
natural_Li2ZrO3.set_density('g/cm3',calculate_crystal_structure_density(natural_Li2ZrO3,4,0.24479e-21))
print('natural_Li2ZrO3 density',natural_Li2ZrO3.density,natural_Li2ZrO3.density_units)

natural_Li2TiO3 = openmc.Material()
natural_Li2TiO3.add_element('Li',4.0,percent_type='ao')
natural_Li2TiO3.add_element('Si',1.0,percent_type='ao')
natural_Li2TiO3.add_element('O',4.0,percent_type='ao')
natural_Li2TiO3.set_density('g/cm3',calculate_crystal_structure_density(natural_Li2TiO3,8,0.42701e-21))
print('natural_Li2TiO3 density',natural_Li2TiO3.density,natural_Li2TiO3.density_units)

