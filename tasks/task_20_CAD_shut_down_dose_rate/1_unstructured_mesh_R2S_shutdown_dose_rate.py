# %% [markdown]
# ---
# title: Unstructured mesh R2S shutdown dose rate
# ---

# %% [markdown]
# In this example we perform a shutdown dose rate simulation using the R2S method on an unstructured mesh.
#
# This is a very minimal example that only has a single cell and single material
#
# First we import all the packages we will need for the simulations

# %%
from cad_to_dagmc import CadToDagmc
import cadquery as cq
import openmc
from matplotlib.colors import LogNorm
import openmc.deplete
from pathlib import Path

# %% [markdown]
# Then we set the cross section path to the correct location in the docker image.
# If you are running this outside the docker image you will have to change this path to your local cross section path.

# %%
openmc.config['chain_file'] = Path.home() / 'nuclear_data' / 'chain-endf-b8.0.xml'
openmc.config['cross_sections'] = Path.home() / 'nuclear_data' / 'cross_sections.xml'

# %% [markdown]
# makes a CAD geometry to use for the neutronics geometry

# %%
s = cq.Workplane("XY")
sPnts = [
    (2.75, 1.5),
    (2.5, 1.75),
    (2.0, 1.5),
    (1.5, 1.0),
    (1.0, 1.25),
    (0.5, 1.0),
    (0, 1.0),
]
r = s.lineTo(3.0, 0).lineTo(3.0, 1.0).spline(sPnts, includeCurrent=True).close()
result = r.extrude(0.5)

# %% [markdown]
# Convert the CAD geometry to a DAGMC surface mesh and MOAB volume mesh

# %%
my_model = CadToDagmc()

my_model.add_cadquery_object(result, material_tags=['mat1'])


# this makes the tet mesh used for the unstructured mesh tally which is overlaid on the geometry
# this also makes the surface mesh used for the material volume
# the outer surface for both mesh have the same mesh nodes, they are conformal
dagmc_filename, umesh_filename = my_model.export_dagmc_h5m_file(
    filename="dagmc.h5m",
    max_mesh_size=0.8,
    min_mesh_size=0.1,
    unstructured_volumes=[1],
    umesh_filename="umesh.vtk",
)

# %% [markdown]
# Now use the two meshes in OpenMC to make the DAGMCUniverse and the UnstructuredMesh
#
# We transport particles on the DAGMCUniverse
#
# We will get the flux on the UnstructuredMesh tets and then activate the materials on each tet and use this information to make source terms

# %%
# add adding distance to avoid source being born on edge of geometry and the 2nd simulation crashing
universe = openmc.DAGMCUniverse("dagmc.h5m").bounded_universe(padding_distance=1)
my_geometry = openmc.Geometry(universe)

# the unstructured mesh to overlay on the DAGMC geometry
umesh = openmc.UnstructuredMesh("umesh.vtk", library="moab")

# %% [markdown]
# Make the material used for the simulation

# %%
my_material = openmc.Material(name='mat1', material_id=1)
my_material.add_nuclide("Fe56", 1, percent_type="ao")
my_material.set_density("g/cm3", 0.001)
my_material.depletable = True
my_materials = openmc.Materials([my_material])

# %% [markdown]
# Make a simple neutron source in the center of the geometry

# %%
# Create a DT point source
my_source = openmc.IndependentSource(
    space=openmc.stats.Point(my_geometry.bounding_box.center),
    angle=openmc.stats.Isotropic(),
    energy=openmc.stats.Discrete([14e6], [1])
)

# %% [markdown]
# Make the simulation settings for the neutron irradiation

# %%
my_settings = openmc.Settings()
my_settings.batches = 5
my_settings.particles = 5000
my_settings.run_mode = "fixed source"
my_settings.output = {'summary': False}
my_settings.source = my_source

# %% [markdown]
# Make the neutron irradiation model

# %%
model = openmc.Model(my_geometry, my_materials, my_settings)

# %% [markdown]
# Get the flux and micro_xs in each unstructured mesh tet

# %%
flux_in_each_voxel, micro_xs = openmc.deplete.get_microxs_and_flux(
    model=model,
    domains=umesh,
    chain_file=openmc.config['chain_file'],
    # needed otherwise the statepoint file is produced in an unknown temporary directory
    run_kwargs={'cwd':'.'},
    nuclides=my_material.get_nuclides()
)

# %% [markdown]
# Read in the unstructured from the statepoint, this contains additional information (centroids and volumes) compared to the umesh object

# %%
sp_filename=f'statepoint.{my_settings.batches}.h5'
sp = openmc.StatePoint(sp_filename)

# normally with regular meshes I would get the mesh from the tally
# but with unstructured meshes the tally does not contain the mesh
# however we can get it from the statepoint file
umesh_from_sp = sp.meshes[umesh.id]
# reading a unstructured mesh from the statepoint trigger internal code in the mesh
#  object so that its centroids and volumes become known.
# centroids and volumes are needed for the get_values and write_data_to_vtk steps
centroids = umesh_from_sp.centroids
mesh_vols = umesh_from_sp.volumes

# %% [markdown]
# make a new fresh material for every tet in the unstructured mesh

# %%
# empty list to be populated with a gamma source for each mesh voxel
all_sources = []

materials_for_every_mesh_voxel = []
for i, vol in enumerate(mesh_vols, start=2):
    # we make a new material with a new id for every mesh voxel
    new_mat = my_material.clone()
    new_mat.id = i
    new_mat.volume = vol
    materials_for_every_mesh_voxel.append(new_mat)

