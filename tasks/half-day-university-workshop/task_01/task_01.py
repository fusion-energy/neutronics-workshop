# %% [markdown]
# ---
# title: Plotting isotope cross sections
# ---

# %% [markdown]
# Knowing the interaction probabilities of isotopes and materials in your model can help you understand simulation results. There are several online tools for plotting nuclear cross sections such as [www.xsplot.com](http://xsplot.com), however, OpenMC can also plot cross sections.
#
# This task allows users to plot neutron interaction cross sections for specific isotopes using OpenMC.
#
# In this first part of the task we are plotting the <b>microscopic</b> cross-section "<b>σ</b>".
#
# Microscopic cross section is the effective target area in $\mathrm{m}^2$ presented by a single nucleus to an incident neutron beam.
#
# This is used to characterize the probability of reaction between a neutron and an individual nucleus.
#
# Microscopic is often stated in units of barns where 1 barn is equal to $10^{−28}$ $\mathrm{m}^2$ 

# %% [markdown]
# First import OpenMC and configure the nuclear data path

# %%
import openmc
from pathlib import Path
# Setting the cross section path to the correct location in the docker image.
# If you are running this outside the docker image you will have to change this path to your local cross section path.
openmc.config['cross_sections'] = Path.home() / 'nuclear_data' / 'cross_sections.xml'

# %% [markdown]
# There is no abundant natural source of tritium on Earth so DT fusion reactors will probably need to be self sufficient in tritium production.
#
# Tritium is required as part of the fuel mix for deuterium (D)tritium (T) fusion reactors.
#
# Tritium production is therefore one of the most important cross section in fusion.
#
# To product sufficient tritium we need a high tritium production cross section.
#
# Neutrons from DT fusion are created with around 14.1MeV of energy, which lithium isotope offers the highest probability of tritium production at that energy?

# %% [markdown]
# The plot below uses the reaction label `(n,Xt)` — the total tritium-production cross section for each lithium isotope.
#
# In ENDF/OpenMC reaction notation:
# - `X` is a wildcard for the number of outgoing neutrons (0 or 1 in practice)
# - `t` means triton (tritium nucleus, ³H)
#
# So `(n,Xt)` combines both tritium-producing channels:
# - `(n,t)`: neutron absorbed, one triton emitted — dominant in **Li6** at thermal and 14 MeV energies
# - `(n,nt)`: neutron scattered and a triton emitted — dominant in **Li7** at high (threshold ~2.5 MeV) energies

# %%
import matplotlib.pyplot as plt

fig = openmc.plotter.plot_xs(
    reactions = {
        'Li6': ['(n,Xt)'],
        'Li7': ['(n,Xt)'],
    }
)
plt.show()

# Note the axis are log scale

# %% [markdown]
# Neutron multiplication is also an important reaction in fusion.
#
# Neutron multiplying reactions increase the number of neutrons available for tritium producing reactions.
#
# This next code block plots the neutron multiplication (n,2n) cross section of the Be and Pb isotopes.
#
# Neutron multiplication is a threshold reaction meaning it only occurs at neutron energies above a certain threshold. You should notice that the threshold energies for Be9 and Pb204 are different.
#
# Which isotope offers the lowest threshold and which isotopes offers the highest probability.

# %%
# PB (lead) and Be (beryllium) are two candidate neutron multipliers with all their isotopes

# The (n,2n) reaction means one incident neutron and two neutrons produced

# we pass in a blank axis as we want to modify it afterwards
fig, ax = plt.subplots()

fig = openmc.plotter.plot_xs(
    axis=ax,
    reactions = {
        'Be9': ['(n,2n)'],
        'Pb204': ['(n,2n)'],
        'Pb206': ['(n,2n)'],
        'Pb207': ['(n,2n)'],
        'Pb208': ['(n,2n)'],
    }
)

# modify the axis afterwards to make the data clearer
ax.set_xscale('linear')
ax.set_yscale('linear')
ax.set_xlim(0, 15e6)  # set the x axis limits from 0 to 15MeV

plt.show()

# %% [markdown]
# However, as well as neutron multiplication cross section, other neutronics factors to consider when selecting a multiplier could include:
# - moderation power (how much they slow down the neutrons)
# - amount of non useful reactions that don't multiply the neutrons (parasitic reactions)
# - the transmutation products

# %% [markdown]
# **Learning Outcomes for Part 1:**
# - OpenMC can be used to plot interaction cross sections for specific isotopes.
# - Reaction probabilities vary for each isotope depending on the energy of the neutron.
# - Li7 and Li6 both offer tritium producing reactions for different energy neutrons.
# - Be and Pb perform well in terms of neutron multiplication. Be9 has the lowest threshold energy for neutron multiplication reactions.
