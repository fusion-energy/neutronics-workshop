# This script simulates D1S method of shut down dose rate
# on a simple model with and one aluminum sphere and one iron sphere.

import openmc
from openmc.deplete import d1s
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import math

import openmc
from pathlib import Path
# Setting the cross section path to the correct location in the docker image.
# If you are running this outside the docker image you will have to change this path to your local cross section path.
openmc.config['cross_sections'] = Path.home() / 'nuclear_data' / 'cross_sections.xml'
# the chain file was downloaded with
# pip install openmc_data
# download_endf_chain -r b8.0
openmc.config['chain_file'] = Path.home() / 'nuclear_data' / 'chain-endf-b8.0.xml'

# We make a iron material which should produce a few activation products
mat_iron = openmc.Material()
mat_iron.add_element("Fe", 1.0)
mat_iron.set_density("g/cm3", 8.0)
mat_iron.volume = 2* (4/3) * math.pi**3

# We make a Al material which should produce a few different activation products
mat_aluminum = openmc.Material()
mat_aluminum.add_element("Al", 1.0)
mat_aluminum.set_density("g/cm3", 2.7)
mat_aluminum.volume = 3* (4/3) * math.pi**3

# First we make a simple geometry with three cells, (two with material)
sphere_surf_1 = openmc.Sphere(r=2, y0=10, x0=-10)
sphere_region_1 = -sphere_surf_1
sphere_cell_1 = openmc.Cell(region=sphere_region_1, fill=mat_iron)

sphere_surf_2 = openmc.Sphere(r=3, y0=-10, x0=10)
sphere_region_2 = -sphere_surf_2
sphere_cell_2 = openmc.Cell(region=sphere_region_2, fill=mat_aluminum)

xplane_surf_1 = openmc.XPlane(x0=-20, boundary_type='vacuum')
xplane_surf_2 = openmc.XPlane(x0=20, boundary_type='vacuum')
yplane_surf_1 = openmc.YPlane(y0=-20, boundary_type='vacuum')
yplane_surf_2 = openmc.YPlane(y0=20, boundary_type='vacuum')
zplane_surf_1 = openmc.ZPlane(z0=-20, boundary_type='vacuum')
zplane_surf_2 = openmc.ZPlane(z0=20, boundary_type='vacuum')
sphere_region_3 = +xplane_surf_1 & -xplane_surf_2 & +yplane_surf_1 & -yplane_surf_2  & +zplane_surf_1 & -zplane_surf_2 & +sphere_surf_1 & +sphere_surf_2  # void space
sphere_cell_3 = openmc.Cell(region=sphere_region_3)


my_geometry = openmc.Geometry([sphere_cell_1, sphere_cell_2, sphere_cell_3])

my_materials = openmc.Materials([mat_iron, mat_aluminum])

# 14MeV neutron source that activates material, located in the center of the geometry
my_source = openmc.IndependentSource()
my_source.space = openmc.stats.Point((0, 0, 0))
my_source.angle = openmc.stats.Isotropic()
my_source.energy = openmc.stats.Discrete([14.06e6], [1])
my_source.particle = "neutron"

# settings for the neutron simulation with decay photons
settings = openmc.Settings()
settings.run_mode = "fixed source"
settings.particles = 1000000
settings.batches = 10
settings.source = my_source
settings.photon_transport = True

# D1S specific setting
settings.use_decay_photons = True


# creates a regular mesh that surrounds the geometry for the tally
mesh = openmc.RegularMesh().from_domain(
    my_geometry,
    dimension=[100, 100, 1],
    # 100 voxels in x and y axis directions and 1 voxel in z as we want a xy plot
)

