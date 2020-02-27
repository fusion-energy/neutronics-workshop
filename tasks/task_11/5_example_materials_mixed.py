
import openmc
import numpy as np
import plotly.graph_objs as go
from neutronics_material_maker import Material, MultiMaterial


helium = Material('He', temperature_in_C=500, pressure_in_Pa=100000)
Li4SiO4 = Material('Li4SiO4', enrichment_fraction=0.6)

mixed_helium_Li4SiO4 = MultiMaterial(material_name='mixed_helium_Li4SiO4',   # name of homogeneous material
                                     materials=[helium, Li4SiO4],   # list of material objects (NOT neutronics materials)
                                     fracs=[0.36, 0.64],   # list of combination fractions for each material object
                                     percent_type='vo')   # combination fraction type
print(mixed_helium_Li4SiO4.neutronics_material)







# we can show how changing the fractions of each material varies the properties of the homogenised material

# We will use a combined material of tungsten carbide and water

# Tungsten carbide density
print(Material('WC').neutronics_material.density)
# Water density
print(Material('H2O', temperature_in_C=25, pressure_in_Pa=100000).neutronics_material.density)

water_fractions = np.linspace(0., 1., 20)

mixed_water_WC_densities = [openmc.Material.mix_materials(name = 'mixed_water_WC',
                                                          materials = [
                                                              Material('WC').neutronics_material,
                                                              Material('H2O', temperature_in_C=25, pressure_in_Pa=100000).neutronics_material
                                                          ],
                                                          fracs = [
                                                              water_fraction,
                                                              (1-water_fraction)
                                                          ],
                                                          percent_type = 'vo').density for water_fraction in water_fractions]

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
