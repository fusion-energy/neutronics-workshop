# %% [markdown]
# ---
# title: Mesh-based R2S shutdown dose rate
# ---

# %% [markdown]
# This example uses the **mesh-based** R2S method, where a regular mesh is overlaid on the geometry and each mesh element is activated independently based on the material fractions within it.
#
# This approach is useful for complex geometries where:
# - Materials span many cells
# - Finer spatial resolution of activation is needed than the cell structure provides
# - You want to decouple the activation spatial discretization from the geometry
#
# The `R2SManager` automatically computes material volume fractions in each mesh element, runs neutron transport, performs activation, creates decay photon sources, and runs photon transport.
#
# First import packages and configure nuclear data paths.

# %%
import openmc
import openmc.deplete
from openmc.deplete.r2s import R2SManager
from pathlib import Path
import math
from matplotlib.colors import LogNorm

# Setting the cross section path to the correct location in the docker image.
# If you are running this outside the docker image you will have to change this path to your local cross section path.
openmc.config['cross_sections'] = Path.home() / 'nuclear_data' / 'cross_sections.xml'
openmc.config['chain_file'] = Path.home() / 'nuclear_data' / 'chain-endf-b8.0.xml'

# %% [markdown]
# ## Geometry and materials
#
# A geometry with two spheres (iron and aluminum) inside a rectangular box also filled with aluminum. The overlapping materials and box region make this a good candidate for mesh-based R2S rather than cell-based.

# %%
n_particles = 100_000
p_particles = 1_000

al_sphere_radius = 7
iron_sphere_radius = 4

# Iron material
mat_iron = openmc.Material()
mat_iron.add_nuclide("Fe56", 1.0)
mat_iron.add_nuclide("Fe57", 1.0)
mat_iron.set_density("g/cm3", 7.7)
mat_iron.depletable = True
mat_iron.volume = (4 / 3) * math.pi * math.pow(iron_sphere_radius, 3)

# Aluminum material
mat_aluminum = openmc.Material()
mat_aluminum.add_element("Al", 1.0)
mat_aluminum.set_density("g/cm3", 2.7)
mat_aluminum.depletable = True
mat_aluminum.volume = (4 / 3) * math.pi * math.pow(al_sphere_radius, 3)

# Geometry
sphere_surf_1 = openmc.Sphere(r=iron_sphere_radius, z0=10)
sphere_surf_2 = openmc.Sphere(r=al_sphere_radius, z0=-5)

sphere_cell_1 = openmc.Cell(region=-sphere_surf_1, fill=mat_aluminum)
sphere_cell_2 = openmc.Cell(region=-sphere_surf_2, fill=mat_iron)

box = openmc.model.RectangularParallelepiped(
    xmin=-20, xmax=20, ymin=-20, ymax=20, zmin=-20, zmax=20, boundary_type="vacuum"
)
box_cell = openmc.Cell(region=-box & +sphere_surf_1, fill=mat_aluminum)

my_geometry = openmc.Geometry([sphere_cell_1, sphere_cell_2, box_cell])
my_materials = openmc.Materials([mat_iron, mat_aluminum])

# %% [markdown]
# ## Neutron model

# %%
my_source = openmc.IndependentSource()
my_source.space = openmc.stats.Point((0, 0, 0))
my_source.angle = openmc.stats.Isotropic()
my_source.energy = openmc.stats.Discrete([14.06e6], [1])
my_source.particle = "neutron"

my_neutron_settings = openmc.Settings()
my_neutron_settings.run_mode = "fixed source"
my_neutron_settings.particles = n_particles
my_neutron_settings.batches = 10
my_neutron_settings.source = my_source
my_neutron_settings.photon_transport = False

neutron_model = openmc.Model(my_geometry, my_materials, my_neutron_settings)

# %% [markdown]
# ## Activation mesh and photon model
#
# Two separate meshes are used:
# - **Activation mesh** (passed to R2SManager as `domains`) — defines the spatial discretization for the R2S calculation
# - **Photon tally mesh** (on the photon model) — can be finer for better dose map resolution

# %%
# Activation mesh
activation_mesh = openmc.RegularMesh().from_domain(my_geometry, dimension=(3, 3, 3))

# Finer photon tally mesh
photon_mesh = openmc.RegularMesh().from_domain(my_geometry, dimension=(10, 10, 10))

