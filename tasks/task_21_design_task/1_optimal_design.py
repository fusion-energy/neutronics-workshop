# %% [markdown]
# ---
# title: Design your own tokamak
# ---

# %% [markdown]
# This activity allows you to put your neutronics knowledge to the test
#
# We are going to simulate a tokamak where you get to decide the materials.
#
# The goal is to:
#
# - maximize the Tritium Breeding Ratio
# - minimize the heating on the center column 
# - maximize the heat in the blanket
#
# I recommend plotting the cross sections before you make your choices.
#
# The [example](https://github.com/fusion-energy/neutronics-workshop/blob/main/tasks/task_01_cross_sections/3_material_xs_plot.py) for plotting cross sections might be useful.
#
# First import OpenMC and configure the nuclear data path

# %%
import openmc
from pathlib import Path
# Setting the cross section path to the correct location in the docker image.
# If you are running this outside the docker image you will have to change this path to your local cross section path.
openmc.config['cross_sections'] = Path.home() / 'nuclear_data' / 'cross_sections.xml'

# %% [markdown]
# Task 1 - enter the names of materials

# %%
# options for coolant

water = openmc.Material(name='water')
water.add_element('H', 2)
water.add_element('O', 1)
water.set_density('g/cm3', 1)

helium = openmc.Material(name='helium')
helium.add_element('He', 1)
helium.set_density('g/cm3', 0.0014)

super_critical_co2 = openmc.Material(name='super critical co2')
super_critical_co2.add_element('C', 1)
super_critical_co2.add_element('O', 2)
super_critical_co2.set_density('g/cm3', 0.001)


# options for first wall

tungsten = openmc.Material(name='your code here')
tungsten.add_element('W', 1, percent_type='wo')
tungsten.set_density('g/cm3', 19.2)

steel = openmc.Material(name='your code here')
steel.add_element('Fe', 0.95, percent_type='wo')
steel.add_element('C', 0.05, percent_type='wo')
steel.set_density('g/cm3', 1)

silicon_carbide = openmc.Material(name='your code here')
silicon_carbide.add_element('Si', 1)
silicon_carbide.add_element('C', 1)
silicon_carbide.set_density('g/cm3', 3.21)

zirconium = openmc.Material(name='your code here')
zirconium.add_element('Zr', 1, percent_type='wo')
zirconium.set_density('g/cm3', 6.49)

# options for reflector

beryllium = openmc.Material(name='mat_reflector')
beryllium.add_element('Be', 1, percent_type='wo')
beryllium.set_density('g/cm3', 1.85)

tungsten = openmc.Material(name='mat_reflector')
tungsten.add_element('W', 1, percent_type='wo')
tungsten.set_density('g/cm3', 19.2)

graphite = openmc.Material(name='mat_reflector')
graphite.add_element('C', 1, percent_type='wo')
graphite.set_density('g/cm3', 2.2)

# options for breeder

# note you can change the enrichment
lithium_lead = openmc.Material(name='your code here')
lithium_lead.add_element('Pb', 84.2, percent_type='ao')
lithium_lead.add_element('Li', 15.8, percent_type='ao', enrichment=90.0, enrichment_target='Li6', enrichment_type='ao')
lithium_lead.set_density('g/cm3', 9.5)

# note you can change the enrichment
lithium_orthosilicate = openmc.Material(name='your code here')
lithium_orthosilicate.add_element('Si', 4, percent_type='ao')
lithium_orthosilicate.add_element('O', 1, percent_type='ao')
lithium_orthosilicate.add_element('Li', 4, percent_type='ao', enrichment=50.0, enrichment_target='Li6', enrichment_type='ao')
lithium_orthosilicate.set_density('g/cm3', 2.2)

# note you can change the enrichment
lithium_titanate = openmc.Material(name='your code here')
lithium_titanate.add_element('O', 12, percent_type='ao')
lithium_titanate.add_element('Ti', 5, percent_type='ao')
lithium_titanate.add_element('Li', 4, percent_type='ao', enrichment=40.0, enrichment_target='Li6', enrichment_type='ao')
lithium_titanate.set_density('g/cm3', 2.4)

# note you can change the enrichment
liquid_lithium = openmc.Material(name='your code here')
liquid_lithium.add_element('Li', 1, percent_type='ao', enrichment=7.0, enrichment_target='Li6', enrichment_type='ao')
liquid_lithium.set_density('g/cm3', 0.5)

# conductor material

mat_conductor = openmc.Material(name='mat_conductor')
mat_conductor.add_element('Nb', 1, percent_type='ao')
mat_conductor.add_element('Sn', 3, percent_type='ao')
mat_conductor.set_density('g/cm3', 8.96)

# %% [markdown]
# Task 2 - plot the tritium production cross sections of all the breeder options 

# %%
# your code goes here

# %% [markdown]
# Task 3 - plot the absorption of all the coolants and first wall options

# %%
# your code goes here

# %% [markdown]
# Task 4 - select your materials

# %%
# put in your chosen material option
my_materials = openmc.Materials([mat_conductor,])  # your code here

# %% [markdown]
# Task 5 - Fill the cells with the materials

# %%
# surfaces
central_column_surface_outer = openmc.ZCylinder(r=100)
central_column_surface_mid = openmc.ZCylinder(r=95)
central_column_surface_inner = openmc.ZCylinder(r=90)

