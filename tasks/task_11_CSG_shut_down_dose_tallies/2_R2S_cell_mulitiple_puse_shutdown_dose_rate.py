# %% [markdown]
# ---
# title: Cell-based R2S shutdown dose rate (multiple pulses)
# ---

# %% [markdown]
# This example builds on the previous single-pulse R2S example by applying **multiple neutron pulses** with cooling periods between them. This demonstrates how activation products build up over repeated irradiation cycles.
#
# The `R2SManager` uses `IndependentOperator` internally, which means only a single neutron transport calculation is performed regardless of how many pulses are in the schedule. The fluxes and microscopic cross sections from that single transport are reused for all depletion steps, making this approach much faster than running transport at each step.
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
# Same geometry as the single-pulse example: two small spheres (iron and aluminum) inside a vacuum sphere.

# %%
n_particles = 100_000
p_particles = 1_000

sphere_surf_1 = openmc.Sphere(r=20, boundary_type="vacuum")
sphere_surf_2 = openmc.Sphere(r=1, y0=10)
sphere_surf_3 = openmc.Sphere(r=5, z0=10)

sphere_region_1 = -sphere_surf_1 & +sphere_surf_2 & +sphere_surf_3
sphere_region_2 = -sphere_surf_2
sphere_region_3 = -sphere_surf_3

sphere_cell_1 = openmc.Cell(region=sphere_region_1)
sphere_cell_2 = openmc.Cell(region=sphere_region_2)
sphere_cell_3 = openmc.Cell(region=sphere_region_3)

mat_iron = openmc.Material()
mat_iron.add_element("Fe", 1.0)
mat_iron.set_density("g/cm3", 7.7)
mat_iron.depletable = True
iron_volume = (4 / 3) * math.pi * math.pow(sphere_surf_2.r, 3)
mat_iron.volume = iron_volume
sphere_cell_2.fill = mat_iron
sphere_cell_2.volume = iron_volume

mat_aluminum = openmc.Material()
mat_aluminum.add_element("Al", 1.0)
mat_aluminum.set_density("g/cm3", 2.7)
mat_aluminum.depletable = True
al_volume = (4 / 3) * math.pi * math.pow(sphere_surf_3.r, 3)
mat_aluminum.volume = al_volume
sphere_cell_3.fill = mat_aluminum
sphere_cell_3.volume = al_volume

my_geometry = openmc.Geometry([sphere_cell_1, sphere_cell_2, sphere_cell_3])
my_materials = openmc.Materials([mat_iron, mat_aluminum])

# %% [markdown]
# ## Neutron and photon models

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

# %%
mesh = openmc.RegularMesh().from_domain(my_geometry, dimension=1000)

energies, pSv_cm2 = openmc.data.dose_coefficients(particle="photon", geometry="AP")
dose_filter = openmc.EnergyFunctionFilter(
    energies, pSv_cm2, interpolation="cubic"
)
particle_filter = openmc.ParticleFilter(["photon"])
mesh_filter = openmc.MeshFilter(mesh)
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
# Seven 1-second neutron pulses, each followed by a 1-hour cooling period. The activation products accumulate with each pulse, so later cooling steps will show higher dose rates than the single-pulse example.

# %%
hour_in_seconds = 60 * 60
timesteps_and_source_rates = [
    (1, 1e18),              # pulse 1
    (hour_in_seconds, 0),   # 1 hour cooling
    (1, 1e18),              # pulse 2
    (hour_in_seconds, 0),   # 2 hours cooling
    (1, 1e18),              # pulse 3
    (hour_in_seconds, 0),   # 3 hours cooling
    (1, 1e18),              # pulse 4
    (hour_in_seconds, 0),   # 4 hours cooling
    (1, 1e18),              # pulse 5
    (hour_in_seconds, 0),   # 5 hours cooling
    (1, 1e18),              # pulse 6
    (hour_in_seconds, 0),   # 6 hours cooling
    (1, 1e18),              # pulse 7
    (hour_in_seconds, 0),   # 7 hours cooling
]

timesteps = [item[0] for item in timesteps_and_source_rates]
source_rates = [item[1] for item in timesteps_and_source_rates]

# Only run photon transport at the cooling steps (odd indices: 1, 3, 5, ...)
photon_time_indices = list(range(1, len(timesteps), 2))

# %% [markdown]
# ## Run the R2S calculation

# %%
activated_cells = [sphere_cell_2, sphere_cell_3]
bounding_boxes = {cell.id: cell.bounding_box for cell in activated_cells}

manager = R2SManager(
    neutron_model=neutron_model,
    domains=activated_cells,
    photon_model=photon_model,
)

output_dir = manager.run(
    timesteps=timesteps,
    source_rates=source_rates,
    photon_time_indices=photon_time_indices,
    bounding_boxes=bounding_boxes,
    chain_file=openmc.config['chain_file'],
    operator_kwargs={"reduce_chain_level": 5},
)

# %% [markdown]
# ## Plot results
#
# Dose maps at each cooling step. Compare with the single-pulse example to see how repeated irradiation increases the shutdown dose rate.

# %%
pico_to_micro = 1e-6
seconds_to_hours = 60 * 60

from openmc_regular_mesh_plotter import plot_mesh_tally
for time_index, tally_list in sorted(manager.results['photon_tallies'].items()):
    photon_tally = tally_list[0]

    scaling_factor = (seconds_to_hours * pico_to_micro) / mesh.volumes[0][0][0]

    plot = plot_mesh_tally(
        tally=photon_tally,
        basis="xz",
        value="mean",
        colorbar_kwargs={
            'label': "Decay photon dose [\u00b5Sv/h]",
        },
        norm=LogNorm(),
        volume_normalization=False,
        scaling_factor=scaling_factor,
    )
    plot.figure.savefig(f'shut_down_dose_map_timestep_{time_index}')

# %% [markdown]
# **Learning Outcomes:**
#
# - Running R2S with a multi-pulse irradiation schedule.
# - Understanding how the `IndependentOperator` enables efficient multi-pulse calculations with only one neutron transport.
# - Using `photon_time_indices` to selectively compute dose at cooling steps only.
# - Observing the build-up of activation products over repeated irradiation cycles.
