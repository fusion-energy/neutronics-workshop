import plotly.graph_objects as go


def add_trace_to_figure(
    figure,
    energy_bins,
    values,
    std_dev
):

    if len(energy_bins)==710:
        #removes energy bins above 20MeV in the CCFE 709 strucuture
        energy_bins=energy_bins[:-59]
        values=values[:-59]
        std_dev=std_dev[:-59]

    # adds a line for the upper stanadard deviation bound
    figure.add_trace(go.Scatter(x=energy_bins,
                            y=values+std_dev,
                            line=dict(shape='hv', width=0)
                            )
                )

    # adds a line for the lower stanadard deviation bound
    figure.add_trace(go.Scatter(x=energy_bins,
                            y=values-std_dev,
                            name='std. dev.',
                            fill='tonext',
                            line=dict(shape='hv', width=0)
                            )
                )

    # adds a line for the tally result
    figure.add_trace(go.Scatter(x=energy_bins,
                            y=values,
                            name='breeder_blanket_spectra',
                            line=dict(shape='hv')
                            )
                )
    
    return figure

def create_plotly_figure(
    y_axis_label
):


    # this section plots the results
    figure = go.Figure()

    figure.update_layout(
          xaxis={'title': 'Energy (eV)',
                 'range': (0, 14.1e6)},
          yaxis={'title': y_axis_label}
    )

    # this adds the dropdown box for log and lin axis selection
    figure.update_layout(
        updatemenus=[
            go.layout.Updatemenu(
                buttons=list([
                    dict(
                        args=[{
                            "xaxis.type": 'lin', "yaxis.type": 'lin',
                            'xaxis.range': (0, 14.1e6)
                            }],
                        label="linear(x) , linear(y)",
                        method="relayout"
                    ),
                    dict(
                        args=[{"xaxis.type": 'log', "yaxis.type": 'log'}],
                        label="log(x) , log(y)",
                        method="relayout"
                    ),
                    dict(
                        args=[{"xaxis.type": 'log', "yaxis.type": 'lin'}],
                        label="log(x) , linear(y)",
                        method="relayout"
                    ),
                    dict(
                        args=[{"xaxis.type": 'lin', "yaxis.type": 'log',
                            'xaxis.range': (0, 14.1e6)
                        }],
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

    return figure
