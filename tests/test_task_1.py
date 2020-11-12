
"""
tests the create_isotope_plot from plotting_utils in the same way the examples
use the function.
"""

import os
import unittest

import plotly.graph_objects as go

from tasks.task_1.plotting_utils import create_isotope_plot


class test_task_1(unittest.TestCase):

    def test_task_1_notebook_1_part_1(self):

        isotopes_of_interest = ['Be9', 'Pb204']
        reactions_of_interest = '(n,2n)'

        fig = create_isotope_plot(
            isotopes=isotopes_of_interest,
            reaction=reactions_of_interest,
        )
        assert isinstance(fig, go.Figure)

    def test_task_1_notebook_1_part_2(self):

        isotopes_of_interest = ['Be9', 'Pb204', 'Pb206', 'Pb207', 'Pb208']
        reactions_of_interest = '(n,2n)'

        fig = create_isotope_plot(
            isotopes=isotopes_of_interest,
            reaction=reactions_of_interest,
        )
        assert isinstance(fig, go.Figure)

    def test_task_1_notebook_1_part_2(self):

        # this is a list of every stable isotope, this list will take a long time to process
        isotopes_of_interest = ['Ag107', 'Ag109', 'Al27', 'Ar36', 'Ar38', 'Ar40', 'As75', 'Au197', 'B10', 'B11', 'Ba130',
                                'Ba132', 'Ba134', 'Ba135', 'Ba136', 'Ba137', 'Ba138', 'Be9', 'Bi209','Br79', 'Br81',
                                'Ca40', 'Ca42', 'Ca43', 'Ca44', 'Ca46', 'Ca48', 'Cd106', 'Cd108', 'Cd110', 'Cd111',
                                'Cd112', 'Cd113', 'Cd114', 'Cd116', 'Ce136', 'Ce138', 'Ce140', 'Ce142', 'Cl35', 'Cl37',
                                'Co59', 'Cr50', 'Cr52', 'Cr53', 'Cr54', 'Cs133', 'Cu63', 'Cu65', 'Dy156', 'Dy158',
                                'Dy160', 'Dy161', 'Dy162', 'Dy163', 'Dy164', 'Er162', 'Er164', 'Er166', 'Er167', 'Er168',
                                'Er170', 'Eu151', 'Eu153', 'F19', 'Fe54', 'Fe56', 'Fe57', 'Fe58', 'Ga69', 'Ga71', 'Gd152',
                                'Gd154', 'Gd155', 'Gd156', 'Gd157', 'Gd158', 'Gd160', 'Ge70', 'Ge72', 'Ge73', 'Ge74',
                                'Ge76', 'H1', 'H2', 'He3', 'He4', 'Hf174', 'Hf176', 'Hf177', 'Hf178', 'Hf179', 'Hf180',
                                'Hg196', 'Hg198', 'Hg199', 'Hg200', 'Hg201', 'Hg202', 'Hg204', 'Ho165', 'I127', 'In113',
                                'In115', 'Ir191', 'Ir193', 'K39', 'K40', 'K41', 'Kr78', 'Kr80', 'Kr82', 'Kr83', 'Kr84',
                                'Kr86', 'La138', 'La139', 'Li6', 'Li7', 'Lu175', 'Lu176', 'Mg24', 'Mg25', 'Mg26', 'Mn55',
                                'Mo100', 'Mo92', 'Mo94', 'Mo95', 'Mo96', 'Mo97', 'Mo98', 'N14', 'N15', 'Na23', 'Nb93',
                                'Nd142', 'Nd143', 'Nd144', 'Nd145', 'Nd146', 'Nd148', 'Nd150', 'Ni58', 'Ni60', 'Ni61',
                                'Ni62', 'Ni64', 'O16', 'O17', 'P31', 'Pa231', 'Pb204', 'Pb206', 'Pb207', 'Pb208', 'Pd102',
                                'Pd104', 'Pd105', 'Pd106', 'Pd108', 'Pd110', 'Pr141', 'Rb85', 'Rb87', 'Re185', 'Re187',
                                'Rh103', 'Ru100', 'Ru101', 'Ru102', 'Ru104', 'Ru96', 'Ru98', 'Ru99', 'S32', 'S33', 'S34',
                                'S36', 'Sb121', 'Sb123', 'Sc45', 'Se74', 'Se76', 'Se77', 'Se78', 'Se80', 'Se82', 'Si28',
                                'Si29', 'Si30', 'Sm144', 'Sm147', 'Sm148', 'Sm149', 'Sm150', 'Sm152', 'Sm154', 'Sn112',
                                'Sn114', 'Sn115', 'Sn116', 'Sn117', 'Sn118', 'Sn119', 'Sn120', 'Sn122', 'Sn124', 'Sr84',
                                'Sr86', 'Sr87', 'Sr88', 'Ta180', 'Ta181', 'Tb159', 'Te120', 'Te122', 'Te123', 'Te124',
                                'Te125', 'Te126', 'Te128', 'Te130', 'Th232', 'Ti46', 'Ti47', 'Ti48', 'Ti49', 'Ti50',
                                'Tl203', 'Tl205', 'Tm169', 'U234', 'U235', 'U238', 'V50', 'V51', 'W180', 'W182', 'W183',
                                'W184', 'W186', 'Xe124', 'Xe126', 'Xe128', 'Xe129', 'Xe130', 'Xe131', 'Xe132', 'Xe134',
                                'Xe136', 'Y89', 'Zn64', 'Zn66', 'Zn67', 'Zn68', 'Zn70', 'Zr90', 'Zr91', 'Zr92', 'Zr94',
                                'Zr96']

        # The (n,2n) is one incident neutron and two neutrons produced
        reactions_of_interest = '(n,2n)'

        fig = create_isotope_plot(
            isotopes=isotopes_of_interest,
            reaction=reactions_of_interest,
        )
        assert isinstance(fig, go.Figure)
