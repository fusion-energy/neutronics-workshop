
import plotly.graph_objects as go
from tqdm import tqdm
import openmc
from openmc.data.reaction import REACTION_NAME
import os

def create_plot(isotopes, reaction):
    """Creates a 
    """
    nuclear_data_path = os.path.dirname(os.environ["OPENMC_CROSS_SECTIONS"]) + '/neutron'

    fig = create_plotly_figure()

    # this loop plots n,2n cross-sections for all isotopes
    # in the candidate_fusion_neutron_multipliers_list

    if isinstance(reaction, str):
        REACTION_NUMBER = dict(zip(REACTION_NAME.values(), REACTION_NAME.keys()))
        MT_number = REACTION_NUMBER[reaction]
    else:
        MT_number = reaction
        reaction = REACTION_NAME[MT_number]

    for isotope_name in tqdm(isotopes):
        isotope_object = openmc.data.IncidentNeutron.from_hdf5(os.path.join(nuclear_data_path, isotope_name+'.h5'))  # you may have to change this directory
        energy = isotope_object.energy['294K']  # 294K is the temperature for endf, others use 293K
        if MT_number in isotope_object.reactions.keys():
            cross_section = isotope_object[MT_number].xs['294K'](energy)
            fig.add_trace(go.Scatter(
                x=energy,
                y=cross_section,
                mode='lines',
                name=isotope_name + reaction
            )
        )
        else:
            print('isotope ', isotope_name, ' does not have the MT reaction number ', MT_number)

    return fig


def create_plotly_figure():
    
    fig = go.Figure()

    fig.update_layout(
          title='Neutron interaction cross sections',
          xaxis={'title': 'Energy (eV)',
                 'range': (0, 14.1e6)},
          yaxis={'title': 'Cross section (barns)'}
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

