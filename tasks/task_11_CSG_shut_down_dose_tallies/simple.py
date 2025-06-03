import numpy as np
import openmc
import openmc.deplete
from pathlib import Path
import math
from matplotlib.colors import LogNorm
import matplotlib.pyplot as plt


# Setting the cross section path to the correct location in the docker image.
# If you are running this outside the docker image you will have to change this path to your local cross section path.
openmc.config['cross_sections'] = Path.home() / 'nuclear_data' / 'cross_sections.xml'
# the chain file was downloaded with
# pip install openmc_data
# download_endf_chain -r b8.0
openmc.config['chain_file'] = Path.home() / 'nuclear_data' / 'chain-endf-b8.0.xml'


statepoints_folder = Path('statepoints_folder')
statepoints_folder.mkdir(exist_ok=True)

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


# First we make a simple geometry with three cells, (two with material)
sphere_surf_1 = openmc.Sphere(r=iron_sphere_radius, z0=10)

sphere_region_1 = -sphere_surf_1

sphere_cell_1 = openmc.Cell(region=sphere_region_1,fill = mat_iron)

box = openmc.model.RectangularParallelepiped(
    xmin=-20, xmax=20, ymin=-20, ymax=20, zmin=-20, zmax=20, boundary_type="vacuum"
)
box_cell = openmc.Cell(region=-box & +sphere_surf_1)

my_geometry = openmc.Geometry([sphere_cell_1, box_cell])


plot = my_geometry.plot(basis='xz')
plt.savefig('xz_geometry_plot.png')

my_materials = openmc.Materials([mat_iron])

# 14MeV neutron source that activates material
my_source = openmc.IndependentSource()
my_source.space = openmc.stats.Point((0, 0, 0))
my_source.angle = openmc.stats.Isotropic()
my_source.energy = openmc.stats.Discrete([14.06e6], [1])
my_source.particle = "neutron"

# settings for the neutron simulation(s)
my_neutron_settings = openmc.Settings()
my_neutron_settings.run_mode = "fixed source"
my_neutron_settings.particles = 1000
my_neutron_settings.batches = 2
my_neutron_settings.source = my_source
my_neutron_settings.photon_transport = False

# # Create mesh which will be used for material segmentation and activation and gamma sources
regular_mesh = openmc.RegularMesh().from_domain(
    my_geometry, # the corners of the mesh are being set automatically to surround the geometry
    dimension=[10,10,10] # 10
)

model_neutron = openmc.Model(my_geometry, my_materials, my_neutron_settings)

# # model_neutron.export_to_xml(directory=statepoints_folder/ "neutrons")
# # model_neutron.export_to_xml()

all_nuclides = my_geometry.get_all_nuclides()

# # Determine material volumes in each mesh element
vols = regular_mesh.material_volumes(model_neutron, n_samples=10_000,max_materials=4)
# and use result to create a
# MeshMaterialFilter with corresponding bins
mmf = openmc.MeshMaterialFilter.from_volumes(mesh=regular_mesh, volumes=vols)

mesh_indices_with_volumes = [int(i[0]) for i in mmf.bins]
# # this does perform transport but just to get the flux and micro xs
# print(f'running neutron transport to activate materials')
flux_in_each_mesh_voxel, all_micro_xs = openmc.deplete.get_microxs_and_flux(
    model=model_neutron,
    domains=mmf,
    energies=[0,30e6],
    nuclides=all_nuclides,
    chain_file=openmc.config['chain_file'],
)

# no longer using this function as we can make the homogenized materials from the MeshMaterialFilter.from_volumes
# mixed_materials_in_each_mesh_voxel = regular_mesh.get_homogenized_materials(model_neutron, n_samples=1_000_000, include_void=False)

# this section makes a mixed material for each voxel
all_materials = my_geometry.get_all_materials()
mixed_materials_in_each_mesh_voxel = []
for i in range(regular_mesh.num_mesh_cells):
    mix_fractions = vols.by_element(i)
    materials = []
    fracts = []

    for mat_id, mat_volume in mix_fractions:
        if mat_id is not None:
            material = all_materials[mat_id]
            materials.append(material)
            fracts.append(mat_volume)

    if len(materials) > 0:
        mixed_material = openmc.Material.mix_materials(
            materials, fracts, 'vo'
        )
        mixed_material.volume = sum(fracts)
        mixed_materials_in_each_mesh_voxel.append(mixed_material)

# # constructing the operator, note we pass in the flux and micro xs
operator = openmc.deplete.IndependentOperator(
    materials=openmc.Materials(mixed_materials_in_each_mesh_voxel),
    fluxes=[flux[0] for flux in flux_in_each_mesh_voxel],
    micros=all_micro_xs,
    reduce_chain_level=5,
    normalization_mode="source-rate",
)

# This section defines the neutron pulse schedule.
# If the method made use of the CoupledOperator then there would need to be a
# transport simulation for each timestep. However as the IndependentOperator is
# used then just a single transport simulation is done, thus speeding up the
# simulation considerably and is a reasonable approximation as the material burn-up
# is not as large enough to perturb the neutron spectra significant.
# This pulse schedule has 1 second pulses of neutrons then a days of cooling steps in 1 hour blocks
hour_in_seconds = 60*60
timesteps_and_source_rates = [
    (1, 1e18),  # 1 second of 1e18 neutrons/second
    (2*hour_in_seconds, 0),  # 2 hours after shut down
    (2*hour_in_seconds, 0),  # 4 hours after shut down
#     (2*hour_in_seconds, 0),  # 6 hours after shut down
#     (2*hour_in_seconds, 0),  # 8 hours after shut down
#     (2*hour_in_seconds, 0),  # 10 hours after shut down
#     (2*hour_in_seconds, 0),  # 12 hours after shut down
#     (2*hour_in_seconds, 0),  # 14 hours after shut down
#     (2*hour_in_seconds, 0),  # 16 hours after shut down
#     (2*hour_in_seconds, 0),  # 18 hours after shut down
#     (2*hour_in_seconds, 0),  # 20 hours after shut down
#     (2*hour_in_seconds, 0),  # 22 hours after shut down
#     (2*hour_in_seconds, 0),  # 24 hours after shut down
]

