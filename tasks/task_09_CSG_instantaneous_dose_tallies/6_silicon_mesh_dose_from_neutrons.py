# %% [markdown]
# ---
# title: Silicon dose map from neutrons in a simple tokamak
# ---

# %% [markdown]
# This example estimates the silicon absorbed dose (KERMA) on a mesh tally across a simplified tokamak geometry, **without putting any silicon in the places where the dose is wanted**. This is useful for predicting the dose in silicon-based detectors or electronics that might be placed inside or near the tokamak.
#
# Two OpenMC features are combined to do this:
#
# - `Tally.multiply_density = False` tells OpenMC to score microscopic reaction rates, leaving out the atom densities of whatever material is actually in each cell.
# - `Tally.apply_virtual_material(material)` then multiplies those microscopic results by the atom densities of any material you choose, once the simulation has finished. Here that material is silicon.
#
# Using a whole material instead of a single isotope means all three naturally occurring silicon isotopes are represented, each weighted by its own atom density. The mass density chosen for the silicon cancels out of the final answer, because it scales the atom densities and the mass of the voxel by the same factor, so what the material really buys you is the isotopic mix.
#
# First import packages and configure the nuclear data path.

# %%
import math
from pathlib import Path

from matplotlib import colormaps
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import openmc

# Setting the cross section path to the correct location in the docker image.
# If you are running this outside the docker image you will have to change this path to your local cross section path.
openmc.config['cross_sections'] = Path.home() / 'nuclear_data' / 'cross_sections.xml'

# %% [markdown]
# ## Materials
#
# We define the tokamak materials. Note that **none of these contain silicon** (except the concrete slab), which is the whole point of using a virtual material to score silicon dose independently of what is actually there.

# %%
iron = openmc.Material(name='iron')
iron.add_element('Fe', 1.0)
iron.set_density("g/cm3", 7.874)

lithium = openmc.Material(name='lithium')
lithium.add_element('Li', 1.0)
lithium.set_density("g/cm3", 0.534)

tungsten = openmc.Material(name='tungsten')
tungsten.add_element('W', 1.0)
tungsten.set_density("g/cm3", 19.3)

concrete = openmc.Material(name='concrete')
concrete.add_element('O', 0.532)
concrete.add_element('Si', 0.337)
concrete.add_element('Ca', 0.044)
concrete.add_element('Al', 0.034)
concrete.add_element('Fe', 0.014)
concrete.add_element('H', 0.023)
concrete.add_element('Na', 0.016)
concrete.set_density("g/cm3", 2.3)

materials = openmc.Materials([iron, lithium, tungsten, concrete])

# %% [markdown]
# ## The virtual material
#
# Next we make the silicon that we want the dose in. This material is deliberately **not** added to the geometry. It is only used after the simulation, to scale the microscopic tally results by the silicon atom densities.
#
# A single isotope could be used here instead, but a material carries all three naturally occurring silicon isotopes, each with its own kerma coefficient, so the mixture is handled properly. Try changing the density and re-running the task, the dose in Gy comes out the same.

# %%
silicon = openmc.Material(name='virtual silicon')
silicon.add_element('Si', 1.0)
silicon.set_density('g/cm3', 2.329)

print(f"mass density {silicon.get_mass_density()} g/cm3")
for nuclide, atom_density in silicon.get_nuclide_atom_densities().items():
    print(f"  {nuclide} {atom_density:.5f} atom/b-cm")

# %% [markdown]
# ## Geometry
#
# A simplified tokamak built from concentric spherical shells and a central column cylinder:
#
# - **Central column** (tungsten), inner cylinder of radius 150 cm
# - **Plasma region** (void), inside the inner sphere and outside the central column
# - **First wall** (iron), 20 cm thick shell around the plasma
# - **Blanket** (lithium), 80 cm thick shell around the first wall
# - **Outer vessel** (void), the region outside the blanket
# - **Concrete slab**, 100 cm thick slab below the tokamak

# %%
R0 = 500.0              # major radius [cm]
FW_THICK = 20.0         # first-wall thickness [cm]
BLK_THICK = 80.0        # blanket thickness [cm]
CC_RADIUS = 150.0       # center-column cylinder radius [cm]
CC_EXTEND = 10.0        # center column extends beyond blanket [cm]

inner_r = R0
fw_r = R0 + FW_THICK
outer_r = R0 + FW_THICK + BLK_THICK
half_height = outer_r + CC_EXTEND

# surfaces
inner_sphere = openmc.Sphere(r=inner_r)
fw_sphere = openmc.Sphere(r=fw_r)
outer_sphere = openmc.Sphere(r=outer_r)
center_cyl = openmc.ZCylinder(r=CC_RADIUS)
top_plane = openmc.ZPlane(z0=half_height, boundary_type='vacuum')
bot_plane = openmc.ZPlane(z0=-half_height)
slab_bot_plane = openmc.ZPlane(z0=-half_height - 100, boundary_type='vacuum')
outer_cyl = openmc.ZCylinder(r=outer_r, boundary_type='vacuum')

