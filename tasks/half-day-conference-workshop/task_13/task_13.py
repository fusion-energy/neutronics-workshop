# %% [markdown]
# ---
# title: Simulation of fast neutron flux on unstructured mesh
# ---

# %% [markdown]
# Fast neutron flux is of particular interest to fusion neutronics analysis as fast neutrons are able to undergo nuclear reactions with nuclei (threshold reactions) that slower neutrons can not.
#
# The fast neutron flux is used to estimate super conducting magnet lifetime among other things
#
# First import OpenMC and configure the nuclear data path

# %%
import openmc
from pathlib import Path
import pyvista as pv
# Setting the cross section path to the correct location in the docker image.
# If you are running this outside the docker image you will have to change this path to your local cross section path.
openmc.config['cross_sections'] = Path.home() / 'nuclear_data' / 'cross_sections.xml'

# %% [markdown]
# First we will make a simple material

# %%
mat1 = openmc.Material(name='mat1')
mat1.add_nuclide("H1", 1, percent_type="ao")
mat1.set_density("g/cm3", 0.001)
my_materials = openmc.Materials([mat1])

# %% [markdown]
# Now we load up the geometry that has previously been made with [cad-to-dagmc](https://github.com/fusion-energy/cad_to_dagmc/) the CSG bounding cell is enlarged to ensure we have space to put a neutron source above the geometry.

# %%
dag_univ = openmc.DAGMCUniverse(filename="dagmc_for_um.h5m").bounded_universe(padding_distance=10)
my_geometry = openmc.Geometry(root=dag_univ)

# %% [markdown]
# Now we load up the unstructured mesh file that was also made with [cad-to-dagmc](https://github.com/fusion-energy/cad_to_dagmc/)

# %%
umesh = openmc.UnstructuredMesh("dagmc.vtk", library="moab")
mesh_filter = openmc.MeshFilter(umesh)
energy_filter = openmc.EnergyFilter([10.0e6, 20.0e6])  # filtering neutrons between 10MeV and 20MeV, this is just an example and your definition of fast neutron may vary

tally = openmc.Tally(name="unstructured_mesh_tally")
tally.filters = [mesh_filter, energy_filter]
tally.scores = ["flux"]
my_tallies = openmc.Tallies([tally])

# %% [markdown]
# This defines some simple settings. There are sufficient particles to result in scores on the mesh

# %%
my_settings = openmc.Settings()
my_settings.batches = 10
my_settings.particles = 5000
my_settings.run_mode = "fixed source"

# %% [markdown]
# This creates a DT point source just shining down on the geometry

# %%
source_location = my_geometry.bounding_box.center
source_location[2] += 9  # moving the source above the geometry so more tetrahedrals get hit
my_source = openmc.IndependentSource(
    space=openmc.stats.Point(source_location),
    angle=openmc.stats.Isotropic(),
    energy=openmc.stats.Discrete([14e6], [1])
)
my_settings.source = my_source

# %% [markdown]
# Now we can run the simulation

# %%
model = openmc.Model(my_geometry, my_materials, my_settings, my_tallies)
sp_filename = model.run()

# %% [markdown]
# Now we load up the tally from the statepoint file.

# %%
sp = openmc.StatePoint(sp_filename)

tally_result = sp.get_tally(name="unstructured_mesh_tally")

flux_mean = tally_result.get_values(scores=["flux"], value="mean").flatten()

# %% [markdown]
# It is also necessary to get the mesh from statepoint from as it contains more information than the mesh loaded from the vtk file. This extra information (e.g. centroids) is needed when writing the mesh

# %%
umesh_from_sp = tally_result.find_filter(openmc.MeshFilter).mesh

# %% [markdown]
# You can at this point use the Python API to access the raw data within the mesh and the tally

# %%
print(f"The volume of voxel 100 in the mesh is {umesh_from_sp.volumes[100]}cm3")
print(f"The tally mean of voxel 100 in the mesh is {flux_mean[100]}")

# %% [markdown]
# The tally data along with the mesh is then saved to a vtkhdf format file. You could also save to the older .vtk file extention if prefered. I am using vtkhdf as is results in a smaller more performant file.

# %%
umesh_from_sp.write_data_to_vtk(filename="tally.vtkhdf", datasets={"mean": flux_mean})

# %% [markdown]
# This vtkhdf or vtk file can be loaded with [Paraview](https://www.paraview.org/download/) for inspection of the results.
#
# In this next code block we simply load up the vtkhdf file and visualise the results here.

# %%
pv.set_jupyter_backend('html')

# Allow empty meshes to be plotted (this will show nothing but won't error)
pv.global_theme.allow_empty_mesh = True

plotter = pv.Plotter()

# adding the tally result and plotting on a log scale
tally_result = pv.read('tally.vtkhdf')
tally_result.set_active_scalars(name='mean')
plotter.add_mesh(tally_result, log_scale=True, cmap='viridis')


# this can be used to remove values
# nonzero = clipped.threshold(0.0005)

# adding the point source location so we can see where the source is
point = pv.PolyData(source_location)
plotter.add_mesh(point, color='red', point_size=15, render_points_as_spheres=True)

plotter.show()

# %% [markdown]
# This example shows how to do the unstructured mesh simulation with a premade DAGMC geometry and a premade mesh
#
# It is important to use a surface mesh (DAGMC) that is conformal with the volume mesh (unstructured mesh)
#
# This example in the cad_to_dagmc repo shows you how to use the package to make a CAD geometry and make the conformal surface and volume mesh
#
# https://github.com/fusion-energy/cad_to_dagmc/tree/main/examples/surface_and_unstructured_mesh
