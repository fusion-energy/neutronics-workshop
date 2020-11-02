
""" test_script.py: run all the examples in the openmc workshop and check each example produces the expected results.
    The example scripts open up various plots, some of which pause / block the running of this test suite.
    The running of the tests can be manually resumed by closing matplotlib and eog windows when they pop up
    run with
    pytest test_scripts.py
"""

# at the moment, we are only testing to see whether the outputs are created
# we are NOT testing to see whether the outputs are also saved locally
# this will have to be implemented

import os
import unittest
from pathlib import Path

import plotly
import plotly.graph_objects as go
import pytest

from tasks.task_1.plotting_utils import *

cwd = os.getcwd()

class test_task_1(unittest.TestCase):


    def test_task_1_part_1(self):

        fig = create_isotope_plot(
            isotopes=['Li6', 'Be9'],
            reaction=205)#,
            # nuclear_data_path='/home/jshim/data/nndc-b7.1-hdf5/neutron/')

        assert isinstance(fig, go.Figure)
