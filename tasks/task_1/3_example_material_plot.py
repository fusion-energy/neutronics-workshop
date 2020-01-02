#!/usr/bin/env python3

"""example_isotope_plot.py: plots cross sections for materials."""

__author__      = "Jonathan Shimwell"

import openmc
import plotly.graph_objects as go

natural_Li4SiO4 = openmc.Material()
natural_Li4SiO4.add_element('Li',4.0,percent_type='ao')
natural_Li4SiO4.add_element('Si',1.0,percent_type='ao')
natural_Li4SiO4.add_element('O',4.0,percent_type='ao')
natural_Li4SiO4.set_density('g/cm3',1.877) # this density was found using crystal volumes function


enrichment_fraction=0.6
enriched_Li4SiO4 = openmc.Material()
enriched_Li4SiO4.add_nuclide('Li6',4.0*enrichment_fraction,percent_type='ao')
enriched_Li4SiO4.add_nuclide('Li7',4.0*(1-enrichment_fraction),percent_type='ao')
enriched_Li4SiO4.add_element('Si',1.0,percent_type='ao')
enriched_Li4SiO4.add_element('O',4.0,percent_type='ao')
enriched_Li4SiO4.set_density('g/cm3',1.844) # this density is lower as there is more Li6 and less

#natural_Li4SiO4 density 1.8770150075137564 g/cm3 
#enriched_Li4SiO4 density 1.8441466011318948 g/cm3 #60% Li6
#natural_Li2SiO3 density 2.619497078021483 g/cm3
#natural_Li2ZrO3 density 2.5288596326567134 g/cm3
#natural_Li2TiO3 density 2.8994147653592983 g/cm3

Endf_MT_number = [205] # MT number 205 is (n,Xt) reaction

Energy_natural_Li4SiO4_MT16, data = openmc.calculate_cexs(natural_Li4SiO4, 'material', Endf_MT_number )
cross_section_natural_Li4SiO4_MT16 = data[0]

Energy_enriched_Li4SiO4_MT16, data = openmc.calculate_cexs(enriched_Li4SiO4, 'material', Endf_MT_number )
cross_section_enriched_Li4SiO4_MT16 = data[0]

fig = go.Figure()

fig.add_trace(go.Scatter(x=Energy_natural_Li4SiO4_MT16, 
              y=cross_section_natural_Li4SiO4_MT16, 
              mode = 'lines', 
              name='natural Li4SiO4 (n,t)')
             )

fig.add_trace(go.Scatter(x=Energy_enriched_Li4SiO4_MT16, 
              y=cross_section_enriched_Li4SiO4_MT16, 
              mode = 'lines', 
              name='enriched Li4SiO4 (n,t)')
             )


fig.update_layout(
      title = 'Material cross sections',
      xaxis = {'title':'Energy (eV)', 'type':'log'},
      yaxis = {'title':'Macroscopic Cross Section (1/cm)', 'type':'log'}
)

fig.show()
fig.write_html("3_example_material_plot.html")
