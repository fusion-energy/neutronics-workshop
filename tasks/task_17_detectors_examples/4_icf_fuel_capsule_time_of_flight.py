# This simulation produces neutrons inside a ICF fusion fuel cavity and
# transports them through a pusher material then tallies the neutrons arriving
# at a surface. Two examples are made, one for Revolver and one for NIC Rev 5
# https://www.lle.rochester.edu/media/publications/presentations/documents/APS17/McKenty_APS17.pdf
# https://nap.nationalacademies.org/read/18288/chapter/6#46


import openmc
import numpy as np
import matplotlib.pyplot as plt

# this function will be called 4 times for the different combinations of
# pusher material and detector distance
def simulate_icf_neutrons(
    pusher_material: openmc.Material,
    pusher_inner_radius: float,
    pusher_outer_radius: float,
    detector_distance: float
):

    # surfaces
    surface_inner_shell = openmc.Sphere(r=pusher_inner_radius)
    surface_outer_shell = openmc.Sphere(r=pusher_outer_radius)
    sphere_surface_detector_1 = openmc.Sphere(r=detector_distance, boundary_type="vacuum")

    # regions
    fuel_region = -surface_inner_shell
    shell_region = +surface_inner_shell & -surface_outer_shell
    void_region_1 = +surface_outer_shell & -sphere_surface_detector_1

    # cells
    fuel_cell = openmc.Cell(region=fuel_region)
    shell_cell = openmc.Cell(region=shell_region, fill=pusher_material)
    void_cell_1 = openmc.Cell(region=void_region_1)

    geometry = openmc.Geometry([fuel_cell, shell_cell, void_cell_1])

    # Create a neutron point source
    source = openmc.Source()
    source.space = openmc.stats.Point((0, 0, 0))
    source.angle = openmc.stats.Isotropic()
    # DT neutron energy distribution is a Muir distribution
    source.energy = openmc.stats.muir(e0=14.08e6, m_rat=5.0, kt=2e3)

    # Instantiate a Settings object
    settings = openmc.Settings()
    settings.batches = 90
    settings.particles = 80000
    settings.run_mode = "fixed source"
    settings.source = source
    settings.photon_transport = False

    # time is in units of seconds, this might need changing if detector distance changes
    time_steps = np.linspace(start=300e-9, stop=1500e-9, num=1000)
    time_filter = openmc.TimeFilter(time_steps)
    surface_filter_1 = openmc.SurfaceFilter(sphere_surface_detector_1)

    time_tally_1 = openmc.Tally(name="time_tally_detector")
    time_tally_1.scores = ["current"]
    time_tally_1.filters = [time_filter, surface_filter_1]

    tallies = openmc.Tallies([time_tally_1])

    materials = openmc.Materials([pusher_material])

    model = openmc.model.Model(geometry, materials, settings, tallies)

    sp_filename = model.run()

    # open the results file for post processing
    with openmc.StatePoint(sp_filename) as sp:
        tally_detector_1 = sp.get_tally(name="time_tally_detector")
        tally_1_values = tally_detector_1.mean.squeeze()

    plt.plot(time_steps[:-1], tally_1_values, label=f"{detector_distance}cm detector, {pusher_material.name} pusher material")


revolver_pusher_material = openmc.Material(name='Revolver')
revolver_pusher_material.add_element("Au", 1.0, percent_type="ao")
revolver_pusher_material.set_density("g/cm3", 1930)

simulate_icf_neutrons(
    pusher_material= revolver_pusher_material,
    pusher_inner_radius= 0.0035,
    pusher_outer_radius=0.0095,
    detector_distance=2000
)
simulate_icf_neutrons(
    pusher_material= revolver_pusher_material,
    pusher_inner_radius= 0.0035,
    pusher_outer_radius=0.0095,
    detector_distance=3000
)

nic_rev4_pusher_material = openmc.Material(name='NIC Rev 5')
nic_rev4_pusher_material.add_nuclide("H2", 0.5, percent_type="ao")
nic_rev4_pusher_material.add_nuclide("H3", 0.5, percent_type="ao")
nic_rev4_pusher_material.set_density("g/cm3", 300)

simulate_icf_neutrons(
    pusher_material= nic_rev4_pusher_material,
    pusher_inner_radius= 0.0035,
    pusher_outer_radius=0.0065,
    detector_distance=2000
)
simulate_icf_neutrons(
    pusher_material= nic_rev4_pusher_material,
    pusher_inner_radius= 0.0035,
    pusher_outer_radius=0.0065,
    detector_distance=3000
)

plt.yscale("log")
plt.legend(loc="upper right")
plt.xlabel("Time [s]")
plt.ylabel("Neutron current on surface")
plt.tight_layout()
plt.savefig("icf_fuel_tof.png", dpi=400)