# regions
plasma_region = -inner_sphere & +center_cyl
fw_region = +inner_sphere & -fw_sphere & +center_cyl
blanket_region = +fw_sphere & -outer_sphere & +center_cyl
center_col_region = -center_cyl & -top_plane & +bot_plane
outer_region = +outer_sphere & +center_cyl & -top_plane & +bot_plane & -outer_cyl
slab_region = -bot_plane & +slab_bot_plane & -outer_cyl

# cells
plasma_cell = openmc.Cell(region=plasma_region, name='plasma')           # void
fw_cell = openmc.Cell(region=fw_region, name='first_wall', fill=iron)
blanket_cell = openmc.Cell(region=blanket_region, name='blanket', fill=lithium)
cc_cell = openmc.Cell(region=center_col_region, name='center_column', fill=tungsten)
outer_cell = openmc.Cell(region=outer_region, name='outer_vessel')       # void
slab_cell = openmc.Cell(region=slab_region, name='concrete_slab', fill=concrete)

geometry = openmc.Geometry([plasma_cell, fw_cell, blanket_cell, cc_cell, outer_cell, slab_cell])

# %% [markdown]
# ## Source
#
# A 14.1 MeV D-T ring source at the plasma midplane, positioned halfway between the central column and the first wall.

# %%
source_r = CC_RADIUS + (R0 - CC_RADIUS) / 2.0   # halfway between CC and FW
source = openmc.IndependentSource(
    space=openmc.stats.CylindricalIndependent(
        r=openmc.stats.Discrete([source_r], [1.0]),
        phi=openmc.stats.Uniform(0.0, 2 * math.pi),
        z=openmc.stats.Discrete([0.0], [1.0]),
    ),
    energy=openmc.stats.Discrete([14.1e6], [1.0]),    # 14.1 MeV
    angle=openmc.stats.Isotropic(),
)

settings = openmc.Settings(
    run_mode='fixed source',
    particles=50_000,
    batches=10,
    source=source,
    seed=42,
)

# the tallies.out ASCII file would contain a line for every one of the half a
# million mesh voxels, so it is switched off and the results are read from the
# in-memory tally objects instead
settings.output = {'tallies': False}

# %% [markdown]
# ## Tallies
#
# One mesh tally, for the silicon absorbed dose (KERMA) from neutrons:
#
# - Scores `heating` for the three silicon nuclides with `multiply_density=False`
# - With `multiply_density=False` OpenMC leaves the atom density out of the score, so the result is a microscopic heating in eV b cm per atom per source particle
# - Because the score is a flux multiplied by a microscopic cross section it works in void cells too, which is what makes the dose to a detector sitting in the vacuum vessel computable
# - `apply_virtual_material` puts the silicon atom densities back in after the simulation
# - The `heating` score is a kerma: it counts the energy handed to charged particles where the neutron interacts and not the energy carried off by secondary photons
#
# Photon transport is left off. The `heating` score is a kerma built from MT=301, which already excludes the energy carried away by secondary photons, so transporting them would cost time without changing this result.
#
# That does mean the gammas are missing from the picture, and they are not a small correction. Simulated separately they carry about 3 times the neutron contribution in the blanket and about 10 times outside it, which is exactly where electronics would sit. The virtual material technique cannot reach them: OpenMC scores photon energy deposition collision by collision against the nuclide that was actually hit, so `multiply_density` has no effect and a silicon nuclide bin scores exactly zero in a cell that contains no silicon. Notebook 7 in this folder covers the gamma case with a different method.

# %%
mesh = openmc.RegularMesh.from_domain(geometry, dimension=500_000)
mesh_filter = openmc.MeshFilter(mesh)

print(f"Mesh: {mesh.dimension} = {math.prod(mesh.dimension)} voxels")
print(f"  lower_left   = {mesh.lower_left}")
print(f"  upper_right  = {mesh.upper_right}")
print(f"  width        = {mesh.width}")
print(f"  voxel volume = {mesh.volumes[0][0][0]} cm3")

# %%
# Si absorbed dose (KERMA) from neutrons, one bin per silicon nuclide.
# If you switch photon transport on, add an openmc.ParticleFilter("neutron")
# here. OpenMC moves any heating tally that is not neutron only onto a
# collision estimator, which breaks the microscopic route this task relies on.
si_n_tally = openmc.Tally(name="si_dose_neutron")
si_n_tally.filters = [mesh_filter]
si_n_tally.scores = ["heating"]
si_n_tally.nuclides = silicon.get_nuclides()
si_n_tally.multiply_density = False

# %% [markdown]
# ## Run the simulation

# %%
# note that the virtual silicon is deliberately absent from the materials
model = openmc.Model(
    geometry=geometry,
    materials=materials,
    settings=settings,
    tallies=[si_n_tally],
)

print(f"Running: {settings.particles} particles x {settings.batches} batches")
statepoint_path = model.run(apply_tally_results=True)
print("Done.")

# %% [markdown]
# ## Apply the virtual material
#
# `apply_virtual_material` multiplies each nuclide bin by that nuclide's atom density in the silicon material, in place. The nuclide dimension is kept, so the contribution of each silicon isotope can still be seen, and the statistical uncertainties are scaled along with the means.
#
# The call scales the tally in place and is not idempotent, so applying it twice would square the atom densities. Reloading the results from the statepoint first makes the cell safe to run as many times as you like.

