
import plotly.graph_objects as go


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

