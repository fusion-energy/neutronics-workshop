# This simulation obtains dose on a cylindical disk phantom at various
# distances from a 14MeV photon source. Dose in millisieverts is found
# and compared to the yearly limit

# The model is built to have a human tissue and human height and volume which
# is typically referred to as a phantom.

# source details based on https://file.scirp.org/pdf/OJMSi_2014011414370625.pdf

import openmc
import math
import matplotlib.pyplot as plt


# Tissue Equivalent, MS20 from PNNL
mat_tissue = openmc.Material()
mat_tissue.add_element("O", 0.079013)
mat_tissue.add_element("C", 0.32948)
mat_tissue.add_element("H", 0.546359)
mat_tissue.add_element("N", 0.008619)
mat_tissue.add_element("Mg", 0.036358)
mat_tissue.add_element("Cl", 0.000172)
mat_tissue.set_density("g/cm3", 1.0)

mat_air = openmc.Material()
mat_air.add_element("C", 0.00015)
mat_air.add_element("N", 0.784431)
mat_air.add_element("O", 0.210748)
mat_air.add_element("Ar", 0.004671)
mat_air.set_density("g/cm3", 0.001205)

my_materials = openmc.Materials([mat_tissue, mat_air])

all_dose = []
distances_to_simulate = [50, 1000, 2000, 4000, 6000]
for distance_from_source in distances_to_simulate:  # units of cm

    # representing a human as a cylindrical phantom
    # average human is 62,000cm3 volume
    # average human height = 169.75
    # resulting cylinder radius = 10.782
    cylinder_surface = openmc.ZCylinder(r=10.782, x0=distance_from_source)
    phantom_upper_surface = openmc.ZPlane(z0=169.75)
    phantom_lower_surface = openmc.ZPlane(z0=0)

    outer_surface = openmc.Sphere(r=10000000, boundary_type="vacuum")

    phantom_region = -cylinder_surface & -phantom_upper_surface & +phantom_lower_surface

    # void region is below the outer surface and not the phantom region
    void_region = -outer_surface & ~phantom_region

    void_cell = openmc.Cell(region=void_region)
    void_cell.fill = mat_air
    phantom_cell = openmc.Cell(region=phantom_region)
    phantom_cell.fill = mat_tissue

    my_geometry = openmc.Geometry([phantom_cell, void_cell])

    # Instantiate a Settings object
    my_settings = openmc.Settings()
    my_settings.output = {"tallies": False}
    my_settings.batches = 2
    my_settings.inactive = 0
    my_settings.particles = 500000
    my_settings.photon_transport = True
    my_settings.run_mode = "fixed source"

    # Create a gamma point source
    source = openmc.Source()
    source.space = openmc.stats.Point((0, 0, 0))
    source.angle = openmc.stats.Isotropic()
    # This is a Co60 source, see the task on sources to understand it
    source.energy = openmc.stats.Discrete([1.1732e6, 1.3325e6], [0.5, 0.5])
    source.particle = "photon"

    my_settings.source = source

    # volume of cylinder V=πr^2h
    # openmc native units for length are cm so volume is in cm3
    phantom_volume = math.pi * math.pow(10.782, 2) * 169.75

    # geometry argument refers to irradiation direction
    # https://academic.oup.com/view-large/figure/119655666/ncx112f01.png
    energy_bins_p, dose_coeffs_p = openmc.data.dose_coefficients(
        particle="photon", geometry="AP"
    )
    energy_function_filter_p = openmc.EnergyFunctionFilter(energy_bins_p, dose_coeffs_p)
    energy_function_filter_p.interpolation == "cubic"

    photon_particle_filter = openmc.ParticleFilter("photon")
    cell_filter = openmc.CellFilter(phantom_cell)

    # Create tally to score dose
    dose_cell_tally = openmc.Tally(name="photon_dose_on_cell")
    # note that the EnergyFunctionFilter is included as a filter
    dose_cell_tally.filters = [
        cell_filter,
        photon_particle_filter,
        energy_function_filter_p,
    ]
    dose_cell_tally.scores = ["flux"]
    my_tallies = openmc.Tallies([dose_cell_tally])

    model = openmc.Model(my_geometry, my_materials, my_settings, my_tallies)

    statepoint_filename = model.run()

    with openmc.StatePoint(statepoint_filename) as statepoint:

        photon_tally_result = statepoint.get_tally(
            name="photon_dose_on_cell"
        ).mean.flatten()[0]

    photons_per_second = 740000000000  # units of photons per second

    # converts units from pSv-cm3/source_photon to pSv-cm3/second
    dose = photon_tally_result * photons_per_second

    # converts from pSv-cm3/second to pSv/second
    dose = dose / phantom_volume

    # converts from (pico) pSv/second to (micro) uSv/second
    dose = dose * 1e-6

    # converts from uSv/second to uSv/hour
    dose = dose * 60 * 60

    all_dose.append(dose)

plt.plot(distances_to_simulate, all_dose, label="dose on phantom")
plt.xlabel("Distance between photon source and phantom")
plt.ylabel("Dose [uSv per hour]")
plt.title("Dose on a phantom as a function of distance from a Co60 source\n")
plt.yscale("log")
plt.grid(True)
plt.show()
