# %% [markdown]
# ---
# title: Mixing materials
# ---

# %% [markdown]
# To simplify a neutronics model it is common to combine regions and their materials. For example, cooling channels are often combined with the structural material which reduces the complexity of the model and makes the simulation faster. 
#
# There are several different ways of making mixed materials based on the methods we have seen in Parts 1 to 4.
#
# | Material type | Combinations | Mixing Method |
# |:-:|:-:|:-:|
# | code block 1 | openmc.Material() + openmc.Material() | openmc.Material.mix_materials() |
# | code block 2 | openmc.Material() + nmm.Material() | openmc.Material.mix_materials() |
# | code block 3 | nmm.Material() + nmm.Material() | openmc.Material.mix_materials() |
# | code block 4 | openmc.Material() + openmc.Material() | nmm.MultiMaterial() |
# | code block 5 | openmc.Material() + nmm.Material() | nmm.MultiMaterial() |
# | code block 6 | nmm.Material() + nmm.Material() | nmm.MultiMaterial() |
#
# Personally I use a combination of these depending on the task. The benefit of using the neutronics_material_maker is that we can use a standard material definition and density is calculated automatically (as a function of pressure, temperature and enrichment), but this is not always required.
#
# This task allows users to make mixed materials using OpenMC and the Neutronics Material Maker.

# %% [markdown]
# First import packages needed and configure the OpenMC nuclear data path

# %%
import neutronics_material_maker as nmm
import openmc
from pathlib import Path
# Setting the cross section path to the correct location in the docker image.
# If you are running this outside the docker image you will have to change this path to your local cross section path.
openmc.config['cross_sections'] = Path.home() / 'nuclear_data' / 'cross_sections.xml'

# %% [markdown]
# ## Code block 1
#
# This first code block is an example of making a mixed material using the native OpenMC mix_materials method with two OpenMC materials.
#
# | Material type | Combinations | Mixing Method |
# |:-:|:-:|:-:|
# | code block 1 | openmc.Material() + openmc.Material() | openmc.Material.mix_materials() |

# %%
steel_mat = openmc.Material()
steel_mat.add_element('Fe', 0.975)
steel_mat.add_element('C', 0.025)
steel_mat.set_density('g/cm3', 7.7)

h2o_mat = openmc.Material()
h2o_mat.add_elements_from_formula('H2O')
h2o_mat.set_density('g/cm3', 1.)

mixed_mat = openmc.Material.mix_materials(
    materials=[
        steel_mat,
        h2o_mat,
        ],
    fracs=[0.7, 0.3], # list of combination fractions for each material
    percent_type='vo') # combination fraction type is by volume

mixed_mat

# %% [markdown]
# ## Code block 2
#
# This code block is an example of making a mixed material using the native OpenMC mix_materials method with an OpenMC material and a neutronics_material_maker material.
#
# | Material type | Combinations | Mixing Method |
# |:-:|:-:|:-:|
# | code block 2 | openmc.Material() + nmm.Material() | openmc.Material.mix_materials() |

# %%
steel_mat = openmc.Material()
steel_mat.add_element('Fe', 0.975)
steel_mat.add_element('C', 0.025)
steel_mat.set_density('g/cm3', 7.7)

h2o_mat = nmm.Material.from_library(
    'H2O',
    temperature=500, # K
    pressure=8e4     # Pa
).openmc_material

mixed_mat = openmc.Material.mix_materials(
    materials=[                 # list of neutronics materials
        steel_mat,
        h2o_mat],
    fracs=[0.7, 0.3],           # list of combination fractions for each neutronics material
    percent_type='vo')          # combination fraction type

mixed_mat

# %% [markdown]
# ## Code block 3
#
# This next code block is an example of making a mixed material using the native OpenMC mix_materials method with two neutronics_material_maker materials.
#
# | Material type | Combinations | Mixing Method |
# |:-:|:-:|:-:|
# | code block 3 | nmm.Material() + nmm.Material() | openmc.Material.mix_materials() |

