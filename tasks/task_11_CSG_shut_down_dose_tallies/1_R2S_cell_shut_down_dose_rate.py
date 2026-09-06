# %% [markdown]
# ---
# title: Cell-based R2S shutdown dose rate (single pulse)
# ---

# %% [markdown]
# This example calculates shutdown dose rate using the **Rigorous 2-Step (R2S)** method with cell-based spatial discretization.
#
# The R2S method works in three steps:
# 1. **Neutron transport** — compute fluxes and microscopic cross sections in the activated cells
# 2. **Activation** — solve depletion equations to determine the radioactive inventory at each cooling time
# 3. **Photon transport** — create decay photon sources from the activated materials and compute dose
#
# The `R2SManager` class handles all three steps with a single `run()` call.
#
# In this example, a single 1-second neutron pulse activates iron and aluminum cells, then decay photon dose maps are computed at several cooling times.
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
# A simple geometry with three cells inside a vacuum sphere: a void region and two small spheres filled with iron and aluminum respectively. These two materials will be activated by the neutron source.
#
# Note that for cell-based R2S, each activated cell must have:
# - A depletable material (`depletable = True`)
# - A volume set on both the material and the cell

# %%
n_particles = 100_000
p_particles = 1_000

sphere_surf_1 = openmc.Sphere(r=20, boundary_type="vacuum")
sphere_surf_2 = openmc.Sphere(r=1, y0=10)
sphere_surf_3 = openmc.Sphere(r=5, z0=10)

sphere_region_1 = -sphere_surf_1 & +sphere_surf_2 & +sphere_surf_3  # void space
sphere_region_2 = -sphere_surf_2
sphere_region_3 = -sphere_surf_3

sphere_cell_1 = openmc.Cell(region=sphere_region_1)
sphere_cell_2 = openmc.Cell(region=sphere_region_2)
sphere_cell_3 = openmc.Cell(region=sphere_region_3)

# Iron material
mat_iron = openmc.Material()
mat_iron.add_element("Fe", 1.0)
mat_iron.set_density("g/cm3", 7.7)
mat_iron.depletable = True
iron_volume = (4 / 3) * math.pi * math.pow(sphere_surf_2.r, 3)
mat_iron.volume = iron_volume
sphere_cell_2.fill = mat_iron
sphere_cell_2.volume = iron_volume  # R2SManager requires cell volumes

# Aluminum material
mat_aluminum = openmc.Material()
mat_aluminum.add_element("Al", 1.0)
mat_aluminum.set_density("g/cm3", 2.7)
mat_aluminum.depletable = True
al_volume = (4 / 3) * math.pi * math.pow(sphere_surf_3.r, 3)
mat_aluminum.volume = al_volume
sphere_cell_3.fill = mat_aluminum
sphere_cell_3.volume = al_volume  # R2SManager requires cell volumes

my_geometry = openmc.Geometry([sphere_cell_1, sphere_cell_2, sphere_cell_3])
my_materials = openmc.Materials([mat_iron, mat_aluminum])

# %% [markdown]
# ## Neutron model
#
# A 14 MeV point source at the origin with isotropic emission. This model is used for Step 1 (neutron transport) of the R2S calculation.

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
# ## Photon model
#
# A separate model for the photon transport step. The R2SManager will set the decay photon sources automatically — we just need to provide the geometry, materials, settings, and the dose tallies we want.
#
# The dose tally uses an `EnergyFunctionFilter` with ICRP-116 dose coefficients to convert photon flux to effective dose.

# %%
mesh = openmc.RegularMesh().from_domain(my_geometry, dimension=1000)

# AP is front facing (worst case) ICRP dose direction
energies, pSv_cm2 = openmc.data.dose_coefficients(particle="photon", geometry="AP")
dose_filter = openmc.EnergyFunctionFilter(
    energies, pSv_cm2, interpolation="cubic"  # interpolation method recommended by ICRP
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
# A single 1-second irradiation pulse at 10^18 neutrons/second, followed by 5 hours of cooling in 1-hour steps.

# %%
hour_in_seconds = 60 * 60
timesteps_and_source_rates = [
    (1, 1e18),              # 1 second irradiation
    (hour_in_seconds, 0),   # 1 hour cooling
    (hour_in_seconds, 0),   # 2 hours cooling
    (hour_in_seconds, 0),   # 3 hours cooling
    (hour_in_seconds, 0),   # 4 hours cooling
    (hour_in_seconds, 0),   # 5 hours cooling
]

timesteps = [item[0] for item in timesteps_and_source_rates]
source_rates = [item[1] for item in timesteps_and_source_rates]

# %% [markdown]
# ## Run the R2S calculation
#
# The `R2SManager` takes the neutron model, the list of cells to activate, and optionally a separate photon model. The `run()` method executes all three steps.
#
# For cell-based R2S, we must provide `bounding_boxes` — a dictionary mapping cell IDs to their bounding boxes, used for spatial sampling of decay photon sources.
#
# We set `photon_time_indices` to skip index 0 (the state immediately after irradiation) and only compute dose at the cooling steps.

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
    # skip index 0 (state right after irradiation, before cooling)
    photon_time_indices=list(range(1, len(timesteps))),
    bounding_boxes=bounding_boxes,
    chain_file=openmc.config['chain_file'],
    operator_kwargs={"reduce_chain_level": 5},
)

# %% [markdown]
# ## Plot results
#
# The dose maps are stored in `manager.results['photon_tallies']`, keyed by time index. We plot the XZ slice of each cooling step's dose map.

# %%
pico_to_micro = 1e-6
seconds_to_hours = 60 * 60

from openmc_regular_mesh_plotter import plot_mesh_tally
for time_index, tally_list in sorted(manager.results['photon_tallies'].items()):
    photon_tally = tally_list[0]  # first (and only) tally

    # normalising: source strength is in photons/second so tally is in pSv-cm3/s
    # divide by voxel volume to cancel cm3, convert pSv to \u00b5Sv, convert s to h
    scaling_factor = (seconds_to_hours * pico_to_micro) / mesh.volumes[0][0][0]

    plot = plot_mesh_tally(
        tally=photon_tally,
        basis="xz",
        value="mean",
        colorbar_kwargs={
            'label': "Decay photon dose [\u00b5Sv/h]",
        },
        norm=LogNorm(),
        volume_normalization=False,  # done in the scaling_factor
        scaling_factor=scaling_factor,
    )
    plot.figure.savefig(f'shut_down_dose_map_timestep_{time_index}')

# %% [markdown]
# **Learning Outcomes:**
#
# - Using `R2SManager` to perform a cell-based R2S shutdown dose rate calculation.
# - Understanding the three steps of R2S: neutron transport, activation, photon transport.
# - Setting up separate neutron and photon models with appropriate tallies.
# - Post-processing decay photon dose maps at different cooling times.
