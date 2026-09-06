# %% [markdown]
# ---
# title: Making a hybrid CAD CSG model
# ---

# %% [markdown]
# This example shows how to use a DAGMC universe withing a CSG geometry.
#
# OpenMC allows you to fill a CSG geometry with a DAGMC geometry. Up to this point we have filled cells with materials but OpenMC also allows CSG cells to be filled with a [DAGMCUniverse](https://docs.openmc.org/en/stable/pythonapi/generated/openmc.DAGMCUniverse.html) type.
#
# Firs twe import the packages and set the cross sections.

# %%
import openmc
import cadquery as cq
from cad_to_dagmc import CadToDagmc
import dagmc_h5m_file_inspector as di
from pathlib import Path

# Setting the cross section path to the correct location in the docker image.
# If you are running this outside the docker image you will have to change this path to your local cross section path.
openmc.config['cross_sections'] = Path.home() / 'nuclear_data' / 'cross_sections.xml'

# %% [markdown]
# Next we make make some simple materials, note that they have names which is useful later in the script.

# %%
mat1 = openmc.Material(name='first_wall')
mat1.add_element('Fe', 1.0)
mat1.set_density('g/cm3', 7.87)

mat2 = openmc.Material(name='plasma')
mat2.add_nuclide('H2', 0.5)
mat2.add_nuclide('H3', 0.5)
mat2.set_density('g/cm3', 1e-6)

mats = openmc.Materials([mat1, mat2])

# %% [markdown]
# Next we make a simple CAD geometry

# %%
major_radius = 1000
minor_radii = 400
thickness = 50

assembly = cq.Assembly()
inner_torus = cq.Solid.makeTorus(major_radius, minor_radii)
outer_torus = cq.Solid.makeTorus(major_radius, minor_radii+thickness)
shell = outer_torus.cut(inner_torus)
assembly.add(shell, name="first_wall")
assembly.add(inner_torus, name="plasma")
assembly

# %% [markdown]
# We use [cad-to-dagmc](https://github.com/fusion-energy/cad_to_dagmc/) to mesh the geometry.
#
# The use of 'assembly_names' makes the dagmc file with material tags according to the names of parts in the assembly
# These two names will be used in the DAGMC file as material tags "first_wall", "plasma"
#     
# We set the sizes of the mesh to use on the components.

# %%
dag_mesh = CadToDagmc()
dag_mesh.add_cadquery_object(
    cadquery_object=assembly,
    material_tags="assembly_names",  # Use names as tags
)
dag_mesh.export_dagmc_h5m_file(
    set_size={'first_wall': 50, 'plasma':50},
    filename='dagmc-hybrid.h5m'
)

# %% [markdown]
# Now we just convert the h5m file to a vtkhdf which can be opened with Paraview.
#
# This allows us to see the material tags and volumes to visually inspect the geometry

# %%
di.convert_h5m_to_vtkhdf(h5m_filename='dagmc-hybrid.h5m', vtkhdf_filename= 'dagmc-hybrid.vtkhdf')

# %% [markdown]
# Now we go back to OpenMC where we make a DAGMCUniverse

# %%
dag_universe = openmc.DAGMCUniverse(filename='dagmc-hybrid.h5m', auto_geom_ids=True)

# %% [markdown]
# Now we make a CSG cell that we fill with the DAGMCUniverse

# %%
surf_x1 = openmc.XPlane(x0=-2000.0, name='x1', boundary_type='vacuum')
surf_x2 = openmc.XPlane(x0=2000.0, name='x2', boundary_type='vacuum')
surf_y1 = openmc.YPlane(y0=-2000.0, name='y1', boundary_type='vacuum')
surf_y2 = openmc.YPlane(y0=2000.0, name='y2', boundary_type='vacuum')
surf_z1 = openmc.ZPlane(z0=-2000.0, name='z1', boundary_type='vacuum')
surf_z2 = openmc.ZPlane(z0=2000.0, name='z2', boundary_type='vacuum')

region_inner_bioshield = +surf_x1 & -surf_x2 & +surf_y1 & -surf_y2 & +surf_z1 & -surf_z2
inner_bioshield = openmc.Cell(name='inner bioshield', region=region_inner_bioshield, fill=dag_universe)

# %% [markdown]
# Now we make the geometry with the single CSG cell (that is fileld with the DAGMC universe

# %%
geometry = openmc.Geometry([inner_bioshield])

# %% [markdown]
# New we make a simple source that fits nicely inside the torus shape of the CAD

# %%
# the distribution of radius is just a single value
radius = openmc.stats.Discrete([major_radius], [1])

# the distribution of source z values is just a single value
z_values = openmc.stats.Discrete([0], [1])

# the distribution of source azimuthal angles values is a uniform distribution between 0 and 2 Pi
angle = openmc.stats.Uniform(a=0., b=2* 3.14159265359)

