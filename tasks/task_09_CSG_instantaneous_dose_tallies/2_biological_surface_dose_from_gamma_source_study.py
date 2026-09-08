# %% [markdown]
# ---
# title: Biological dose on a surface as a function of distance
# ---

# %% [markdown]
# Sometimes it is useful to have the dose as function of distance from the source. The following example builds on the previous example by finding the dose as a function of distance.
#
# The geometry is a little more complex in this example as we need additional surfaces to tally on.

# %% [markdown]
# The following section makes the geometry, assigns materials and plots the result.
#
# This is the similar to the previous task geometry, but this time we have nested spheres which will be used to tally the dose on.

# %% [markdown]
# First import OpenMC and configure the nuclear data path

# %%
import openmc
from pathlib import Path
# Setting the cross section path to the correct location in the docker image.
# If you are running this outside the docker image you will have to change this path to your local cross section path.
openmc.config['cross_sections'] = Path.home() / 'nuclear_data' / 'cross_sections.xml'

# %%
import openmc

# dimensions are in cm
height = 150
outer_radius = 74.5 / 2
thickness = 1.5

outer_cylinder = openmc.ZCylinder(r=outer_radius)
inner_cylinder = openmc.ZCylinder(r=outer_radius-thickness)
inner_top = openmc.ZPlane(z0=height*0.5)
inner_bottom = openmc.ZPlane(z0=-height*0.5)
outer_top = openmc.ZPlane(z0=(height*0.5)+thickness)
outer_bottom = openmc.ZPlane(z0=(-height*0.5)-thickness)

# these spheres are used to tally the dose
sphere_1 = openmc.Sphere(r=200)
sphere_2 = openmc.Sphere(r=250)
sphere_3 = openmc.Sphere(r=300)
sphere_4 = openmc.Sphere(r=350)
sphere_5 = openmc.Sphere(r=400)
sphere_6 = openmc.Sphere(r=450)
sphere_7 = openmc.Sphere(r=500)
# can't actually tally on the end of universe sphere so sphere_8 is not in the tally
sphere_8 = openmc.Sphere(r=501, boundary_type='vacuum')

steel = openmc.Material()
steel.set_density('g/cm3', 7.75)
steel.add_element('Fe', 0.95, percent_type='wo')
steel.add_element('C', 0.05, percent_type='wo')

my_materials = openmc.Materials([steel])

cylinder_region = -outer_cylinder & +inner_cylinder & -inner_top & +inner_bottom
cylinder_cell = openmc.Cell(region=cylinder_region)
cylinder_cell.fill = steel

top_cap_region = -outer_top & +inner_top & -outer_cylinder
top_cap_cell = openmc.Cell(region=top_cap_region)
top_cap_cell.fill = steel

bottom_cap_region = +outer_bottom & -inner_bottom & -outer_cylinder
bottom_cap_cell = openmc.Cell(region=bottom_cap_region)
bottom_cap_cell.fill = steel

inner_void_region = -inner_cylinder & -inner_top & +inner_bottom
inner_void_cell = openmc.Cell(region=inner_void_region)

# sphere 1 region is below -sphere_1 and not (~) in the other regions
sphere_1_region = -sphere_1
sphere_1_cell = openmc.Cell(
    region= sphere_1_region
    & ~bottom_cap_region
    & ~top_cap_region
    & ~cylinder_region
    & ~inner_void_region
)

sphere_2_region = +sphere_1 & -sphere_2
sphere_2_cell = openmc.Cell(region= sphere_2_region)

sphere_3_region = +sphere_2 & -sphere_3
sphere_3_cell = openmc.Cell(region= sphere_3_region)

sphere_4_region = +sphere_3 & -sphere_4
sphere_4_cell = openmc.Cell(region= sphere_4_region)

sphere_5_region = +sphere_4 & -sphere_5
sphere_5_cell = openmc.Cell(region= sphere_5_region)

sphere_6_region = +sphere_5 & -sphere_6
sphere_6_cell = openmc.Cell(region= sphere_6_region)

sphere_7_region = +sphere_6 & -sphere_7
sphere_7_cell = openmc.Cell(region= sphere_7_region)

sphere_8_region = +sphere_7 & -sphere_8
sphere_8_cell = openmc.Cell(region= sphere_8_region)

my_geometry = openmc.Geometry([
    inner_void_cell, cylinder_cell, top_cap_cell,
    bottom_cap_cell, sphere_1_cell, sphere_2_cell,
    sphere_3_cell, sphere_4_cell,
    sphere_5_cell, sphere_6_cell, sphere_7_cell,
    sphere_8_cell])

# %% [markdown]
# This section plots the geometry and colours it according to cell.

