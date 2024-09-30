# This script simulates R2S method of shut down dose rate
# on a simple sphere model.

import numpy as np
import openmc
import openmc.deplete
from pathlib import Path
import math
from matplotlib.colors import LogNorm

# users might want to change these to use specific xml files to use particular decay data or transport cross sections
# the chain file was downloaded with
# pip install openmc_data
# download_endf_chain -r b8.0
openmc.config['chain_file'] = '/nuclear_data/chain-endf-b8.0.xml'
openmc.config['cross_sections'] = '/nuclear_data/cross_sections.xml'

# a few user settings
# Set up the folders to save all the data in
n_particles = 1_00000
p_particles = 1_000
statepoints_folder = Path('statepoints_folder')


al_sphere_radius = 7
iron_sphere_radius = 4

# We make a iron material which should produce a few activation products
mat_iron = openmc.Material()
mat_iron.id = 1
mat_iron.add_nuclide("Fe56", 1.0)
mat_iron.add_nuclide("Fe57", 1.0)
mat_iron.set_density("g/cm3", 7.7)
# must set the depletion to True to deplete the material
mat_iron.depletable = True
# volume must set the volume as well as openmc calculates number of atoms
mat_iron.volume = (4 / 3) * math.pi * math.pow(iron_sphere_radius, 3)

# We make a Al material which should produce a few different activation products
mat_aluminum = openmc.Material()
mat_aluminum.id = 2
mat_aluminum.add_element("Al", 1.0)
mat_aluminum.set_density("g/cm3", 2.7)
# must set the depletion to True to deplete the material
mat_aluminum.depletable = True
# volume must set the volume as well as openmc calculates number of atoms
mat_aluminum.volume = (4 / 3) * math.pi * math.pow(al_sphere_radius, 3)



# First we make a simple geometry with three cells, (two with material)
sphere_surf_1 = openmc.Sphere(r=iron_sphere_radius, z0=10)
sphere_surf_2 = openmc.Sphere(r=al_sphere_radius, z0=-5)

sphere_region_1 = -sphere_surf_1
sphere_region_2 = -sphere_surf_2

sphere_cell_1 = openmc.Cell(region=sphere_region_1,fill = mat_aluminum)
sphere_cell_2 = openmc.Cell(region=sphere_region_2,fill = mat_iron)

box = openmc.model.RectangularParallelepiped(
    xmin=-20, xmax=20, ymin=-20, ymax=20, zmin=-20, zmax=20, boundary_type="vacuum"
)
box_cell = openmc.Cell(region=-box & +sphere_surf_1, fill=mat_aluminum)

my_geometry = openmc.Geometry([sphere_cell_1, sphere_cell_2, box_cell])

# to plot the geometry uncomment this line
# plot = my_geometry.plot(basis='xz')
# import matplotlib.pyplot as plt
# plt.show()

my_materials = openmc.Materials([mat_iron, mat_aluminum])

# 14MeV neutron source that activates material
my_source = openmc.IndependentSource()
my_source.space = openmc.stats.Point((0, 0, 0))
my_source.angle = openmc.stats.Isotropic()
my_source.energy = openmc.stats.Discrete([14.06e6], [1])
my_source.particle = "neutron"

# settings for the neutron simulation(s)
my_neutron_settings = openmc.Settings()
my_neutron_settings.run_mode = "fixed source"
my_neutron_settings.particles = n_particles
my_neutron_settings.batches = 10
my_neutron_settings.source = my_source
my_neutron_settings.photon_transport = False

# Create mesh which will be used for material segmentation and activation and gamma sources
regular_mesh = openmc.RegularMesh().from_domain(
    my_geometry, # the corners of the mesh are being set automatically to surround the geometry
    dimension=[10,10,10] # 10
)

model_neutron = openmc.Model(my_geometry, my_materials, my_neutron_settings)

model_neutron.export_to_xml(directory=statepoints_folder/ "neutrons")
model_neutron.export_to_xml()

all_nuclides = []
for material in my_geometry.get_all_materials().values():
    for nuclide in material.get_nuclides():
        if nuclide not in all_nuclides:
            all_nuclides.append(nuclide)

# this does perform transport but just to get the flux and micro xs
print(f'running neutron transport to activate materials')
flux_in_each_mesh_voxel, all_micro_xs = openmc.deplete.get_microxs_and_flux(
    model=model_neutron,
    domains=regular_mesh,
    energies=[0,30e6],
    nuclides=all_nuclides,
    chain_file=openmc.config['chain_file']
)

