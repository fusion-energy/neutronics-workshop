import os

import openmc
from neutronics_material_maker import Material, MultiMaterial


def find_tbr_hcpb(
    breeder_percent_in_breeder_plus_multiplier_ratio, blanket_breeder_li6_enrichment=60
):

    inputs_and_outputs = sphere_with_firstwall_model(
        material_for_structure="eurofer",
        blanket_breeder_material="Li4SiO4",
        blanket_multipler_material="Be12Ti",
        blanket_coolant_material="He",
        firstwall_coolant_material="He",
        blanket_breeder_li6_enrichment=blanket_breeder_li6_enrichment,
        blanket_multiplier_fraction=0.007
        * (100 - breeder_percent_in_breeder_plus_multiplier_ratio),
        blanket_breeder_fraction=0.007
        * breeder_percent_in_breeder_plus_multiplier_ratio,
        blanket_breeder_material_packing_fraction=0.62,
        blanket_multiplier_packing_fraction=0.62,
        coolant_pressure=15.5e6,
        blanket_coolant_temperature_in_C=400,
        firstwall_coolant_temperature_in_C=400,
        blanket_coolant_fraction=0.1,
        blanket_structural_fraction=0.2,
    )
    return inputs_and_outputs


def sphere_with_firstwall_model(
    material_for_structure,
    blanket_breeder_material,
    blanket_coolant_material,
    firstwall_coolant_material,
    blanket_breeder_li6_enrichment,  # this is a percentage
    coolant_pressure,  # this is in Pa
    blanket_coolant_temperature_in_C,
    firstwall_coolant_temperature_in_C,
    blanket_breeder_fraction,
    blanket_coolant_fraction,
    blanket_structural_fraction,
    blanket_breeder_temperature_in_C=None,  # needed for liquid breeders like lithium lead
    firstwall_thickness=2.7,  # this is in cm
    blanket_thickness=200,  # this is in cm
    inner_radius=1000,
    firstwall_armour_fraction=0.106305,  # equivilent to 3mm and based on https://doi.org/10.1016/j.fusengdes.2017.02.008
    firstwall_coolant_fraction=0.333507,  # based on https://doi.org/10.1016/j.fusengdes.2017.02.008
    firstwall_structural_fraction=0.560188,  # based on https://doi.org/10.1016/j.fusengdes.2017.02.008
    blanket_multipler_material=None,  # used for combined breeder multiplier options
    blanket_multiplier_fraction=None,  # used for combined breeder multiplier options
    blanket_breeder_material_packing_fraction=None,  # used for combined breeder multiplier options
    blanket_multiplier_packing_fraction=None,  # used for combined breeder multiplier options
    blanket_multiplier_material=None,  # used for combined breeder multiplier options
):

    breeder_percent_in_breeder_plus_multiplier_ratio = 100 * (
        blanket_breeder_fraction
        / (blanket_breeder_fraction + blanket_multiplier_fraction)
    )

    inputs = locals()

    """ 
    This function builds materials for the homogenised blanket material, homogenised firstwall material
    The creates a simple sphere geometry with a simple point source and TBR tally on the blanket
    The function also carries out the simulation and writes the results to a JSON file
    """

    # creates homogensied blanket material using a single breeder / multiplier material (e.g lithium lead)
    if blanket_breeder_material == "Pb842Li158":
        blanket_material = MultiMaterial(
            material_tag="blanket_material",
            materials=[
                Material(material_name=material_for_structure),
                Material(
                    material_name=blanket_coolant_material,
                    temperature_in_C=blanket_coolant_temperature_in_C,
                    pressure_in_Pa=coolant_pressure,
                ),
                Material(
                    material_name=blanket_breeder_material,
                    enrichment=blanket_breeder_li6_enrichment,
                    temperature_in_C=blanket_breeder_temperature_in_C,
                ),
            ],
            fracs=[
                blanket_structural_fraction,
                blanket_coolant_fraction,
                blanket_breeder_fraction,
            ],
            percent_type="vo",
        ).openmc_material

    # creates homogensied blanket material using a combined breeder multiplier material (e.g lithium ceramic with be multiplier)
    else:

        blanket_material = MultiMaterial(
            material_tag="blanket_material",
            materials=[
                Material(material_name=material_for_structure),
                Material(
                    material_name=blanket_coolant_material,
                    temperature_in_C=blanket_coolant_temperature_in_C,
                    pressure_in_Pa=coolant_pressure,
                ),
                Material(
                    material_name=blanket_breeder_material,
                    enrichment=blanket_breeder_li6_enrichment,
                    packing_fraction=blanket_breeder_material_packing_fraction,
                ),
                Material(
                    material_name=blanket_multipler_material,
                    packing_fraction=blanket_multiplier_packing_fraction,
                ),
            ],
            fracs=[
                blanket_structural_fraction,
                blanket_coolant_fraction,
                blanket_breeder_fraction,
                blanket_multiplier_fraction,
            ],
            percent_type="vo",
        ).openmc_material

    # creates homogensied firstwall material with eurofer, tungsten and a coolant
    firstwall_material = MultiMaterial(
        material_tag="firstwall_material",
        materials=[
            Material(material_name="tungsten"),
            Material(
                material_name=firstwall_coolant_material,
                temperature_in_C=firstwall_coolant_temperature_in_C,
                pressure_in_Pa=coolant_pressure,
            ),
            Material(material_name="eurofer"),
        ],
        fracs=[
            firstwall_armour_fraction,
            firstwall_coolant_fraction,
            firstwall_structural_fraction,
        ],
    ).openmc_material

    mats = openmc.Materials([blanket_material, firstwall_material])

    # creates surfaces
    breeder_blanket_inner_surface = openmc.Sphere(r=inner_radius + firstwall_thickness)
    firstwall_outer_surface = openmc.Sphere(r=inner_radius)

    inner_void_region = -firstwall_outer_surface
    inner_void_cell = openmc.Cell(region=inner_void_region)
    inner_void_cell.name = "inner_void"

    firstwall_region = +firstwall_outer_surface & -breeder_blanket_inner_surface
    firstwall_cell = openmc.Cell(name="firstwall", region=firstwall_region)
    firstwall_cell.fill = firstwall_material

    breeder_blanket_outer_surface = openmc.Sphere(
        r=inner_radius + firstwall_thickness + blanket_thickness, boundary_type="vacuum"
    )
    breeder_blanket_region = (
        -breeder_blanket_outer_surface & +breeder_blanket_inner_surface
    )
    breeder_blanket_cell = openmc.Cell(
        name="breeder_blanket", region=breeder_blanket_region
    )
    breeder_blanket_cell.fill = blanket_material

    universe = openmc.Universe(
        cells=[inner_void_cell, firstwall_cell, breeder_blanket_cell]
    )

    geom = openmc.Geometry(universe)

    # assigns simulation settings
    sett = openmc.Settings()
    sett.batches = 5  # this is minimum number of batches that will be run
    sett.trigger_active = True
    sett.trigger_max_batches = (
        1500  # this is maximum number of batches that will be run
    )
    sett.particles = 300
    sett.verbosity = 1
    sett.run_mode = "fixed source"

    # sets a 14MeV (distributuion) point source
    source = openmc.Source()
    source.space = openmc.stats.Point((0, 0, 0))
    source.angle = openmc.stats.Isotropic()
    source.energy = openmc.stats.Muir(
        e0=14080000.0, m_rat=5.0, kt=20000.0
    )  # neutron energy = 14.08MeV, AMU for D + T = 5, temperature is 20KeV
    sett.source = source

    # this is the tally set up
    tallies = openmc.Tallies()

    # define filters
    cell_filter_breeder = openmc.CellFilter(breeder_blanket_cell)
    particle_filter = openmc.ParticleFilter(["neutron"])

    # creates the TBR tally using the filters and sets a completion trigger
    tally = openmc.Tally(name="TBR")
    tally.filters = [cell_filter_breeder, particle_filter]
    tally.scores = [
        "(n,Xt)"
    ]  # where X is a wildcard, if MT 105 or (n,t) then some tritium production will be missed, for example (n,nt) which happens in Li7 would be missed
    tally.triggers = [
        openmc.Trigger(trigger_type="rel_err", threshold=0.1)
    ]  # This stops the simulation if the threshold is meet
    tallies.append(tally)

    # collects all the model parts and runs the model
    model = openmc.model.Model(geom, mats, sett, tallies)
    sp_filename = model.run(output=False)

    # opens the output file and retrieves the tally results
    sp = openmc.StatePoint(sp_filename)

    tally = sp.get_tally(name="TBR")

    df = tally.get_pandas_dataframe()

    tally_result = df["mean"].sum()
    tally_std_dev = df["std. dev."].sum()

    # combines the tally results with the input data
    inputs.update({"tbr": tally_result})
    inputs.update({"tbr_error": tally_std_dev})

    return inputs


def objective(x):
    """
    Used to find TBR for different breeder_percent_in_breeder_plus_multiplier_ratio 
    and blanket_breeder_li6_enrichment
    """,
    if type(x) == int or type(x) == float:
        result = find_tbr_hcpb(breeder_percent_in_breeder_plus_multiplier_ratio=x)
    elif len(x) == 1:
        result = find_tbr_hcpb(breeder_percent_in_breeder_plus_multiplier_ratio=x[0])
    elif len(x) == 2:
        result = find_tbr_hcpb(
            breeder_percent_in_breeder_plus_multiplier_ratio=x[0],
            blanket_breeder_li6_enrichment=x[1],
        )
    return -1 * result["tbr"]
