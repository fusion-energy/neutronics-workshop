# %% [markdown]
# ---
# title: Making materials from components
# ---

# %% [markdown]
# To carry out a neutronics simulation material definitions are needed.
#
# In OpenMC, materials can be defined using components that define elements, nuclides and their fractions.
#
# This task allows users to create different materials from components using OpenMC. 

# %% [markdown]
# First import OpenMC and configure the nuclear data path

# %%
import openmc
from pathlib import Path
# Setting the cross section path to the correct location in the docker image.
# If you are running this outside the docker image you will have to change this path to your local cross section path.
openmc.config['cross_sections'] = Path.home() / 'nuclear_data' / 'cross_sections.xml'

# %% [markdown]
# The following code block is a simple example of creating a material (water H2O) from components.
#
# This allows one to make a material in a single function call.

# %%
import openmc


water_mat = openmc.Material(
    name="water",
    components={'H': 2.0, 'O': 1.0},
    percent_type="ao",
    density=0.99821,
    density_units='g/cm3'
)

water_mat

# %% [markdown]
# Materials can also be made from nuclides as well as elements. For example in this material we specify both nuclides and elements.

# %%
heavy_water_mat = openmc.Material(
    name="water",
    components={'H1': 1.0, 'H2':1.0, 'O': 1.0},
    percent_type="ao",
    density=1.11,
    density_units='g/cm3'
)

heavy_water_mat

# %% [markdown]
# More complicated keyword dictionaries can be made with other material keywords such as enrichment.

# %%
components = {
    'Li': {'percent': 4, 'enrichment': 60.0, 'enrichment_target': 'Li7'},
    'Si': 1.0,
    'O': 4
}

enriched_Li4SiO4 = openmc.Material(
    name="water",
    components=components,
    percent_type="ao",
    density=1.11,
    density_units='g/cm3'
)

enriched_Li4SiO4

# %% [markdown]
# Dictionary expansion can also be used. This is where a ** is placed before a dictionary and it gets expanded to keyword args. This can be use full when making a material from a dictionary

# %%
mat_from_dict = openmc.Material(
    **{
        "components": {
            "H": 0.1,
            "H2": 1.0,
            "He": 4
        },
        "material_id": 1,
        "name": "neutron_star",
        "percent_type": "ao",
        "density": 1e17,
        "density_units": "kg/m3",
    }
)
mat_from_dict

# %% [markdown]
# **Learning Outcomes from Part 6:**
# - Materials can be made in OpenMC using components and keyword args in a single function call.