print(f'running transport to sample within the mesh and get material fractions')
mixed_materials_in_each_mesh_voxel = regular_mesh.get_homogenized_materials(model_neutron, n_samples=1_000_000)

# constructing the operator, note we pass in the flux and micro xs
operator = openmc.deplete.IndependentOperator(
    materials=openmc.Materials(mixed_materials_in_each_mesh_voxel),
    fluxes=[flux[0] for flux in flux_in_each_mesh_voxel],
    micros=all_micro_xs,
    reduce_chain=True,  # reduced to only the isotopes present in depletable materials and their possible progeny
    reduce_chain_level=4,
    normalization_mode="source-rate"
)

# This section defines the neutron pulse schedule.
# If the method made use of the CoupledOperator then there would need to be a
# transport simulation for each timestep. However as the IndependentOperator is
# used then just a single transport simulation is done, thus speeding up the
# simulation considerably.
# This pulse schedule has 1 second pulses of neutrons then a days of cooling steps in 1 hour blocks
hour_in_seconds = 60*60
timesteps_and_source_rates = [
    (1, 1e18),  # 1 second of 1e18 neutrons/second
    (2*hour_in_seconds, 0),  # 2 hours after shut down
    (2*hour_in_seconds, 0),  # 4 hours after shut down
    (2*hour_in_seconds, 0),  # 6 hours after shut down
    (2*hour_in_seconds, 0),  # 8 hours after shut down
    (2*hour_in_seconds, 0),  # 10 hours after shut down
    (2*hour_in_seconds, 0),  # 12 hours after shut down
    (2*hour_in_seconds, 0),  # 14 hours after shut down
    (2*hour_in_seconds, 0),  # 16 hours after shut down
    (2*hour_in_seconds, 0),  # 18 hours after shut down
    (2*hour_in_seconds, 0),  # 20 hours after shut down
    (2*hour_in_seconds, 0),  # 22 hours after shut down
    (2*hour_in_seconds, 0),  # 24 hours after shut down
]

timesteps = [item[0] for item in timesteps_and_source_rates]
source_rates = [item[1] for item in timesteps_and_source_rates]

integrator = openmc.deplete.PredictorIntegrator(
    operator=operator,
    timesteps=timesteps,
    source_rates=source_rates,
    timestep_units='s'
)

# this runs the depletion calculations for the timesteps
# this does the neutron activation simulations and produces a depletion_results.h5 file
integrator.integrate(
    path=statepoints_folder / "neutrons" / "depletion_results.h5"
)

# Now we have done the neutron activation simulations we can start the work needed for the decay gamma simulations.

my_gamma_settings = openmc.Settings()
my_gamma_settings.run_mode = "fixed source"
my_gamma_settings.batches = 100
my_gamma_settings.particles = p_particles

# First we add make dose tally on a regular mesh

# # creates a regular mesh that surrounds the geometry
mesh_photon = openmc.RegularMesh().from_domain(
    my_geometry,
    dimension=[20, 20, 20],  # 20 voxels in each axis direction (x, y, z)
)

# adding a dose tally on a regular mesh
# AP, PA, LLAT, RLAT, ROT, ISO are ICRP incident dose field directions, AP is front facing
energies, pSv_cm2 = openmc.data.dose_coefficients(particle="photon", geometry="AP")
dose_filter = openmc.EnergyFunctionFilter(
    energies, pSv_cm2, interpolation="cubic"  # interpolation method recommended by ICRP
)
particle_filter = openmc.ParticleFilter(["photon"])
mesh_filter = openmc.MeshFilter(mesh_photon)
dose_tally = openmc.Tally()
dose_tally.filters = [mesh_filter, dose_filter, particle_filter]
dose_tally.scores = ["flux"]
dose_tally.name = "photon_dose_on_mesh"

my_gamma_tallies = openmc.Tallies([dose_tally])

cells = model_neutron.geometry.get_all_cells()

results = openmc.deplete.Results(statepoints_folder / "neutrons" / "depletion_results.h5")