inner_sphere_surface = openmc.Sphere(r=495)
middle_sphere_surface = openmc.Sphere(r=500) 
outer_sphere_surface = openmc.Sphere(r=505)
outer_outer_sphere_surface = openmc.Sphere(r=600)
edge_of_simulation_surface = openmc.Sphere(r=700, boundary_type='vacuum')

# regions
central_column_region = -central_column_surface_inner & -edge_of_simulation_surface
central_column_coolant_region = +central_column_surface_inner & -central_column_surface_mid & -edge_of_simulation_surface
central_column_fw_region = +central_column_surface_mid & -central_column_surface_outer & -edge_of_simulation_surface

inner_vessel_region = +central_column_surface_outer & -inner_sphere_surface

blanket_fw_region = -middle_sphere_surface & +inner_sphere_surface & +central_column_surface_outer
blanket_coolant_region = +middle_sphere_surface & -outer_sphere_surface & +central_column_surface_outer
blanket_breeder_region = +outer_sphere_surface & -outer_outer_sphere_surface & +central_column_surface_outer
blanket_reflector_region = +outer_outer_sphere_surface & -edge_of_simulation_surface & +central_column_surface_outer

# cells
central_column_cell = openmc.Cell(region=central_column_region, fill=mat_conductor)
central_column_coolant_cell = openmc.Cell(region=central_column_coolant_region) # your code here
central_column_fw_cell = openmc.Cell(region=central_column_fw_region) # your code here
inner_vessel_cell = openmc.Cell(region=inner_vessel_region)
blanket_fw_cell = openmc.Cell(region=blanket_fw_region) # your code here
blanket_coolant_cell = openmc.Cell(region=blanket_coolant_region) # your code here
blanket_breeder_cell  = openmc.Cell(region=blanket_breeder_region) # your code here
blanket_reflector_cell = openmc.Cell(region=blanket_reflector_region) # your code here

my_geometry = openmc.Geometry([
    central_column_cell,
    central_column_coolant_cell,
    central_column_fw_cell,
    inner_vessel_cell,
    blanket_fw_cell,
    blanket_coolant_cell,
    blanket_breeder_cell,
    blanket_reflector_cell,
])

# %% [markdown]
# Task 6 - plot the geometry

# %%
# your code here

# %% [markdown]
# Task 7 - plot the source location and energy

# %%
# the distribution of radius is just a single value
radius = openmc.stats.Discrete([300], [1])
# the distribution of source z values is just a single value
z_values = openmc.stats.Discrete([0], [1])
# the distribution of source azimuthal angles values is a uniform distribution between 0 and 2 Pi
angle = openmc.stats.Uniform(a=0., b=2* 3.14159265359)
# initialises a ring source using the three distributions and a radius
my_source = openmc.IndependentSource(
    space=openmc.stats.CylindricalIndependent(r=radius, phi=angle, z=z_values, origin=(0.0, 0.0, 0.0)),
    angle=openmc.stats.Isotropic(),
    energy=openmc.stats.muir(e0=14080000.0, m_rat=5.0, kt=20000.0)
)

my_settings = openmc.Settings()
my_settings.batches = 10
my_settings.particles = 500
my_settings.run_mode = 'fixed source'
my_settings.source = my_source

# plot the source term
# your code goes here

# %% [markdown]
# Task 8 - complete the tally scores and filters

# %%
cell_filter_breeder = openmc.CellFilter(blanket_breeder_cell)
tbr_tally = openmc.Tally(name='TBR')
tbr_tally.filters = [cell_filter_breeder]
# tbr_tally.scores = [# your code here]

cell_filter_blanket_fw_coolant = openmc.CellFilter([
    blanket_breeder_cell,
    blanket_coolant_cell,
    blanket_fw_cell,
    central_column_coolant_cell,
    central_column_fw_cell,
])
blanket_heating_tally = openmc.Tally(name='heating')
blanket_heating_tally.filters = [cell_filter_blanket_fw_coolant]
blanket_heating_tally.scores = ['heating']

# material_filter_conductor = openmc.MaterialFilter('# your code here')
conductor_damage_tally = openmc.Tally(name='conductor_damage')
# conductor_damage_tally.filters = [# your code here]
# conductor_damage_tally.scores = [# your code here]

my_tallies = openmc.Tallies([tbr_tally, blanket_heating_tally, conductor_damage_tally])

# %%
model = openmc.Model(my_geometry, my_materials, my_settings, my_tallies)

# removes the old output files
for f in Path('.').glob('*.h5'):
    f.unlink(missing_ok=True)
for f in Path('.').glob('*.xml'):
    f.unlink(missing_ok=True)

# this will need to be run once the code above is fixed.
# sp_filename = model.run()

# %% [markdown]
# Task 9 - complete the code to get the correct tally names

# %%
# sp = openmc.StatePoint(sp_filename)

# tbr_tally = sp.get_tally(name='# Your code here')
# print(f'TBR={tbr_tally.mean.flatten()[0]} with standard deviation of {tbr_tally.std_dev.flatten()[0]}')

# heating_tally = sp.get_tally(name='# Your code here')
# print(f'Heating={heating_tally.mean.flatten()[0]/1e6}MeV per source neutron with standard deviation of {heating_tally.std_dev.flatten()[0]}')

# damage_tally = sp.get_tally(name='# Your code here')
# print(f'damage={damage_tally.mean.flatten()[0]} with standard deviation of {damage_tally.std_dev.flatten()[0]}')
