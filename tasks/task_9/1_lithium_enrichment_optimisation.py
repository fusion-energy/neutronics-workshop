
import json

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from skopt.acquisition import gaussian_ei
from skopt.utils import load

from openmc_model import objective

# Note, optimisation functions tend to minimise the value therefore there are a few negative signs in these scripts


# Loads true data for comparison
data = pd.read_json('enrichment_vs_tbr.json')

x_data=data['enrichment']
fx=-data['tbr']

res = load('saved_optimisation_1d.dat')

number_of_initial_points = len(res.specs['args']['x0'])

number_of_calls = res.specs['args']['n_calls']

x = np.linspace(0, 100, 101).reshape(-1, 1)
x_gp = res.space.transform(x)


fig = make_subplots(rows=2, cols=1)


for n_iter in range(number_of_initial_points + 1, number_of_calls +1):
    gp = res.models[n_iter]
    curr_x_iters = [i[0] for i in res.x_iters[number_of_initial_points:
                                              number_of_initial_points + n_iter]]
    curr_func_vals = res.func_vals[number_of_initial_points:

                                   number_of_initial_points + n_iter]




    y_pred, sigma = gp.predict(x_gp, return_std=True)


    fig.add_trace(go.Scatter(name='Uncertainty',
                             x=[i[0] for i in np.concatenate([x, x[::-1]])],
                             y=np.concatenate([-y_pred - 1.9600 * sigma, (-y_pred + 1.9600 * sigma)[::-1]]),
                             visible=False,
                             line = {'shape': 'spline'},
                            #  mode='markers',
                             fill='toself', fillcolor = 'rgba(0, 0, 255, 0.1)',line_color='rgba(0, 0, 255, 0.1)'
                            ),
                            row=1,
                            col=1,
                 )

    fig.add_trace(go.Scatter(name="Predicted values",
                             x = np.linspace(0, 100, 101), 
                             y = -y_pred,
                             visible=False,
                             line = {'shape': 'spline', 'dash': 'dash'},
                             marker=dict(color='rgba(0, 0, 255, 0.5)')
                            ),
                            row=1,
                            col=1,
                )


    # Plot samples from optimsation points
    fig.add_trace(go.Scatter(x = curr_x_iters,
                             y = -curr_func_vals,
                             name="Samples from optimisation",
                             visible=False,
                             mode='markers',
                             marker=dict(color='red', size=10)
                            ),
                            row=1,
                            col=1,
                 )

    # # Plot acquisition function
    if n_iter > 0:
        acq = gaussian_ei(x_gp, gp, y_opt=np.min(curr_func_vals))
        # fig.add_trace(go.Scatter(name = 'Acquisition function',
        #                          x = x_data, 
        #                          y = acq,
        #                          visible=False,
        #                          line = {'shape': 'spline', 'color': 'pink'},
        #                         ),
        #                     row=2,
        #                     col=1
        #              )


        fig.add_trace(go.Scatter(name='Acquisition function',
                                 x = x_data, 
                                 y = acq,
                                 visible=False,
                                 line = {'shape': 'spline', 'color': 'pink'},
                                 fill='tozeroy', fillcolor = 'rgba(255,192,203, 0.5)',line_color='rgba(255,192,203, 0.1)'
                                ),
                            row=2,
                            col=1
                     )
    else:
        fig.add_trace(go.Scatter(name = 'Acquisition function',
                                 x = [0], 
                                 y = [0],
                                 visible=False,
                                 line = {'shape': 'spline', 'color': 'pink'},
                                ),
                            row=2,
                            col=1
                     )

        # plt.plot(x, acq, "b", label="EI(x)")
        # plt.fill_between(x.ravel(), 0, acq.ravel(), alpha=0.3, color='blue')

        # if n_iter+1 < number_of_calls:
        #     next_x = res.x_iters[n_iter+1]
        #     next_acq = gaussian_ei(res.space.transform([next_x]), gp,
        #                         y_opt=np.min(curr_func_vals))
        #     plt.plot(next_x, next_acq, "bo", markersize=6, label="Next query point")

# Plot true function.
fig.add_trace(go.Scatter(name="True value (unknown)",
                          x = x_data,
                          y = [-i for i in fx],
                          mode='lines',
                          visible=False,
                          line = {'shape': 'spline'},
                          marker=dict(color='green')
                         ),
                            row=1,
                            col=1,
              )

# Plot provided points (from adative sampling)
fig.add_trace(go.Scatter(name = "Initial values (provided)",
                            x = [i[0] for i in res.x_iters[0:number_of_initial_points]], 
                            y = -res.func_vals[0:number_of_initial_points],
                            visible=False,
                            mode='markers',
                            marker=dict(color='red', symbol='square', size=10)
                        ),
                            row=1,
                            col=1,
                )


fig.data[0].visible = True
fig.data[1].visible = True
fig.data[2].visible = True
fig.data[3].visible = True
fig.data[-1].visible = True
fig.data[-2].visible = True
# fig.data[-4].visible = True
# fig.data[-6].visible = True
# fig.data[-7].visible = True
# fig.data[-8].visible = True

# Create and add slider
steps = []
number_of_traces = 4
for i in range(int((len(fig.data)-2)/number_of_traces)):
    step = dict(
        method="restyle",
        args=["visible", [False] * len(fig.data)],
    )
    step["args"][1][-1] = True  # Toggle i'th trace to "visible"
    step["args"][1][-2] = True  # Toggle i'th trace to "visible"

    step["args"][1][i*number_of_traces] = True  # Toggle i'th trace to "visible"
    step["args"][1][i*number_of_traces+1] = True  # Toggle i'th trace to "visible"
    step["args"][1][i*number_of_traces+2] = True  # Toggle i'th trace to "visible"
    step["args"][1][i*number_of_traces+3] = True  # Toggle i'th trace to "visible"
    # step["args"][1][i*number_of_traces+4] = True  # Toggle i'th trace to "visible"
    # step["args"][1][i*number_of_traces+5] = True  # Toggle i'th trace to "visible"
    # step["args"][1][i*number_of_traces+6] = True  # Toggle i'th trace to "visible"
    steps.append(step)

sliders = [dict(
    active=0,
    currentvalue={"prefix": "Opimisation simulation number : "},
    pad={"t": 50},
    steps=steps
)]

fig.update_layout(
    sliders=sliders
)


fig.update_layout(title='Optimal Li6 enrichment',
                  xaxis={'title': 'Li6 enrichment percent', 'range': [0, 100]},
                  yaxis={'title': 'TBR', 'range': [0.1, 1.15]}
                 )



print('Maximum TBR of ', -res.fun, 'found with an enrichment of ', res.x[0])
print('Maximum TBR of ', data.loc[data['tbr'].idxmax()]['tbr'], 
      'found with an enrichment of ', data.loc[data['tbr'].idxmax()]['enrichment'])

fig.write_html("lithium_optimization.html")
try:
    fig.write_html("/my_openmc_workshop/lithium_optimization.html")
except (FileNotFoundError, NotADirectoryError):  # for both inside and outside docker container
    pass

fig.show()
