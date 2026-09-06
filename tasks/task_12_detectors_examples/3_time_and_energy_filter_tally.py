# %% [markdown]
# ---
# title: Time and energy resolved neutron detection
# ---

# %% [markdown]
# This example extends the reflective sphere setup by adding an `EnergyFilter` alongside the `TimeFilter`. This allows us to see neutron absorption at the detector resolved by both arrival time and neutron energy.
#
# The source emits only 14 MeV neutrons. The energy filter with 16 bins reveals how neutrons lose energy through scattering off the beryllium reflector — the direct signal arrives at high energy and early time, while reflected neutrons arrive later and at lower energies.
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
# Same He-3 detector and beryllium reflector as the previous example.

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
# Same geometry as the reflective sphere example: a box-shaped He-3 detector at x=100 cm and a beryllium sphere centred at (-50, 0, 0).

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
# ## Source and settings
#
# This time the source emits only 14 MeV neutrons (mono-energetic). More batches (100) are used to improve statistics since the signal is split across many time and energy bins.

# %%
source = openmc.IndependentSource()
source.space = openmc.stats.Point((0, 0, 0))
source.angle = openmc.stats.Isotropic()
source.energy = openmc.stats.Discrete([14e6], [1.0])

settings = openmc.Settings()
settings.batches = 100
settings.particles = 50000
settings.run_mode = "fixed source"
settings.source = source

# %% [markdown]
# ## Tallies
#
# The tally now uses both a `TimeFilter` (1 ns to 150 ns, 1500 bins) and an `EnergyFilter` (16 bins from 0 to 14 MeV). This produces a 2D histogram of absorption vs time and energy.

# %%
# 1 nanosecond to 150 nanoseconds with 1500 bins
time_steps = np.linspace(start=1e-9, stop=150e-9, num=1500)

time_tally = openmc.Tally(name="time_tally_in_cell")
time_filter = openmc.TimeFilter(time_steps)
energy_filter = openmc.EnergyFilter(np.linspace(0, 14e6, 16))
cell_filter = openmc.CellFilter(detector_cell)
time_tally.scores = ["absorption"]
time_tally.filters = [time_filter, cell_filter, energy_filter]
tallies = openmc.Tallies([time_tally])

# %% [markdown]
# ## Run the simulation

# %%
model = openmc.Model(geometry, materials, settings, tallies)

sp_filename = model.run()

# %% [markdown]
# ## Plot results
#
# We plot a separate time series for each energy bin. This reveals how the direct 14 MeV neutrons arrive as a sharp early peak in the highest energy bin, while reflected neutrons populate the lower energy bins at later times.

# %%
with openmc.StatePoint(sp_filename) as sp:

    tally = sp.get_tally(name="time_tally_in_cell")
    df = tally.get_pandas_dataframe()
    print(df)

    energy_bins_high_edge = sorted(df['energy high [eV]'].unique())
    energy_bins_low_edge = sorted(df['energy low [eV]'].unique())

    for high_energy_edge, low_energy_edge in zip(energy_bins_high_edge, energy_bins_low_edge):
        filtered_df = df[df['energy high [eV]'] == high_energy_edge]
        plt.plot(
            filtered_df["time low [s]"],
            filtered_df["mean"],
            label=f'{low_energy_edge:.1e}eV to {high_energy_edge:.1e}eV'
        )

plt.legend(loc='upper right')
plt.tight_layout()
plt.xlabel('Time [s]')
plt.ylabel('Neutron absorption')
plt.savefig('energy_filtering_on_time_tally_with_reflective_object.png', dpi=400)
plt.show()

# %% [markdown]
# **Learning Outcomes:**
#
# - Combining `TimeFilter` and `EnergyFilter` to create 2D tally histograms.
# - Understanding how neutron scattering off a reflector degrades neutron energy.
# - Visualising the correlation between arrival time and neutron energy after scattering.
