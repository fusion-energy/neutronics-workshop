# This example has a Helium 3 detector with a point source of neutrons next to
# a sphere of beryllium which is particularly good reflector of neutrons
# The emitted neutrons have two energies (14MeV and 2.5MeV)
# The example shows the neutron flux as a function of time at the detector.
# The simulation results show the arrival time of the neutrons at the detector
# The higher energy faster neutrons arrive first and then we start to see
# reflected neutrons and the lower energy neutrons arriving.
# It is hard to spot the peak for the arrival of the lower energy neutrons as
# it is swamped by the reflected neutrons.

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


universe.plot(width=(1000.0, 1000.0), basis="xz")
plt.show()
universe.plot(width=(1000.0, 1000.0), basis="yz")
plt.show()
universe.plot(width=(1000.0, 1000.0), basis="xy")
plt.show()

# SOURCE

# Create a neutron point source
source = openmc.Source()
source.space = openmc.stats.Point((0, 0, 0))
source.angle = openmc.stats.Isotropic()
source.energy = openmc.stats.Discrete([2.5e6, 14e6], [0.5, 0.5])


# SETTINGS

# Instantiate a Settings object
settings = openmc.Settings()
settings.batches = 10
settings.particles = 50000
settings.run_mode = "fixed source"
settings.source = source

# TALLIES

tallies = openmc.Tallies()

# 1 nano second to 100 nano second
time_steps = np.linspace(start=1e-9, stop=100e-9, num=1000)


time_tally = openmc.Tally(name="time_tally_in_cell")
time_filter = openmc.TimeFilter(time_steps)
cell_filter = openmc.CellFilter(detector_cell)
time_tally.scores = ["absorption"]
time_tally.filters = [time_filter, cell_filter]
tallies.append(time_tally)


model = openmc.model.Model(geometry, materials, settings, tallies)

sp_filename = model.run()

# open the results file
sp = openmc.StatePoint(sp_filename)

# access the tally using pandas dataframes
tally = sp.get_tally(name="time_tally_in_cell")
df = tally.get_pandas_dataframe()
print(df)

# plot the
df.plot(x="time low [s]", y="mean")
plt.show()