energies, pSv_cm2 = openmc.data.dose_coefficients(particle="photon", geometry="AP")
dose_filter = openmc.EnergyFunctionFilter(
    energies, pSv_cm2, interpolation="cubic"
)
particle_filter = openmc.ParticleFilter(["photon"])
mesh_filter = openmc.MeshFilter(photon_mesh)
dose_tally = openmc.Tally()
dose_tally.filters = [mesh_filter, dose_filter, particle_filter]
dose_tally.scores = ["flux"]
dose_tally.name = "photon_dose_on_mesh"

photon_settings = openmc.Settings()
photon_settings.run_mode = "fixed source"
photon_settings.batches = 100
photon_settings.particles = p_particles

photon_model = openmc.Model(
    my_geometry, my_materials, photon_settings, openmc.Tallies([dose_tally])
)

# %% [markdown]
# ## Pulse schedule
#
# A single 1-second pulse followed by 24 hours of cooling in 2-hour steps.

# %%
hour_in_seconds = 60 * 60
timesteps_and_source_rates = [
    (1, 1e18),                  # 1 second of 1e18 neutrons/second
    (2 * hour_in_seconds, 0),   # 2 hours after shut down
    (2 * hour_in_seconds, 0),   # 4 hours after shut down
    (2 * hour_in_seconds, 0),   # 6 hours after shut down
    (2 * hour_in_seconds, 0),   # 8 hours after shut down
    (2 * hour_in_seconds, 0),   # 10 hours after shut down
    (2 * hour_in_seconds, 0),   # 12 hours after shut down
    (2 * hour_in_seconds, 0),   # 14 hours after shut down
    (2 * hour_in_seconds, 0),   # 16 hours after shut down
    (2 * hour_in_seconds, 0),   # 18 hours after shut down
    (2 * hour_in_seconds, 0),   # 20 hours after shut down
    (2 * hour_in_seconds, 0),   # 22 hours after shut down
    (2 * hour_in_seconds, 0),   # 24 hours after shut down
]

timesteps = [item[0] for item in timesteps_and_source_rates]
source_rates = [item[1] for item in timesteps_and_source_rates]

# %% [markdown]
# ## Run the R2S calculation
#
# For mesh-based R2S, we pass the activation mesh as the `domains` argument. No `bounding_boxes` are needed — the mesh elements define the spatial regions automatically.

# %%
manager = R2SManager(
    neutron_model=neutron_model,
    domains=activation_mesh,
    photon_model=photon_model,
)

output_dir = manager.run(
    timesteps=timesteps,
    source_rates=source_rates,
    # skip index 0 (state right after irradiation, before cooling)
    photon_time_indices=list(range(1, len(timesteps))),
    chain_file=openmc.config['chain_file'],
    operator_kwargs={"reduce_chain_level": 4},
)

# %% [markdown]
# ## Plot results
#
# Dose maps at each 2-hour cooling step over 24 hours, with the geometry outline overlaid. You should see the dose rate decrease over time as the activation products decay.

# %%
pico_to_micro = 1e-6
seconds_to_hours = 60 * 60

from openmc_regular_mesh_plotter import plot_mesh_tally
for time_index, tally_list in sorted(manager.results['photon_tallies'].items()):
    photon_tally = tally_list[0]

    scaling_factor = seconds_to_hours * pico_to_micro

    plot = plot_mesh_tally(
        tally=photon_tally,
        basis="xz",
        score='flux',
        value="mean",
        colorbar_kwargs={
            'label': "Decay photon dose [\u00b5Sv/h]",
        },
        norm=LogNorm(),
        volume_normalization=True,  # divides by voxel volume
        scaling_factor=scaling_factor,
        outline=True,
        geometry=my_geometry,
    )
    cumulative_cooling_time = sum(timesteps[1:time_index]) / (60 * 60)
    plot.title.set_text(f"{cumulative_cooling_time:.0f} hours after shut down")
    plot.figure.savefig(f'mesh_shut_down_dose_map_timestep_{str(time_index).zfill(3)}')

# %% [markdown]
# **Learning Outcomes:**
#
# - Using `R2SManager` with a mesh as the domain for mesh-based R2S calculations.
# - Understanding the difference between cell-based and mesh-based R2S approaches.
# - Using separate activation and photon tally meshes at different resolutions.
# - Visualising the decay of shutdown dose rate over a 24-hour cooling period.
