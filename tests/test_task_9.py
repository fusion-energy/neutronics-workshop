
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





class test_task_9(unittest.TestCase):
    def test_task_9_part_1(self):
        # assumes get_true_values_1d.py has been run previously and json file in repo
        # just checks the json file exisits as it is needed in the task
        os.chdir(Path(cwd))
        os.chdir(Path('tasks/task_9'))
        output_filenames = ['1d_tbr_values.json']

        for output_filename in output_filenames:
            assert Path(output_filename).exists() is True
            # file not removed as it is needed in the next test

    def test_task_9_part_2(self):
        # runs a 1d optimisation

        os.chdir(Path(cwd))
        os.chdir(Path('tasks/task_9'))
        output_filenames = ['saved_optimisation_1d.dat']
        for output_filename in output_filenames:
            os.system('rm '+output_filename)

        os.system('python get_optimised_values_1d.py')

        for output_filename in output_filenames:
            assert Path(output_filename).exists() is True
            # file not removed as it is needed in the next test

    def test_task_9_part_3(self):
        # plots a graph

        os.chdir(Path(cwd))
        os.chdir(Path('tasks/task_9'))
        output_filenames = ['1d_optimization_graph.html']
        for output_filename in output_filenames:
            os.system('rm '+output_filename)

        os.system('python 1_plot_1d_optimisation.py')
        for output_filename in output_filenames:
            assert Path(output_filename).exists() is True
            os.system('rm '+output_filename)

    def test_task_9_part_4(self):
        # assumes get_true_values_2d.py has been run previously and json file in repo

        os.chdir(Path(cwd))
        os.chdir(Path('tasks/task_9'))
        output_filenames = ['2d_tbr_values.json']

        for output_filename in output_filenames:
            assert Path(output_filename).exists() is True
            # file not removed as it is needed in the next test

    def test_task_9_part_5(self):
        # runs a 2d optimisation

        os.chdir(Path(cwd))
        os.chdir(Path('tasks/task_9'))
        output_filenames = ['saved_optimisation_2d.dat']
        for output_filename in output_filenames:
            os.system('rm '+output_filename)

        os.system('python get_optimised_values_2d.py')
        for output_filename in output_filenames:
            assert Path(output_filename).exists() is True
            # file not removed as it is needed in the next test

    def test_task_9_part_6(self):
        # plots a scatter graph

        os.chdir(Path(cwd))
        os.chdir(Path('tasks/task_9'))
        output_filenames = ['2d_optimization_graph_scatter.html']
        for output_filename in output_filenames:
            os.system('rm '+output_filename)

        os.system('python 2_plot_2d_optimisation_scatter.py')
        for output_filename in output_filenames:
            assert Path(output_filename).exists() is True
            os.system('rm '+output_filename)

    def test_task_9_part_7(self):
        # plots a contour graph

        os.chdir(Path(cwd))
        os.chdir(Path('tasks/task_9'))
        output_filenames = ['2d_optimization_graph_contour.html']
        for output_filename in output_filenames:
            os.system('rm '+output_filename)

        os.system('python 2_plot_2d_optimisation_contour.py')
        for output_filename in output_filenames:
            assert Path(output_filename).exists() is True
            os.system('rm '+output_filename)