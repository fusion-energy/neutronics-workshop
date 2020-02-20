
import openmc
import numpy as np
import plotly.graph_objs as go
from neutronics_material_maker import Material, MultiMaterial

# learn how to use new MultiMaterial function
# check that packing_fraction gets propagated through to the homogenised materials for both MultiMaterial and mix_materials


# # remember that these do not have to be neutronics materials passed
# test_material = MultiMaterial(material_name = 'test_material',
#                               materials = [
#                                   Material('H2O', temperature_in_C=25, pressure_in_Pa=100000),
#                                   Material('Li4SiO4')
#                               ],
#                               fracs = [0.5, 0.5],
#                               percent_type = 'vo').neutronics_material

# perform same test as mix_materials

# water_fractions = np.linspace(0., 1., 20)

# water_densities = [MultiMaterial(material_name = 'test_material',
#                                  materials = [
#                                     Material('H2O', temperature_in_C=25, pressure_in_Pa=100000),
#                                     Material('Li4SiO4')
#                                  ],
#                                  fracs = [
#                                      water_fraction,
#                                      (1-water_fraction)
#                                  ],
#                                  percent_type = 'vo').neutronics_material.density for water_fraction in water_fractions]

# fig = go.Figure()
# fig.add_trace(go.Scatter(x=water_fractions,
#                          y=water_densities,
#                          mode='lines+markers'))
# fig.update_layout(title='title',
#                   xaxis={'title': 'title'},
#                   yaxis={'title': 'title'})
# # fig.show()

# this shows that the MultiMaterial function works the same as the mix_materials function



# Don't think this is working correctly with multimaterial
packing_fractions = np.linspace(0., 1., 20)
material_densities = [MultiMaterial(material_name = 'test_material',
                                    materials = [
                                        Material('H2O', temperature_in_C=25, pressure_in_Pa=100000),
                                        Material('Li4SiO4', packing_fraction=packing_fraction)
                                    ],
                                    fracs = [
                                        0.5,
                                        0.5
                                    ],
                                    percent_type = 'vo').neutronics_material.density for packing_fraction in packing_fractions]

fig = go.Figure()
fig.add_trace(go.Scatter(x=packing_fractions,
                         y=material_densities,
                         mode='lines+markers'))
fig.update_layout(title='Density vs Packing Fraction for a MultiMaterial',
                  xaxis={'title': 'Li4SiO4 packing fraction'},
                  yaxis={'title': 'MultiMaterial density'})
fig.show()



# Going to test with mix_materials to see if we get the same answer
packing_fractions = np.linspace(0., 1., 20)
material_densities = [openmc.Material.mix_materials(name = 'test_material',
                                                    materials = [
                                                        Material('H2O', temperature_in_C=25, pressure_in_Pa=100000).neutronics_material,
                                                        Material('Li4SiO4', packing_fraction=packing_fraction).neutronics_material
                                                    ],
                                                    fracs = [
                                                        0.5, 
                                                        0.5
                                                    ],
                                                    percent_type = 'vo').density for packing_fraction in packing_fractions]

fig = go.Figure()
fig.add_trace(go.Scatter(x=packing_fractions,
                         y=material_densities,
                         mode='lines+markers'))
fig.update_layout(title='Density vs Packing Fraction for a mix_material',
                  xaxis={'title': 'Li4SiO4 packing fraction'},
                  yaxis={'title': 'Mix_material density'})
fig.show()