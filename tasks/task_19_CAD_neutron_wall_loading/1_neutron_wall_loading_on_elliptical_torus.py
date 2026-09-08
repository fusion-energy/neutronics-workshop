# %% [markdown]
# ---
# title: Neutron Wall Loading on an Elliptical Torus Shell
# ---

# %% [markdown]
# Neutron wall loading (NWL) is the neutron power per unit area incident on the first wall of a fusion reactor, typically expressed in MW/m². It is a key design parameter that determines material damage rates, shielding requirements, and component lifetimes.
#
# NWL is the **uncollided** neutron flux on the first wall surface, so the geometry between the source and wall must be void.
#
# This example computes the spatial distribution of NWL on an elliptical torus shell by:
# 1. Creating an elliptical torus shell in CadQuery
# 2. Converting to DAGMC format with cad-to-dagmc
# 3. Using dagmc_h5m_file_inspector to identify surfaces and set boundary conditions
# 4. Running OpenMC with particle tracks in void geometry
# 5. Extracting surface crossing positions from the tracks
# 6. Binning crossings by poloidal angle to show the wall loading distribution
#
# With the neutron source offset toward the outboard side, we expect higher wall loading on the outboard and lower on the inboard.

# %%
import math
from pathlib import Path

import cadquery as cq
import dagmc_h5m_file_inspector as di
import matplotlib.pyplot as plt
import numpy as np
import openmc
from cad_to_dagmc import CadToDagmc

openmc.config['cross_sections'] = Path.home() / 'nuclear_data' / 'cross_sections.xml'

# %% [markdown]
# ## Create the elliptical torus shell geometry
#
# We build a hollow elliptical torus (shell) by subtracting an inner solid torus from an outer one. The elliptical cross-section is vertically elongated, similar to a tokamak plasma shape.
#
# Each solid torus is constructed by revolving an ellipse around the Z axis in two 180° halves (a CadQuery limitation for full revolutions).

# %%
# Geometry parameters (cm)
major_radius = 100      # distance from Z axis to center of cross-section
inner_minor_r = 20      # inner ellipse radial semi-axis
inner_minor_v = 30      # inner ellipse vertical semi-axis
outer_minor_r = 25      # outer ellipse radial semi-axis
outer_minor_v = 35      # outer ellipse vertical semi-axis

# Source offset toward outboard (positive = outboard)
source_offset = 5       # cm from the major radius
source_radius = major_radius + source_offset


def make_elliptical_torus(R, a, b):
    """Create a solid elliptical torus by revolving an ellipse.

    Args:
        R: major radius (distance from Z axis to ellipse center)
        a: radial semi-axis (perpendicular to revolution axis)
        b: vertical semi-axis (parallel to revolution axis)
    """
    half1 = (
        cq.Workplane("XZ", origin=(R, 0, 0))
        .ellipse(a, b)
        .revolve(180, (-R, 0, 0), (-R, 1, 0))
    )
    half2 = (
        cq.Workplane("XZ", origin=(-R, 0, 0))
        .ellipse(a, b)
        .revolve(180, (R, 0, 0), (R, 1, 0))
    )
    return half1.union(half2)


# Inner solid torus (fills the cavity where the source sits)
inner_torus = make_elliptical_torus(major_radius, inner_minor_r, inner_minor_v)

# Outer solid torus (cavity + shell)
outer_torus = make_elliptical_torus(major_radius, outer_minor_r, outer_minor_v)

# Shell = outer minus inner
shell = outer_torus.cut(inner_torus)

print("Geometry created: inner solid torus + surrounding shell")

# %% [markdown]
# ## Convert to DAGMC
#
# We add both volumes to the DAGMC model as separate regions with distinct material tags. The interior cavity and the shell need to be separate DAGMC volumes so we can detect when a particle crosses from one into the other.

# %%
ctd = CadToDagmc()
ctd.add_cadquery_object(shell, material_tags=["shell"])
ctd.export_dagmc_h5m_file("dagmc.h5m")

print("DAGMC file created: dagmc.h5m")

# %% [markdown]
# ## Inspect the DAGMC file and set boundary conditions
#
# We use `dagmc_h5m_file_inspector` to:
# - Identify the surface IDs and their areas
# - Find the inner surface (smallest area) and outer surface (largest area)
# - Set the outer surface to vacuum so particles are killed on exit

