#!/usr/bin/env python3

"""example_isotope_plot.py: plots few 2D views of a simple tokamak geometry with neutron flux."""

__author__  = "Jonathan Shimwell"

import openmc
import plotly.graph_objects as go
from tqdm import tqdm


def make_materials_geometry_tallies(enrichment):

    # MATERIALS

    breeder_material = openmc.Material(1, "PbLi")  # Pb84.2Li15.8
    breeder_material.add_element('Pb', 84.2, percent_type='ao')
    breeder_material.add_element('Li', 15.8, percent_type='ao', enrichment=enrichment, enrichment_target='Li6', enrichment_type='ao')
    breeder_material.set_density('atom/b-cm', 3.2720171e-2)  # around 11 g/cm3


    steel = openmc.Material(name='steel')
    steel.set_density('g/cm3', 7.75)
    steel.add_element('Fe', 0.95, percent_type='wo')
    steel.add_element('C', 0.05, percent_type='wo')

    mats = openmc.Materials([breeder_material, steel])


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

    universe = openmc.Universe(cells=[inner_vessel_cell, first_wall_cell, breeder_blanket_cell])
    geom = openmc.Geometry(universe)


    # SIMULATION SETTINGS
    sett = openmc.Settings()
    sett.batches = 2  # this is minimum number of batches that will be run
    sett.trigger_active = True
    sett.trigger_max_batches =  200  # this is maximum number of batches that will be run
    sett.inactive = 0
    sett.particles = 1000
    sett.run_mode = 'fixed source'

    source = openmc.Source()
    source.space = openmc.stats.Point((0, 0, 0))
    source.angle = openmc.stats.Isotropic()
    source.energy = openmc.stats.Discrete([14e6], [1])
    sett.source = source

    # TALLIES

    tallies = openmc.Tallies()

    cell_filter = openmc.CellFilter(breeder_blanket_cell)
    tbr_tally = openmc.Tally(name='TBR')
    tbr_tally.filters = [cell_filter]
    tbr_tally.scores = ['(n,Xt)']  # MT 205 is the (n,Xt) reaction where X is a wildcard, if MT 105 or (n,t) then some tritium production will be missed, for example (n,nt) which happens in Li7 would be missed
    tbr_tally.triggers = [openmc.Trigger(trigger_type='std_dev', threshold=0.01)]  # This stops the simulation if the threshold is meet
    tallies.append(tbr_tally)

    # RUN OPENMC
    model = openmc.model.Model(geom, mats, sett, tallies)
    sp_filename = model.run()

    # OPEN OUPUT FILE
    sp = openmc.StatePoint(sp_filename)

    tbr_tally = sp.get_tally(name='TBR')

    df = tbr_tally.get_pandas_dataframe()

    tbr_tally_result = df['mean'].sum()
    tbr_tally_std_dev = df['std. dev.'].sum()

    return {'enrichment': enrichment,
            'tbr_tally_result': tbr_tally_result,
            'tbr_tally_std_dev': tbr_tally_std_dev}


results = []
for enrichment in tqdm([0, 25, 50, 75, 100]):  # percentage enrichment from 0% Li6 to 100% Li6
    results.append(make_materials_geometry_tallies(enrichment))

print('results', results)

fig = go.Figure()

# PLOTS RESULTS
fig.add_trace(go.Scatter(x=[entry['enrichment'] for entry in results],
                         y=[entry['tbr_tally_result'] for entry in results],
                         mode='lines',
                         error_y={'array': [entry['tbr_tally_std_dev'] for entry in results]},
                )
             )

fig.update_layout(
      title='Tritium production as a function of Li6 enrichment',
      xaxis={'title': 'Li6 enrichment (%)'},
      yaxis={'title': 'TBR'}
)

fig.write_html("tbr_study.html")
try:
    fig.write_html("/my_openmc_workshop/tbr_study.html")
except (FileNotFoundError, NotADirectoryError):  # for both inside and outside docker container
    pass

fig.show()