# %%
steel_mat = nmm.Material.from_library('a36_steel').openmc_material

h2o_mat = nmm.Material.from_library(
    'H2O',
    temperature=500, # K
    pressure=8e4     # Pa
).openmc_material

mixed_mat = openmc.Material.mix_materials(
    materials=[                 # list of neutronics materials
        steel_mat,
        h2o_mat],
    fracs=[0.7, 0.3],           # list of combination fractions for each neutronics material
    percent_type='vo')          # combination fraction type

mixed_mat

# %% [markdown]
# ## Code block 4
#
# This code block is an example of making a mixed material using the neutronics_material_maker MultiMaterial class with two OpenMC materials.
#
# | Material type | Combinations | Mixing Method |
# |:-:|:-:|:-:|
# | code block 4 | openmc.Material() + openmc.Material() | nmm.MultiMaterial() |

# %%
steel_mat = openmc.Material()
steel_mat.add_element('Fe', 0.975)
steel_mat.add_element('C', 0.025)
steel_mat.set_density('g/cm3', 7.7)

h2o_mat = openmc.Material()
h2o_mat.add_elements_from_formula('H2O')
h2o_mat.set_density('g/cm3', 1.)

mixed_mat = nmm.Material.from_mixture(
    materials=[
        steel_mat,
        h2o_mat
    ],
    fracs=[0.7, 0.3],           # list of combination fractions for each neutronics material
    percent_type='vo')          # combination fraction type

mixed_mat.openmc_material   # returns the OpenMC-compatible version of the nmm.MultiMaterial

# %% [markdown]
# ## Code block 5
#
# The next code block is an example of making a mixed material using the neutronics_material_maker MultiMaterial class with an OpenMC and a neutronics_material_maker material.
#
# | Material type | Combinations | Mixing Method |
# |:-:|:-:|:-:|
# | code block 5 | openmc.Material() + nmm.Material() | nmm.MultiMaterial() |

# %%
steel_mat = openmc.Material()
steel_mat.add_element('Fe', 0.975)
steel_mat.add_element('C', 0.025)
steel_mat.set_density('g/cm3', 7.7)

h2o_mat = nmm.Material.from_library(
    'H2O',
    temperature=700, # K
    pressure=8e4     # Pa
).openmc_material

mixed_mat = nmm.Material.from_mixture(
    name='mixed_material',  # name of homogeneous material
    materials=[
        steel_mat,
        h2o_mat
    ],
    fracs=[0.7, 0.3],           # list of combination fractions for each neutronics material
    percent_type='vo')          # combination fraction type

mixed_mat.openmc_material   # returns the OpenMC-compatible version of the nmm.MultiMaterial

# %% [markdown]
# ## Code block 6
#
# Finally, this last code block is an example of making a mixed material using the neutronics_material_maker MultiMaterial class with two neutronics_material_maker materials.
#
# | Material type | Combinations | Mixing Method |
# |:-:|:-:|:-:|
# | code block 6 | nmm.Material() + nmm.Material() | nmm.MultiMaterial() |

# %%
steel_mat = nmm.Material.from_library('a36_steel').openmc_material

h2o_mat = nmm.Material.from_library(
    name='H2O',
    temperature=500, # K
    pressure=8e4     # Pa
).openmc_material

mixed_mat = nmm.Material.from_mixture(
    name='mixed_material',  # name of homogeneous material
    materials=[
        steel_mat,
        h2o_mat
    ],
    fracs=[0.7, 0.3],           # list of combination fractions for each neutronics material
    percent_type='vo')          # combination fraction type

mixed_mat.openmc_material

# %% [markdown]
# **Learning Outcomes for Part 5:**
#
# - Mixed materials can be created using in-built OpenMC features or the neutronics material maker.
# - The mix fraction of each material will have an impact on the overall properties of the mixed material.
