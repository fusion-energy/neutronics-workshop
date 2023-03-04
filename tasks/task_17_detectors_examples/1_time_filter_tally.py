# this example has a Helium 3 detector with a point source of neutrons.
# The emitted neutrons have two energies (14MeV and 2.5MeV)
# The example shows the neutron flux as a function of time at the detector.
# The simulation results show the arrival time of the neutrons at the detector
# The higher energy faster neutrons arrive first and have a smaller spread of
# arrival times while the lower energy neutrons arrive later and have a larger
# spread of arrival times across the detector face.


import openmc
import numpy as np
import matplotlib.pyplot as plt


# MATERIALS

detector_material = openmc.Material()
detector_material.add_nuclide("He3", 100.0, percent_type="ao")
detector_material.set_density("g/cm3", 0.178e-3)

my_materials = openmc.Materials([detector_material])


# GEOMETRY

# surfaces

# large radius as 14MeV neutrons travel at 5.2cm per nano second (1e-9s)
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

universe = openmc.Universe(cells=[void_space_cell, detector_cell])
my_geometry = openmc.Geometry(universe)


# universe.plot(width=(1000.0, 1000.0), basis='xz')
# plt.show()
# universe.plot(width=(1000.0, 1000.0), basis='yz')
# plt.show()
# universe.plot(width=(1000.0, 1000.0), basis='xy')
# plt.show()

# SOURCE

# Create a neutron point source
source = openmc.Source()
source.space = openmc.stats.Point((0, 0, 0))
source.angle = openmc.stats.Isotropic()
source.energy = openmc.stats.Discrete([2.5e6, 14e6], [0.5, 0.5])


# SETTINGS

# Instantiate a Settings object
my_settings = openmc.Settings()
my_settings.batches = 10
my_settings.particles = 50000
my_settings.run_mode = "fixed source"
my_settings.source = source

# TALLIES



# 1 nano second to 100 nano seconds with 500 bins
time_steps = np.linspace(start=1e-9, stop=100e-9, num=500)


time_tally = openmc.Tally(name="time_tally_in_cell")
time_filter = openmc.TimeFilter(time_steps)
cell_filter = openmc.CellFilter(detector_cell)
time_tally.scores = ["absorption"]
time_tally.filters = [time_filter, cell_filter]
my_tallies = openmc.Tallies(time_tally)


model = openmc.model.Model(my_geometry, my_materials, my_settings, my_tallies)

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