# %%
# reload the raw results so that this cell can be re-run safely
model.apply_tally_results(statepoint_path)

si_n_tally.apply_virtual_material(silicon)

# the result now has units of eV per source particle in each voxel, still split
# by nuclide, so summing over the nuclide axis gives the silicon total
ev_per_source = si_n_tally.mean.sum(axis=1).flatten()

# each isotope has its own kerma coefficient, so its share of the heating is not
# the same as its share of the atoms
nuclide_totals = si_n_tally.mean.sum(axis=0).flatten()
atom_densities = silicon.get_nuclide_atom_densities()
total_atoms = sum(atom_densities.values())
for nuclide, total in zip(si_n_tally.nuclides, nuclide_totals):
    print(
        f"{nuclide}: {100 * atom_densities[nuclide] / total_atoms:5.1f}% of the atoms, "
        f"{100 * total / nuclide_totals.sum():5.1f}% of the heating"
    )

# %% [markdown]
# ## Post-processing
#
# Convert the raw tally results into physical dose rates. OpenMC does not divide mesh tally results by the voxel volume, so that division has to be done here.
#
# **Silicon dose from neutrons**, from eV per source particle to Gy/s:
#
# 1. Multiply by `openmc.data.JOULE_PER_EV` to get J per source particle
# 2. Divide by the voxel volume to get J/cm3 per source particle
# 3. Divide by the silicon mass density in kg/cm3 to get Gy per source particle
# 4. Multiply by the source rate in n/s to get Gy/s
#
# The silicon density cancels between steps 1 and 3. `apply_virtual_material` scaled by atom densities that are proportional to the mass density, and step 3 divides by that same mass density, so both the number of interactions and the mass of the target scale together and the dose in Gy depends only on the isotopic composition.

# %%
SOURCE_RATE = 1e20  # neutrons per second

voxel_volume = mesh.volumes[0][0][0]                 # cm3
si_kg_per_cm3 = silicon.get_mass_density() * 1e-3    # kg/cm3

si_n = (
    ev_per_source * openmc.data.JOULE_PER_EV / voxel_volume / si_kg_per_cm3 * SOURCE_RATE
)                                                                          # Gy/s

# most voxels are never reached so the minimum is always zero, the smallest
# non-zero value is more informative
def describe(name, values, unit):
    reached = values[values > 0]
    if reached.size == 0:
        print(f"{name}: no voxels were reached")
        return
    print(
        f"{name}: {reached.min():.3e} to {values.max():.3e} {unit} "
        f"in the {reached.size} of {values.size} voxels that were reached"
    )

describe("Silicon dose from neutrons", si_n, "Gy/s")

# %% [markdown]
# ## Plot results
#
# An XZ slice through the midplane (y=0).
#
# Voxels that no particle reached have a tally result of zero, which a logarithmic colour scale cannot show, so they are masked out and drawn in white.

# %%
nx, ny, nz = mesh.dimension
y_mid = ny // 2  # index of the voxel containing y=0

x_extent = [mesh.lower_left[0], mesh.upper_right[0]]
z_extent = [mesh.lower_left[2], mesh.upper_right[2]]
extent = x_extent + z_extent

def xz_slice(data):
    """Extract an XZ slice at y=0. Mesh results are ordered with x varying fastest."""
    sliced = data.reshape(nz, ny, nx)[:, y_mid, :]
    return np.ma.masked_less_equal(sliced, 0.0)

cmap = colormaps.get_cmap('inferno').resampled(12)
cmap.set_bad('white')

fig, ax = plt.subplots(figsize=(8, 9))

im = ax.imshow(
    xz_slice(si_n), origin='lower', extent=extent,
    aspect='equal', norm=mcolors.LogNorm(), cmap=cmap,
)
geometry.plot(basis='xz', outline='only', axes=ax, pixels=1_000_000)
ax.set_title('Silicon absorbed dose from neutrons')
ax.set_xlabel('X (cm)')
ax.set_ylabel('Z (cm)')
fig.colorbar(im, ax=ax, label='Gy/s')

fig.tight_layout()
plt.savefig('silicon_dose_xz.png', dpi=150)
plt.show()
print("Saved silicon_dose_xz.png")

# %% [markdown]
# **Learning Outcomes:**
#
# - Scoring dose in a material that is not present in the geometry, by combining `multiply_density=False` with `Tally.apply_virtual_material`.
# - Using a whole material rather than a single isotope, so that every naturally occurring nuclide is weighted by its own atom density, and seeing that the mass density chosen cancels out.
# - Reading a per-nuclide breakdown out of a tally whose nuclide dimension has been preserved.
# - Converting mesh tally results into physical dose rates, remembering that OpenMC does not divide mesh results by the voxel volume.
# - Knowing the limits of the virtual material technique. It works for neutron heating, but not for photon heating, which OpenMC scores against the nuclide that was actually hit. Notebook 7 covers the gamma case.
