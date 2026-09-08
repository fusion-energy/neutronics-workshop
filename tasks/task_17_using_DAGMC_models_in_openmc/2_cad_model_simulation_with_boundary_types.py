# %% [markdown]
# ---
# title: CAD model simulation with boundary tpyes
# ---

# %% [markdown]
# In this example we make a CAD model and convert it into a DAGMC model for use in OpenMC.
#
# The model is a quarter of a sphere and when making a OpenMC model from this we add reflecting surfaces on two of the sides. This is effectivly a minimal sector model.

# %%
import openmc
import cadquery as cq
from pathlib import Path
from cad_to_dagmc import CadToDagmc
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm


# Setting the cross section path to the correct location in the docker image.
# If you are running this outside the docker image you will have to change this path to your local cross section path.
openmc.config['cross_sections'] = Path.home() / 'nuclear_data' / 'cross_sections.xml'

# %% [markdown]
# First we make a material. This is a normal material the only thing to be mindfull of is that the material name should match the material tag within the DAGMC file.

# %%
material = openmc.Material()
material.add_nuclide('Fe56', 1)
material.set_density('g/cm3', 7.87)
material_tag_name = "quarter_sphere"  # this name will be used later
material.name = material_tag_name 

# %% [markdown]
# Next we make a CAD assembly and name the shape when we add it to the CAD assembly. Note the name used

# %%
# Define the sphere radius
radius = 10  # cm

# Create a full sphere
sphere = cq.Workplane("XY").sphere(radius)

# Create a cutting box to get the positive quadrant (1/4 sphere)
# The box removes everything in the negative X and negative Y regions
cutting_box = (
    cq.Workplane("XY")
    .box(2 * radius, 2 * radius, 2 * radius)
    .translate((radius , radius, 0))
)

# Cut the sphere to create a quarter sphere
quarter_sphere = sphere.intersect(cutting_box)

assembly = cq.Assembly()
assembly.add(quarter_sphere, name=material_tag_name)  # note the use of material_tag_name is nessecary here

# %% [markdown]
# Next we convert the CAD assembly to a DAGMC file

# %%
my_model = CadToDagmc()
my_model.add_cadquery_object(
    cadquery_object=assembly,
    material_tags="assembly_names"  # this ensures the material_tag_name is used to name the one material in the DAGMC file
)

# mesh and save the file to a h5m file
my_model.export_dagmc_h5m_file(
    filename="dagmc_quarter.h5m",
    max_mesh_size=10,
    min_mesh_size=2,
)

# %% [markdown]
# Now we make a wedge shaped CSG cell and fill it with the DAGMC Universe.
#
# Note that the surfaces that make up the wedge shaped CSG cell have boundary_type of ```vacuum``` and ```reflective```

# %%
dag_universe = openmc.DAGMCUniverse(filename='dagmc_quarter.h5m', auto_geom_ids=True)

sphere = openmc.Sphere(r=10, boundary_type='vacuum')
xplane = openmc.XPlane(x0=0, boundary_type='reflective')
yplane = openmc.YPlane(y0=0, boundary_type='reflective')

region = -sphere & +xplane & +yplane

cell = openmc.Cell(region=region, fill=dag_universe)

my_geometry = openmc.Geometry([cell])

plt.show()

# %% [markdown]
# Now we make a source and put it within the sector at x=5 amd y=5
#
# We also plot the model with the source to check the location

# %%
source = openmc.IndependentSource(
    space=openmc.stats.Point((5, 5, 0)),
    angle=openmc.stats.Isotropic(),
    energy=openmc.stats.Discrete([1e6], [1])
)

settings = openmc.Settings()
settings.batches = 10
settings.particles = 1000
settings.source = source
settings.run_mode = 'fixed source'

model = openmc.Model(geometry=my_geometry, materials=[material], settings=settings)
plot = model.plot(width=(20, 20), n_samples=1)
plt.show()

# %% [markdown]
# Now to show that neutrons stay within the sector we can do a mesh tally that extends beyond the sector geometry

# %%
mesh = openmc.RegularMesh()
mesh.dimension=[100, 100, 1] # only 1 cell in the Z dimension
mesh.lower_left=(-10,-10,-10)
mesh.upper_right=(10,10,10)

tally = openmc.Tally()
tally.filters.append(openmc.MeshFilter(mesh))
tally.scores.append("flux")

model.tallies = [tally]

# %% [markdown]
# Now we run the model and use apply_tally_results so that the previously made tally object gets populated with the results.

# %%
model.run(apply_tally_results=True)

# %% [markdown]
# Now we plot the mesh tally with the geometry overlayed.
#
# This should show that we only get 

# %%
my_slice = tally.get_slice(scores=['flux'])
my_slice.mean.shape = (mesh.dimension[0], mesh.dimension[1])

fig, ax1 = plt.subplots()

# when plotting the 2d data, added the extent is required.
# otherwise the plot uses the index of the 2d data arrays
# as the x y axis
plot_1 = ax1.imshow(
    X=my_slice.mean,
    extent=(-10,10,-10,10),
    norm=LogNorm(),
    cmap='viridis',
    origin='lower',
)

# we are setting the origin and width to zoom out a bit so the sector and surounding void can be seen
ax2 = my_geometry.plot(
    outline='only',
    origin=(0,0,0),
    width=(20,20),
    axes=ax1,  # Use the same axis as ax1
    pixels=10_000_000,  #avoids rounded corners on outline
)
plt.xlabel('X [cm]')
plt.ylabel('Y [cm]')
plt.show()

# %% [markdown]
# The model shows that neutron flux does not leave the sector model.
#
# Summary:
#
# - We can easily make use of DAGMC geometry within CSG cells.
# - We can set boundary conditions on the CSG surfaces and these are used during particle transport
