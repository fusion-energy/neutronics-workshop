
""" test_script.py: run all the examples in the openmc workshop and check each example produces the expected results.
    The example scripts open up various plots, some of which pause / block the running of this test suite.
    The running of the tests can be manually resumed by closing matplotlib and eog windows when they pop up
    run with
    pytest test_scripts.py
"""

# at the moment, we are only testing to see whether the outputs are created
# we are NOT testing to see whether the outputs are also saved locally
# this will have to be implemented

from pathlib import Path 
import os
import pytest
import unittest

cwd = os.getcwd()




class test_task_10(unittest.TestCase):
    def test_task_10_part_1(self):

        os.chdir(Path(cwd))
        os.chdir(Path('../tasks/task_10'))
        output_filename = 'cad_simulation_results.json'
        os.system('rm '+output_filename)
        os.system('python example_CAD_simulation.py')
        assert Path(output_filename).exists() == True
        os.system('rm '+output_filename)