# %%
# Inspect volumes and materials
vol_mat = di.get_volumes_and_materials("dagmc.h5m")
print(f"Volume-material mapping: {vol_mat}")

# Inspect surfaces and their areas
areas = di.get_surface_area_by_surface_id("dagmc.h5m")
print(f"Surface areas: {areas}")

# The inner surface has the smaller area, the outer has the larger
inner_surface_id = min(areas, key=areas.get)
outer_surface_id = max(areas, key=areas.get)
print(f"Inner surface ID: {inner_surface_id} (area = {areas[inner_surface_id]:.1f} cm\u00b2)")
print(f"Outer surface ID: {outer_surface_id} (area = {areas[outer_surface_id]:.1f} cm\u00b2)")

# Set vacuum boundary condition on the outer surface
di.set_boundary_condition("dagmc.h5m", outer_surface_id, "vacuum")
print(f"Vacuum boundary condition set on surface {outer_surface_id}")

# %% [markdown]
# ## Set up the OpenMC simulation
#
# Both volumes are filled with extremely low density material (effectively void) so neutrons travel in straight lines without colliding. The source is a ring of 14.1 MeV DT neutrons offset toward the outboard side.

# %%
# Materials - near-void so particles stream without interaction
mat_shell = openmc.Material(name="shell")
mat_shell.add_nuclide("H1", 1.0)
mat_shell.set_density("g/cm3", 1e-10)

materials = openmc.Materials([mat_shell])

# Geometry
dag_universe = openmc.DAGMCUniverse(filename="dagmc.h5m")
geometry = openmc.Geometry(root=dag_universe.bounded_universe())

# Source - ring of DT neutrons offset toward outboard
source = openmc.IndependentSource(
    space=openmc.stats.CylindricalIndependent(
        r=openmc.stats.Discrete([source_radius], [1]),
        phi=openmc.stats.Uniform(0, 2 * math.pi),
        z=openmc.stats.Discrete([0], [1]),
    ),
    angle=openmc.stats.Isotropic(),
    energy=openmc.stats.Discrete([14.1e6], [1]),
)

settings = openmc.Settings()
settings.batches = 1
settings.particles = 10000
settings.run_mode = "fixed source"
settings.max_tracks = 10000
settings.source = source

model = openmc.Model(geometry, materials, settings)

print(f"Source ring at r = {source_radius} cm ({source_offset} cm outboard of major radius)")
print(f"Distance from source to outboard inner wall: {(major_radius + inner_minor_r) - source_radius:.0f} cm")
print(f"Distance from source to inboard inner wall: {source_radius - (major_radius - inner_minor_r):.0f} cm")

# %% [markdown]
# ## Run the simulation with particle tracks

# %%
for f in Path(".").glob("*.h5"):
    if f.name != "dagmc.h5m":
        f.unlink(missing_ok=True)

sp_filename = model.run(tracks=True)

# %% [markdown]
# ## Extract surface crossing positions from tracks
#
# In void geometry, each particle's track contains only surface crossing events (no collisions). The track states are:
# - State 0: birth position (inside the torus cavity)
# - State 1: inner surface crossing (entering the shell) ← **this is the wall loading event**
# - State 2: outer surface crossing (killed by vacuum BC)
#
# We detect inner surface crossings by finding the first `cell_id` change in each track.

# %%
tracks = openmc.Tracks("tracks.h5")

crossing_positions = []
for track in tracks:
    for pt in track.particle_tracks:
        states = pt.states
        if len(states) < 2:
            continue
        birth_cell = states[0]["cell_id"]
        for i in range(1, len(states)):
            if states[i]["cell_id"] != birth_cell:
                crossing_positions.append([
                    states[i]["r"]["x"],
                    states[i]["r"]["y"],
                    states[i]["r"]["z"],
                ])
                break  # one inner crossing per particle

crossing_positions = np.array(crossing_positions)
print(f"Recorded {len(crossing_positions)} inner surface crossings from {len(tracks)} tracked particles")

# %% [markdown]
# ## Compute poloidal angle and wall loading distribution
#
# For each crossing point we compute the **poloidal angle** on the torus cross-section:
# - θ = 0: outboard midplane (closest to source)
# - θ = ±π: inboard midplane (furthest from source)
# - θ = π/2: top
# - θ = -π/2: bottom
#
# The wall loading distribution as a function of poloidal angle shows the outboard enhancement caused by the source offset.