timesteps = [item[0] for item in timesteps_and_source_rates]
source_rates = [item[1] for item in timesteps_and_source_rates]

integrator = openmc.deplete.PredictorIntegrator(
    operator=operator,
    timesteps=timesteps,
    source_rates=source_rates,
    timestep_units='s',
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
my_gamma_settings.particles = 10000

# First we add make dose tally on a regular mesh


# adding a dose tally on a regular mesh
# AP, PA, LLAT, RLAT, ROT, ISO are ICRP incident dose field directions, AP is front facing
energies, pSv_cm2 = openmc.data.dose_coefficients(particle="photon", geometry="AP")
dose_filter = openmc.EnergyFunctionFilter(
    energies, pSv_cm2, interpolation="cubic"  # interpolation method recommended by ICRP
)
particle_filter = openmc.ParticleFilter(["photon"])
mesh_filter = openmc.MeshFilter(regular_mesh)
dose_tally = openmc.Tally()
dose_tally.filters = [mesh_filter, dose_filter, particle_filter]
dose_tally.scores = ["flux"]
dose_tally.name = "photon_dose_on_mesh"

my_gamma_tallies = openmc.Tallies([dose_tally])

cells = model_neutron.geometry.get_all_cells()

results = openmc.deplete.Results(statepoints_folder / "neutrons" / "depletion_results.h5")


blank_source = openmc.IndependentSource()
blank_source.strength = 0

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

            photon_sources_for_timestep.append(source)
            strengths_for_timestep.append(strength)

    index_to_obj = dict(zip(mesh_indices_with_volumes, photon_sources_for_timestep))
    photon_sources_for_timestep = [index_to_obj.get(i, blank_source) for i in range(regular_mesh.num_mesh_cells)]
    
    mesh_source = openmc.MeshSource(
        regular_mesh, photon_sources_for_timestep
    )

    # you have options for the normalization of the source.
    # you could set the mesh_source.strength to the total Bq of all the sources in that time step
    mesh_source.strength = cumulative_strength_for_time_step
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

for i_cool in range(1, len(timesteps)): # skipping the first depletion step as we just want the part where the machine is off for the shut down dose rate
    with openmc.StatePoint(statepoints_folder / "photons" / f"photon_at_time_{i_cool}" / f'statepoint.{my_gamma_settings.batches}.h5') as statepoint:
        my_mesh_tally_result = statepoint.get_tally(name="photon_dose_on_mesh")


        # this part of the script plots the images
        tally_slice = my_mesh_tally_result.get_slice(scores=['flux'])

        tally_data = tally_slice.get_reshaped_data(
            expand_dims=True, value='mean'
        ).squeeze()

        # gets a 2d slice of data to later plot
        data_slice = tally_data[:,:,5]

        # tally.mean is in units of pSv-cm3/source neutron
        # multiplication by neutrons_per_pulse changes units to neutron to pSv-cm3/pulse
        neutrons_per_pulse = 1e8  # units of neutrons per pulse

        # multiplication by pico_to_milli converts from (pico) pSv-cm3/pulse to (milli) mSv-cm3/pulse
        pico_to_milli = 1e-9

        # dividing by the mesh volume gives the units of mSv/pulse
        mesh_voxel_volume = regular_mesh.volumes[0][0][0]

        # converts the units
        data_slice = (data_slice * neutrons_per_pulse * pico_to_milli) / mesh_voxel_volume

        meter_scaled_extent = [i/100 for i in my_geometry.bounding_box.extent['xy']]

        # First plot (ax1)
        fig, ax1 = plt.subplots(figsize=(10, 8))
        # plot_1 = ax1.imshow(
        #     np.rot90(data_slice, -3),
        #     extent=meter_scaled_extent,
        #     interpolation=None,
        #     norm=LogNorm(
        #         vmin=np.min(data_slice[data_slice > 0]),  # Smallest non-zero value
        #         vmax=np.max(data_slice),
        #     ),
        # )
        ax1.set_xlabel("X (cm)")
        ax1.set_ylabel("Y (cm)")
        # cbar = plt.colorbar(plot_1, ax=ax1)
        # cbar.set_label("Dose [milli Sv per pulse]")  # Label for the color bar

        X = np.linspace(meter_scaled_extent[0], meter_scaled_extent[1], data_slice.shape[1])
        Y = np.linspace(meter_scaled_extent[2], meter_scaled_extent[3], data_slice.shape[0])
        X, Y = np.meshgrid(X, Y)

        # Second plot (ax2) overlaid on ax1
        ax2 = my_geometry.plot(
            outline='only',
            extent=my_geometry.bounding_box.extent['xy'],
            # axes=ax1,  # Use the same axis as ax1
            color_by='material',
            axis_units='m',
            pixels=10_000_00,  #avoids rounded corners on outline
        )
        # ax2.set_title(f"Dose map with at time step {i_cool}")
        # ax2.set_xlim(ax1.get_xlim())
        # ax2.set_ylim(ax1.get_ylim())
        # ax2.set_aspect(ax1.get_aspect())  # Match aspect ratio

        # Show the combined plot
        # plt.show()
        plt.savefig(f'dose_map_{str(i_cool).zfill(2)}.png')
