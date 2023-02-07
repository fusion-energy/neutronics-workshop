# This simulation obtains dose on a 30cm diameter sphere disk phantom made of a
# material as defined in ICP 116 page 39
#
# Various distances from a 14MeV neutron source. Dose in millisieverts is found
# and compared to a back of the envelop calculation


import openmc
import math
import matplotlib.pyplot as plt


def manual_dose_calc(particles_per_shot, distance_from_source):
    # as the model is so simple we can calculate the dose manually by finding
    # neutrons across the surface area of the sphere.

    sphere_surface_area = 4 * math.pi * math.pow(distance_from_source, 2)

    particles_per_unit_area = particles_per_shot / sphere_surface_area

    # Conversion factor from fluence to dose at 14.1MeV = 495pSv cm2 per neutron (AP)
    return particles_per_unit_area * 495e-12



mat_tissue = openmc.Material()
mat_tissue.add_element("O", 76.2)
mat_tissue.add_element("C", 11.1)
mat_tissue.add_element("H", 10.1)
mat_tissue.add_element("N", 2.6)
mat_tissue.set_density("g/cm3", 1.0)

my_materials = openmc.Materials([mat_tissue])


def simulate_dose(distance_from_source, particle, particles_per_shot, energy):
    phantom_surface = openmc.Sphere(r=15, x0=distance_from_source - 15.1)

    outer_surface = openmc.Sphere(r=distance_from_source, boundary_type="vacuum")

    phantom_region = -phantom_surface

    # void region is below the outer surface and above the phantom region
    void_region = -outer_surface & +phantom_surface

    void_cell = openmc.Cell(region=void_region)
    phantom_cell = openmc.Cell(region=phantom_region)
    phantom_cell.fill = mat_tissue

    my_geometry = openmc.Geometry([phantom_cell, void_cell])

    # Instantiate a Settings object
    my_settings = openmc.Settings()
    my_settings.output = {"tallies": False}
    my_settings.batches = 30
    my_settings.inactive = 0
    my_settings.particles = 6000000
    my_settings.run_mode = "fixed source"

    source = openmc.Source()
    source.particle = particle
    source.angle = openmc.stats.Isotropic()
    source.energy = openmc.stats.Discrete([energy], [1])
    source.space = openmc.stats.Point((0.0, 0.0, 0.0))

    my_settings.source = source

    # volume of cylinder V=πr^2h
    # openmc native units for length are cm so volume is in cm3
    phantom_volume = (4 / 3) * math.pi * math.pow(phantom_surface.r, 3)

    energy_bins, dose_coeffs = openmc.data.dose_coefficients(
        particle=particle, geometry="AP"
    )
    energy_function_filter = openmc.EnergyFunctionFilter(energy_bins, dose_coeffs)
    energy_function_filter.interpolation == "cubic"

    neutron_particle_filter = openmc.ParticleFilter("neutron")
    cell_filter = openmc.CellFilter(phantom_cell)
    surface_filter = openmc.SurfaceFilter(phantom_surface)

    # Create tally to score dose
    dose_cell_tally = openmc.Tally(name="neutron_dose_on_cell")
    dose_cell_tally.filters = [
        cell_filter,
        energy_function_filter,
        neutron_particle_filter
    ]
    dose_cell_tally.scores = ["flux"]

    surface_flux = openmc.Tally(name="surface_current")
    surface_flux.filters = [cell_filter, surface_filter]  # , neutron_particle_filter]
    surface_flux.scores = ["current"]
    my_tallies = openmc.Tallies([dose_cell_tally, surface_flux])

    model = openmc.Model(my_geometry, my_materials, my_settings, my_tallies)

    statepoint_filename = model.run()

    with openmc.StatePoint(statepoint_filename) as statepoint:

        tally_result = statepoint.get_tally(
            name="neutron_dose_on_cell"
        ).mean.flatten()[0]

    # tally.mean is in units of pSv-cm3/source neutron
    # this multiplication changes units to neutron to pSv-cm3/shot
    total_dose = tally_result * particles_per_shot

    # converts from pSv-cm3/shot to pSv/shot
    total_dose = total_dose / phantom_volume

    # converts from (pico) pSv/shot to Sv/shot
    total_dose = total_dose * 1e-12

    print(f"dose on phantom is {total_dose}Sv per shot")

    calculated_dose = manual_dose_calc(
        particles_per_shot=particles_per_shot, distance_from_source=distance_from_source
    )

    print(f"dose on phantom is {calculated_dose}Sv per shot")

    return total_dose, calculated_dose

particle="neutron"
energy=14e6
particles_per_shot=1e18
dose_for_each_shot_simulation = []
dose_for_each_shot_calc = []
distances_to_simulate = [1000, 2000]#, 3000, 4000, 5000, 6000]
for distance_from_source in distances_to_simulate:  # units of cm
    total_dose, calculated_dose = simulate_dose(distance_from_source, particle, particles_per_shot, energy)
    dose_for_each_shot_simulation.append(total_dose)
    dose_for_each_shot_calc.append(calculated_dose)

plt.plot(
    distances_to_simulate,
    dose_for_each_shot_simulation,
    label="dose on phantom simulation",
)
plt.plot(
    distances_to_simulate, dose_for_each_shot_calc, label="dose on phantom calculation"
)
plt.xlabel(f"Distance between {particle} source and phantom [cm]")
plt.ylabel("Dose [Sv per shot]")
plt.title(
    f"Simulation and calculation of dose for different distances between {particle} source and phantom,\n"
    f"{particles_per_shot} {particle}s per shot "
)
plt.legend()
plt.grid(True, which="both")
plt.yscale("log")
plt.savefig(f"{energy}eV_{particle}_dose_as_function_of_distance.png")
