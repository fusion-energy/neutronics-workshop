import openmc
import cadquery as cq
from pathlib import Path
from cad_to_dagmc import CadToDagmc
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm


# Setting the cross section path to the correct location in the docker image.
# If you are running this outside the docker image you will have to change this path to your local cross section path.
openmc.config['cross_sections'] = Path.home() / 'nuclear_data' /'endf-b8.0-hdf5'/ 'cross_sections.xml'


material = openmc.Material()
material.add_nuclide('Fe56', 1)
material.set_density('g/cm3', 7.87)
material.name = "quarter_sphere"

# Define the sphere radius
radius = 10  # mm

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
assembly.add(quarter_sphere, name="quarter_sphere")

my_model = CadToDagmc()
my_model.add_cadquery_object(
    cadquery_object=assembly,
    material_tags="assembly_names"
)


my_model.export_dagmc_h5m_file(
    filename="dagmc_quarter.h5m",
    max_mesh_size=10,
    min_mesh_size=2,
)


dag_universe = openmc.DAGMCUniverse(filename='dagmc_quarter.h5m', auto_geom_ids=True)

sphere = openmc.Sphere(r=10, boundary_type='vacuum')
xplane = openmc.XPlane(x0=0, boundary_type='vacuum')
yplane = openmc.YPlane(y0=0, boundary_type='vacuum')

region = -sphere & +xplane & +yplane

cell = openmc.Cell(region=region, fill=dag_universe)

my_geometry = openmc.Geometry([cell])


# plot = my_geometry.plot(width=(20, 20))

# plt.show()

mesh = openmc.RegularMesh().from_domain(
    my_geometry, # the corners of the mesh are being set automatically to surround the geometry
    dimension=[100, 100, 1] # only 1 cell in the Z dimension
)


tally = openmc.Tally(name="heating_tally")
tally.filters.append(openmc.MeshFilter(mesh))
tally.scores.append("heating")

source = openmc.Source()
source.space = openmc.stats.Point((5, 5, 0))
source.angle = openmc.stats.Isotropic()
source.energy = openmc.stats.Discrete([1e6], [1])

settings = openmc.Settings()
settings.batches = 100
settings.particles = 1000
settings.source = source
settings.run_mode = 'fixed source'

model = openmc.Model(geometry=my_geometry, materials=[material], tallies=[tally], settings=settings)


# plot = model.plot(width=(20, 20), n_samples=1)
# plt.show()

model.run(apply_tally_results=True)

my_slice = tally.get_slice(scores=['heating'])
my_slice.mean.shape = (mesh.dimension[0], mesh.dimension[1])

fig, ax1 = plt.subplots(figsize=(6, 4))

# when plotting the 2d data, added the extent is required.
# otherwise the plot uses the index of the 2d data arrays
# as the x y axis
plot_1 = ax1.imshow(
    X=my_slice.mean, extent=mesh.bounding_box.extent['xy'],
norm=LogNorm(), cmap='viridis',origin='lower'
    )


ax2 = my_geometry.plot(
    outline='only',
    extent=my_geometry.bounding_box.extent['xy'],
    axes=ax1,  # Use the same axis as ax1
    pixels=10_000_000,  #avoids rounded corners on outline

)

ax2.set_xlim(ax1.get_xlim())
ax2.set_ylim(ax1.get_ylim())
ax2.set_aspect(ax1.get_aspect())  # Match aspect ratio

plt.show()