# adding a dose tally on a regular mesh
# AP, PA, LLAT, RLAT, ROT, ISO are ICRP incident dose field directions, AP is front facing
energies, pSv_cm2 = openmc.data.dose_coefficients(particle="photon", geometry="AP")
dose_filter = openmc.EnergyFunctionFilter(
    energies, pSv_cm2, interpolation="cubic"  # interpolation method recommended by ICRP
)
particle_filter = openmc.ParticleFilter(["photon"])
mesh_filter = openmc.MeshFilter(mesh)
dose_tally = openmc.Tally()
dose_tally.filters = [particle_filter, mesh_filter, dose_filter]
dose_tally.scores = ["flux"]
dose_tally.name = "photon_dose_on_mesh"

tallies = openmc.Tallies([dose_tally])

model = openmc.Model(my_geometry, my_materials, settings, tallies)

d1s.prepare_tallies(model=model)

output_path = model.run()

# This section defines the neutron pulse schedule.
# Warning, be sure to add sufficient timesteps and run the neutron simulation with enough 
# batches/particles as the solver can produce unstable results otherwise.
timesteps_and_source_rates = [
    (1, 1e18),  # 1 second
    (60*60, 0),  # 1 hour
    (60*60, 0),  # 2 hour
    (60*60, 0),  # 3 hour
    (60*60, 0),  # 4 hour
    (60*60, 0),  # 5 hour
    (60*60, 0),  # 6 hour
    (60*60, 0),  # 7 hour
    (60*60, 0),  # 8 hour
    (60*60, 0),  # 9 hour
    (60*60, 0),  # 10 hour
]

timesteps = [item[0] for item in timesteps_and_source_rates]
source_rates = [item[1] for item in timesteps_and_source_rates]

# get_radionuclides
radionuclides = d1s.prepare_tallies(model)

# Compute time correction factors based on irradiation schedule
time_factors = d1s.time_correction_factors(
    nuclides=radionuclides,
    timesteps=timesteps,
    source_rates=source_rates,
    timestep_units = 's'
)

# Get tally from statepoint
with openmc.StatePoint(output_path) as sp:
    dose_tally_from_sp = sp.get_tally(name='photon_dose_on_mesh')



# tally.mean is in units of pSv-cm3/source neutron
# multiplication by neutrons_per_second changes units to neutron to pSv-cm3/second
neutrons_per_second = 1e8

# multiplication by pico_to_milli converts from (pico) pSv/second to (milli) mSv/second
pico_to_milli = 1e-9

# multiplication by mesh element volume converts from dose-cm3/second to dose/second
volume_normalization = mesh.volumes[0][0][0]

for i_cool in range(1, len(timesteps)):  # missing the first timestep as it is the irradiation step

    # Apply time correction factors
    corrected_tally = d1s.apply_time_correction(
        tally=dose_tally_from_sp,
        time_correction_factors=time_factors,
        index=i_cool,
        sum_nuclides=True
    )
    
    # this section simply gets the maximum value of the mean tally across all time steps
    # and uses this to set the max value of the color bar in the plots
    if i_cool == 1:
        max_tally_value = max(corrected_tally.mean).flatten()
        scaled_max_tally_value = (max_tally_value * pico_to_milli * neutrons_per_second) / volume_normalization

    # get a slice of mean values on the xy basis mid z axis
    corrected_tally_mean = corrected_tally.get_reshaped_data(value='mean', expand_dims=True).squeeze()
    # create a plot of the mean flux values
    
    scaled_corrected_tally_mean = (corrected_tally_mean * pico_to_milli * neutrons_per_second) / volume_normalization
    
    plt.imshow(
        X=scaled_corrected_tally_mean.T,
        origin="lower",
        extent=mesh.bounding_box.extent['xy'],
        norm=LogNorm(vmin=10e5, vmax=scaled_max_tally_value)
    )

    plt.xlabel("x [cm]")
    plt.ylabel("y [cm]")
    plt.colorbar(label="Dose [milli Sv per second]")
    plt.title(f"Dose Rate at time {round(sum(timesteps[1:i_cool+1])/(60*60),2)} hours after irradiation")
    plt.savefig(f'shut_down_dose_map_timestep_{i_cool}.png')
    plt.close()
