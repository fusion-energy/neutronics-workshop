
import openmc
import numpy as np
import plotly.graph_objs as go
from neutronics_material_maker import Material

# Materials can also be made by combining other materials

# Passing neutronics materials to the mix_materials function produces materials according to specified fractions

# for ease, the following example uses the neutronics_material_maker to produce the neutronics materials


# Here is am example of enriched Li4SiO4 with Helium pruge gas at atmospheric pressure, this is a typical material for the HCPB blanket design

mixed_helium_Li4SiO4 = openmc.Material.mix_materials(name = 'mixed_water_Li4SiO4',
                                                    materials = [
                                                        Material('He', temperature_in_C=500, pressure_in_Pa=100000).neutronics_material,
                                                        Material('Li4SiO4', enrichment_fraction = 0.6).neutronics_material
                                                    ],
                                                    fracs = [
                                                        0.36,
                                                        0.64
                                                    ],
                                                    percent_type='vo')
print(mixed_helium_Li4SiO4)
# fracs specifies the proportion of each material in the mixed material
# percent_type specifies the proportion type. vo = volume percent, wo = weight percent, ao = atom percent


# we can show how changing the fractions of each material varies the properties of the homogenised material

# water density 
print(Material('H2O', temperature_in_C=25, pressure_in_Pa=100000).neutronics_material.density)
# Li4SiO4 density
print(Material('Li4SiO4').neutronics_material.density)

water_fractions = np.linspace(0., 1., 20)

mixed_material_densities = [openmc.Material.mix_materials(name = 'mixed_material',
                                                        materials = [
                                                            Material('H2O', temperature_in_C=25, pressure_in_Pa=100000).neutronics_material,
                                                            Material('WC').neutronics_material
                                                        ],
                                                        fracs = [
                                                            water_fraction,
                                                            (1 - water_fraction)
                                                        ],
                                                        percent_type='vo').density for water_fraction in water_fractions]

fig = go.Figure()
fig.add_trace(go.Scatter(x=water_fractions,
                         y=mixed_material_densities,
                         mode='lines+markers'))
fig.update_layout(
    title='Mixed material density as a function of water fraction',
    xaxis={'title': 'Water fraction'},
    yaxis={'title': 'Density (g/cm3)'}
)
fig.show()

# as we can see, when water fraction = 0, material made up completely of Li4SiO4, so has the density of Li4SiO4
# as water fraction increases, proportion of Li4SiO4 replaced by water which is less dense, so reduces in density
# eventually, completely made up of water so just has the density of water
