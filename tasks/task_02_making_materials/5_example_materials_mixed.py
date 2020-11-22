
import openmc
import numpy as np
import plotly.graph_objs as go
from neutronics_material_maker import Material, MultiMaterial

# Homogeneous mixture of helium and Li4SiO4 using MultiMaterial class

# MultiMaterial class requires list of Material objects to be passed
helium = Material('He', temperature_in_C=500, pressure_in_Pa=100000)
Li4SiO4 = Material('Li4SiO4', enrichment=60)

mixed_helium_Li4SiO4 = MultiMaterial(material_name='mixed_helium_Li4SiO4',   # name of homogeneous material
                                     materials=[helium, Li4SiO4],            # list of material objects (NOT neutronics materials)
                                     fracs=[0.36, 0.64],                     # list of combination fractions for each material object
                                     percent_type='vo')                      # combination fraction type
# print(mixed_helium_Li4SiO4.openmc_material)


# Homogenous mixture of tungsten carbide and water using mix_materials function

mixed_water_WC = openmc.Material.mix_materials(name='mixed_water_WC',      # name of homogeneous material
                                               materials=[                 # list of neutronics materials
                                                   Material('WC').openmc_material,
                                                   Material('H2O', temperature_in_C=25, pressure_in_Pa=100000).openmc_material
                                               ],
                                               fracs=[0.8, 0.2],           # list of combination fractions for each neutronics material
                                               percent_type='vo')          # combination fraction type


# Demonstration of changing combination fractions of each material

print('Tungsten carbide density = ' + str(Material('WC').openmc_material.density))
print('Water density = ' + str(Material('H2O', temperature_in_C=25, pressure_in_Pa=100000).openmc_material.density))

water_fractions = np.linspace(0., 1., 20)

mixed_water_WC_densities = [openmc.Material.mix_materials(name='mixed_water_WC',
                                                          materials=[
                                                              Material('WC').openmc_material,
                                                              Material('H2O', temperature_in_C=25, pressure_in_Pa=100000).openmc_material
                                                          ],
                                                          fracs=[
                                                              water_fraction,
                                                              (1-water_fraction)
                                                          ],
                                                          percent_type='vo').density for water_fraction in water_fractions]

fig = go.Figure()
fig.add_trace(go.Scatter(x=water_fractions,
                         y=mixed_water_WC_densities,
                         mode='lines+markers'))
fig.update_layout(
    title='Mixed water and tungsten carbide material density as a function of water fraction',
    xaxis={'title': 'Water fraction'},
    yaxis={'title': 'Density (g/cm3)'}
)
fig.show()

# as we can see, when water fraction = 0, material made up completely of Li4SiO4, so has the density of Li4SiO4
# as water fraction increases, proportion of Li4SiO4 replaced by water which is less dense, so reduces in density
# eventually, completely made up of water so just has the density of water
