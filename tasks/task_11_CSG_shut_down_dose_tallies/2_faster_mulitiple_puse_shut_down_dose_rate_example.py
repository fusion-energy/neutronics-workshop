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
# openmc.config['chain_file'] = '/nuclear_data/chain-endf-b8.0.xml'
# openmc.config['cross_sections'] = 'cross_sections.xml'

# a few user settings
# Set up the folders to save all the data in
n_particles = 1_00000
p_particles = 1_000
statepoints_folder = Path('statepoints_folder')

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
mat_iron.id = 1
mat_iron.add_element("Fe", 1.0)
mat_iron.set_density("g/cm3", 7.7)
# must set the depletion to True to deplete the material
mat_iron.depletable = True
# volume must set the volume as well as openmc calculates number of atoms
mat_iron.volume = (4 / 3) * math.pi * math.pow(sphere_surf_2.r, 3)
sphere_cell_2.fill = mat_iron

# We make a Al material which should produce a few different activation products
mat_aluminum = openmc.Material()
mat_aluminum.id = 2
mat_aluminum.add_element("Al", 1.0)
mat_aluminum.set_density("g/cm3", 2.7)
# must set the depletion to True to deplete the material
mat_aluminum.depletable = True
# volume must set the volume as well as openmc calculates number of atoms
mat_aluminum.volume = (4 / 3) * math.pi * math.pow(sphere_surf_3.r, 3)
sphere_cell_3.fill = mat_aluminum

my_geometry = openmc.Geometry([sphere_cell_1, sphere_cell_2, sphere_cell_3])

my_materials = openmc.Materials([mat_iron, mat_aluminum])

pristine_mat_iron = mat_iron.clone()
pristine_mat_aluminium = mat_aluminum.clone()

# gets the cell ids of any depleted cell
activated_cell_ids = [c.id for c in my_geometry.get_all_material_cells().values() if c.fill.depletable]
print("activated_cell_ids", activated_cell_ids)
all_depletable_cells = [c for _, c in my_geometry.get_all_material_cells().items() if c.fill.depletable is True]
print("depletable_cell_ids", activated_cell_ids)
all_depletable_materials = [c.fill for _, c in my_geometry.get_all_material_cells().items() if c.fill.depletable is True]

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

model_neutron = openmc.Model(my_geometry, my_materials, my_neutron_settings)

hour_in_seconds = 60*60

# This section defines the neutron pulse schedule.
# If the method made use of the CoupledOperator then there would need to be a
# transport simulation for each timestep. However as the IndependentOperator is
# used then just a single transport simulation is done, thus speeding up the
# simulation considerably.
timesteps_and_source_rates = [
    (1, 1e18),  # 1 second
    (hour_in_seconds, 0),  # 1 hour
    (1, 1e18),  # 1 second
    (hour_in_seconds, 0),  # 2 hour
    (1, 1e18),  # 1 second
    (hour_in_seconds, 0),  # 3 hour
    (1, 1e18),  # 1 second
    (hour_in_seconds, 0),  # 4 hour
    (1, 1e18),  # 1 second
    (hour_in_seconds, 0),  # 4 hour
    (1, 1e18),  # 1 second
    (hour_in_seconds, 0),  # 4 hour
    (1, 1e18),  # 1 second
    (hour_in_seconds, 0),  # 5 hour
]

timesteps = [item[0] for item in timesteps_and_source_rates]
source_rates = [item[1] for item in timesteps_and_source_rates]

model_neutron.export_to_xml(directory=statepoints_folder/ "neutrons")

# this does perform transport but just to get the flux and micro xs
flux_in_each_group, micro_xs = openmc.deplete.get_microxs_and_flux(
    model=model_neutron,
    domains=all_depletable_cells,
    energies='CCFE-709', # different group structures see this file for all the groups available https://github.com/openmc-dev/openmc/blob/develop/openmc/mgxs/__init__.py
)

# constructing the operator, note we pass in the flux and micro xs
operator = openmc.deplete.IndependentOperator(
    materials=openmc.Materials(all_depletable_materials),
    fluxes=flux_in_each_group,
    micros=micro_xs,
    reduce_chain=True,  # reduced to only the isotopes present in depletable materials and their possible progeny
    reduce_chain_level=5,
    normalization_mode="source-rate"
)

integrator = openmc.deplete.PredictorIntegrator(
    operator=operator,
    timesteps=timesteps,
    source_rates=source_rates,
    timestep_units='s'
)

# this runs the depletion calculations for the timesteps
# this does the neutron activation simulations and produces a depletion_results.h5 file
integrator.integrate()
# TODO add output dir to integrate command so we don't have to move the file like this
# integrator.integrate(path=statepoints_folder / "neutrons" / "depletion_results.h5")
# PR on openmc is open
import os
os.system(f'mv depletion_results.h5 {statepoints_folder / "neutrons" / "depletion_results.h5"}')

