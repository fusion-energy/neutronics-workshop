# %% [markdown]
# ---
# title: TBR parametric study using openmc.lib
# ---

# %% [markdown]
# This example finds the Tritium Breeding Ratio (TBR) as a function of lithium-6 enrichment by running multiple simulations **without reloading nuclear data** between runs.
#
# Normally each `model.run()` call loads all nuclear data from scratch. For quick simulations like TBR on a simple geometry, data loading can dominate the total runtime. The `openmc.lib` module provides Python bindings to the C/C++ API, giving fine-grained control over:
# - Loading data once with `openmc.lib.init()`
# - Modifying material compositions between runs
# - Resetting tallies with `openmc.lib.hard_reset()`
# - Running simulations with `openmc.lib.run()`
#
# This approach is significantly faster when sweeping over many parameter values.
#
# First import packages and configure the nuclear data path.

# %%
import openmc
from pathlib import Path

# Setting the cross section path to the correct location in the docker image.
# If you are running this outside the docker image you will have to change this path to your local cross section path.
openmc.config['cross_sections'] = Path.home() / 'nuclear_data' / 'cross_sections.xml'

import plotly.graph_objects as go

# %% [markdown]
# ## Materials
#
# A simple model with a steel first wall and a lead-lithium (Pb84.2Li15.8) breeder blanket. The lithium enrichment in the breeder will be varied during the parametric study.

# %%
breeder_material = openmc.Material(material_id=12)  # Pb84.2Li15.8
breeder_material.add_element('Pb', 84.2)
breeder_material.add_element('Li', 15.8)
breeder_material.set_density('g/cm3', 11.)

steel = openmc.Material(material_id=6)
steel.set_density('g/cm3', 7.75)
steel.add_element('Fe', 0.95)
steel.add_element('C', 0.05)

my_materials = openmc.Materials([breeder_material, steel])

# %% [markdown]
# ## Geometry
#
# A concentric sphere model:
# - Inner void (plasma region) — r < 500 cm
# - Steel first wall — 500 to 510 cm
# - Breeder blanket — 510 to 610 cm

# %%
# surfaces
vessel_inner = openmc.Sphere(r=500)
first_wall_outer_surface = openmc.Sphere(r=510)
breeder_blanket_outer_surface = openmc.Sphere(r=610, boundary_type='vacuum')

# cells
inner_vessel_region = -vessel_inner
inner_vessel_cell = openmc.Cell(region=inner_vessel_region)

first_wall_region = -first_wall_outer_surface & +vessel_inner
first_wall_cell = openmc.Cell(region=first_wall_region)
first_wall_cell.fill = steel

breeder_blanket_region = +first_wall_outer_surface & -breeder_blanket_outer_surface
breeder_blanket_cell = openmc.Cell(region=breeder_blanket_region)
breeder_blanket_cell.fill = breeder_material

my_geometry = openmc.Geometry([inner_vessel_cell, first_wall_cell, breeder_blanket_cell])

# %% [markdown]
# ## Settings and source
#
# A 14 MeV point source at the origin with trigger-based batching — the simulation runs between 10 and 100 batches, stopping when statistical triggers are satisfied.

# %%
my_settings = openmc.Settings()
my_settings.batches = 10
my_settings.trigger_active = True
my_settings.trigger_max_batches = 100
my_settings.inactive = 0
my_settings.particles = 1000
my_settings.run_mode = 'fixed source'

source = openmc.IndependentSource()
source.space = openmc.stats.Point((0, 0, 0))
source.angle = openmc.stats.Isotropic()
source.energy = openmc.stats.Discrete([14e6], [1])
my_settings.source = source

# %% [markdown]
# ## Tallies
#
# A single tally scoring tritium production (H3-production) in the breeder blanket cell. This gives us the TBR directly — the number of tritium atoms produced per source neutron.

# %%
cell_filter = openmc.CellFilter(breeder_blanket_cell)
tbr_tally = openmc.Tally(name='TBR', tally_id=42)
tbr_tally.filters = [cell_filter]
tbr_tally.scores = ['H3-production']
my_tallies = openmc.Tallies([tbr_tally])

# %% [markdown]
# ## Export model and initialise openmc.lib
#
# We export the model to XML, then call `openmc.lib.init()` which loads the nuclear data **once**. All subsequent runs reuse this data.

# %%
model = openmc.Model(my_geometry, my_materials, my_settings, my_tallies)
model.export_to_model_xml()

import openmc.lib
openmc.lib.init()

# %% [markdown]
# ## Run a single simulation
#
# First we run once with the default natural lithium enrichment to verify everything works.

# %%
openmc.lib.run()
tally = openmc.lib.tallies[42]
print(f'tally result {tally.mean} with std. dev. {tally.std_dev}')

# %% [markdown]
# ## Parametric study: TBR vs Li-6 enrichment
#
# Now we loop over several Li-6 enrichment values. For each enrichment:
# 1. Reset tallies to zero with `openmc.lib.hard_reset()`
# 2. Update the breeder material composition via `openmc.lib` — replacing natural Li with a specific Li-6/Li-7 ratio
# 3. Run the simulation
# 4. Read the TBR tally result
#
# Nuclear data is **not** reloaded between runs, saving significant time.

# %%
results = []
enrichments = [0.0001, 0.25, 0.50, 0.75, 0.9999]

for enrichment in enrichments:

    # reset tallies so we don't combine with previous simulation
    openmc.lib.hard_reset()

    # update the python material object to get new densities
    breeder_material.remove_element('Li')
    breeder_material.add_nuclide('Li6', 15.8 * enrichment)
    breeder_material.add_nuclide('Li7', 15.8 * (1. - enrichment))

    # get nuclide atom densities in atom/b-cm
    new_composition = breeder_material.get_nuclide_atom_densities()
    nuclides = list(new_composition.keys())
    densities = list(new_composition.values())

    # update the openmc.lib material
    lib_breeder_material = openmc.lib.materials[breeder_material.id]
    print(f'old nuclides {lib_breeder_material.nuclides}')
    print(f'old densities {lib_breeder_material.densities}')
    lib_breeder_material.set_densities(densities=densities, nuclides=nuclides)
    print(f'new nuclides {lib_breeder_material.nuclides}')
    print(f'new densities {lib_breeder_material.densities}')

    # run simulation
    openmc.lib.run()

    # get the TBR tally result
    tally = openmc.lib.tallies[42]
    print(f'tally result {tally.mean} with std. dev. {tally.std_dev}')

    results.append(tally.mean.flatten()[0])

# close down openmc.lib interface
openmc.lib.finalize()

# %% [markdown]
# ## Plot results
#
# TBR as a function of Li-6 enrichment. Higher Li-6 enrichment generally increases TBR due to the larger Li-6(n,t) cross section at thermal energies.

# %%
fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=enrichments,
        y=results,
        mode='lines',
    )
)

fig.update_layout(
    title="TBR as a function of Li6 enrichment",
    xaxis_title="Li6 enrichment (%)",
    yaxis_title="TBR",
)

fig.show()

# %% [markdown]
# **Learning Outcomes:**
#
# - Using `openmc.lib` to avoid reloading nuclear data between parametric runs.
# - Modifying material compositions at runtime via the C/C++ API bindings.
# - Running a parametric sweep over lithium-6 enrichment to study its effect on TBR.
# - Understanding the workflow: `init()` -> `run()` -> `hard_reset()` -> modify -> `run()` -> `finalize()`.
