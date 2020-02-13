
import openmc
from openmc.data import *
from neutronics_material_maker import Material 
import numpy as np
from tqdm import tqdm
import plotly.graph_objs as go

# Isotopes

water_isotope = openmc.Material(name='water_isotope')
water_isotope.add_nuclide('H1', 2*NATURAL_ABUNDANCE['H1'], percent_type='ao')
water_isotope.add_nuclide('H2', 2*NATURAL_ABUNDANCE['H2'], percent_type='ao')
water_isotope.add_nuclide('O16', NATURAL_ABUNDANCE['O16'], percent_type='ao')
water_isotope.add_nuclide('O17', NATURAL_ABUNDANCE['O17'], percent_type='ao')
water_isotope.add_nuclide('O18', NATURAL_ABUNDANCE['O18'], percent_type='ao')
water_isotope.set_density('g/cm3', 0.99821)

Li4SiO4_isotope = openmc.Material(name='Li4SiO4_isotope')
Li4SiO4_isotope.add_nuclide('Li6', 4*NATURAL_ABUNDANCE['Li6'], percent_type='ao')
Li4SiO4_isotope.add_nuclide('Li7', 4*NATURAL_ABUNDANCE['Li7'], percent_type='ao')
Li4SiO4_isotope.add_nuclide('Si28', NATURAL_ABUNDANCE['Si28'], percent_type='ao')
Li4SiO4_isotope.add_nuclide('Si29', NATURAL_ABUNDANCE['Si29'], percent_type='ao')
Li4SiO4_isotope.add_nuclide('Si30', NATURAL_ABUNDANCE['Si30'], percent_type='ao')
Li4SiO4_isotope.add_nuclide('O16', 4*NATURAL_ABUNDANCE['O16'], percent_type='ao')
Li4SiO4_isotope.add_nuclide('O17', 4*NATURAL_ABUNDANCE['O17'], percent_type='ao')
Li4SiO4_isotope.add_nuclide('O18', 4*NATURAL_ABUNDANCE['O18'], percent_type='ao')
Li4SiO4_isotope.set_density('g/cm3', 2.32)

# Elements

water_element = openmc.Material(name='water_element')
water_element.add_element('H', 2.0, percent_type='ao')
water_element.add_element('O', 1.0, percent_type='ao')
water_element.set_density('g/cm3', 0.99821)

Li4SiO4_element = openmc.Material(name='Li4SiO4_element')
Li4SiO4_element.add_element('Li', 4.0, percent_type='ao')
Li4SiO4_element.add_element('Si', 1.0, percent_type='ao')
Li4SiO4_element.add_element('O', 4.0, percent_type='ao')
Li4SiO4_element.set_density('g/cm3', 2.32)

# Material maker

water_material_maker = Material('H2O').neutronics_material

Li4SiO4_material_maker = Material('Li4SiO4').neutronics_material

# this function can also take arguments such as enrichment fraction, packing fraction

# enriched_Li4SiO4 = Material('Li4SiO4', enrichment_fraction=0.6, packing_fraction=0.8).neutronics_material

# helium and water can also take the arguments
# temperature_in_C
# temperature_in_K
# pressure_in_Pa
# water_test = Material('H2O', temperature_in_C=60, pressure_in_Pa=value)

# showing how parameters change

# for some reason, still doesn't expect pressure_in_Pa as an argument

temperatures = np.linspace(0., 100., 11)
pressures = np.linspace(0., 1000., 11)
densities = [Material('H2O', temperature_in_C=temperature).neutronics_material.density for temperature in tqdm(temperatures)]
pressures = [Material('H2O', pressure_in_Pa=pressure).neutronics_material.density for pressure in tqdm(pressures)]

fig = go.Figure()
fig.add_trace(go.Scatter(x = pressures,
                         y = densities,
                         mode = 'lines+markers'))
fig.update_layout(
    title = 'Water density as a function of pressure',
    xaxis = {'title': 'Pressure(Pa)'},
    yaxis = {'title': 'Density'}
)
fig.show()


# Mixed material
# this function needs to be passed openmc-type materials. for ease, we have used the Material() and converted to neutronics_material.
# again, these materials can accept arguments such as enrichment, packing fraction and temperature.

mixed_water_Li4SiO4 = openmc.Material.mix_materials(name='mixed_water_Li4SiO4',
                                                    materials = [
                                                        Material('H2O').neutronics_material,
                                                        Material('Li4SiO4').neutronics_material
                                                    ],
                                                    fracs = [
                                                        0.5,
                                                        0.5
                                                    ],
                                                    percent_type = 'vo')
