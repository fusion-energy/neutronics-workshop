# This example shows the energy loss per collision for a large mass absorbing
# element (W) and a low mass element (H). The both end up stopping neutrons
# The hydrogen slows the neutron down quickly and absorbs low energy neutrons
# The Tungsten slows the neutron down less effectively but absorbs high energy neutrons

import openmc
import matplotlib.pyplot as plt
from shutil import move


def generate_tracks_file_for_material(element):
    iron = openmc.Material()
    iron.set_density("g/cm3", 7.75)
    iron.add_element(element, 1.0, percent_type="ao")

    my_materials = openmc.Materials([iron])
    vessel_inner = openmc.Sphere(r=100, boundary_type="vacuum")
    inner_vessel_region = -vessel_inner
    inner_vessel_cell = openmc.Cell(region=inner_vessel_region, fill=iron)

    my_geometry = openmc.Geometry([inner_vessel_cell])

    my_settings = openmc.Settings()
    my_settings.batches = 1
    my_settings.inactive = 0
    my_settings.particles = 20
    my_settings.run_mode = "fixed source"
    my_source = openmc.Source()
    my_source.space = openmc.stats.Point((0, 0, 0))
    my_source.energy = openmc.stats.Discrete([14e6], [1])
    my_settings.source = my_source

    model = openmc.model.Model(my_geometry, my_materials, my_settings)

    model.run(tracks=True)
    move("tracks.h5", f"tracks_{element}.h5")
    return f"tracks_{element}.h5"


tracks_file_w = generate_tracks_file_for_material("W")


for element, color in zip(["H", "W"], ["red", "blue"]):
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

plt.legend()
plt.xlabel("Interaction number")
plt.ylabel("Energy [eV]")
plt.yscale("log")
plt.xscale("log")
plt.show()
