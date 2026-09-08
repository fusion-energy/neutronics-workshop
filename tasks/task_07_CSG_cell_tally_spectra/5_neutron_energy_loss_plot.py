# %% [markdown]
# ---
# title: Plotting energy loss per collision
# ---

# %% [markdown]
# This example shows the energy loss per collision for a large mass absorbing element (W) and a low mass element (H).
#
# They both end up stopping neutrons, however they accomplish this in different ways.
#
# The hydrogen slows the neutron down quickly and absorbs low energy neutrons.
#
# The Tungsten slows the neutron down less effectively but absorbs high energy neutrons.

# %% [markdown]
# First import OpenMC and configure the nuclear data path

# %%
import matplotlib.pyplot as plt
from shutil import move

import openmc
from pathlib import Path
# Setting the cross section path to the correct location in the docker image.
# If you are running this outside the docker image you will have to change this path to your local cross section path.
openmc.config['cross_sections'] = Path.home() / 'nuclear_data' / 'cross_sections.xml'


# %% [markdown]
# This section a function that makes use of the openmc tracks feature.
#
# Track data for each particle simulatated is saved and then used to find out the energy loss per collision.

# %%
def generate_tracks_file_for_material(mat):

    my_materials = openmc.Materials([mat])
    vessel_inner = openmc.Sphere(r=100, boundary_type="vacuum")
    inner_vessel_region = -vessel_inner
    inner_vessel_cell = openmc.Cell(region=inner_vessel_region, fill=mat)

    my_geometry = openmc.Geometry([inner_vessel_cell])

    my_settings = openmc.Settings()
    my_settings.batches = 1
    my_settings.inactive = 0
    my_settings.particles = 20
    my_settings.run_mode = "fixed source"

    my_source = openmc.IndependentSource(
        space=openmc.stats.Point((0, 0, 0)),
        energy=openmc.stats.Discrete([14e6], [1])
    )
    my_settings.source = my_source

    model = openmc.Model(my_geometry, my_materials, my_settings)

    model.run(tracks=True)
    move("tracks.h5", f"tracks_{mat.name}.h5")
    return f"tracks_{mat.name}.h5"


# %% [markdown]
# This section makes two materials to compare

# %%
# makes the material
tungsten = openmc.Material()
tungsten.set_density("g/cm3", 19.25)
tungsten.add_element('W', 1.0, percent_type="ao")

liquid_hydrogen = openmc.Material()
liquid_hydrogen.set_density("g/cm3", 0.07)
liquid_hydrogen.add_element('H', 1.0, percent_type="ao")

# %% [markdown]
# This section calls the function and plots the results

# %%
# remove old summary and statepoint files
for f in Path('.').glob('*.h5'):
    f.unlink(missing_ok=True)

for element, color in zip([liquid_hydrogen, tungsten], ["red", "blue"]):
    plt.plot([0], label=element, color=color)
    tracks_filename = generate_tracks_file_for_material(element)
    tracks = openmc.Tracks(tracks_filename)
    for track in tracks:
        for p_number, particle in enumerate(track.particle_tracks):
            energy = []
            if particle.particle == 0:  # 0 is a neutron
                for state in particle.states:
                    energy.append(state[2])
                plt.plot(energy, color=color)

plt.yscale('log')
plt.xlabel('Collision number')
plt.ylabel('Neutron Energy [eV]')
plt.ylabel('Energy loss per collision of neutrons travelling through materials')
plt.show()

# %% [markdown]
# # Learning outcomes
#
# - We learned that energy lost is related to atom mass
# - Large mass atoms reduce the energy of neutrons by small amounts per collision e.g W
# - Small mass atoms reduce the energy of neutrons by large amounts per collision e.g H
#
#
# # Additional tasks
#
# - See if you can spot a neutron that has reached thermal equalibrium with the material (these neutrons can gain or lose energy with each collision)
# - Try changing the material to a transparent material like Zirconium (Zr) which has a density of 6.511g/cm3
