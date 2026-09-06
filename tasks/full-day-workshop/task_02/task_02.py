# %% [markdown]
# ---
# title: Making materials from elements
# ---

# %% [markdown]
# As we saw in Part 1, materials can be defined in OpenMC using isotopes. However, materials can also be made from elements - this is more concise and still supports isotopic enrichment.
#
# This task allows users to create different materials from elements using OpenMC.

# %% [markdown]
# First import OpenMC and configure the nuclear data path

# %%
import openmc
from pathlib import Path
# Setting the cross section path to the correct location in the docker image.
# If you are running this outside the docker image you will have to change this path to your local cross section path.
openmc.config['cross_sections'] = Path.home() / 'nuclear_data' / 'cross_sections.xml'

# %% [markdown]
# The following code block is a simple example of creating a material (water H2O) from elements. (Note how Hydrogen and Oxygen elements have been specified rather than each specific isotope).

# %%
# Making water from elements

water_mat = openmc.Material()
water_mat.add_element('H', 2.0, percent_type='ao')
water_mat.add_element('O', 1.0, percent_type='ao')
water_mat.set_density('g/cm3', 0.99821)

water_mat

# %% [markdown]
# The next code block is an example of making a ceramic breeder material.

# %%
# Making Li4SiO4 from elements

Li4SiO4_mat = openmc.Material()
Li4SiO4_mat.add_element('Li', 4.0, percent_type='ao')
Li4SiO4_mat.add_element('Si', 1.0, percent_type='ao')
Li4SiO4_mat.add_element('O', 4.0, percent_type='ao')
Li4SiO4_mat.set_density('g/cm3', 2.32)

Li4SiO4_mat

# %% [markdown]
# It is also possible to enrich specific isotopes while still benefitting from the concise code of making materials from elements.
#
# Here is an example of making the same ceramic breeder material but this time with Li6 enrichment.

# %%
# Making enriched Li4SiO4 from elements with enrichment of Li6 enrichment

Li4SiO4_mat = openmc.Material()
Li4SiO4_mat.add_element('Li', 4.0, percent_type='ao',
                        enrichment=60,
                        enrichment_target='Li6',
                        enrichment_type='ao'
                        )
Li4SiO4_mat.add_element('Si', 1.0, percent_type='ao')
Li4SiO4_mat.add_element('O', 4.0, percent_type='ao')
Li4SiO4_mat.set_density('g/cm3', 2.32)  # this would actually be lower than 2.32 g/cm3 but this would need calculating

Li4SiO4_mat

# %% [markdown]
# In the case of materials that can be represented as a chemical formula (e.g. 'H2O', 'Li4SiO4') there is an even more concise way of making these materials by using their chemical formula.

# %%
# making Li4SiO4 from a formula

Li4SiO4_mat = openmc.Material()
Li4SiO4_mat.add_elements_from_formula('Li4SiO4')
Li4SiO4_mat

# %% [markdown]
# This add_elements_from_formula (which was added to OpenMC source code by myself) can also support enrichment.

# %%
# making Li4SiO4 from a formula with enrichment

Li4SiO4_mat = openmc.Material()
Li4SiO4_mat.add_elements_from_formula('Li4SiO4',
                        enrichment=60,
                        enrichment_target='Li6',
                        enrichment_type='ao'
                        )
Li4SiO4_mat

# %% [markdown]
# Making more detailed materials such as a low activation steel Eurofer would require about 20 elements. While this is fewer user inputs than making the material from isotopes it is still quite a lot of coding for the user. Unfortunately, they cannot be input as a chemical formula either.

# %% [markdown]
# **Learning Outcomes for Part 2:**
# - Materials can be made in OpenMC using element fractions and densities.
# - Making materials from elements is more concise than making materials from isotopes.
# - If materials can be represented as a chemical formula, OpenMC also offers a way to construct those materials from that.
# - Making materials from elements also supports isotopic enrichment.
