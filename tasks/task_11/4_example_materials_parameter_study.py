
import openmc
import numpy as np
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from tqdm import tqdm

from neutronics_material_maker import Material

# Because the neutronics_material_maker makes it easy to adjust material properties, we can easily perform parameter studies


# Water density as a function of temperature (at constant pressure)
# Based on WCLL, pressure = 15.5 MPa, inlet and outlet temperatures = 285 and 325 degrees C
# We will show density as a function of temperature over a larger range, but at correct pressure

temperatures = np.linspace(0.1, 600., 200)
water_densities = [Material('H2O', temperature_in_C=temperature, pressure_in_Pa=15500000).neutronics_material.density for temperature in temperatures]

fig = make_subplots(rows=2, cols=2, 
                    subplot_titles=("Water density as a function of temperature (at constant pressure)","title2","title3","title4"))

fig.add_trace(go.Scatter(x=temperatures,
                         y=water_densities,
                         mode='lines+markers')
                         ,row=1, col=1)

fig.update_xaxes({'title': 'Temperature in C'}, row=1, col=1)
fig.update_yaxes({'title': 'Density (g/cm3)'}, row=1, col=1)

fig.show()


# # Helium density as a function of temperature (at constant pressure)
# # Based on the HCPB, helium coolant is 8 MPa, inlet and outlet temperatures = 300 and 500 degrees C
# # We will show density as a function of temperature over a larger range, but at correct pressure

# temperatures = np.linspace(0.1, 600., 200)
# helium_densities = [Material('He', temperature_in_C=temperature, pressure_in_Pa=8000000).neutronics_material.density for temperature in temperatures]

# fig = go.Figure()
# fig.add_trace(go.Scatter(x=temperatures,
#                          y=helium_densities,
#                          mode='lines+markers'))
# fig.update_layout(
#     title='Helium density as a function of temperature (at constant pressure)',
#     xaxis={'title': 'Temperature in C'},
#     yaxis={'title': 'Density (g/cm3)'}
# )
# fig.show()


# # Helium density as a function of pressure (at constant temperature)
# # Based on the HCPB
# # Pressure is kept constant in HCPB, however, this is just demonstrating the effect

# pressures = np.linspace(1000000., 10000000., 100)
# helium_densities = [Material('He', temperature_in_C=400, pressure_in_Pa=pressure).neutronics_material.density for pressure in pressures]

# fig = go.Figure()
# fig.add_trace(go.Scatter(x=pressures,
#                          y=helium_densities,
#                          mode='lines+markers'))
# fig.update_layout(
#     title='Helium density as a function of pressure (at constant temperature)',
#     xaxis={'title': 'Pressure (Pa)'},
#     yaxis={'title': 'Density (g/cm3)'}
# )
# fig.show()
