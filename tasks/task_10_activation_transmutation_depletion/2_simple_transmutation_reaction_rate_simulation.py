# %% [markdown]
# ---
# title: Simple transmutation reaction rate simulation
# ---

# %% [markdown]
# This introductory example finds the transmutation reaction rates in a material exposed to 14 MeV neutrons.
#
# When a neutron interacts with a nucleus it can cause transmutation — changing the element or isotope. Common reactions include (n,2n), (n,p), (n,alpha), etc. Each reaction changes the atomic number and/or mass number of the target nucleus.
#
# This simulation tallies all possible transmutation reactions for every nuclide in an iron material and reports the reaction rates per source neutron, along with the resulting product nuclides.
#
# This is a simplified introduction to the topic — for real inventory tracking, decay chains and material evolution over time would also need to be considered (see the following examples in this task).
#
# First import the required packages.

# %%
import re
from pathlib import Path

import openmc
from openmc.data import ATOMIC_NUMBER, ATOMIC_SYMBOL, DADZ
from openmc.deplete.chain import REACTIONS

# Setting the cross section path to the correct location in the docker image.
# If you are running this outside the docker image you will have to change this path to your local cross section path.
openmc.config['cross_sections'] = Path.home() / 'nuclear_data' / 'cross_sections.xml'

# %% [markdown]
# ## Material
#
# A simple iron material. All natural isotopes of iron will be included and each will have its transmutation reactions tallied.

# %%
material = openmc.Material()
material.add_element("Fe", 1)
material.set_density("g/cm3", 7.7)
materials = openmc.Materials([material])

# %% [markdown]
# ## Geometry
#
# A single iron sphere with a vacuum boundary.

# %%
surface = openmc.Sphere(r=500, boundary_type="vacuum")
cell = openmc.Cell(region=-surface)
cell.fill = material
geometry = openmc.Geometry([cell])

# %% [markdown]
# ## Settings and source
#
# A 14 MeV (D-T) point source at the origin.

# %%
settings = openmc.Settings()
settings.batches = 10
settings.inactive = 0
settings.particles = 500
settings.run_mode = "fixed source"

my_source = openmc.IndependentSource()
my_source.energy = openmc.stats.Discrete([14e6], [1])
settings.source = my_source

# %% [markdown]
# ## Tallies
#
# We tally every possible transmutation reaction for every nuclide present in the iron material. The list of reactions comes from `openmc.deplete.chain.REACTIONS`, which includes reactions like (n,2n), (n,p), (n,alpha), (n,gamma), etc.

# %%
reactions = list(REACTIONS.keys())

rr_tally = openmc.Tally(name="RR")
rr_tally.nuclides = material.get_nuclides()
rr_tally.scores = reactions
tallies = openmc.Tallies([rr_tally])

# %% [markdown]
# ## Run the simulation

# %%
model = openmc.Model(geometry, materials, settings, tallies)
sp_filename = model.run()

# %% [markdown]
# ## Process results
#
# We extract the tally results as a pandas DataFrame, sort by reaction rate (highest first), and then for each non-zero reaction we work out what product nuclide is created.
#
# Each reaction has an entry in `openmc.data.DADZ` — a tuple giving the change in mass number (dA) and atomic number (dZ). By applying these deltas to the target nuclide we can identify the transmutation product.

# %%
with openmc.StatePoint(sp_filename) as sp:

    tbr_tally = sp.get_tally(name="RR")

    df = tbr_tally.get_pandas_dataframe()
    df = df.sort_values("mean", ascending=False)

    print("Reaction rates per source neutron")
    for index, row in df.iterrows():
        if row["mean"] != 0.0:
            score = row["score"]
            nuclide = row["nuclide"]

            # delta atomic number (dA) and delta mass number (dZ)
            delta_A, delta_Z = DADZ[score]

            # extract element symbol and mass number from nuclide name
            element_symbol = re.split(r"(\d+)", nuclide)[0]
            neutron_plus_proton_number = int(re.split(r"(\d+)", nuclide)[1])

            proton_number = ATOMIC_NUMBER[element_symbol]

            # apply the reaction deltas
            new_proton_number = proton_number + delta_Z
            new_neutron_plus_proton_number = neutron_plus_proton_number + delta_A
            secondaries = REACTIONS[score].secondaries
            secondaries_str = ""
            if len(secondaries) > 0:
                secondaries_str = f"+{'+'.join(secondaries)}"

            new_element_symbol = ATOMIC_SYMBOL[new_proton_number]

            print(
                f"{element_symbol}{neutron_plus_proton_number} -> {score} -> "
                f"{new_element_symbol}{new_neutron_plus_proton_number}{secondaries_str} "
                f"per source neutron {row['mean']}"
            )

# %% [markdown]
# **Learning Outcomes:**
#
# - Understanding transmutation reactions and how neutrons can change one element into another.
# - Tallying all possible reaction channels for each nuclide in a material.
# - Using `openmc.data.DADZ` and `openmc.deplete.chain.REACTIONS` to look up reaction properties (delta A, delta Z, secondaries).
# - Post-processing tally results to identify transmutation products.
