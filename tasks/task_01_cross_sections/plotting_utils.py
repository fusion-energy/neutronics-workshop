
import os

import openmc
import plotly.graph_objects as go
from openmc.data import atomic_weight
from openmc.data import REACTION_MT
from openmc.data.reaction import REACTION_NAME
from tqdm import tqdm
import neutronics_material_maker as nmm
import numpy as np


def create_isotope_plot(isotopes, reaction, nuclear_data_path=None):
    """Creates a plot of isotopes and reaction provided
    """
    if nuclear_data_path == None:
        nuclear_data_path = os.path.dirname(os.environ["OPENMC_CROSS_SECTIONS"]) + '/neutron'

    if reaction not in REACTION_MT.keys():
        print('Reaction not found, only these reactions are accepted', REACTION_MT.keys())
        return None
   
    mt_number = REACTION_MT[reaction]

    fig = create_plotly_figure()

    # this loop plots n,2n cross-sections for all isotopes
    # in the candidate_fusion_neutron_multipliers_list

    for isotope_name in tqdm(isotopes):
        isotope_object = openmc.data.IncidentNeutron.from_hdf5(os.path.join(nuclear_data_path, isotope_name+'.h5'))  # you may have to change this directory
        energy = isotope_object.energy['294K']  # 294K is the temperature for endf, others use 293K
        if mt_number in isotope_object.reactions.keys():
            cross_section = isotope_object[mt_number].xs['294K'](energy)
            fig.add_trace(go.Scatter(
                x=energy,
                y=cross_section,
                mode='lines',
                name=isotope_name + str(reaction)
            )
        )
        else:
            print('isotope ', isotope_name, ' does not have the MT reaction number ', reaction)

    return fig


def create_element_plot(elements, reaction):
    """Creates a plot of elements and reaction provided
    """

    if reaction not in REACTION_MT.keys():
        print('Reaction not found, only these reactions are accepted', REACTION_MT.keys())
        return None

    fig = create_plotly_figure()

    # this loop extracts the cross section and energy of reactions when they exist
    for element_name in tqdm(elements):

        element_object = openmc.Element(element_name)

        try:
            atomic_weight(element_name)
        except ValueError:
            print('There are no natural isotopes of ', element_name)
            continue

        energy, cross_sections = openmc.calculate_cexs(
            element_object,
            'element',
            [reaction])
        cross_section = cross_sections[0]
        if cross_section.sum() != 0.0:
            fig.add_trace(go.Scatter(
                x=energy,
                y=cross_section,
                mode='lines',
                name=element_name + ' ' + str(reaction))
            )
        else:
            print('Element ', element_name, ' has no cross section data for ', reaction)

    return fig


def create_material_plot(materials, reaction):

    if reaction not in REACTION_MT.keys():
        print('Reaction not found, only these reactions are accepted', REACTION_MT.keys())
        return None

    fig = create_plotly_figure(y_axis_label='Macroscopic Cross Section (1/cm)')

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
        energy, xs_data = openmc.calculate_cexs(
            material,
            'material',
            [MT_number])

        # adds the energy dependnat cross sction to the plot
        fig.add_trace(go.Scatter(
            x=energy,
            y=xs_data[0],
            mode='lines',
            name=material.name + ' ' + reaction)
        )

    return fig


def create_temperature_plot_for_isotope(
    isotope, temperatures,
    path_to_wmp='/WMP_Library',
    reaction='(n,total)',
    samples=50000,
    min_energy=1,
    max_energy=2000
):

    energy = np.linspace(min_energy, max_energy, samples)

    fig = create_plotly_figure()

    if reaction not in REACTION_MT.keys():
        print('Reaction not found, only these reactions are accepted', REACTION_MT.keys())
        return None

    mt_number = REACTION_MT[reaction]

    for temperature in temperatures:

        h5_file = os.path.join(path_to_wmp, nmm.isotope_to_zaid(isotope) + '.h5')

        isotope_multipole = openmc.data.WindowedMultipole.from_hdf5(h5_file)

        fig.add_trace(go.Scatter(
                        x=energy,
                        y=isotope_multipole(energy, temperature)[mt_number],
                        mode='lines',
                        name=isotope + ' ' + reaction + ' ' + str(temperature)+' Kelvin')
                    )
    return fig


def create_plotly_figure(y_axis_label='Cross section (barns)'):
    
    fig = go.Figure()

    fig.update_layout(
          title='Neutron interaction cross sections',
          xaxis={'title': 'Energy (eV)',
                 'range': (0, 14.1e6)},
          yaxis={'title': y_axis_label}
    )


    # this adds the dropdown box for log and lin axis selection
    fig.update_layout(
        updatemenus=[
            go.layout.Updatemenu(
                buttons=list([
                    dict(
                        args=[{"xaxis.type": 'lin', "yaxis.type": 'lin', 'yaxis.range': (0, 14.1e6)}],
                        label="linear(x) , linear(y)",
                        method="relayout"
                    ),
                    dict(
                        args=[{"xaxis.type": 'log', "yaxis.type": 'log'}],
                        label="log(x) , log(y)",
                        method="relayout"
                    ),
                    dict(
                        args=[{"xaxis.type": 'log', "yaxis.type": 'lin', 'yaxis.range': (0, 14.1e6)}],
                        label="log(x) , linear(y)",
                        method="relayout"
                    ),
                    dict(
                        args=[{"xaxis.type": 'lin', "yaxis.type": 'log'}],
                        label="linear(x) , log(y)",
                        method="relayout"
                    )
                ]),
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.5,
                xanchor="left",
                y=1.1,
                yanchor="top"
            ),
        ]
    )
    
    return fig
