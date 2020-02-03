
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



class test_task_8(unittest.TestCase):

    def test_task_8_part_1(self):

        os.chdir(Path(cwd))
        os.chdir(Path('../tasks/task_8'))
        os.system('rm outputs/*.json')
        os.system('rmdir outputs')
        os.system('python 1_simulate_with_random_sample.py')
        assert Path('outputs').exists() == True
        assert len(os.listdir('outputs')) != 0

    def test_task_8_part_2(self):

        os.chdir(Path(cwd))
        os.chdir(Path('../tasks/task_8'))
        output_filenames = ['TBR_vs_enrichment_fraction.html', 'TBR_vs_thickness.html']
        for output_filename in output_filenames:
            os.system('rm '+output_filename)
        os.system('python plot_simulation_results_2d.py')
        for output_filename in output_filenames:
            assert Path(output_filename).exists() == True
            os.system('rm '+output_filename)

    def test_task_8_part_3(self):

        os.chdir(Path(cwd))
        os.chdir(Path('../tasks/task_8'))
        output_filename = 'TBR_vs_thickness_vs_enrichment_fraction.html'
        os.system('rm '+output_filename)
        os.system('python plot_simulation_results_3d.py')
        assert Path(output_filename).exists() == True
        os.system('rm '+output_filename)
        os.system('rm outputs/*.json')
        os.system('rmdir outputs')

    def test_task_8_part_4(self):

        os.chdir(Path(cwd))
        os.chdir(Path('../tasks/task_8'))
        os.system('rm outputs/*.json')
        os.system('rmdir outputs')
        os.system('python 1_simulate_with_halton_sample.py')
        assert Path('outputs').exists() == True
        assert len(os.listdir('outputs')) != 0