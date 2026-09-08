# %% [markdown]
# ---
# title: Biological dose on a cell from gammas
# ---

# %% [markdown]
# This simulation obtains effective dose on a cylindrical disk phantom at various distances from a Co-60 photon source. Dose in microsieverts per hour is found and plotted as a function of distance.
#
# The model represents a human as a cylinder with tissue-equivalent material, matching average human height and volume. This is typically referred to as a **phantom**.
#
# Effective dose is used to assess the potential for long-term radiation effects. It provides a single number that reflects the overall risk from exposure. The dose coefficients used here come from [ICRP Publication 116](https://journals.sagepub.com/doi/10.1016/j.icrp.2011.10.001).
#
# Read more about absorbed, equivalent, and effective dose on the [ICRP website](http://icrpaedia.org/Absorbed,_Equivalent,_and_Effective_Dose).
#
# Source details are based on [this paper](https://file.scirp.org/pdf/OJMSi_2014011414370625.pdf).
#
# First import packages needed and configure the OpenMC nuclear data path.

# %%
import math
import openmc
from pathlib import Path
# Setting the cross section path to the correct location in the docker image.
# If you are running this outside the docker image you will have to change this path to your local cross section path.
openmc.config['cross_sections'] = Path.home() / 'nuclear_data' / 'cross_sections.xml'

import matplotlib.pyplot as plt

# %% [markdown]
# Now we make the materials. The phantom uses Tissue Equivalent MS20 from PNNL, and we also define air for the surrounding void region.

# %%
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

# %% [markdown]
# Now we loop through a range of distances. At each step we move the phantom cell to the new distance and simulate photon dose on the cell.
#
# The phantom is a cylinder representing an average human:
# - Volume: ~62,000 cm³
# - Height: 169.75 cm
# - Resulting cylinder radius: 10.782 cm
#
# The source is a Co-60 gamma source emitting two photon energies (1.1732 MeV and 1.3325 MeV) with equal probability.

# %%
all_dose = []
distances_to_simulate = [50, 1000, 2000, 4000, 6000]
for distance_from_source in distances_to_simulate:  # units of cm

    # representing a human as a cylindrical phantom
    cylinder_surface = openmc.ZCylinder(r=10.782, x0=distance_from_source)
    phantom_upper_surface = openmc.ZPlane(z0=169.75)
    phantom_lower_surface = openmc.ZPlane(z0=0)

    outer_surface = openmc.Sphere(r=1e7, boundary_type="vacuum")

    phantom_region = -cylinder_surface & -phantom_upper_surface & +phantom_lower_surface

    # void region is inside the outer surface and not the phantom region
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

    # Create a Co-60 gamma point source
    source = openmc.IndependentSource()
    source.space = openmc.stats.Point((0, 0, 0))
    source.angle = openmc.stats.Isotropic()
    source.energy = openmc.stats.Discrete([1.1732e6, 1.3325e6], [0.5, 0.5])
    source.particle = "photon"

    my_settings.source = source

    # volume of cylinder V=\u03c0r\u00b2h
    # openmc native units for length are cm so volume is in cm3
    phantom_volume = math.pi * math.pow(10.782, 2) * 169.75

    # geometry argument refers to irradiation direction
    # https://academic.oup.com/view-large/figure/119655666/ncx112f01.png
    energy_bins_p, dose_coeffs_p = openmc.data.dose_coefficients(
        particle="photon", geometry="AP"
    )
    energy_function_filter_p = openmc.EnergyFunctionFilter(energy_bins_p, dose_coeffs_p)
    energy_function_filter_p.interpolation = "cubic"  # cubic interpolation is recommended by ICRP

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

    photons_per_second = 7.4e11  # units of photons per second

    # converts units from pSv-cm3/source_photon to pSv-cm3/second
    dose = photon_tally_result * photons_per_second

    # converts from pSv-cm3/second to pSv/second
    dose = dose / phantom_volume

    # converts from (pico) pSv/second to (micro) uSv/second
    dose = dose * 1e-6

    # converts from uSv/second to uSv/hour
    dose = dose * 60 * 60

    all_dose.append(dose)

# %% [markdown]
# Now we plot the graph of dose vs distance. The log scale on the y-axis shows how dose falls off rapidly with distance from the Co-60 source, following an approximate inverse-square law.

# %%
plt.plot(distances_to_simulate, all_dose, label="dose on phantom")
plt.xlabel("Distance between photon source and phantom")
plt.ylabel(r"Dose [$\mu$Sv/h]")
plt.title("Dose on a phantom as a function of distance from a Co60 source\n")
plt.yscale("log")
plt.grid(True)
plt.show()

# %% [markdown]
# **Learning Outcomes:**
#
# - Simulating photon dose using OpenMC with dose coefficients from ICRP.
# - Understanding how dose rate varies with distance from a gamma source.
# - Post-processing tally results to obtain dose rate in practical units (uSv/hour).
