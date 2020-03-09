#!/usr/bin/env python3

"""example_material_plot.py: plots cross sections for materials."""

import openmc
import plotly.graph_objects as go

natural_Li4SiO4 = openmc.Material()
natural_Li4SiO4.add_element('Li',4.0,percent_type='ao')
natural_Li4SiO4.add_element('Si',1.0,percent_type='ao')
natural_Li4SiO4.add_element('O',4.0,percent_type='ao')
natural_Li4SiO4.set_density('g/cm3',1.877)
#Li4SiO4 density 1.8770150075137564 g/cm3

# we can enrich the material directly by enriching the element
# removes the need to specify isotopes
enrichment = 60    # percentage enrichment
enriched_Li4SiO4 = openmc.Material()
enriched_Li4SiO4.add_element('Li', 4.0, percent_type='ao', enrichment=enrichment, enrichment_target='Li6', enrichment_type='ao')
enriched_Li4SiO4.add_element('Si',1.0,percent_type='ao')
enriched_Li4SiO4.add_element('O',4.0,percent_type='ao')
enriched_Li4SiO4.set_density('g/cm3',1.844) # this density is lower as there is more Li6 and less Li7
#Li4SiO4 density 1.8441466011318948 g/cm3 with 60% Li6


# Try adding another candidate breeder material (e.g. Li2SiO3, Li2ZrO3 or Li2TiO3) to the plot
#Li2SiO3 density 2.619497078021483 g/cm3
#Li2ZrO3 density 2.5288596326567134 g/cm3
#Li2TiO3 density 2.8994147653592983 g/cm3

Endf_MT_number = [205] # MT number 205 is (n,Xt) reaction

Energy_natural_Li4SiO4_MT16, xs_data = openmc.calculate_cexs(natural_Li4SiO4, 'material', Endf_MT_number )
cross_section_natural_Li4SiO4_MT16 = xs_data[0]

Energy_enriched_Li4SiO4_MT16, xs_data = openmc.calculate_cexs(enriched_Li4SiO4, 'material', Endf_MT_number )
cross_section_enriched_Li4SiO4_MT16 = xs_data[0]

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


fig.write_html("3_example_material_plot.html")
try:
      fig.write_html("/my_openmc_workshop/3_example_material_plot.html")
except (FileNotFoundError, NotADirectoryError):   # for both inside and outside docker container
      pass

fig.show()