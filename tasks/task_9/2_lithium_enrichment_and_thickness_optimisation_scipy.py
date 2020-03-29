
import numpy as np
import plotly.graph_objects as go
from skopt import gp_minimize

import ghalton
from openmc_model import objective

# objective is a function that returns -1 the TBR value when provided with the Li6 enrichment as an argument

coordinates_of_the_corners = [(0,10), (0,200), (100,10), (100,200)]
values_at_the_corners = [-0.0865, -0.15773, -0.66504, -0.92599]

sequencer = ghalton.Halton(2)
coordinates_of_halton_sample = []
for x1, x2 in sequencer.get(6):
    coordinates_of_halton_sample.append((int(x1*100) , int(x2*200) ))

# for s in coordinates_of_halton_sample:
#     print(objective(s))

values_at_halton_samples = [-0.9824353617820968,-1.0082879243700122,-0.8488502137501063,-1.010285169362084,-0.9730493189782068,-0.9741671906168285]

starting_coords = coordinates_of_the_corners + coordinates_of_halton_sample
starting_values = values_at_the_corners + values_at_halton_samples


# This returns an scipy optimisation object
res_gp = gp_minimize(func=objective,
                     dimensions=[(0, 100), (10, 200)], # as these are integers values the optimiers only tries integers
                     x0=starting_coords,  # specifying first simulation coordinates (these are the periphery of the parameter space)
                     y0=starting_values,  # specifying results of first simulation coordinates
                     n_random_starts=0,  # setting this to 0 as well spaced starting points have been set
                     n_calls=10,
                     verbose=True)

print('Optimal Li6 enrichment = ', res_gp.x[0])
print('Optimal thickness = ', res_gp.x[1])
print('Maximum TBR = ', -res_gp.fun)

fig = go.Figure()

fig.add_trace(go.Scatter3d(name='All TBR values found',
                         x=[x[0] for x in res_gp.x_iters],
                         y=[x[1] for x in res_gp.x_iters],
                         z=-res_gp.func_vals,
                         mode='markers'
                        )
             )

fig.add_trace(go.Scatter3d(name='Maximum TBR value found',
                         x=[res_gp.x[0]],
                         y=[res_gp.x[1]],
                         z=[-res_gp.fun],
                         mode='markers'
                        )
             )

fig.add_trace(go.Scatter3d(name='Starting points',
                         x=[x[0] for x in res_gp.x_iters][0:10],
                         y=[x[1] for x in res_gp.x_iters][0:10],
                         z=-res_gp.func_vals[0:10],
                         mode='markers'
                        )
             )

fig.update_layout(title='Optimal Li6 enrichment and blanket thickness',
                  scene={'xaxis': {'title': 'Li6 enrichment percent'},
                         'yaxis': {'title': 'Blanket thickness'},
                         'zaxis': {'title': 'TBR'}
                        }
                 )

fig.show()
