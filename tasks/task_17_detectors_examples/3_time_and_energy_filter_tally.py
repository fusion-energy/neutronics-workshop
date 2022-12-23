# This example has a Helium 3 detector with a point source of neutrons next to
# a sphere of beryllium which is particularly good reflector of neutrons
# The emitted neutrons has a single neutron energy (14MeV)
# The example shows the neutron flux as a function of time and energy at the
# detector.
# The simulation results show the arrival time of the neutrons at the detector
# grouped by the energy of the neutron. There are 16 energy bins 

import openmc
import numpy as np
import matplotlib.pyplot as plt

# MATERIALS

reflective_material = openmc.Material()
reflective_material.add_nuclide("Be9", 100.0, percent_type="ao")
reflective_material.set_density("g/cm3", 2)

detector_material = openmc.Material()
detector_material.add_nuclide("He3", 100.0, percent_type="ao")
detector_material.set_density("g/cm3", 0.178e-3)

materials = openmc.Materials([detector_material, reflective_material])


# GEOMETRY

# surfaces

# large radius as 14MeV neutrons travel at 5.2cm per nano second (1e-9s)
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

universe = openmc.Universe(cells=[void_space_cell, detector_cell, reflective_cell])
geometry = openmc.Geometry(universe)

# SOURCE

# Create a neutron point source
source = openmc.Source()
source.space = openmc.stats.Point((0, 0, 0))
source.angle = openmc.stats.Isotropic()
source.energy = openmc.stats.Discrete([14e6], [1.0])


# SETTINGS

# Instantiate a Settings object
settings = openmc.Settings()
settings.batches = 100
settings.particles = 50000
settings.run_mode = "fixed source"
settings.source = source

# TALLIES

tallies = openmc.Tallies()

# 1 nano second to 100 nano second
time_steps = np.linspace(start=1e-9, stop=150e-9, num=1500)


time_tally = openmc.Tally(name="time_tally_in_cell")
time_filter = openmc.TimeFilter(time_steps)
energy_filter = openmc.EnergyFilter(np.linspace(0,14e6,16))
cell_filter = openmc.CellFilter(detector_cell)
time_tally.scores = ["flux"]
time_tally.filters = [time_filter, cell_filter, energy_filter]
tallies.append(time_tally)


model = openmc.model.Model(geometry, materials, settings, tallies)

sp_filename = model.run()

# open the results file
sp = openmc.StatePoint(sp_filename)

# access the tally using pandas dataframes
tally = sp.get_tally(name="time_tally_in_cell")
df = tally.get_pandas_dataframe()
print(df)

energy_bins_high_edge = sorted(df['energy high [eV]'].unique())
energy_bins_low_edge = sorted(df['energy low [eV]'].unique())

import matplotlib.pyplot as plt

for high_energy_edge, low_energy_edge in zip(energy_bins_high_edge, energy_bins_low_edge):
    filtered_df =  df[df['energy high [eV]']==high_energy_edge]
    plt.plot(
        filtered_df["time low [s]"],
        filtered_df["mean"],
        label=f'{low_energy_edge:.1e}eV to {high_energy_edge:.1e}eV'
    )

plt.legend(loc='upper right')
plt.tight_layout()
plt.xlabel('Time [s]')
plt.ylabel('Neutron flux')
# plt.show()
plt.savefig('energy_filtering_on_time_tally_with_reflective_object.png', dpi=400)
