
import openmc
from neutronics_material_maker import Material 

# making materials using mix_materials function in OpenMC

# can make a material mixed from other materials using the mix_materials function
# this function must be passed OpenMC/neutronics-type materials
# for ease, we will combine the neutronics_material_maker to make neutronics materials

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