# initialises a ring source using the three distributions and a radius
my_source = openmc.IndependentSource(
    space=openmc.stats.CylindricalIndependent(r=radius, phi=angle, z=z_values, origin=(0.0, 0.0, 0.0)),
    angle=openmc.stats.Isotropic(),
    energy=openmc.stats.muir(e0=14080000.0, m_rat=5.0, kt=20000.0)
)

# %% [markdown]
# Next we make the settings object

# %%
settings = openmc.Settings(
    run_mode="fixed source",
    source =my_source,
    particles=1000,
    batches=5
)

# %% [markdown]
# Then we bring the geometry, materials and settings together to make the model

# %%
model = openmc.Model(geometry, mats, settings)

# %% [markdown]
# We can now plot the geometry with the source to again visually inspect the model.

# %%
model.plot(
    basis='xy',
    color_by='material',
    n_samples=100,
    legend=True,
    colors={mat1:'grey', mat2:'pink'}
)

# %% [markdown]
# The model can be run and we are transporting neutrons through the meshed CAD in the form of a DAGMC universe and the CSG geometry.

# %% [markdown]
# model.run()

# %% [markdown]
# We can go beyond a minimal example and make use of the implicit material which is a useful DAGMC feature.
#
# First notice that the CSG cell itself is a void material and the DAGMC geometry does not completly fill all the space in the CSG cube.
#
# In DAGMC, the implicit complement is the region of space not occupied by any explicitly defined volume
#
# We can produce the DAGMC h5m file and assign a material tag for the implicit complement material
#
# We then make a new DAGMC universe with this new DAGMC h5m file

# %%
dag_mesh = CadToDagmc()
dag_mesh.add_cadquery_object(
    cadquery_object=assembly,
    material_tags="assembly_names",  # Use names as tags
)
dag_mesh.export_dagmc_h5m_file(
    set_size={'first_wall': 50, 'plasma':50},
    implicit_complement_material_tag="air",  # Tag the void as "air"
    filename='dagmc-with-imp-comp-mat.h5m'
)

dag_universe_with_imp_comp = openmc.DAGMCUniverse(filename='dagmc-with-imp-comp-mat.h5m', auto_geom_ids=True)

# %% [markdown]
# Now we need to make another material with a name that matches the implicit_complement_material_tag 'air'

# %%
mat1 = openmc.Material(name='first_wall')
mat1.add_element('Fe', 1.0)
mat1.set_density('g/cm3', 7.87)

mat2 = openmc.Material(name='plasma')
mat2.add_nuclide('H2', 0.5)
mat2.add_nuclide('H3', 0.5)
mat2.set_density('g/cm3', 1e-6)

mat3 = openmc.Material(name='air')
mat3.add_element('N', 0.78)
mat3.add_element('O', 0.21)
mat3.set_density('g/cm3', 0.00125)

mats_with_air = openmc.Materials([mat1, mat2, mat3])

# %% [markdown]
# The we make the geometry again this time with the new DAGMC universe

# %%
surf_x1 = openmc.XPlane(x0=-2000.0, name='x1', boundary_type='vacuum')
surf_x2 = openmc.XPlane(x0=2000.0, name='x2', boundary_type='vacuum')
surf_y1 = openmc.YPlane(y0=-2000.0, name='y1', boundary_type='vacuum')
surf_y2 = openmc.YPlane(y0=2000.0, name='y2', boundary_type='vacuum')
surf_z1 = openmc.ZPlane(z0=-2000.0, name='z1', boundary_type='vacuum')
surf_z2 = openmc.ZPlane(z0=2000.0, name='z2', boundary_type='vacuum')

region_inner_bioshield = +surf_x1 & -surf_x2 & +surf_y1 & -surf_y2 & +surf_z1 & -surf_z2
inner_bioshield = openmc.Cell(name='inner bioshield', region=region_inner_bioshield, fill=dag_universe_with_imp_comp)

geometry = openmc.Geometry([inner_bioshield])

# %% [markdown]
# Now we make a model from the new material, the new DAGMC file and the same settings.

# %%
model_with_air_imp_comp_mat = openmc.Model(geometry, mats_with_air, settings)

# %% [markdown]
# Plotting the geometry shows that we have a new material inside the CSG cell that is not occupied by the mesh geometry.

# %%
model_with_air_imp_comp_mat.plot(
    basis='xy',
    color_by='material',
    n_samples=100,
    legend=True,
    colors={mat1:'grey', mat2:'pink', mat3:'lightblue'}
)

# %% [markdown]
# Just transport a few particles to check the model works

# %%
model_with_air_imp_comp_mat.run()

# %% [markdown]
# Summary
#
# - We have made a CAD geometry and converted that into a DAGMC geometry
# - We have seen different ways to visually inspect the geometry and materials
# - We have made a minimal CSG geometry that contains a DAGMC universe
# - We then extended the example to define the implicit complement material tag which in this case avoids having to make a CAD of the air
