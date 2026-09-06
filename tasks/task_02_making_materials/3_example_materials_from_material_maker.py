# %% [markdown]
# ---
# title: Making materials from a library
# ---

# %% [markdown]
# As we have seen in Parts 1 and 2, materials can be defined in OpenMC using isotopes and elements.
#
# The problem with this is that to construct some materials the user would be required to input many lines of code. As a result, there is opportunity for errors and the code becomes harder to maintain.
#
# Wouldn't it be great if someone had made a nice collection of the material definitions used in fusion neutronics that could simply be used without having to remember all of the isotopes or elements that go into each one? It would be even better if the density was automatically adjusted to account for isotopic enrichment, temperature and pressure effects.
#
# Fortunately, there is an app for that called the Neutronics Material Maker which makes material making very convenient. Full transparency - the author of this package is also the author of this OpenMC workshop :-)
#
# Further details on this open-source Python package are available here:
# https://github.com/fusion-energy/neutronics_material_maker
# https://neutronics-material-maker.readthedocs.io/en/latest/
# https://pypi.org/project/neutronics-material-maker/
#
# This task allows users to create different materials using the Neutronics Material Maker.

# %% [markdown]
# The following code block is a simple example of importing the package and using it to create Eurofer.

# %%
# example material from the library

import neutronics_material_maker as nmm

eurofer_mat = nmm.Material.from_library('eurofer')

eurofer_mat.openmc_material

# %% [markdown]
# Some materials require additional arguments to correctly calculate material properties.
#
# Coolants such as water, helium, CO2 and others require temperature and pressure information to find the density.
#
# This code block creates H2O at a particular temperature and pressure.

# %%
# Water requires temperature and pressure arguments to be passed
water = nmm.Material.from_library('H2O', temperature=300, pressure=1e5) # temperature in K, pressure in Pa

water.openmc_material

# %% [markdown]
# Some materials can also take enrichment arguments which adjust the material density.
#
# The following code blocks create Li4SiO4 materials with different enrichments and packing fractions.

# %%
# Lithium Orthosilicate (Li4SiO4) can take arguments of 'enrichment', 'enrichment_target', 'enrichment_type' and 'packing_fraction'
# Note: for some lithium crystals, 'enrichment_target' and 'enrichment_type' are defined by default, but can be changed

default_Li4SiO4 = nmm.Material.from_library('Li4SiO4')
default_Li4SiO4.openmc_material

# %%
# the following command creates Li4SiO4 with respect to given arguments but uses the default values for enrichment_target and enrichment_type
# enrichment_target='Li6', enrichment_type='ao' defined by default

enriched_and_packed_Li4SiO4 = nmm.Material.from_library(
    'Li4SiO4',
    enrichment=60,
    packing_fraction=0.64
)   
enriched_and_packed_Li4SiO4.openmc_material

# %% [markdown]
# The Neutronics Material Maker is a powerful tool which allows complicated materials to be created easily, but what about fine tuning these materials or mixing them together? These are covered in the next parts.

# %% [markdown]
# **Learning Outcomes for Part 3:**
#
# - The Neutronics Material Maker is a python package which can be used to create neutronics materials easily.
# - The package makes it easy to account for isotopic enrichment, temperature and pressure effects.