# %%
# Compute poloidal angle for each crossing
x = crossing_positions[:, 0]
y = crossing_positions[:, 1]
z = crossing_positions[:, 2]

r_cyl = np.sqrt(x**2 + y**2)          # cylindrical radius
dr = r_cyl - major_radius              # radial distance from torus center
poloidal_angle = np.arctan2(z, dr)     # poloidal angle in radians

# Histogram of crossings vs poloidal angle
fig, ax = plt.subplots(figsize=(10, 5))
counts, bin_edges, _ = ax.hist(
    np.degrees(poloidal_angle),
    bins=36,
    edgecolor="black",
    alpha=0.7,
)
ax.set_xlabel("Poloidal angle (degrees)")
ax.set_ylabel("Number of surface crossings")
ax.set_title("Neutron Wall Loading Distribution vs Poloidal Angle")
ax.axvline(0, color="red", linestyle="--", label="Outboard midplane")
ax.axvline(180, color="blue", linestyle="--", label="Inboard midplane")
ax.axvline(-180, color="blue", linestyle="--")
ax.legend()
plt.tight_layout()
plt.savefig("wall_loading_vs_poloidal_angle.png", dpi=150)
plt.show()

# Report the outboard/inboard ratio
outboard_mask = np.abs(poloidal_angle) < np.radians(30)
inboard_mask = np.abs(poloidal_angle) > np.radians(150)
if inboard_mask.sum() > 0:
    ratio = outboard_mask.sum() / inboard_mask.sum()
    print(f"Outboard/inboard crossing ratio: {ratio:.1f}x")

# %% [markdown]
# ## 3D visualisation of surface crossings
#
# A 3D scatter plot of the crossing positions on the inner torus surface. Denser regions indicate higher wall loading.

# %%
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection="3d")

# Color by poloidal angle to show the distribution
sc = ax.scatter(
    x, y, z,
    c=np.degrees(poloidal_angle),
    cmap="coolwarm",
    s=1,
    alpha=0.3,
)
fig.colorbar(sc, label="Poloidal angle (degrees)", shrink=0.6)

ax.set_xlabel("X (cm)")
ax.set_ylabel("Y (cm)")
ax.set_zlabel("Z (cm)")
ax.set_title("Inner Surface Crossing Positions")

# Equal aspect ratio
max_range = max(
    x.max() - x.min(),
    y.max() - y.min(),
    z.max() - z.min(),
) / 2
mid_x = (x.max() + x.min()) / 2
mid_y = (y.max() + y.min()) / 2
mid_z = (z.max() + z.min()) / 2
ax.set_xlim(mid_x - max_range, mid_x + max_range)
ax.set_ylim(mid_y - max_range, mid_y + max_range)
ax.set_zlim(mid_z - max_range, mid_z + max_range)

plt.tight_layout()
plt.savefig("wall_loading_3d.png", dpi=150)
plt.show()

# %% [markdown]
# ## Converting to physical units
#
# To convert from crossings per source particle to MW/m²:
#
# $$\text{NWL} = \frac{N_{\text{crossings in bin}}}{N_{\text{source particles}}} \times \frac{S_n \times E_n}{A_{\text{bin}}}$$
#
# where:
# - $S_n$ = neutron source strength (neutrons/second), from the fusion power
# - $E_n$ = 14.1 MeV = 2.26 × 10⁻¹² J per neutron
# - $A_{\text{bin}}$ = surface area of the poloidal angle bin (m²)
# - For a 500 MW DT fusion reactor: $S_n \approx 1.77 \times 10^{20}$ neutrons/second

# %% [markdown]
# **Learning Outcomes:**
#
# - Neutron wall loading is the uncollided flux on the first wall and must be computed in void geometry
# - Particle tracks in OpenMC record surface crossing positions that can be post-processed for spatial wall loading
# - `dagmc_h5m_file_inspector` can identify surfaces by area and set boundary conditions on DAGMC geometries
# - An outboard-offset source produces higher wall loading on the outboard side, as expected in tokamak reactors
# - The poloidal angle distribution of crossings directly maps to the wall loading profile
