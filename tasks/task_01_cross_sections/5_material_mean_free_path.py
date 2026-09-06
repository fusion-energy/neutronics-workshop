# %% [markdown]
# ---
# title: Mean free path neutrons
# ---

# %% [markdown]
# OpenMC can also be used find the mean free path of a neutron in a specific material.
#
# This task allows users to find the mean free path of some common fusion materials.
#
# This follows on from the previous task where material (Macroscopic) cross sections were plotted.
#
# These plots show the <b>Macroscopic</b> cross section which is the the effective target area of all of the nuclei contained in the volume of the material.
#
# Macroscopic cross section (Σ) is related to Microscopic cross section (σ) with the following equation.
#
# The units of (Σ) Macroscopic cross section are $\mathrm{m}^{-1}$ and therefore the mean free path is just 1/Σ at the energy of the neutron

# %% [markdown]
# First import OpenMC and configure the nuclear data path

# %%
import openmc
from pathlib import Path
import matplotlib.pyplot as plt
# Setting the cross section path to the correct location in the docker image.
# If you are running this outside the docker image you will have to change this path to your local cross section path.
openmc.config['cross_sections'] = Path.home() / 'nuclear_data' / 'cross_sections.xml'

# %% [markdown]
# We will now make some materials and get the mean free path at 14MeV (14e6eV) which is the rough energy DT neutrons are emitted with.
#
# We will also get the mean free path at thermal neutron energy, this is the energy neutrons have when they have been slowed down (moderated) to be in equilibrium with the material.
#
# We can start with a minimal steel.

# %%
mat1 = openmc.Material(name = 'Steel')
mat1.add_element('Fe', 0.975)
mat1.add_element('C', 0.025)
mat1.set_density('g/cm3', 7.7)

mean_free_path_14 = mat1.mean_free_path(energy=14e6)
mean_free_path_thermal = mat1.mean_free_path(energy=0.025)

print(f'Mean free path of a neutron in {mat1.name} at 14e6 eV = {mean_free_path_14:.4f} cm')
print(f'Mean free path of a neutron in {mat1.name} at 0.025 eV = {mean_free_path_thermal:.4f} cm')

# %% [markdown]
# Next material is tungsten which is often used as first wall armour.

# %%
mat2 = openmc.Material(name = 'Tungsten')
mat2.add_element('W', 1)
mat2.set_density('g/cm3', 19.3)

mean_free_path_14 = mat2.mean_free_path(energy=14e6)
mean_free_path_thermal = mat2.mean_free_path(energy=0.025)

print(f'Mean free path of a neutron in {mat2.name} at 14e6 eV = {mean_free_path_14:.4f} cm')
print(f'Mean free path of a neutron in {mat2.name} at 0.025 eV = {mean_free_path_thermal:.4f} cm')

# %% [markdown]
# Next up is a lithium ceramic, Li4SiO4 is a candidate breeder material

# %%
mat3 = openmc.Material(name = 'Li4SiO4')
mat3.add_element('Li', 4.0, percent_type='ao')
mat3.add_element('Si', 1.0, percent_type='ao')
mat3.add_element('O', 4.0, percent_type='ao')
mat3.set_density('g/cm3', 2.32)

mean_free_path_14 = mat3.mean_free_path(energy=14e6)
mean_free_path_thermal = mat3.mean_free_path(energy=0.025)

print(f'Mean free path of a neutron in {mat3.name} at 14e6 eV = {mean_free_path_14:.4f} cm')
print(f'Mean free path of a neutron in {mat3.name} at 0.025 eV = {mean_free_path_thermal:.4f} cm')

# %% [markdown]
# Finally concrete which is often used for bioshields, this is regular concrete and one might also consider borated or other concretes

# %%
mat4 = openmc.Material(name='Concrete')
mat4.add_element("H",0.168759)
mat4.add_element("C",0.001416)
mat4.add_element("O",0.562524)
mat4.add_element("Na",0.011838)
mat4.add_element("Mg",0.0014)
mat4.add_element("Al",0.021354)
mat4.add_element("Si",0.204115)
mat4.add_element("K",0.005656)
mat4.add_element("Ca",0.018674)
mat4.add_element("Fe",0.00426)
mat4.set_density("g/cm3", 2.3)

mean_free_path_14 = mat4.mean_free_path(energy=14e6)
mean_free_path_thermal = mat4.mean_free_path(energy=0.025)

print(f'Mean free path of a neutron in {mat4.name} at 14e6 eV = {mean_free_path_14:.4f} cm')
print(f'Mean free path of a neutron in {mat4.name} at 0.025 eV = {mean_free_path_thermal:.4f} cm')

# %% [markdown]
# This code block then plots the mean free path of the materials for comparison

# %%
all_materials = [mat1, mat2, mat3, mat4]

labels = [m.name for m in all_materials]
mfp_14 = [m.mean_free_path(energy=14e6) for m in all_materials]
mfp_thermal = [m.mean_free_path(energy=0.025) for m in all_materials]

bar_width = 0.35
y = range(len(labels))

fig, ax = plt.subplots(figsize=(8, 4))
ax.barh([i + bar_width/2 for i in y], mfp_14, bar_width, label='14e6 eV')
ax.barh([i - bar_width/2 for i in y], mfp_thermal, bar_width, label='Thermal (0.025 eV)')

ax.set_yticks(y)
ax.set_yticklabels(labels)
ax.set_xlabel('Mean Free Path (cm)')
ax.set_title('Mean Free Path of Neutrons in Different Materials')
ax.legend()
plt.tight_layout()
plt.show()

# %% [markdown]
# **Learning Outcomes:**
# - OpenMC can be used to find the mean free path of a neutron in the material
# - The mean free path varies with neutron energy
# - The mean free path varies with material (composition and density)
# - The mean free path is shorter at thermal energies compared to the birth energy of a DT fusion neutron (14MeV)
#
# **Additional information**
#
# The mean free path information is useful when setting mesh sizes for weight window generation, more on that in the variance reduction tasks.
