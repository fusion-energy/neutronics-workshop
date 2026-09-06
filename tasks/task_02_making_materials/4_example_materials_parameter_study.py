# %% [markdown]
# ---
# title: Changing materials
# ---

# %% [markdown]
# As we saw in Part 3, the Neutronics Material Maker makes it easy to find the density of materials.
#
# It is important to account for material density correctly in neutronics simulations as the density of a material impacts the number density of atoms and therefore the neutronics reaction rate.
#
# Density is impacted by material properties such as temperature, enrichment and pressure.

# %%
# imports packages needed for the example

import numpy as np
import plotly.graph_objs as go

import neutronics_material_maker as nmm

# %% [markdown]
# The following example calculates water density as a function of temperature (at constant pressure) using the Neutronics Material Maker. The Neutronics Material Maker uses the Python CoolProp package to do this.
#
# Using input parameters from the WCLL blanket, we will show density as a function of temperature over a large range (at constant pressure).
#
# WCLL input parameters:
# - pressure = 15.5 MPa
# - inlet temperature = 285 degrees C
# - outlet temperature = 325 degrees C

# %%
temperatures = np.linspace(400, 800., 100) # in K

water_densities = [nmm.Material.from_library('H2O', temperature=temperature, pressure=15.5e6).openmc_material.density for temperature in temperatures] # pressure in Pa

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=temperatures,
    y=water_densities,
    mode='lines+markers',
    showlegend=False),
)

fig.update_layout(
    title="Water density as a function of temperature (at constant pressure)",
    xaxis_title="Temperature in K",
    yaxis_title="Density (g/cm3)"
)

fig.show()

# %% [markdown]
# Similarly, the next example shows how Helium density changes as a function of pressure (at constant temperature).

# %%
pressures = np.linspace(1e6, 10e6, 100) # in Pa

helium_densities = [nmm.Material.from_library('He', temperature=700, pressure=pressure).openmc_material.density for pressure in pressures]

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=pressures,
    y=helium_densities,
    mode='lines+markers',
    showlegend=False),
)

fig.update_layout(
    title="Helium density as a function of pressure (at constant temperature)",
    xaxis_title="Pressure in Pa",
    yaxis_title="Density (g/cm3)"
)

fig.show()

# %% [markdown]
# This example shows how the density of a Lithium ceramic changes as a function of Lithium-6 enrichment.

# %%
enrichments = np.linspace(0., 100., 50)

li4sio4_densities = [nmm.Material.from_library('Li4SiO4', enrichment=enrichment).openmc_material.density for enrichment in enrichments]

fig =go.Figure()

fig.add_trace(go.Scatter(
    x=enrichments,
    y=li4sio4_densities,
    mode='lines+markers',
    showlegend=False),
)

fig.update_layout(
    title="Lithium ceramic density as a function of Li-6 enrichment",
    xaxis_title="Li-6 enrichment",
    yaxis_title="Density (g/cm3)"
)

fig.show()

# %% [markdown]
# (Note: A density parameter study like this is not possible using in-built OpenMC functions as material densities must be specified explicitly).

# %% [markdown]
# **Learning Outcomes for Part 4:**
#
# - Understand that density varies for materials as a function of pressure, temperature and enrichment.
# - It is important to account for materials properties correctly, especially when they impact material density.