# Now we have done the neutron activation simulations we can start the work needed for the decay gamma simulations.

my_gamma_settings = openmc.Settings()
my_gamma_settings.run_mode = "fixed source"
my_gamma_settings.batches = 100
my_gamma_settings.particles = p_particles


# First we add make dose tally on a regular mesh


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
flux_tally = openmc.Tally()
flux_tally.filters = [mesh_filter, dose_filter, particle_filter]
flux_tally.scores = ["flux"]
flux_tally.name = "photon_dose_on_mesh"

tallies = openmc.Tallies([flux_tally])

cells = model_neutron.geometry.get_all_cells()
activated_cells = [cells[uid] for uid in activated_cell_ids]

# this section makes the photon sources from each active material at each
# timestep and runs the photon simulations
results = openmc.deplete.Results(statepoints_folder / "neutrons" / "depletion_results.h5")

for i_cool in range(1, len(timesteps)):

    # range starts at 1 to skip the first step as that is an irradiation step and there is no
    # decay gamma source from the stable material at that time
    # also there are no decay products in this first timestep for this model

        photon_sources_for_timestep = []
        print(f"making photon source for timestep {i_cool}")

        all_activated_materials_in_timestep = []

        for activated_cell_id in activated_cell_ids:
            # gets the material id of the material filling the cell
            material_id = cells[activated_cell_id].fill.id

            # gets the activated material using the material id
            activated_mat = results[i_cool].get_material(str(material_id))
            # gets the energy and probabilities for the 
            energy = activated_mat.get_decay_photon_energy(
                clip_tolerance = 1e-6,  # cuts out a small fraction of the very low energy (and hence negligible dose contribution) photons
                units = 'Bq',
            )
            strength = energy.integral()

            if strength > 0.:  # only makes sources for 
                space = openmc.stats.Box(*cells[activated_cell_id].bounding_box)
                source = openmc.IndependentSource(
                    space=space,
                    energy=energy,
                    particle="photon",
                    strength=strength,
                    domains=[cells[activated_cell_id]],
                )
                photon_sources_for_timestep.append(source)


        my_gamma_settings.source = photon_sources_for_timestep


        # one should also fill the cells with the activated material
        # the activated material contains ALL the nuclides produced during activation
        # sphere_cell_2.fill =  results[i_cool].get_material("1")
        # sphere_cell_3.fill =  results[i_cool].get_material("2")
        # my_geometry = openmc.Geometry([sphere_cell_1, sphere_cell_2, sphere_cell_3])

        # however it is unlikely that they all appear in your transport cross_sections.xml
        # so you could make use of openmc.deplete.Results.export_to_materials to export the modified activated material that
        # just contains isotopes that appear in your cross_sections.xml

        # however in this example we just use the original pristine material my_materials that were cloned earlier
        # my_geometry is also the same as the neutron simulation
        pristine_mat_iron.id = 1
        pristine_mat_aluminium.id =2
        my_materials = openmc.Materials([pristine_mat_iron, pristine_mat_aluminium])

        model_gamma = openmc.Model(my_geometry, my_materials, my_gamma_settings, tallies)

        model_gamma.run(cwd=statepoints_folder / "photons" / f"photon_at_time_{i_cool}")


pico_to_micro = 1e-6
seconds_to_hours = 60*60

# You may wish to plot the dose tally on a mesh, this package makes it easy to include the geometry with the mesh tally
from openmc_regular_mesh_plotter import plot_mesh_tally
for i_cool in range(1, len(timesteps)):
    with openmc.StatePoint(statepoints_folder / "photons" / f"photon_at_time_{i_cool}" / 'statepoint.100.h5') as statepoint:
        photon_tally = statepoint.get_tally(name="photon_dose_on_mesh")

        # normalising this tally is a little different to other examples as the source strength has been using units of photons per second.
        # tally.mean is in units of pSv-cm3/source photon.
        # as source strength is in photons_per_second this changes units to pSv-/second

        # multiplication by pico_to_micro converts from (pico) pSv/s to (micro) uSv/s
        # dividing by mesh voxel volume cancles out the cm3 units
        # could do the mesh volume scaling on the plot and vtk functions but doing it here instead
        scaling_factor = (seconds_to_hours * pico_to_micro) / mesh.volumes[0][0][0]

        plot = plot_mesh_tally(
                tally=photon_tally,
                basis="xz",
                # score='flux', # only one tally so can make use of default here
                value="mean",
                colorbar_kwargs={
                    'label': "Decay photon dose [µSv/h]",
                },
                norm=LogNorm(),
                volume_normalization=False,  # this is done in the scaling_factor
                scaling_factor=scaling_factor,
            )
        plot.figure.savefig(f'shut_down_dose_map_timestep_{i_cool}')
