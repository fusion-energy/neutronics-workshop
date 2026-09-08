# %% [markdown]
# ---
# title: Simple CAD model simulation
# ---

# %% [markdown]
# In this example we make use of a DAGMC neutronics geometry that has been made in the previous tasks.
#
# This task simply loads up the DAGMC h5m file into OpenMC to show how one makes an openmc.Model
#
# This specific example is an absolute minimal example, others in this same task show a few more additions on top of this.

# %%
import openmc
import dagmc_h5m_file_inspector as di
import pyvista as pv
from pathlib import Path

# Setting the cross section path to the correct location in the docker image.
# If you are running this outside the docker image you will have to change this path to your local cross section path.
openmc.config['cross_sections'] = Path.home() / 'nuclear_data' / 'cross_sections.xml'

# %% [markdown]
# Optionally we can visually inspect the geometry with Paraview and check it is as expected.
#
# We convert the DAGMC h5m file to a vtkhdf file which can be opened with [Paraview](https://www.paraview.org/download/) or as we do here, loaded with pyvista and viewed interactively here.

# %%
di.convert_h5m_to_vtkhdf(h5m_filename='dagmc.h5m', vtkhdf_filename='dagmc.vtkhdf')

# %% [markdown]
# We need to load up the DAGMC file into a CSG containing cell.
#
# There are several ways to do this however this is the most concise. Other methods are shown in the other examples.
#
# Here we reply on openmc to automatically make a bounding CSG cell that just fits around our DAGMC geometry.
#
# The [bounded_universe()]() method does accept some user arguments for padding and other options so I encourage you to checkout the docs for that method.

# %%
dag_universe = openmc.DAGMCUniverse(filename='dagmc.h5m')

csg_with_dag_inside = dag_universe.bounded_universe()

my_geometry = openmc.Geometry(csg_with_dag_inside)

# %% [markdown]
# The next step is to make materials for the model.
#
# The DAGMC file contains material tags which are just string values to identify the material for each volume.
#
# We actually know these tag names as we made this model in the earlier example but let us find them using openmc anyway.

# %%
print(dag_universe.material_names)

# %% [markdown]
# Now we have the names we should make materials for each name tag.
#
# This DAGMC file contains a single material tag so we will just make one material

# %%
material_iron = openmc.Material(name="mat1")  #  <--- the name of this material must match the available name in the DAGMC file
material_iron.add_nuclide("Fe56", 1, "ao")
material_iron.set_density("g/cm3", 7)


my_materials = openmc.Materials([material_iron])

# %% [markdown]
# Next we make a simple source
#
# - Using default position (0,0,0 which is inside the CSG cell)
# - Using default directions (isotropic)
# - The center of the DAGMC geometry is used to avoid birthing neutrons outside the geometry.

# %%
my_source = openmc.IndependentSource(
    space=openmc.stats.Point(dag_universe.bounding_box.center),
    energy=openmc.stats.Discrete([14e6], [1])
)

# %% [markdown]
# Next we can make a normal openmc.Settings object and then we have all the components needed to transport particles through the DAGMC geometry 

# %%
my_settings = openmc.Settings(
    batches=10,
    particles=50,
    run_mode="fixed source",
    source=my_source,
)

# %% [markdown]
# Now we can combine the geometry, materials and settings and run the model

# %%
my_model = openmc.Model(
    geometry=my_geometry,
    materials=my_materials,
    settings=my_settings
)

my_model.run()

# %% [markdown]
# In subsequent tasks we will add tallies to DAGMC models.
#
# This task aimed to make a DAGMC file into a OpenMC geometry.
#
# We also learned how to put the source in the middle of the DAGMC model and how to bound the DAGMC model into a CSG universe.
