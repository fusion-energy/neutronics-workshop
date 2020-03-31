
import json

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from skopt import gp_minimize
from skopt.acquisition import gaussian_ei
from skopt.utils import load

from openmc_model import objective

# Note, optimisation functions tend to minimise the value therefore there are a few negative signs in these scripts


# Loads true data for comparison
with open('enrichment_vs_tbr.json', 'r') as f: 
    data = json.load(f)

x_data=[i[0] for i in data]
fx=[-i[1] for i in data]

res = load('saved_optimisation_1d.dat')

number_of_initial_points = len(res.specs['args']['x0'])

number_of_calls = res.specs['args']['n_calls']


x = np.linspace(0, 100, 101).reshape(-1, 1)
x_gp = res.space.transform(x)


fig = go.Figure()




for n_iter in range(0, number_of_calls - number_of_initial_points +1):
    gp = res.models[n_iter]
    curr_x_iters = [i[0] for i in res.x_iters[number_of_initial_points:
                                              number_of_initial_points + n_iter]]
    curr_func_vals = res.func_vals[number_of_initial_points:
                                   number_of_initial_points + n_iter]




    y_pred, sigma = gp.predict(x_gp, return_std=True)

    fig.add_trace(go.Scatter(name='uncertainty',
                             x=[i[0] for i in np.concatenate([x, x[::-1]])],
                             y=np.concatenate([-y_pred - 1.9600 * sigma, (-y_pred + 1.9600 * sigma)[::-1]]),
                             visible=False,
                            #  mode='markers',
                             fill='toself', fillcolor = 'rgba(0, 0, 255, 0.1)',line_color='rgba(0, 0, 255, 0.1)'

    )
    )

    fig.add_trace(go.Scatter(name="Predicted values",
                             x = np.linspace(0, 100, 101), 
                             y = -y_pred,
                             visible=False,
                             marker=dict(color='blue')
                            )
                )


    # Plot sampled points
    fig.add_trace(go.Scatter(x = curr_x_iters,
                             y = -curr_func_vals,
                             name="Observations",
                             visible=False,
                             mode='markers',
                             marker=dict(color='red')
                            )
                 )

    # # Plot EI(x)
    # plt.subplot(2, 1, 2)
    # if n_iter > 0:
    #     acq = gaussian_ei(x_gp, gp, y_opt=np.min(curr_func_vals))
    #     plt.plot(x, acq, "b", label="EI(x)")
    #     plt.fill_between(x.ravel(), 0, acq.ravel(), alpha=0.3, color='blue')

    #     if n_iter+1 < number_of_calls:
    #         next_x = res.x_iters[n_iter+1]
    #         next_acq = gaussian_ei(res.space.transform([next_x]), gp,
    #                             y_opt=np.min(curr_func_vals))
    #         plt.plot(next_x, next_acq, "bo", markersize=6, label="Next query point")

# Plot true function.
fig.add_trace(go.Scatter(name="True value (unknown)",
                          x = x_data,
                          y = [-i for i in fx],
                          mode='lines',
                          visible=False,
                          marker=dict(color='green')
                         )
              )

# Plot provided points (from adative sampling)
fig.add_trace(go.Scatter(name = "Initial values (provided)",
                            x = [i[0] for i in res.x_iters[0:number_of_initial_points]], 
                            y = -res.func_vals[0:number_of_initial_points],
                             mode='markers',
                            marker=dict(color='pink')
                        )
                )

# fig.data[0].visible = True
# fig.data[1].visible = True
# fig.data[2].visible = True

fig.data[-1].visible = True
fig.data[-2].visible = True
fig.data[-3].visible = True
fig.data[-4].visible = True
fig.data[-5].visible = True

# Create and add slider
steps = []
for i in range(int((len(fig.data)-2)/3)):
    step = dict(
        method="restyle",
        args=["visible", [False] * len(fig.data)],
    )
    step["args"][1][-1] = True  # Toggle i'th trace to "visible"
    step["args"][1][-2] = True  # Toggle i'th trace to "visible"
    
    step["args"][1][i*3] = True  # Toggle i'th trace to "visible"
    step["args"][1][i*3+1] = True  # Toggle i'th trace to "visible"
    step["args"][1][i*3+2] = True  # Toggle i'th trace to "visible"
    # step["args"][1][i+3] = True  # Toggle i'th trace to "visible"
    steps.append(step)

sliders = [dict(
    active=10,
    currentvalue={"prefix": "Frequency: "},
    pad={"t": 50},
    steps=steps
)]

fig.update_layout(
    sliders=sliders
)


fig.update_layout(title='Optimal Li6 enrichment',
                  xaxis={'title': 'Li6 enrichment percent'},
                  yaxis={'title': 'TBR'}
                 )

fig.show()


fx=[-i[1] for i in data]

print('Maximum TBR of ', res.fun, 'found with an enrichment of ', res.x)
print('Maximum TBR of ', min(fx), 'found with an enrichment of ', fx.index(min(fx)))

fig.write_html("lithium_optimization.html")
try:
    fig.write_html("/my_openmc_workshop/lithium_optimization.html")
except (FileNotFoundError, NotADirectoryError):  # for both inside and outside docker container
    pass

fig.show()
