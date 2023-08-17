# This script simulates R2S method of shut down dose rate
# on a simple sphere model.

import numpy as np
import openmc
import openmc.deplete
import pint
from pathlib import Path
import math

# users might want to change these to use specific xml files to use particular decay data or transport cross sections
# the chain file was downloaded with
# pip install openmc_data
# download_endf_chain -r b8.0
openmc.config['chain_file'] = '/nuclear_data/chain-endf-b8.0.xml'
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


# gets the cell ids of any depleted cell
activated_cell_ids = [c.id for c in my_geometry.get_all_material_cells().values() if c.fill.depletable]
print("activated_cell_ids", activated_cell_ids)

# 14MeV neutron source that activates material
my_source = openmc.Source()
my_source.space = openmc.stats.Point((0, 0, 0))
my_source.angle = openmc.stats.Isotropic()
my_source.energy = openmc.stats.Discrete([14.06e6], [1])
my_source.particle = "neutron"

# settings for the neutron simulation(s)
my_neutron_settings = openmc.Settings()
my_neutron_settings.run_mode = "fixed source"
my_neutron_settings.particles = n_particles
my_neutron_settings.batches = 100
my_neutron_settings.source = my_source
my_neutron_settings.photon_transport = False

model = openmc.Model(my_geometry, my_materials, my_neutron_settings)

hour_in_seconds = pint.Quantity(1.0, "hour").to("s").magnitude

# This section defines the neutron pulse schedule.
# Warning, be sure to add sufficient timesteps and run the neutron simulation with enough 
# batches/particles as the solver can produce unstable results otherwise. I typically plot
# activity of gamma sources as a function of step to see if they decay according to the
# half lives of the main unstable nuclides, this helps me check the solution is stable.
timesteps_and_source_rates = [
    (1, 1e18),  # 1 second
    (hour_in_seconds, 0),  # 1 hour
    (hour_in_seconds, 0),  # 2 hour
    (hour_in_seconds, 0),  # 3 hour
    (hour_in_seconds, 0),  # 4 hour
    (hour_in_seconds, 0),  # 5 hour
]

timesteps = [item[0] for item in timesteps_and_source_rates]
source_rates = [item[1] for item in timesteps_and_source_rates]

model.export_to_xml(directory=statepoints_folder)

model.deplete(
    timesteps,
    source_rates=source_rates,
    directory=statepoints_folder / "neutrons",
    method="predictor",  # predictor is a simple but quick method
    # method="cf4",  # CF4Integrator is an accurate but slower method
    # final_step=False,
    operator_kwargs={
        "normalization_mode": "source-rate",  # needed as this is a fixed source simulation
        "chain_file": chain_file,
        "reduce_chain_level": 5,
        "redcue_chain": True
    },
)

# creates a regular mesh that surrounds the geometry
mesh = openmc.RegularMesh().from_domain(
    model.geometry,
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
model.tallies = tallies

cells = model.geometry.get_all_cells()
activated_cells = [cells[uid] for uid in activated_cell_ids]

activity_of_all_gamma_sources_for_step = []

# this section makes the photon sources from each active material at each
# timestep and runs the photon simulations
results = openmc.deplete.Results(statepoints_folder / "neutrons" / "depletion_results.h5")
for i_cool in range(len(timesteps)):
    photon_sources_for_timestep = []
    print(f"making photon source for timestep {i_cool}")
    cumlative_source_strength = 0
    for cell_uid in activated_cell_ids:
        mat_id = cells[cell_uid].fill.id
        mat = results[i_cool].get_material(str(mat_id))
        energy = mat.decay_photon_energy

        space = openmc.stats.Box(*cells[cell_uid].bounding_box)
        print(f'source strength {energy.integral()}')
        source = openmc.Source(
            space=space,
            energy=energy,
            particle="photon",
            strength=energy.integral(),
            domains=[cells[cell_uid]],
        )
        photon_sources_for_timestep.append(source)
        cumlative_source_strength=cumlative_source_strength+source.strength

    # this is needed to normalise the tally results during post processing steps
    # as tally results are per simulated source particle
    activity_of_all_gamma_sources_for_step.append(cumlative_source_strength)

    model.settings = openmc.Settings()
    model.settings.run_mode = "fixed source"
    model.settings.batches = 100
    model.settings.particles = p_particles
    model.settings.source = photon_sources_for_timestep

    # we skip the first step as that is an irradiation step and there is no
    # decay gamma source from the stable material at that time
    if i_cool != 0: 
        # there are no decay products in this first timestep for this model
        model.run(cwd=statepoints_folder / "photons" / f"photon_at_time_{i_cool}")

# You may wish to add a dose tally on a mesh and plot the result, but I wanted to keep this already complex example minimal so I've not added tallies to the decay gamma step.