# %% [markdown]
# Perform the activation / depletion / transmutation of all the materials

# %%
# constructing the operator, note we pass in the flux and micro xs
operator = openmc.deplete.IndependentOperator(
    materials=openmc.Materials(materials_for_every_mesh_voxel),
    fluxes=[flux[0] for flux in flux_in_each_voxel],  # Flux in each group in [n-cm/src] for each domain
    micros=micro_xs,
    reduce_chain_level=5,
    normalization_mode="source-rate"
)

integrator = openmc.deplete.PredictorIntegrator(
    operator=operator,
    timesteps=[5, 60, 60],
    source_rates=[1e20, 0 , 0], # a 5 second pulse of neutrons followed by 120 seconds of decay
    timestep_units='s'
)

integrator.integrate()

# %% [markdown]
# Get the last timestep in the depletion results
#
# Extract all the materials and get their gamma emission spectrum
#
# Turn these gamma spectra into source terms for later use

# %%
results = openmc.deplete.Results("depletion_results.h5")
last_time_step=results[-1]

for i, (flux, mesh_vol) in enumerate(zip(flux_in_each_voxel, mesh_vols), start=2):
    activated_material = last_time_step.get_material(str(i))
    activated_material.volume = mesh_vol
    energy = activated_material.get_decay_photon_energy(
        clip_tolerance = 1e-6,  # cuts out a small fraction of the very low energy (and hence negligible dose contribution) photons
        units = 'Bq',
    )

    if energy:
        strength = energy.integral()
    # for the strength == None case
    else:
        strength = 0
    my_source = openmc.IndependentSource(
        # energy = energy,
        energy=energy,
        particle = "photon",
        strength = strength,
    )
    all_sources.append(my_source)

# %% [markdown]
# Make a mesh source out of the IndependentSource just made

# %%
mesh_source = openmc.MeshSource(
    mesh=umesh_from_sp,
    sources=all_sources,
)

# %% [markdown]
# Make simulation settings for the gamma transport simulation

# %%
my_gamma_settings = openmc.Settings()
my_gamma_settings.run_mode = "fixed source"
my_gamma_settings.batches = 100
my_gamma_settings.particles = 10000
my_gamma_settings.source = mesh_source
my_gamma_settings.output = {'summary': False}
my_gamma_settings.photon_transport = True

# %% [markdown]
# Make a dose tally on a regular mesh for the photon / gamma dose

# %%
energies, pSv_cm2 = openmc.data.dose_coefficients(particle="photon", geometry="AP")
dose_filter = openmc.EnergyFunctionFilter(
    energies, pSv_cm2, interpolation="cubic"  # interpolation method recommended by ICRP
)

regularmesh = openmc.RegularMesh().from_domain(my_geometry, dimension=27000)

particle_filter = openmc.ParticleFilter(["photon"])
mesh_filter = openmc.MeshFilter(regularmesh)
dose_tally = openmc.Tally()
dose_tally.filters = [mesh_filter, dose_filter, particle_filter]
dose_tally.scores = ["flux"]
dose_tally.name = "photon_dose_on_mesh"
tallies = openmc.Tallies([dose_tally])

# %% [markdown]
# make the model for the gamma / photon transport and run the simulation

# %%
model_gamma = openmc.Model(my_geometry, my_materials, my_gamma_settings, tallies)

Path("photons").mkdir(exist_ok=True)
gamma_sp_filename = model_gamma.run(cwd="photons")

# %% [markdown]
# You may wish to plot the dose tally on a mesh, this package makes it easy to include the geometry with the mesh tally

# %%
from openmc_regular_mesh_plotter import plot_mesh_tally
with openmc.StatePoint(gamma_sp_filename) as statepoint:
    photon_tally = statepoint.get_tally(name="photon_dose_on_mesh")

    # normalising this tally is a little different to other examples as the source strength has been using units of photons per second.
    # tally.mean is in units of pSv-cm3/source photon.
    # as source strength is in photons_per_second this changes units to pSv-/second

    # multiplication by pico_to_micro converts from (pico) pSv/s to (micro) uSv/s
    # dividing by mesh voxel volume cancels out the cm3 units
    # could do the mesh volume scaling on the plot and vtk functions but doing it here instead
    pico_to_micro = 1e-6
    seconds_to_hours = 60*60
    scaling_factor = (seconds_to_hours * pico_to_micro) / regularmesh.volumes[0][0][0]

    plot = plot_mesh_tally(
            tally=photon_tally,
            basis="xz",
            # score='flux', # only one tally so can make use of default here
            value="mean",
            colorbar_kwargs={
                'label': "Decay photon dose [µSv/h]",
            },
            norm=LogNorm(),
            volume_normalization=False,  # this is done in the scaling_factor
            scaling_factor=scaling_factor,
        )
    plot.figure.savefig(f'shut_down_dose_map_timestep.png')

# %% [markdown]
# You may want to increase the resolution of the regularmesh and rerun the simulation
#
# I can also recommend taking a look at shutdown dose rate simulations using the D1S
#
# D1S is generally quicker than R2S.
#
# R2S allows the user the possibility of changing the geometry between the neutron and gamma simulation.
# This can be useful for doing shutdown dose rate simulations with moving geometry of geometry that has been irradiated in one position then moved for maintenance and is still active.
