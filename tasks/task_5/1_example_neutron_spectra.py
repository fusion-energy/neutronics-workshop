#!/usr/bin/env python3

"""1_example_neutron_spectra_tokamak.py: plots neutron spectra."""

import openmc
import plotly.graph_objects as go

# MATERIALS

eurofer = openmc.Material(name='eurofer')
eurofer.add_element('Fe', 89.067, percent_type='wo')
eurofer.add_element('C', 0.11, percent_type='wo')
eurofer.add_element('Mn', 0.4, percent_type='wo')
eurofer.add_element('Cr', 9.0, percent_type='wo')
eurofer.add_element('Ta', 0.12, percent_type='wo')
eurofer.add_element('W', 1.1, percent_type='wo')
eurofer.add_element('N', 0.003, percent_type='wo')
eurofer.add_element('V', 0.2, percent_type='wo')
eurofer.set_density('g/cm3', 7.75)

mats = openmc.Materials([eurofer])


# GEOMETRY

# surfaces
vessel_surface = openmc.Sphere(r=500)
outer_surface = openmc.Sphere(r=600, boundary_type='vacuum')

# cells
inner_vessel_cell = openmc.Cell(region=-vessel_surface)
# this is filled with a void / vauum by default

blanket_cell = openmc.Cell(region=-outer_surface & +vessel_surface)
blanket_cell.fill = eurofer

universe = openmc.Universe(cells=[inner_vessel_cell,blanket_cell])
geom = openmc.Geometry(universe)


# SIMULATION SETTINGS

# Instantiate a Settings object
sett = openmc.Settings()
sett.batches = 40
sett.particles = 100
sett.run_mode = 'fixed source'

# Create a DT point source
source = openmc.Source()
source.space = openmc.stats.Point((0, 0, 0))
source.angle = openmc.stats.Isotropic()
source.energy = openmc.stats.Discrete([14e6], [1])
sett.source = source

# setup the  filters for the tallies

neutron_particle_filter = openmc.ParticleFilter(['neutron'])
cell_filter = openmc.CellFilter(blanket_cell) # detects particles across a cell / volume
# surface_filter = openmc.SurfaceFilter(outer_surface) # detects particles across a surface
energy_bins = openmc.mgxs.GROUP_STRUCTURES['VITAMIN-J-175'] # other energy group structures are avaiable https://github.com/openmc-dev/openmc/blob/develop/openmc/mgxs/__init__.py
energy_filter = openmc.EnergyFilter(energy_bins)
spectra_tally = openmc.Tally(name='blanket_cell_neutron_spectra')
spectra_tally.filters = [cell_filter, neutron_particle_filter, energy_filter]
spectra_tally.scores = ['flux']

tallies = openmc.Tallies()
tallies.append(spectra_tally)


# combine all the required parts to make a model
model = openmc.model.Model(geom, mats, sett, tallies)
# Run OpenMC!
results_filename = model.run()

# open the results file
results = openmc.StatePoint(results_filename)


spectra_tally = results.get_tally(name='blanket_cell_neutron_spectra')  # add another tally for first_wall_spectra
df = spectra_tally.get_pandas_dataframe()
spectra_tally_result = df['mean']


fig = go.Figure()

fig.add_trace(go.Scatter(x=energy_bins,
                         y=spectra_tally_result,
                         name='breeder_blanket_spectra',
                         line=dict(shape='hv')
                        )
              )

fig.update_layout(
      title='Neutron energy spectra',
      xaxis={'title': 'Energy (eV)'},
      yaxis={'title': 'Neutrons per cm2 per source neutron',
             'type': 'log'
            }
)

fig.write_html("tokamak_spectra.html")
try:
    fig.write_html("/my_openmc_workshop/tokamak_spectra.html")
except (FileNotFoundError, NotADirectoryError):  # for both inside and outside docker container
    pass

fig.show()