# %%
color_assignment = {sphere_1_cell: 'green',
                    sphere_2_cell: 'brown',
                    sphere_3_cell: 'lime',
                    sphere_4_cell: 'lightgray',
                    sphere_5_cell: 'maroon',
                    sphere_6_cell: 'magenta',
                    sphere_7_cell: 'cyan',
                    sphere_8_cell: 'purple',
                    inner_void_cell: 'grey',
                    bottom_cap_cell: 'red',
                    top_cap_cell: 'blue',
                    cylinder_cell:'yellow',
                   }

plot = my_geometry.plot(basis='xz',  color_by='cell', colors=color_assignment)
plot.figure.savefig('xz-cell.png')

plot = my_geometry.plot(basis='xy',  color_by='cell', colors=color_assignment)
plot.figure.savefig('yz-cell.png')

# %% [markdown]
# This section makes the source, note the use of the Co60 gamma source with two energy levels.

# %%
# Instantiate a Settings object
my_settings = openmc.Settings()
my_settings.batches = 10
my_settings.particles = 500
my_settings.run_mode = 'fixed source'

# Create a gamma point source
source = openmc.IndependentSource(
    space=openmc.stats.Point((0, 0, 0)),
    angle=openmc.stats.Isotropic(),
# This is a Co60 source, see the task on sources to understand it
    energy=openmc.stats.Discrete([1.1732e6,1.3325e6], [0.5, 0.5]),
    particle='photon'
)
my_settings.source = source

energy_bins_p, dose_coeffs_p = openmc.data.dose_coefficients(
    particle='photon',
    geometry='AP'
)

energy_function_filter_p = openmc.EnergyFunctionFilter(
    energy_bins_p,
    dose_coeffs_p
)
energy_function_filter_p.interpolation = 'cubic'  # cubic interpolation is recommended by ICRP

photon_particle_filter = openmc.ParticleFilter(["photon"])

my_tallies = openmc.Tallies()

surfaces_to_tally = [
    sphere_1, sphere_2, sphere_3, sphere_4, sphere_5, sphere_6, sphere_7
]

# this loops adds tallies for each sphere surface
for surface_id, surface in zip(range(1,9), surfaces_to_tally):
    surface_filter = openmc.SurfaceFilter(surface)
    dose_tally = openmc.Tally(name="dose_tally_on_surface_"+str(surface_id))
    dose_tally.scores = ["current"]
    dose_tally.filters = [
        surface_filter,
        photon_particle_filter,
        energy_function_filter_p,
    ]
    my_tallies.append(dose_tally)

# %% [markdown]
# This section runs the simulation.

# %%
# Run OpenMC!
model = openmc.Model(my_geometry, my_materials, my_settings, my_tallies)
for f in Path('.').glob('*.h5'):
    f.unlink(missing_ok=True)
sp_filename = model.run()

# %% [markdown]
# This section loads up the results and post processes them so that the units are more useful.

# %%
import math

# open the results file
with openmc.StatePoint(sp_filename) as sp:

    dose_rates_in_pSv = []
    distances = []
    # access the tally using pandas dataframes
    for surface_id, surface in zip(range(1,9), surfaces_to_tally):
        tally = sp.get_tally(name='dose_tally_on_surface_'+str(surface_id))
        df = tally.get_pandas_dataframe()
        tally_result = df['mean'].sum()
        tally_std_dev = df['std. dev.'].sum()

        # convert from the tally output units of pSv cm² to pSv by dividing by the surface area of the surface
        dose_in_pSv = tally_result / (4 * math.pi * math.pow(surface.r, 2))
        distances.append(surface.r)

        source_activity = 56000  # in decays per second (Bq)
        emission_rate = 2  # the number of gammas emitted per decay which is approximately 2 for Co60
        gamma_per_second = source_activity * emission_rate
        dose_rate_in_pSv = dose_in_pSv * gamma_per_second
    
        dose_rates_in_pSv.append(dose_rate_in_pSv)

# print results
print('The surface dose = ', dose_rates_in_pSv, 'pSv per second')
print('At distances = ', distances)

# %% [markdown]
# This section plots the dose as a function of distance from the source.

# %%
import matplotlib.pyplot as plt
plt.plot(distances, dose_rates_in_pSv, 'o')
plt.ylabel('Dose rates (pSv per second)')
plt.xlabel('Distance (cm)')
plt.savefig('dose_rate_from_co60_cask.svg')

# %% [markdown]
# As expected, the dose decreases as a function of distance from the source.

# %% [markdown]
# **Learning Outcomes for Part 2:**
#
# - Several geometry surfaces can be utilised to obtain a tally result as a function of a physical parameter, such as distance from source.
