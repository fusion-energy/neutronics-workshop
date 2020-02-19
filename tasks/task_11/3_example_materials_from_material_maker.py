
import openmc
from neutronics_material_maker import Material 
import numpy as np
from tqdm import tqdm
import plotly.graph_objs as go

# Making water using neutronics_material_maker

# this calls a Material() object using the neutronics_material_maker
water_material_object = Material('H2O')

# this converts this Material() type object into a neutronics material that can be used in OpenMC
water_neutronics_material = Material('H2O').neutronics_material

print(type(water_material_object))
print(water_material_object)
print(type(water_neutronics_material))
print(water_neutronics_material)

# the material object also takes arguments such as enrichment fraction, packing fraction, temperature and pressure which adjust the material parameters
# look at the material class to see which arguments are permitted/required
# note. pressure_in_Pa does not currently work because the thermo package is not working

Li4SiO4_material_maker = Material('Li4SiO4').neutronics_material 

enriched_Li4SiO4_material_maker = Material('Li4SiO4', enrichment_fraction=0.6, packing_fraction=0.8).neutronics_material

water_with_temperature = Material('H2O', temperature_in_C=25).neutronics_material

# we can inspect these materials to extract information

print(water_with_temperature.density)

# because it is easy to make materials and adjust parameters, we can easily perform parameter studies

# water density as a function of temperature (think this must be at some sort of standard pressure?)
# this does not yet work

# temperatures = np.linspace(0., 1000., 11)
# water_densities = [Material('H2O', temperature_in_C=temperature).neutronics_material.density for temperature in tqdm(temperatures)]

# water_density_vs_temp_fig = go.Figure()
# water_density_vs_temp_fig.add_trace(go.Scatter(x=temperatures,
#                                                y=water_densities,
#                                                mode='lines+markers')
# )
# water_density_vs_temp_fig.update_layout(
#     title='Water density as a function of temperature',
#     xaxis={'title': 'Temperature'},
#     yaxis={'title': 'Density'}
# )
# water_density_vs_temp_fig.show()

# helium density as a function of pressure (think this must be at some sort of standard temperature?)
# this does not yet work

# pressures = np.linspace(0., 1000., 11)
# helium_densities = [Material('He', pressure_in_Pa=pressre).neutronics_material.density for pressure in tqdm(pressures)]

# helium_density_vs_pressure_fig = go.Figure()
# helium_density_vs_pressure_fig.add_trace(go.Scatter(x=pressures,
#                                                     y=helium_densities,
#                                                     mode='lines+markers')
# )
# helium_density_vs_pressure_fig.update_layout(
#     title='Helium density as a function of pressure',
#     xaxis={'title': 'Pressure'},
#     yaxis={'title': 'Density'}
# )
# helium_density_vs_pressure_fig.show()

