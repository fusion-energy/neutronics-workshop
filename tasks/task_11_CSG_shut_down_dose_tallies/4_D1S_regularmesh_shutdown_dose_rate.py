# This script simulates R2S method of shut down dose rate
# on a simple sphere model.

import openmc
from openmc.deplete import d1s
from pathlib import Path
from matplotlib.colors import LogNorm

import openmc
from pathlib import Path
# Setting the cross section path to the correct location in the docker image.
# If you are running this outside the docker image you will have to change this path to your local cross section path.
openmc.config['cross_sections'] = Path.home() / 'nuclear_data' / 'cross_sections.xml'
# the chain file was downloaded with
# pip install openmc_data
# download_endf_chain -r b8.0
openmc.config['chain_file'] = Path.home() / 'nuclear_data' / 'chain-endf-b8.0.xml'


# First we make a simple geometry with three cells, (two with material)
sphere_surf_1 = openmc.Sphere(r=20, boundary_type="vacuum")
sphere_surf_2 = openmc.Sphere(r=1, y0=10)
sphere_surf_3 = openmc.Sphere(r=5, z0=10)

sphere_region_1 = -sphere_surf_1 & +sphere_surf_2 & +sphere_surf_3  # void space
sphere_region_2 = -sphere_surf_2
sphere_region_3 = -sphere_surf_3

sphere_cell_1 = openmc.Cell(region=sphere_region_1)
sphere_cell_2 = openmc.Cell(region=sphere_region_2)
sphere_cell_3 = openmc.Cell(region=sphere_region_3)

# We make a iron material which should produce a few activation products
mat_iron = openmc.Material()
mat_iron.add_element("Fe", 1.0)
mat_iron.set_density("g/cm3", 7.7)

# We make a Al material which should produce a few different activation products
mat_aluminum = openmc.Material()
mat_aluminum.add_element("Al", 1.0)
mat_aluminum.set_density("g/cm3", 2.7)

my_geometry = openmc.Geometry([sphere_cell_1, sphere_cell_2, sphere_cell_3])

my_materials = openmc.Materials([mat_iron, mat_aluminum])

# 14MeV neutron source that activates material
my_source = openmc.IndependentSource()
my_source.space = openmc.stats.Point((0, 0, 0))
my_source.angle = openmc.stats.Isotropic()
my_source.energy = openmc.stats.Discrete([14.06e6], [1])
my_source.particle = "neutron"

# settings for the neutron simulation(s)
settings = openmc.Settings()
settings.run_mode = "fixed source"
settings.particles = 1000
settings.batches = 10
settings.source = my_source
settings.photon_transport = True

# D1S specific setting
settings.use_decay_photons = True


# creates a regular mesh that surrounds the geometry
mesh = openmc.RegularMesh().from_domain(
    my_geometry,
    dimension=[10, 10, 10],  # 10 voxels in each axis direction (x, y, z)
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
dose_tally.filters = [particle_filter] # TODO add more filters dose_filter mesh_filter
dose_tally.scores = ["flux"]
dose_tally.name = "photon_dose_on_mesh"

tallies = openmc.Tallies([dose_tally])

model = openmc.Model(my_geometry, my_materials, settings, tallies)

d1s.prepare_tallies(model=model)

output_path = model.run()

# This section defines the neutron pulse schedule.
# Warning, be sure to add sufficient timesteps and run the neutron simulation with enough 
# batches/particles as the solver can produce unstable results otherwise. I typically plot
# activity of gamma sources as a function of step to see if they decay according to the
# half lives of the main unstable nuclides, this helps me check the solution is stable.
timesteps_and_source_rates = [
    (1, 1e18),  # 1 second
    (1, 1e18),  # 1 second
    (60*60, 0),  # 1 hour
    (60*60, 0),  # 2 hour
    (60*60, 0),  # 3 hour
    (60*60, 0),  # 4 hour
    (60*60, 0),  # 5 hour
]

timesteps = [item[0] for item in timesteps_and_source_rates]
source_rates = [item[1] for item in timesteps_and_source_rates]

# get_radionuclides
radionuclides = d1s.prepare_tallies(model)

# Compute time correction factors based on irradiation schedule
time_factors = d1s.time_correction_factors(
    nuclides=radionuclides,
    timesteps=timesteps,
    source_rates=source_rates
)

# Get tally from statepoint
with openmc.StatePoint(output_path) as sp:
    dose_tally_from_sp = sp.get_tally(name='photon_dose_on_mesh')


for i_cool in range(len(timesteps)):

    # Apply time correction factors
    corrected_tally = d1s.apply_time_correction(
        tally=dose_tally_from_sp,
        time_correction_factors=time_factors,
        index=i_cool,
        sum_nuclides=True
    )
    
    print(corrected_tally.mean)  # <---- this gives zero values


    # normalising this tally is a little different to other examples as the source strength has been using units of photons per second.
    # tally.mean is in units of pSv-cm3/source photon.
    # as source strength is in photons_per_second this changes units to pSv-/second

    # multiplication by pico_to_micro converts from (pico) pSv/s to (micro) uSv/s
    # dividing by mesh voxel volume cancles out the cm3 units
    # could do the mesh volume scaling on the plot and vtk functions but doing it here instead
    pico_to_micro = 1e-6
    seconds_to_hours = 60*60
    scaling_factor = (seconds_to_hours * pico_to_micro) / mesh.volumes[0][0][0]

    # # You may wish to plot the dose tally on a mesh, this package makes it easy to include the geometry with the mesh tally
    # from openmc_regular_mesh_plotter import plot_mesh_tally
    # plot = plot_mesh_tally(
    #         tally=corrected_tally,
    #         basis="xz",
    #         # score='flux', # only one tally so can make use of default here
    #         value="mean",
    #         colorbar_kwargs={
    #             'label': "Decay photon dose [µSv/h]",
    #         },
    #         # norm=LogNorm(),
    #         volume_normalization=False,  # this is done in the scaling_factor
    #         scaling_factor=scaling_factor,
    #     )
    # plot.figure.savefig(f'shut_down_dose_map_timestep_{i_cool}')
