# %% [markdown]
# ---
# title: Unstructured mesh R2S shutdown dose rate with different materials
# ---

# %% [markdown]
# In this example, we perform a shutdown dose rate simulation using the R2S method on an unstructured mesh.
#
# This is an upgraded example that includes three cells, three materials (instead of one) and two cooling timesteps
#
# When material regions are in contact, it's possible for a single tetrahedral element to contain multiple materials. This must be carefully accounted for when depleting the element volume
#
# First, we import all the necessary packages for the simulation.

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
#
# three volumes and three material tags, one for each letter

# %%
text = cq.Workplane().text(txt="R2S", fontsize=10, distance=1)

my_model = CadToDagmc()
my_model.add_cadquery_object(
    cadquery_object=text,
    material_tags=[
        "mat1",
        "mat2",
        "mat3",
    ],
)

# %% [markdown]
# Convert the CAD geometry to a DAGMC surface mesh and MOAB volume mesh. This conversion ensures that the surface mesh matches the outer surface of the volume mesh. This helps ensure that tetrahedral elements have a single material within.

# %%
dagmc_filename, umesh_filename = my_model.export_dagmc_h5m_file(
    filename="dagmc.h5m",
    max_mesh_size=10,
    min_mesh_size=2,
    unstructured_volumes=[1,2,3],
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
universe = openmc.DAGMCUniverse("dagmc.h5m").bounded_universe()
my_geometry = openmc.Geometry(universe)

# the unstructured mesh to overlay on the DAGMC geometry
umesh = openmc.UnstructuredMesh("umesh.vtk", library="moab")

# %% [markdown]
# Define the materials used in the simulation.
#
# The number of material names must match the number of tags included in the DAGMC file.

# %%
fe_material = openmc.Material(name='mat1')
fe_material.add_nuclide("Fe56", 1, percent_type="ao") 
fe_material.set_density("g/cm3", 7.874)
fe_material.depletable = True

Li4SiO4_mat = openmc.Material(name='mat2')
Li4SiO4_mat.add_element('Li', 4.0, percent_type='ao')
Li4SiO4_mat.add_element('Si', 1.0, percent_type='ao')
Li4SiO4_mat.add_element('O', 4.0, percent_type='ao')
Li4SiO4_mat.set_density('g/cm3', 2.32) 
Li4SiO4_mat.depletable = True

water_mat = openmc.Material(name='mat3')
water_mat.add_element('H', 2.0, percent_type='ao')
water_mat.add_element('O', 1.0, percent_type='ao')
water_mat.set_density('g/cm3', 0.99821) 
water_mat.depletable = True


my_materials = openmc.Materials([fe_material, Li4SiO4_mat, water_mat])

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
model.export_to_xml()

# %% [markdown]
# Collect a list of all nuclides present in the model
#
# Get the flux and micro_xs in each unstructured mesh tet

# %%
all_nuclides = set()
for material in my_materials:
    all_nuclides.update(material.get_nuclides())

Path('statepoint.5.h5').unlink(missing_ok=True)

flux_in_each_voxel, micro_xs = openmc.deplete.get_microxs_and_flux(
    model=model,
    domains=umesh,
    chain_file=openmc.config['chain_file'],
    # needed otherwise the statepoint file is produced in an unknown temporary directory
    run_kwargs={'cwd':'.'},
    nuclides=list(all_nuclides)  # Convert set to list
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
# Calculate the material volumes for each mesh element from the unstructured mesh

# %%
mat_vols = umesh_from_sp.material_volumes(model=model,n_samples=1_000_000)

# %% [markdown]
# Make a new fresh material for every tet in the unstructured mesh.
#
# Assign the material volume for each tet as the volume is needed to deplete the material.

# %%
# Get material IDs from my_materials object
material_ids = [mat.id for mat in my_materials]

materials_for_every_mesh_voxel = []
for i in range(len(mat_vols[material_ids[0]])):
    # Find which material is present in this voxel (only one material per voxel)
    material_id = next(mid for mid in material_ids if mat_vols[mid][i] > 0)
    material = next(mat for mat in my_materials if mat.id == material_id)
    
    # Create a new material instance for this voxel
    new_mat = material.clone()
    new_mat.id = i
    # Use the volume of this material in this voxel from mat_vol
    new_mat.volume = mat_vols[material_id][i]
    materials_for_every_mesh_voxel.append(new_mat) 

# %% [markdown]
# Define irradiation and cooling time steps.
#
# Set source rates to zero during decay-only steps.

# %%
timesteps_and_source_rates = [
    (5, 1e20),  # 5 second  
    (60, 0),  # 60 seconds
    (60, 0) # 60 seconds
]

timesteps = [item[0] for item in timesteps_and_source_rates]
source_rates = [item[1] for item in timesteps_and_source_rates]

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
    timesteps=timesteps,
    source_rates=source_rates, # a 5 second pulse of neutrons followed by 120 seconds of decay
    timestep_units='s'
)

integrator.integrate()

# %% [markdown]
# Make a dose tally on a regular mesh for the photon / gamma dose.
#
# The tallies will be used in each of the gamma simulations to see the shutdown dose

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
# We will collect the gamma source for all cooling time steps
#
# Extract all the materials and get their gamma emission spectrum
#
# Turn these gamma spectra into source terms for later use

# %%
results = openmc.deplete.Results("depletion_results.h5")

all_mesh_sources = []
for i_cool in range(1,len(timesteps)):  # skip the first time step as it is the irradiation step
    all_sources = []
    for i, mesh_vol in enumerate(mesh_vols):
        material_id = str(i)

        activated_material = results[i_cool].get_material(material_id)
        activated_material.volume = mesh_vol
        energy = activated_material.get_decay_photon_energy(
            clip_tolerance = 1e-6,
            units = 'Bq',
        )

        if energy:
            strength = energy.integral()
        # for the strength == None case
        else:
            strength = 0

        my_source = openmc.IndependentSource(
            energy=energy,
            particle = "photon",
            strength = strength,
            # constraints={'domains':my_material}
        )

        all_sources.append(my_source)

    # Make a mesh source out of the IndependentSource just made in the inner loop
    mesh_source = openmc.MeshSource(
        mesh=umesh_from_sp,
        sources=all_sources,
    )

    all_mesh_sources.append(mesh_source)

# %% [markdown]
# Makes and runs a simulation model for each time meshsource that has been made.

# %%
#Make simulation settings for the gamma transport simulation
my_gamma_settings = openmc.Settings()
my_gamma_settings.run_mode = "fixed source"
my_gamma_settings.batches = 10
my_gamma_settings.particles = 1000000
my_gamma_settings.output = {'summary': False}
my_gamma_settings.photon_transport = True

all_gamma_sp_filename = []

for mesh_source in all_mesh_sources:
    
    my_gamma_settings.source = mesh_source

    # here we use the same pristine materials from before neutron irradiation as the burnup is low
    # and the materials have not changed much so they would not perturb the neutron spectrum significantly
    # you could also use the activated materials from the depletion results but this would significantly slow the simulation down
    model_gamma = openmc.Model(my_geometry, my_materials, my_gamma_settings, tallies)

    # Make the model for the gamma / photon transport and run the simulation
    # a folder will be made for each photon transport, XML files will be saved there as well as the plot
    # Create directories with parents=True to ensure parent directories are created
    output_dir = Path(f"photons/photon_at_time_{i_cool}")
    output_dir.mkdir(parents=True, exist_ok=True)

    gamma_sp_filename = model_gamma.run(cwd=str(output_dir))
    all_gamma_sp_filename.append(gamma_sp_filename)

# %% [markdown]
# Loads up each of the simulation and plots the results

# %%
from openmc_regular_mesh_plotter import plot_mesh_tally

for gamma_sp_filename in all_gamma_sp_filename:
# You may wish to plot the dose tally on a mesh, this package makes it easy to include the geometry with the mesh tally
    with openmc.StatePoint(gamma_sp_filename) as statepoint:
        photon_tally = statepoint.get_tally(name="photon_dose_on_mesh")

        pico_to_micro = 1e-6
        seconds_to_hours = 60*60
        scaling_factor = (seconds_to_hours * pico_to_micro) / regularmesh.volumes[0][0][0]

        plot = plot_mesh_tally(
                tally=photon_tally,
                basis="xy",
                # score='flux', # only one tally so can make use of default here
                value="mean",
                colorbar_kwargs={
                    'label': "Decay photon dose [µSv/h]",
                },
                norm=LogNorm(),
                volume_normalization=False,
                scaling_factor=scaling_factor,
            )
        plot.figure.savefig(output_dir / f'shut_down_dose_map_timestep_{i_cool}.png')

# %% [markdown]
# You may want to increase the resolution of the regularmesh and rerun the simulation
#
# I can also recommend taking a look at shutdown dose rate simulations using the D1S
#
# D1S is generally quicker than R2S.
#
# R2S allows the user the possibility of changing the geometry between the neutron and gamma simulation.
# This can be useful for doing shutdown dose rate simulations with moving geometry of geometry that has been irradiated in one position then moved for maintenance and is still active.
