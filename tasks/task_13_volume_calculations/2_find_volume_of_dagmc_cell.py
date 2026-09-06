# %% [markdown]
# ---
# title: Finding Volume of DAGMC Cell
# ---

# %% [markdown]
# Following on from the task on finding the volume of a CSG cell it is also possible to find the volume of a DAGMC cell.
#
# One of the nice features of DAGMC is that we can get the volume without having to run a simulation.
#
# There is a nice Python package that we can use for this [https://github.com/fusion-energy/dagmc_h5m_file_inspector](https://github.com/fusion-energy/dagmc_h5m_file_inspector)
#
# First we import the dagmc_h5m_file_inspector Python package

# %%
import dagmc_h5m_file_inspector as di
import openmc

# %% [markdown]
# Then we load up a DAGMC file and print the volumes of each material tag within. The one has just a single cell

# %%
volumes_for_each_material = di.get_volumes_by_material_name("dagmc.h5m")

print(volumes_for_each_material)

# %% [markdown]
# We can also get the volumes of each cell in the DAGMC file

# %%
volumes_for_each_cell = di.get_volumes_by_cell_id("dagmc.h5m")

print(volumes_for_each_cell)

# %% [markdown]
# The volume of materials and cell ids can also be found

# %%
volumes_by_cell_and_material = di.get_volumes_by_cell_id_and_material_name("dagmc.h5m")

print(volumes_by_cell_and_material)

# %% [markdown]
# In openmc we typically want volumes of material tags so that we can perform depletion on these materials.
#
# dagmc_h5m_file_inspector provides a convenient function which sets the volumes of materials when the match material tags within the h5m file.

# %%
mat_steel = openmc.Material(name='mat1')
mat_steel.add_element('Fe', 99)
mat_steel.add_element('C', 1)
mat_steel.set_density('g/cm3', 7)
# notice mat_steel has not got a volume set here

materials = openmc.Materials([mat_steel])

# Set volumes from DAGMC geometry
di.set_openmc_material_volumes(materials, "dagmc.h5m")

# mat_steel now has a volume from the DAGMC file
print(mat_steel.volume)

# %% [markdown]
# The dagmc_h5m_file_inspector package can also convert the h5m file to a colored vtk file to allow visulisation in Paraview
#
# Take a look at the read me to see what else can be done [https://github.com/fusion-energy/dagmc_h5m_file_inspector](https://github.com/fusion-energy/dagmc_h5m_file_inspector)
