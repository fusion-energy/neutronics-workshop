import os

import openmc
import plotly.graph_objects as go
from openmc.data import atomic_weight
from openmc.data import REACTION_MT
from openmc.data.reaction import REACTION_NAME
from tqdm import tqdm
import neutronics_material_maker as nmm
import numpy as np


def create_isotope_plot(isotopes, reaction):
    """Creates a plot of elements and reaction provided"""

    if reaction not in REACTION_MT.keys():
        print(
            "Reaction not found, only these reactions are accepted", REACTION_MT.keys()
        )
        return None

    fig = create_plotly_figure()

    # this loop extracts the cross section and energy of reactions when they exist
    for isotope_name in tqdm(isotopes):

        isotope_object = openmc.Nuclide(isotope_name)

        energy, cross_sections = openmc.calculate_cexs(
            isotope_object, "nuclide", [reaction]
        )
        cross_section = cross_sections[0]
        if cross_section.sum() != 0.0:
            fig.add_trace(
                go.Scatter(
                    x=energy,
                    y=cross_section,
                    mode="lines",
                    name=isotope_name + " " + str(reaction),
                )
            )
        else:
            print("isotope ", isotope_name, " has no cross section data for ", reaction)

    return fig


def find_temperature_to_use(list_of_string_temps):

    # 294K is the temperature for endf, others use 293K
    list_of_ints = [int(t[:-1]) for t in list_of_string_temps]

    temp_value = min(list_of_ints, key=lambda x: abs(x - 294))

    return str(temp_value) + "K"


def create_element_plot(elements, reaction):
    """Creates a plot of elements and reaction provided"""

    if reaction not in REACTION_MT.keys():
        print(
            "Reaction not found, only these reactions are accepted", REACTION_MT.keys()
        )
        return None

    fig = create_plotly_figure()

    # this loop extracts the cross section and energy of reactions when they exist
    for element_name in tqdm(elements):

        element_object = openmc.Element(element_name)

        try:
            atomic_weight(element_name)
        except ValueError:
            print("There are no natural isotopes of ", element_name)
            continue

        energy, cross_sections = openmc.calculate_cexs(
            element_object, "element", [reaction]
        )
        cross_section = cross_sections[0]
        if cross_section.sum() != 0.0:
            fig.add_trace(
                go.Scatter(
                    x=energy,
                    y=cross_section,
                    mode="lines",
                    name=element_name + " " + str(reaction),
                )
            )
        else:
            print("Element ", element_name, " has no cross section data for ", reaction)

    return fig


def create_material_plot(materials, reaction):

    if reaction not in REACTION_MT.keys():
        print(
            "Reaction not found, only these reactions are accepted", REACTION_MT.keys()
        )
        return None

    fig = create_plotly_figure(y_axis_label="Macroscopic Cross Section (1/cm)")

    if isinstance(reaction, str):
        REACTION_NUMBER = dict(zip(REACTION_NAME.values(), REACTION_NAME.keys()))
        MT_number = REACTION_NUMBER[reaction]
    else:
        MT_number = reaction
        reaction = REACTION_NAME[MT_number]

    if not isinstance(materials, list):
        materials = [materials]

    for material in materials:
        # extracts energy and cross section for the material for the provided MT reaction mumber
        energy, xs_data = openmc.calculate_cexs(material, "material", [MT_number])

        # adds the energy dependnat cross sction to the plot
        fig.add_trace(
            go.Scatter(
                x=energy,
                y=xs_data[0],
                mode="lines",
                name=material.name + " " + reaction,
            )
        )

    return fig


def create_temperature_plot_for_isotope(
    isotope,
    temperatures,
    path_to_wmp="/WMP_Library",
    reaction="(n,total)",
    samples=50000,
    min_energy=1,
    max_energy=2000,
):

    energy = np.linspace(min_energy, max_energy, samples)

    fig = create_plotly_figure()

    if reaction not in REACTION_MT.keys():
        print(
            "Reaction not found, only these reactions are accepted", REACTION_MT.keys()
        )
        return None

    mt_number = REACTION_MT[reaction]

    for temperature in temperatures:

        h5_file = os.path.join(path_to_wmp, nmm.isotope_to_zaid(isotope) + ".h5")

        isotope_multipole = openmc.data.WindowedMultipole.from_hdf5(h5_file)

        fig.add_trace(
            go.Scatter(
                x=energy,
                y=isotope_multipole(energy, temperature)[mt_number],
                mode="lines",
                name=isotope + " " + reaction + " " + str(temperature) + " Kelvin",
            )
        )
    return fig


def create_plotly_figure(y_axis_label="Cross section (barns)"):

    fig = go.Figure()

    fig.update_layout(
        title="Neutron interaction cross sections",
        xaxis={"title": "Energy (eV)", "range": (0, 14.1e6)},
        yaxis={"title": y_axis_label},
    )

    # this adds the dropdown box for log and lin axis selection
    fig.update_layout(
        updatemenus=[
            go.layout.Updatemenu(
                buttons=list(
                    [
                        dict(
                            args=[
                                {
                                    "xaxis.type": "lin",
                                    "yaxis.type": "lin",
                                    "yaxis.range": (0, 14.1e6),
                                }
                            ],
                            label="linear(x) , linear(y)",
                            method="relayout",
                        ),
                        dict(
                            args=[{"xaxis.type": "log", "yaxis.type": "log"}],
                            label="log(x) , log(y)",
                            method="relayout",
                        ),
                        dict(
                            args=[
                                {
                                    "xaxis.type": "log",
                                    "yaxis.type": "lin",
                                    "yaxis.range": (0, 14.1e6),
                                }
                            ],
                            label="log(x) , linear(y)",
                            method="relayout",
                        ),
                        dict(
                            args=[{"xaxis.type": "lin", "yaxis.type": "log"}],
                            label="linear(x) , log(y)",
                            method="relayout",
                        ),
                    ]
                ),
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.5,
                xanchor="left",
                y=1.1,
                yanchor="top",
            ),
        ]
    )

    return fig
