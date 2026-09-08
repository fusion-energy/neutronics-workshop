# %% [markdown]
# ---
# title: Time-resolved neutron detection
# ---

# %% [markdown]
# This example simulates a He-3 detector with a point source of neutrons emitting at two energies (14 MeV and 2.5 MeV).
#
# A `TimeFilter` is used to tally neutron absorption as a function of time at the detector. The results show:
# - Higher energy (faster) neutrons arrive first with a narrow spread of arrival times
# - Lower energy (slower) neutrons arrive later with a broader spread of arrival times
#
# This demonstrates how time-of-flight measurements can distinguish between neutron energies.
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
# The detector is a volume of He-3 gas, which has a large neutron absorption cross section.

# %%
detector_material = openmc.Material()
detector_material.add_nuclide("He3", 100.0, percent_type="ao")
detector_material.set_density("g/cm3", 0.178e-3)

my_materials = openmc.Materials([detector_material])

# %% [markdown]
# ## Geometry
#
# The geometry consists of a box-shaped He-3 detector (100 cm x 100 cm x 10 cm thick) placed 100 cm from the origin, inside a vacuum sphere. The sphere is large enough (500 cm radius) to allow sufficient flight time — 14 MeV neutrons travel at approximately 5.2 cm per nanosecond.

# %%
# surfaces
sphere_surface = openmc.Sphere(r=500, boundary_type="vacuum")

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

void_space_region = -sphere_surface
void_space_cell = openmc.Cell(region=void_space_region & ~detector_region)

my_geometry = openmc.Geometry([void_space_cell, detector_cell])

# %% [markdown]
# ## Source and settings
#
# An isotropic point source at the origin emitting neutrons at two energies with equal probability: 2.5 MeV (D-D fusion) and 14 MeV (D-T fusion).

# %%
source = openmc.IndependentSource()
source.space = openmc.stats.Point((0, 0, 0))
source.angle = openmc.stats.Isotropic()
source.energy = openmc.stats.Discrete([2.5e6, 14e6], [0.5, 0.5])

my_settings = openmc.Settings()
my_settings.batches = 10
my_settings.particles = 50000
my_settings.run_mode = "fixed source"
my_settings.source = source

# %% [markdown]
# ## Tallies
#
# We create a time-binned absorption tally on the detector cell. The time bins span from 1 ns to 100 ns with 500 bins, covering the expected flight times for both neutron energies over the 100 cm source-to-detector distance.

# %%
# 1 nanosecond to 100 nanoseconds with 500 bins
time_steps = np.linspace(start=1e-9, stop=100e-9, num=500)

time_tally = openmc.Tally(name="time_tally_in_cell")
time_filter = openmc.TimeFilter(time_steps)
cell_filter = openmc.CellFilter(detector_cell)
time_tally.scores = ["absorption"]
time_tally.filters = [time_filter, cell_filter]
my_tallies = openmc.Tallies([time_tally])

# %% [markdown]
# ## Run the simulation

# %%
model = openmc.Model(my_geometry, my_materials, my_settings, my_tallies)

sp_filename = model.run()

# %% [markdown]
# ## Plot results
#
# We extract the tally results as a pandas DataFrame and plot neutron absorption vs time. You should see two distinct peaks — the earlier, sharper peak from 14 MeV neutrons and the later, broader peak from 2.5 MeV neutrons.

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
# - Using `TimeFilter` to resolve neutron arrival times at a detector.
# - Understanding how neutron energy affects time-of-flight and arrival time spread.
# - Extracting and plotting tally results using pandas DataFrames.
