# %% [markdown]
# ---
# title: Making materials from isotopes
# ---

# %% [markdown]
# To carry out a neutronics simulation material definitions are needed.
#
# In OpenMC, materials can be defined using isotope fractions and densities. I.e. each isotope in the material is defined along with the overall material density.
#
# This task allows users to create different materials from isotopes using OpenMC. 

# %% [markdown]
# First import OpenMC and configure the nuclear data path

# %%
import openmc
from pathlib import Path
# Setting the cross section path to the correct location in the docker image.
# If you are running this outside the docker image you will have to change this path to your local cross section path.
openmc.config['cross_sections'] = Path.home() / 'nuclear_data' / 'cross_sections.xml'

# %% [markdown]
# The following code block is a simple example of creating a material (water H2O) from isotopes.
#
# The natural abundances of each isotope in the material have been found using the NIST website: https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl?ele=

# %%
water_mat = openmc.Material()

# add each isotope with their relative abundance to material object
# note that H20 requires hydrogen to be multiplied by 2
water_mat.add_nuclide('H1', 2.*0.999885, percent_type='ao')
water_mat.add_nuclide('H2', 2.*0.000115, percent_type='ao')
water_mat.add_nuclide('O16', 0.99757, percent_type='ao')
water_mat.add_nuclide('O17', 0.00038, percent_type='ao')
water_mat.add_nuclide('O18', 0.00205, percent_type='ao')

# set material density
water_mat.set_density('g/cm3', 0.99821)

water_mat

# %% [markdown]
# Looking up natural abundances on a website can take time and is error prone - there is a better way.
#
# Instead, OpenMC can find the natural abundance of isotopes from internal data using the [NATURAL_ABUNDANCE](https://github.com/openmc-dev/openmc/blob/develop/openmc/data/data.py) dictionary in OpenMC.
#
# The next code block is an example of creating a material (water H2O) from isotopes but this time using the inbuilt NATURAL_ABUMDANCE dictionary to find the natural abundances of each isotope.

# %%
from openmc.data import NATURAL_ABUNDANCE  # this imports the NATURAL_ABUNDANCE dictionary

water_mat = openmc.Material()

# add each isotope with their relative abundance to material object
# note that H20 requires hydrogen to be multiplied by 2
water_mat.add_nuclide('H1', 2.0*NATURAL_ABUNDANCE['H1'], percent_type='ao')
water_mat.add_nuclide('H2', 2.0*NATURAL_ABUNDANCE['H2'], percent_type='ao')
water_mat.add_nuclide('O16', NATURAL_ABUNDANCE['O16'], percent_type='ao')
water_mat.add_nuclide('O17', NATURAL_ABUNDANCE['O17'], percent_type='ao')
water_mat.add_nuclide('O18', NATURAL_ABUNDANCE['O18'], percent_type='ao')

# set material density
water_mat.set_density('g/cm3', 0.99821)

water_mat

# %% [markdown]
# One of the reasons that we might want to define materials from isotopes is so that we can specify the enrichment of particular isotopes.
#
# The following example makes Li4SiO4 with an enriched Li6 content.
#
# This is the typical lithium ceramic and enrichment level found in the HCPB design.

# %%
# Making enriched Li4SiO4 from isotopes

enrichment_fraction = 0.6

enriched_Li4SiO4_isotope = openmc.Material()
enriched_Li4SiO4_isotope.add_nuclide('Li6', 4.0*enrichment_fraction, percent_type='ao')
enriched_Li4SiO4_isotope.add_nuclide('Li7', 4.0*(1-enrichment_fraction), percent_type='ao')
enriched_Li4SiO4_isotope.add_nuclide('Si28', NATURAL_ABUNDANCE['Si28'], percent_type='ao')
enriched_Li4SiO4_isotope.add_nuclide('Si29', NATURAL_ABUNDANCE['Si29'], percent_type='ao')
enriched_Li4SiO4_isotope.add_nuclide('Si30', NATURAL_ABUNDANCE['Si30'], percent_type='ao')
enriched_Li4SiO4_isotope.add_nuclide('O16', 4.0*NATURAL_ABUNDANCE['O16'], percent_type='ao')
enriched_Li4SiO4_isotope.add_nuclide('O17', 4.0*NATURAL_ABUNDANCE['O17'], percent_type='ao')
enriched_Li4SiO4_isotope.add_nuclide('O18', 4.0*NATURAL_ABUNDANCE['O18'], percent_type='ao')
enriched_Li4SiO4_isotope.set_density('g/cm3', 2.32)  # this would be lower than 2.32 but this would need calculating

enriched_Li4SiO4_isotope

# %% [markdown]
# Making more detailed materials such as a low activation steel Eurofer using this method would require over 50 isotopes to be specified. This can become quite a lot of coding for the user.
#
# Luckily, this is just the start of making materials - there are more methods available which are described in the following tasks.

# %% [markdown]
# **Learning Outcomes from Part 1:**
# - Materials can be made in OpenMC using isotope fractions and densities.
# - Making materials from isotopes allows the enrichment of particular isotopes to be specified.
