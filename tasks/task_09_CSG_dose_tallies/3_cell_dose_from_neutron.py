# This simulation obtains dose on a cylindical disk phantom at various
# distances from a 14MeV neutron source. Dose in millisieverts is found
# and compared to the yearly limit

# The model is built to have a human tissue and human height and volume which
# is typically referred to as a phantom.


import openmc
import math
import matplotlib.pyplot as plt


# Tissue Equivalent, MS20 from PNNL
mat_tissue = openmc.Material()
mat_tissue.add_element("H", 0.546359)
mat_tissue.add_element("C", 0.32948)
mat_tissue.add_element("Mg", 0.036358)
mat_tissue.add_element("Cl", 0.000172)
mat_tissue.set_density("g/cm3", 1.0)
my_materials = openmc.Materials([mat_tissue])

yearly_dose = []
distances_to_simulate = [100, 200, 300, 400, 500]
for distance_from_source in distances_to_simulate:  # units of cm

    # representing a human as a cylindrical phantom
    # average human is 62,000cm3 volume
    # average human height = 169.75
    # resulting cylinder radius = 10.782
    cylinder_surface = openmc.ZCylinder(r=10.782, x0=distance_from_source)
    phantom_upper_surface = openmc.ZPlane(z0=169.75)
    phantom_lower_surface = openmc.ZPlane(z0=0)

    outer_surface = openmc.Sphere(r=10000, boundary_type="vacuum")

    phantom_region = -cylinder_surface & -phantom_upper_surface & +phantom_lower_surface

    # void region is below the outer surface and not the phantom region
    void_region = -outer_surface & ~phantom_region

    void_cell = openmc.Cell(region=void_region)
    phantom_cell = openmc.Cell(region=phantom_region)
    phantom_cell.fill = mat_tissue

    my_geometry = openmc.Geometry([phantom_cell, void_cell])

    # Instantiate a Settings object
    my_settings = openmc.Settings()
    my_settings.output = {"tallies": False}
    my_settings.batches = 2
    my_settings.inactive = 0
    my_settings.particles = 500000
    my_settings.run_mode = "fixed source"

    source = openmc.Source()
    source.angle = openmc.stats.Isotropic()
    source.energy = openmc.stats.Discrete([14e6], [1])
    source.space = openmc.stats.Point((0.0, 0.0, 0.0))

    my_settings.source = source

    # volume of cylinder V=πr^2h
    # openmc native units for length are cm so volume is in cm3
    phantom_volume = math.pi * math.pow(10.782, 2) * 169.75

    energy_bins_n, dose_coeffs_n = openmc.data.dose_coefficients(
        particle="neutron", geometry="AP"
    )
    energy_function_filter_n = openmc.EnergyFunctionFilter(energy_bins_n, dose_coeffs_n)
    energy_function_filter_n.interpolation == "cubic"

    neutron_particle_filter = openmc.ParticleFilter("neutron")
    cell_filter = openmc.CellFilter(phantom_cell)

    # Create tally to score dose
    dose_cell_tally = openmc.Tally(name="neutron_dose_on_cell")
    dose_cell_tally.filters = [cell_filter, neutron_particle_filter]
    dose_cell_tally.scores = ["flux"]
    my_tallies = openmc.Tallies([dose_cell_tally])

    model = openmc.Model(my_geometry, my_materials, my_settings, my_tallies)

    statepoint_filename = model.run()

    with openmc.StatePoint(statepoint_filename) as statepoint:

        neutron_tally_result = statepoint.get_tally(
            name="neutron_dose_on_cell"
        ).mean.flatten()[0]

    neutrons_per_second = 1e8  # units of neutrons per second

    # tally.mean is in units of pSv-cm3/source neutron
    # this multiplication changes units to neutron to pSv-cm3/second
    total_dose = neutron_tally_result * neutrons_per_second

    # converts from pSv-cm3 to pSv
    total_dose = total_dose / phantom_volume

    # converts from pico Sv to milli Sv
    total_dose = total_dose * 1e-9

    print(f"dose on phantom is {total_dose}mSv per second")
    print(f"dose on phantom is {total_dose*60*60*24*365}mSv per year")

    yearly_dose.append(total_dose * 60 * 60 * 24 * 365)

plt.plot(distances_to_simulate, yearly_dose, label="dose on phantom")
# UK limit for public dose is 2.7 millisieverts per year
plt.plot(distances_to_simulate, [2.7] * 5, label="UK public dose limit")
plt.xlabel("Distance between neutron source and phantom")
plt.ylabel("Dose [mSv per year]")
plt.title("Dose on a phantom as a function of distance [cm]\n")
plt.legend()
plt.show
