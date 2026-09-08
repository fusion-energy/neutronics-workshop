# %% [markdown]
# ---
# title: Simulating TBR as a function of Lithium enrichment
# ---

# %% [markdown]
# Lithium isotopes have natural abundances of 7.59% Li6 and 92.41% Li7. However, due to the different tritium-production cross sections of the two isotopes it is often beneficial to enrich the Li6 content to increase tritium breeding.
#
# This task allows users to make a simple model with a Lithium blanket of controllable enrichment. Simulations are then performed for several different Li6 enrichments and the TBR found.

# %% [markdown]
# First import OpenMC and configure the nuclear data path

# %%
import openmc
from pathlib import Path
# Setting the cross section path to the correct location in the docker image.
# If you are running this outside the docker image you will have to change this path to your local cross section path.
openmc.config['cross_sections'] = Path.home() / 'nuclear_data' / 'cross_sections.xml'

import plotly.graph_objects as go


# %% [markdown]
# This first code block a neutronics model for the provided enrichment value, runs the simulation and returns the TBR value obtained.

# %%
def make_materials_geometry_tallies(enrichment):
    """Makes a neutronics model of a blanket and simulates the TBR value.

    Arguments:
        enrichment (float): the enrichment percentage of Li6 in the breeder material
    
    Returns:
        results (dict): simulation tally results for TBR along with the standard deviation and enrichment
    """

    # MATERIALS

    breeder_material = openmc.Material()  # Pb84.2Li15.8
    breeder_material.add_element('Pb', 84.2, percent_type='ao')
    breeder_material.add_element('Li', 15.8, percent_type='ao', enrichment=enrichment, enrichment_target='Li6', enrichment_type='ao')
    breeder_material.set_density('atom/b-cm', 3.2720171e-2)  # around 11 g/cm3


    steel = openmc.Material()
    steel.set_density('g/cm3', 7.75)
    steel.add_element('Fe', 0.95, percent_type='wo')
    steel.add_element('C', 0.05, percent_type='wo')

    my_materials = openmc.Materials([breeder_material, steel])


    # GEOMETRY

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


    # SIMULATION SETTINGS
    my_settings = openmc.Settings()
    my_settings.batches = 10  # this is minimum number of batches that will be run
    my_settings.trigger_active = True
    my_settings.trigger_max_batches =  100  # this is maximum number of batches that will be run
    my_settings.inactive = 0
    my_settings.particles = 1000
    my_settings.run_mode = 'fixed source'

    source = openmc.IndependentSource(
        space=openmc.stats.Point((0, 0, 0)),
        angle=openmc.stats.Isotropic(),
        energy=openmc.stats.Discrete([14e6], [1])
    )
    my_settings.source = source

    # TALLIES

    cell_filter = openmc.CellFilter(breeder_blanket_cell)
    tbr_tally = openmc.Tally(name='TBR')
    tbr_tally.filters = [cell_filter]
    tbr_tally.scores = ['H3-production']  # H3-production tallies all tritium-producing reactions (equivalent to '(n,Xt)')
    tbr_tally.triggers = [openmc.Trigger(trigger_type='std_dev', threshold=0.01)]  # This stops the simulation if the threshold is meet
    my_tallies = openmc.Tallies([tbr_tally])

    # RUN OPENMC
    model = openmc.Model(my_geometry, my_materials, my_settings, my_tallies)
    for f in Path('.').glob('*.h5'):
        f.unlink(missing_ok=True)
    sp_filename = model.run(output=False)  # runs with reduced amount of output printing

    # OPEN OUPUT FILE
    with openmc.StatePoint(sp_filename) as sp:

        tbr_tally = sp.get_tally(name='TBR')

        df = tbr_tally.get_pandas_dataframe()

        tbr_tally_result = df['mean'].sum()
        tbr_tally_std_dev = df['std. dev.'].sum()

    return {'enrichment': enrichment,
            'tbr_tally_result': tbr_tally_result,
            'tbr_tally_std_dev': tbr_tally_std_dev}

# %% [markdown]
# This code block runs the code defined above with different blanket enrichments and returns the TBR tally results.

# %%
results = []
for enrichment in [0, 25, 50, 75, 100]:  # percentage enrichment from 0% Li6 to 100% Li6
    results.append(make_materials_geometry_tallies(enrichment))

# %% [markdown]
# Finally, this code block plots a figure showing TBR as a function of Li6 enrichment.

# %%
fig = go.Figure()

# PLOTS RESULTS
fig.add_trace(
    go.Scatter(
        x=[entry['enrichment'] for entry in results],
        y=[entry['tbr_tally_result'] for entry in results],
        mode='lines',
        error_y={'array': [entry['tbr_tally_std_dev'] for entry in results]},
        )
)

fig.update_layout(
    title="TBR as a function of Li6 enrichment",
    xaxis_title="Li6 enrichment (%)",
    yaxis_title="TBR"
)

fig.show()

# %% [markdown]
# **Learning Outcomes for Part 2:**
#
# - Performing parameter studies with OpenMC.
# - Simple methods of increasing the TBR using Lithium enrichment.
