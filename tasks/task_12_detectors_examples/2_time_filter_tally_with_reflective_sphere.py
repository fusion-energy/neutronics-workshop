# %% [markdown]
# ---
# title: Time-resolved detection with a reflective sphere
# ---

# %% [markdown]
# This example builds on the previous time-filter tally by adding a beryllium sphere near the source. Beryllium is a particularly good neutron reflector, so the detector now sees both direct and reflected neutrons.
#
# The source emits neutrons at two energies (14 MeV and 2.5 MeV). The time-resolved results show:
# - The fast 14 MeV neutrons arriving first as a sharp peak
# - Reflected neutrons arriving over a broader time window
# - The 2.5 MeV neutron peak is difficult to distinguish as it is swamped by reflected neutrons arriving at similar times
#
# First import the required packages.

# %%
from pathlib import Path

import openmc
import numpy as np
import matplotlib.pyplot as plt

# Setting the cross section path to the correct location in the docker image.
# If you are running this outside the docker image you will have to change this path to your local cross section path.
openmc.config['cross_sections'] = Path.home() / 'nuclear_data' / 'cross_sections.xml'

# %% [markdown]
# ## Materials
#
# We define two materials: a He-3 gas detector and a beryllium reflector.

# %%
reflective_material = openmc.Material()
reflective_material.add_nuclide("Be9", 100.0, percent_type="ao")
reflective_material.set_density("g/cm3", 2)

detector_material = openmc.Material()
detector_material.add_nuclide("He3", 100.0, percent_type="ao")
detector_material.set_density("g/cm3", 0.178e-3)

materials = openmc.Materials([detector_material, reflective_material])

# %% [markdown]
# ## Geometry
#
# The same box-shaped He-3 detector as before, but now with a beryllium sphere (radius 90 cm) centred at (-50, 0, 0) — on the opposite side of the source from the detector. The source sits at the origin between the reflector and the detector.

# %%
# surfaces
sphere_surface = openmc.Sphere(r=500, boundary_type="vacuum")
sphere_surface_reflector = openmc.Sphere(r=90, x0=-50, y0=0, z0=0)

detector_front_surface = openmc.XPlane(x0=100)
detector_back_surface = openmc.XPlane(x0=110)
detector_left_side_surface = openmc.YPlane(y0=50)
detector_right_side_surface = openmc.YPlane(y0=-50)
detector_top_surface = openmc.ZPlane(z0=50)
detector_bottom_surface = openmc.ZPlane(z0=-50)

# cells
detector_region = (
    +detector_front_surface
    & -detector_back_surface
    & -detector_left_side_surface
    & +detector_right_side_surface
    & -detector_top_surface
    & +detector_bottom_surface
)

detector_cell = openmc.Cell(region=detector_region)
detector_cell.fill = detector_material

void_space_region = -sphere_surface & +sphere_surface_reflector
void_space_cell = openmc.Cell(region=void_space_region & ~detector_region)

reflective_region = -sphere_surface_reflector
reflective_cell = openmc.Cell(region=reflective_region & ~detector_region)
reflective_cell.fill = reflective_material

geometry = openmc.Geometry([void_space_cell, detector_cell, reflective_cell])

# %% [markdown]
# Let's plot the geometry to see the arrangement of the detector, reflector, and source.

# %%
geometry.plot(basis="xz")
plt.show()
geometry.plot(basis="yz")
plt.show()
geometry.plot(basis="xy")
plt.show()

# %% [markdown]
# ## Source and settings
#
# Same dual-energy isotropic point source as before.

# %%
source = openmc.IndependentSource()
source.space = openmc.stats.Point((0, 0, 0))
source.angle = openmc.stats.Isotropic()
source.energy = openmc.stats.Discrete([2.5e6, 14e6], [0.5, 0.5])

settings = openmc.Settings()
settings.batches = 10
settings.particles = 50000
settings.run_mode = "fixed source"
settings.source = source

# %% [markdown]
# ## Tallies
#
# Time-binned absorption tally from 1 ns to 100 ns with 1000 bins. More bins than the previous example to better resolve the overlapping direct and reflected neutron arrival times.

# %%
# 1 nanosecond to 100 nanoseconds with 1000 bins
time_steps = np.linspace(start=1e-9, stop=100e-9, num=1000)

time_tally = openmc.Tally(name="time_tally_in_cell")
time_filter = openmc.TimeFilter(time_steps)
cell_filter = openmc.CellFilter(detector_cell)
time_tally.scores = ["absorption"]
time_tally.filters = [time_filter, cell_filter]
tallies = openmc.Tallies([time_tally])

# %% [markdown]
# ## Run the simulation

# %%
model = openmc.Model(geometry, materials, settings, tallies)

sp_filename = model.run()

# %% [markdown]
# ## Plot results
#
# The plot should show the initial sharp peak from direct 14 MeV neutrons, followed by a long tail of reflected neutrons. The 2.5 MeV direct neutron peak is hard to spot as it overlaps with the reflected neutron signal.

# %%
with openmc.StatePoint(sp_filename) as sp:

    tally = sp.get_tally(name="time_tally_in_cell")
    df = tally.get_pandas_dataframe()
    print(df)

    df.plot(x="time low [s]", y="mean")
plt.show()

# %% [markdown]
# **Learning Outcomes:**
#
# - Understanding how a reflective material (beryllium) creates secondary neutron signals in time-of-flight measurements.
# - Seeing how reflected neutrons can obscure direct signals from slower particles.
# - Building on the basic `TimeFilter` tally with a more complex geometry.
