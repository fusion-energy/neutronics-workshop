# %% [markdown]
# ---
# title: Converting CAD geometry to neutronics
# ---

# %% [markdown]
# CAD geometry can be converted with cad-to-dagmc
#
# This makes DAGMC geometry which particle transport codes like OpenMC can understand and simulate particle transport through
#
# In this example we are going to convert some CAD to a neutronics model and simulate particles
#
# Read more about DAGMC geometry here
# https://svalinn.github.io/DAGMC/
#
# First import the package used to convert CAD to DAGMC geometry

# %%
from cad_to_dagmc import CadToDagmc

# %% [markdown]
# Make a instance of CadToDagmc 

# %%
my_model = CadToDagmc()

# %% [markdown]
# Add the step file to the model. This step file contains 6

# %%
my_model.add_stp_file(
    filename="step_cad_file_for_conversion.step",
    material_tags=[
        "mat1",
        "mat2",
        "mat3",
        "mat4",
        "mat5",
        "mat6",
    ],  # 6 volumes one for each letter in the CAD STEP file
)

# %% [markdown]
# Now export the DAGMC h5m geometry file that can be used in OpenMC and other codes that support DAGMC
#
# The mesh will be made with default meshing parameters

# %%
my_model.export_dagmc_h5m_file(filename="dagmc.h5m")

# %% [markdown]
# The mesh production was quick but you might want to customise it. For example add extra mesh nods to a particular solid.
#
# The next mesh is customised with the set_size argument to have small mesh (size is 0.5) elements for the first solid and large mesh (size is 2.0) for the other solids.
#
# You can change the numbers used for each solid to specify different mesh sizes for each solid in the geometry.

# %%
my_model.export_dagmc_h5m_file(
    filename="dagmc.h5m",
    set_size={1:0.5, 2:2.0, 3:2.0, 4:2.0, 5:2.0, 6:2.0},
)

# %% [markdown]
# The resulting DAGMC.h5m can be used in neutronics simulations.
#
# For more details of how to convert CAD geometry see then next task which goes over 
# - Additional mesh parameters
# - 3D volume mesh production
# - Making a mesh from CAD without writing a file
#
# Also take a look at 
#
# Learning objectives
#
#  - We learned how to make a simple DAGMC geometry from a STEP CAD file
#  - We learned how to customise the mesh to make it finer on a specific volume ID number
