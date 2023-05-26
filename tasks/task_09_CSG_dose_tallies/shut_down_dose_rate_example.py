# This script simulates R2S method of shut down dose rate
# on a simple sphere model.

import numpy as np
import openmc
import openmc.deplete
import pint
from pathlib import 
import math

# users might want to change these to use specific xml files to use particular decay data or transport cross sections
# openmc.config['chain_file'] = 'chain.xml'
# openmc.config['cross_sections'] = 'cross_sections.xml'

# a few user settings
# Set up the folders to save all the data in
n_particles = 1_000
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
mat_iron.volume = (4 / 3) * math.pi * math.pow(1, 3)
sphere_cell_2.fill = mat_iron

# We make a Al material which should produce a few different activation products
mat_aluminum = openmc.Material()
mat_aluminum.id = 2
mat_aluminum.add_element("Al", 1.0)
mat_aluminum.set_density("g/cm3", 2.7)
# must set the depletion to True to deplete the material
mat_aluminum.depletable = True
# volume must set the volume as well as openmc calculates number of atoms
mat_aluminum.volume = (4 / 3) * math.pi * math.pow(5, 3)
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

model = openmc.Model(my_geometry, my_materials, my_neutron_settings)

hour_in_seconds = pint.Quantity(1.0, "hour").to("s").magnitude

# defines the neutron pulse schedule
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
        "dilute_initial": 0,  # need to avoid adding small amounts of fissle material
    },
)

# this section makes the photon sources from each active material at each time step
all_photon_sources = {}
cells = model.geometry.get_all_cells()
results = openmc.deplete.Results(statepoints_folder / "neutrons" / "depletion_results.h5")
for i_cool in range(len(timesteps)):
    print(f"getting results {i_cool}")
    all_photon_sources[i_cool] = {}
    for uid in activated_cell_ids:
        mat_id = cells[uid].fill.id
        mat = results[i_cool].get_material(str(mat_id))
        all_photon_sources[i_cool][uid] = mat.decay_photon_energy

print("all_photon_sources", all_photon_sources)

# creates a regular mesh that surrounds the geometry
mesh = openmc.RegularMesh().from_domain(
    model.geometry,  # the corners of the mesh are being set automatically to surround the geometry
    dimension=[10, 10, 10],  # 10 voxels in each axis direction (r, z, phi)
)

# adding a dose tally on a regular mesh
# AP, PA, LLAT, RLAT, ROT, ISO are geomety options
energies, pSv_cm2 = openmc.data.dose_coefficients(particle="photon", geometry="AP")
dose_filter = openmc.EnergyFunctionFilter(
    energies, pSv_cm2, interpolation="cubic"
)
particle_filter = openmc.ParticleFilter(["photon"])
mesh_filter = openmc.MeshFilter(mesh)
flux_tally = openmc.Tally()
flux_tally.filters = [mesh_filter, dose_filter, particle_filter]
flux_tally.scores = ["flux"]
flux_tally.name = "photon_dose_on_mesh"

tallies = openmc.Tallies([flux_tally])
model.tallies = tallies

activated_cells = [cells[uid] for uid in activated_cell_ids]

for step_number in list(all_photon_sources.keys()):
    photon_sources_for_timestep = []

    cells = model.geometry.get_all_cells()

    for cell in activated_cells:
        space = openmc.stats.Box(*cell.bounding_box)
        energy = all_photon_sources[step_number][cell.id]
        source = openmc.Source(
            space=space,
            energy=energy,
            particle="photon",
            strength=energy.integral(),
            domains=[cell],
        )
        photon_sources_for_timestep.append(source)

    model.settings = openmc.Settings()
    model.settings.run_mode = "fixed source"
    model.settings.batches = 100
    model.settings.particles = p_particles
    model.settings.source = photon_sources_for_timestep
    model.settings.export_to_xml(
        path=statepoints_folder / "photons" / "settings.xml"
    )

    model.run(cwd=statepoints_folder / "photons" / f"photon_at_time_{step_number}")

