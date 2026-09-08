# %% [markdown]
# ---
# title: Finding Volume of a Cell by sampling simulation.
# ---

# %% [markdown]
# For the cell in this example we know the volume as it is a sphere.
#
# The method in this example can be adapted and then applied to a cell of unknown volume.
#
# We have a cell of known volume so that you can see how accurate the method is when the number of samples is increased.
#
# OpenMC samples within a provided bounding box and counts the samples that appear within the cell compared to those that appear outside the cell.
#
# By knowing the volume of the bounding box (which is a rectangle) one can determine the volume of the cell within that bounding box by looking at the ratio of volumes and samples in side the cell to outside the cell.
#
# The diagram shows the equations carried out by OpenMC in the background

# %% [markdown]
# ![stochastic volume calculation openmc](https://user-images.githubusercontent.com/8583900/229852560-ed349d4c-4c4f-4b3e-98d0-c48f14feffe5.png)

# %% [markdown]
# First import OpenMC and configure the nuclear data path

# %%
import openmc
from pathlib import Path
# Setting the cross section path to the correct location in the docker image.
# If you are running this outside the docker image you will have to change this path to your local cross section path.
openmc.config['cross_sections'] = Path.home() / 'nuclear_data' / 'cross_sections.xml'

# %% [markdown]
# This first stage sets up the geometry and materials for the simulation.

# %%
# MATERIALS

mat_iron = openmc.Material()
mat_iron.set_density('g/cm3', 7.75)
mat_iron.add_element('Fe', 1.0, percent_type='wo')
mat_iron.id = 1 # the id is set so that is can be accessed later from the volume calculation
my_materials = openmc.Materials([mat_iron])
my_materials.export_to_xml()

# GEOMETRY

# surfaces
outer_surface = openmc.Sphere(r=100, boundary_type='vacuum')

# cells
vessel_region = -outer_surface
vessel_cell = openmc.Cell(region=vessel_region)
vessel_cell.id = 1 # the id is set so that is can be accessed later from the volume calculation
vessel_cell.fill = mat_iron

my_geometry = openmc.Geometry([vessel_cell])
my_geometry.export_to_xml()


# SIMULATION SETTINGS

# Instantiate a Settings object
my_settings = openmc.Settings()
batches = 10
my_settings.batches = batches
my_settings.inactive = 0
my_settings.particles = 10000
my_settings.run_mode = 'fixed source'

# Create a DT point source
my_source = openmc.IndependentSource(
    space=openmc.stats.Point((0, 0, 0)),
    angle=openmc.stats.Isotropic(),
    energy=openmc.stats.Discrete([14e6], [1])
)
my_settings.source = my_source

# %% [markdown]
# This section carries out a volume calculation for the CSG cell. Particles are created randomly within the bounding box (of known volume). Upon creation of particles a check is carried out to see if the particle is also in the CSG volume. The ratio of the particles made in the bounding box to the particles made in the CSG cell is then used to determine the volume of the CSG cell. And error for the CSG cell is also determined.

# %%
# volume calculates for materials require a bounding box
# you can make the simulation more efficient if the bounding box volume is set to twice the volume of the cell volume
lower_left, upper_right = my_geometry.bounding_box

material_vol_calc = openmc.VolumeCalculation([mat_iron], 100000, lower_left, upper_right)

cell_vol_calc = openmc.VolumeCalculation([vessel_cell], 100000)

settings = openmc.Settings()
settings.volume_calculations = [cell_vol_calc, material_vol_calc]
settings.run_mode = 'volume'
settings.export_to_xml()

for f in Path('.').glob('*.h5'):
    f.unlink(missing_ok=True)
openmc.run()

# %% [markdown]
# This next section extracts the results from the output files

# %%
cell_vol_calc_results = openmc.VolumeCalculation.from_hdf5('volume_1.h5')
print('\n cell volume', cell_vol_calc_results.volumes[1], 'cm3')  # the [1] is the ID of the cell

material_vol_calc_results = openmc.VolumeCalculation.from_hdf5('volume_2.h5')
print(' material volume', material_vol_calc_results.volumes[1], 'cm3')  # the [1] is the ID of the material

# the cell_vol_calc_results are combined with errors, you can access the
# result on its own using the .nominal_value method

volume_of_cell_1 = cell_vol_calc_results.volumes[1].nominal_value

# %% [markdown]
# As we know th volume of the cell in this case (4/3PiR^3=4.18879e6cm3 if radius is 100) then we can check the accuracy of the answer against this known value.
#
# This method is intended to be used when the cell is more complex and the volume is not known. However for this example we wanted to be able to check.
#
# Now try reducing the number of particles and see how the answer varies in accuracy.

# %% [markdown]
# **Learning Outcomes for Task**
#
# - The volume of a cell or a material can be found using the stochastic volume method.
# - Volume found in this way is accompanied by a uncertainty.
