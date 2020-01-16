#!/usr/bin/env python3

"""example_isotope_plot.py: plots cross sections for a couple of isotopes."""

import openmc
import plotly.graph_objects as go
import openmc.data
from tqdm import tqdm
import os


#this list will take a long time to process
all_stable_isotope_list = ['Ag107', 'Ag109', 'Al27', 'Ar36', 'Ar38', 'Ar40', 'As75', 'Au197', 'B10', 'B11', 'Ba130', 'Ba132', 'Ba134', 'Ba135', 'Ba136', 'Ba137', 'Ba138', 'Be9', 'Bi209','Br79', 'Br81', 'Ca40', 'Ca42', 'Ca43', 'Ca44', 'Ca46', 'Ca48', 'Cd106', 'Cd108', 'Cd110', 'Cd111', 'Cd112', 'Cd113', 'Cd114', 'Cd116', 'Ce136', 'Ce138', 'Ce140', 'Ce142', 'Cl35', 'Cl37', 'Co59', 'Cr50', 'Cr52', 'Cr53', 'Cr54', 'Cs133', 'Cu63', 'Cu65', 'Dy156', 'Dy158', 'Dy160', 'Dy161', 'Dy162', 'Dy163', 'Dy164', 'Er162', 'Er164', 'Er166', 'Er167', 'Er168', 'Er170', 'Eu151', 'Eu153', 'F19', 'Fe54', 'Fe56', 'Fe57', 'Fe58', 'Ga69', 'Ga71', 'Gd152', 'Gd154', 'Gd155', 'Gd156', 'Gd157', 'Gd158', 'Gd160', 'Ge70', 'Ge72', 'Ge73', 'Ge74', 'Ge76', 'H1', 'H2', 'He3', 'He4', 'Hf174', 'Hf176', 'Hf177', 'Hf178', 'Hf179', 'Hf180', 'Hg196', 'Hg198', 'Hg199', 'Hg200', 'Hg201', 'Hg202', 'Hg204', 'Ho165', 'I127', 'In113', 'In115', 'Ir191', 'Ir193', 'K39', 'K40', 'K41', 'Kr78', 'Kr80', 'Kr82', 'Kr83', 'Kr84', 'Kr86', 'La138', 'La139', 'Li6', 'Li7', 'Lu175', 'Lu176', 'Mg24', 'Mg25', 'Mg26', 'Mn55', 'Mo100', 'Mo92', 'Mo94', 'Mo95', 'Mo96', 'Mo97', 'Mo98', 'N14', 'N15', 'Na23', 'Nb93', 'Nd142', 'Nd143', 'Nd144', 'Nd145', 'Nd146', 'Nd148', 'Nd150', 'Ni58', 'Ni60', 'Ni61', 'Ni62', 'Ni64', 'O16', 'O17', 'P31', 'Pa231', 'Pb204', 'Pb206', 'Pb207', 'Pb208', 'Pd102', 'Pd104', 'Pd105', 'Pd106', 'Pd108', 'Pd110', 'Pr141', 'Rb85', 'Rb87', 'Re185', 'Re187', 'Rh103', 'Ru100', 'Ru101', 'Ru102', 'Ru104', 'Ru96', 'Ru98', 'Ru99', 'S32', 'S33', 'S34', 'S36', 'Sb121', 'Sb123', 'Sc45', 'Se74', 'Se76', 'Se77', 'Se78', 'Se80', 'Se82', 'Si28', 'Si29', 'Si30', 'Sm144', 'Sm147', 'Sm148', 'Sm149', 'Sm150', 'Sm152', 'Sm154', 'Sn112', 'Sn114', 'Sn115', 'Sn116', 'Sn117', 'Sn118', 'Sn119', 'Sn120', 'Sn122', 'Sn124', 'Sr84', 'Sr86', 'Sr87', 'Sr88', 'Ta180', 'Ta181', 'Tb159', 'Te120', 'Te122', 'Te123', 'Te124', 'Te125', 'Te126', 'Te128', 'Te130', 'Th232', 'Ti46', 'Ti47', 'Ti48', 'Ti49', 'Ti50', 'Tl203', 'Tl205', 'Tm169', 'U234', 'U235', 'U238', 'V50', 'V51', 'W180', 'W182', 'W183', 'W184', 'W186', 'Xe124', 'Xe126', 'Xe128', 'Xe129', 'Xe130', 'Xe131', 'Xe132', 'Xe134', 'Xe136', 'Y89', 'Zn64', 'Zn66', 'Zn67', 'Zn68', 'Zn70', 'Zr90', 'Zr91', 'Zr92', 'Zr94', 'Zr96']


#therefore we use this list instead
candidate_fusion_neutron_multipliers_list = ['Be9', 'Pb204', 'Pb206']  # ,'Pb207','Pb208']
candidate_fusion_tritium_producers_list = ['Li6','Li7']

MT_number = 16 # MT number 16 is (n,2n) reaction others can be found https://www.oecd-nea.org/dbdata/data/manual-endf/endf102_MT.pdf
# MT 205 is the (n,Xt) reaction where X is a wildcard
# MT 444 is DPA damage

nuclear_data_path = os.path.dirname(os.environ["OPENMC_CROSS_SECTIONS"]) + '/neutron'

fig = go.Figure()
# this loop extracts the cross section data for each isotope in the list
for isotope_name in tqdm(candidate_fusion_neutron_multipliers_list):
      isotope_object = openmc.data.IncidentNeutron.from_hdf5(os.path.join(nuclear_data_path,isotope_name+'.h5')) # you may have to change this directory
      energy = isotope_object.energy['294K'] # 294K is the temperature for endf, others use 293K
      if MT_number in isotope_object.reactions.keys():
            cross_section = isotope_object[MT_number].xs['294K'](energy)
            fig.add_trace(go.Scatter(x=energy,
                              y=cross_section,
                              mode = 'lines',
                              name=isotope_name+' MT '+ str(MT_number)
                              )
                        )
      else:
            print('isotope ', isotope_name , ' does not have the MT reaction number ',MT_number)


fig.update_layout(
      title = 'Isotope cross sections MT '+ str(MT_number),
      xaxis = {'title':'Energy (eV)',
               'range':(0,14.1e6)
               },
      yaxis = {'title':'Cross section (barns)'
              }
)


# this adds the dropdown box for log and lin axis selection
fig.update_layout(
    updatemenus=[
        go.layout.Updatemenu(
            buttons=list([
                dict(
                    args=[{"xaxis.type":'lin', "yaxis.type":'lin', 'yaxis.range':(0,14.1e6)}],
                    label="linear(x) , linear(y)",
                    method="relayout"
                ),
                dict(
                    args=[{"xaxis.type":'log', "yaxis.type":'log'}],
                    label="log(x) , log(y)",
                    method="relayout"
                ),
                dict(
                    args=[{"xaxis.type":'log', "yaxis.type":'lin', 'yaxis.range':(0,14.1e6)}],
                    label="log(x) , linear(y)",
                    method="relayout"
                ),
                dict(
                    args=[{"xaxis.type":'lin', "yaxis.type":'log'}],
                    label="linear(x) , log(y)",
                    method="relayout"
                )
            ]),
            pad={"r": 10, "t": 10},
            showactive=True,
            x=0.5,
            xanchor="left",
            y=1.1,
            yanchor="top"
        ),
    ]
)

fig.write_html("1_example_isotope_plot.html")
try:
    fig.write_html("/my_openmc_workshop/1_example_isotope_plot.html")
except (FileNotFoundError, NotADirectoryError):   # for both inside and outside docker container
    pass

fig.show()