# this section makes the photon sources from each active material at each
# timestep and runs the photon simulations
# range starts at 1 to skip the first step as that is an irradiation step and there is no
for i_cool in range(1, len(timesteps)):
    # we can loop through the materials in each step
    # from the material ID we can get the mesh voxel id
    # then we can make a MeshSource
    # https://docs.openmc.org/en/develop/pythonapi/generated/openmc.MeshSource.html
    # decay gamma source from the stable material at that time
    # also there are no decay products in this first timestep for this model
    photon_sources_for_timestep = []
    strengths_for_timestep = []
    print(f"making photon source for timestep {i_cool}")
    step = results[i_cool]
    # activated_mat_ids = step.volume.keys()
    activated_mat_ids = step.index_mat
    # print(activated_mat_ids)
    cumulative_strength_for_time_step = 0 # in Bq
    for activated_mat_id in activated_mat_ids:
        # gets the energy and probabilities for the 
        activated_mat = step.get_material(activated_mat_id)
        energy = activated_mat.get_decay_photon_energy(
            clip_tolerance = 1e-6,  # cuts out a small fraction of the very low energy (and hence negligible dose contribution) photons
            units = 'Bq',
        )
        strength = energy.integral()
        cumulative_strength_for_time_step = cumulative_strength_for_time_step +strength
        if strength > 0.:  
            source = openmc.IndependentSource(
                energy=energy,
                particle="photon",
                strength=strength
            )
        else:
            print('source has no gammas')
            source = openmc.IndependentSource() # how to make an empty source, source strength is set to 0

        photon_sources_for_timestep.append(source)
        strengths_for_timestep.append(strength)
    
    mesh_source = openmc.MeshSource(
        regular_mesh, photon_sources_for_timestep
    )

    # you have options for the normalization of the source.
    # you could set the mesh_source.strength to the total Bq of all the sources in that time step
    # mesh_source.strength = cumulative_strength_for_time_step
    # then use mesh_source.normalize_source_strengths() to update all element source strengths such that they sum to 1.0.
    # or
    # you can leave it so the individual sources have their own strength in Bq
    # perhaps best to experiment here and check the answers, do let me know if you find one option better than the others

    my_gamma_settings.source = mesh_source
    model_gamma = openmc.Model(my_geometry, my_materials, my_gamma_settings, my_gamma_tallies)

    print(f'running gamma transport on stimestep {i_cool}')
    model_gamma.run(cwd=statepoints_folder / "photons" / f"photon_at_time_{i_cool}")

# this part post processes the results to get a dose map for each time step
pico_to_micro = 1e-6
seconds_to_hours = 60*60

# You may wish to plot the dose tally on a mesh, this package makes it easy to include the geometry with the mesh tally
from openmc_regular_mesh_plotter import plot_mesh_tally
for i_cool in range(1, len(timesteps)): # skipping the first depletion step as we just want the part where the machine is off for the shut down dose rate
    with openmc.StatePoint(statepoints_folder / "photons" / f"photon_at_time_{i_cool}" / f'statepoint.{my_gamma_settings.batches}.h5') as statepoint:
        photon_tally = statepoint.get_tally(name="photon_dose_on_mesh")
        # normalizing this tally is a little different to other examples as the source strength has been using units of photons per second.
        # tally.mean is in units of pSv-cm3/source photon.
        # as source strength is in photons_per_second this changes units to pSv-/second
        # multiplication by pico_to_micro converts from (pico) pSv/s to (micro) uSv/s
        # dividing by mesh voxel volume is not needed as the volume_normalization in the plotting function does this
        scaling_factor = (seconds_to_hours * pico_to_micro)
        print('max',(max(photon_tally.mean.flatten())*scaling_factor)/mesh_photon.volumes[0][0][0])
        print('min',(min(photon_tally.mean.flatten())*scaling_factor)/mesh_photon.volumes[0][0][0])
        plot = plot_mesh_tally(
            tally=photon_tally,
            basis="xz",
            score='flux', # only one tally so could leave this unspecified
            value="mean",
            colorbar_kwargs={
                'label': "Decay photon dose [µSv/h]",
            },
            norm=LogNorm(), # TODO find the bounds automatically in a loop above this section
            volume_normalization=True,  # this divides by voxel volume which is not done in the scaling_factor
            scaling_factor=scaling_factor,
            outline=True,
            geometry = my_geometry
        )
        plot.title.set_text(f"timestep {sum(timesteps[1:i_cool])/(60*60)} hours after shut down")
        plot.figure.savefig(f'mesh_shut_down_dose_map_timestep_{str(i_cool).zfill(3)}')
