# %% [markdown]
# ---
# title: Plotting element cross sections
# ---

# %% [markdown]
# As shown in Part 1, OpenMC is able to plot neutron interaction cross sections for specific isotopes. However, we can also do the same for elements.
#
# This task allows users to plot neutron interaction cross sections for specific elements using OpenMC.
#
# To plot elemental cross sections, the cross sections of each stable isotope of the element are combined.

# %% [markdown]
# First import OpenMC and configure the nuclear data path

# %%
import openmc
from pathlib import Path
# Setting the cross section path to the correct location in the docker image.
# If you are running this outside the docker image you will have to change this path to your local cross section path.
openmc.config['cross_sections'] = Path.home() / 'nuclear_data' / 'cross_sections.xml'

# %% [markdown]
# This first code block plots the (n,2n) neutron multiplication cross section for elements up to Iron.

# %%
import openmc
import matplotlib.pyplot as plt

# we pass in a blank axis as we want to modify it afterwards
fig, ax = plt.subplots()

fig = openmc.plotter.plot_xs(
    axis=ax,
    reactions = {
        "H": ["(n,2n)"],
        "He": ["(n,2n)"],
        "Li": ["(n,2n)"],
        "Be": ["(n,2n)"],
        "B": ["(n,2n)"],
        "C": ["(n,2n)"],
        "N": ["(n,2n)"],
        "O": ["(n,2n)"],
        "F": ["(n,2n)"],
        "Ne": ["(n,2n)"],
        "Na": ["(n,2n)"],
        "Mg": ["(n,2n)"],
        "Al": ["(n,2n)"],
        "Si": ["(n,2n)"],
        "Cl": ["(n,2n)"],
        "Ar": ["(n,2n)"],
        "K": ["(n,2n)"],
        "Ca": ["(n,2n)"],
        "Sc": ["(n,2n)"],
        "Ti": ["(n,2n)"],
        "V": ["(n,2n)"],
        "Cr": ["(n,2n)"],
        "Mn": ["(n,2n)"],
        "Fe": ["(n,2n)"],
    }
)
ax.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.0)
# modify the axis afterwards to make the data clearer
ax.set_xscale('linear')
ax.set_yscale('linear')
ax.set_xlim(0, 15e6)  # set the x axis limits from 0 to 15MeV

plt.show()

# %% [markdown]
# Tritium production is another important reaction in fusion as it affects the rate at which tritium can be bred. When designing breeder blankets we need to use materials which maximise both neutron multiplication AND tritium production.
#
# The next code block plots the (n,Xt) tritium production reaction for all elements.

# %%
# we pass in a blank axis as we want to modify it afterwards
fig, ax = plt.subplots()

fig = openmc.plotter.plot_xs(
    axis=ax,
    reactions = {
        "H": ["(n,Xt)"],
        "He": ["(n,Xt)"],
        "Li": ["(n,Xt)"],
        "Be": ["(n,Xt)"],
        "B": ["(n,Xt)"],
        "C": ["(n,Xt)"],
        "N": ["(n,Xt)"],
        "O": ["(n,Xt)"],
        "F": ["(n,Xt)"],
        "Ne": ["(n,Xt)"],
        "Na": ["(n,Xt)"],
        "Mg": ["(n,Xt)"],
        "Al": ["(n,Xt)"],
        "Si": ["(n,Xt)"],
        "Cl": ["(n,Xt)"],
        "Ar": ["(n,Xt)"],
        "K": ["(n,Xt)"],
        "Ca": ["(n,Xt)"],
        "Sc": ["(n,Xt)"],
        "Ti": ["(n,Xt)"],
        "V": ["(n,Xt)"],
        "Cr": ["(n,Xt)"],
        "Mn": ["(n,Xt)"],
        "Fe": ["(n,Xt)"],
    }
)

# modify the axis afterwards to make the data clearer
ax.set_xscale('linear')
ax.set_yscale('log')
ax.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.0)
ax.set_xlim(0, 15e6)  # set the x axis limits from 0 to 15MeV

plt.show()

# %% [markdown]
# Lithium is the typical candidate tritium breeder material used in D-T fusion reactor designs. 
#
# The graph shows that Lithium has a high (n,Xt) cross section for low energy neutrons which decreases as neutron energy increases.

# %% [markdown]
# **Learning Outcomes for Part 2:**
# - OpenMC can be used to plot interaction cross sections for specific elements.
# - Tritium production is an important reaction to consider when selecting a breeder material.
# - Lithium is a good material for tritium production.
