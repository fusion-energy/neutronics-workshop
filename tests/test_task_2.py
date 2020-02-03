
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

class test_task_2(unittest.TestCase):

    def test_task_2_part_1(self): #  This test launches matplotlib that pauses the running of the script

        os.chdir(Path(cwd))
        os.chdir(Path('../tasks/task_2'))
        output_filenames = ['xz_sphere.png', 'xy_sphere.png', 'yz_sphere.png']
        for output_filename in output_filenames:
            os.system('rm '+output_filename)
        os.system('python 1_example_geometry_viewer_2d.py')
        for output_filename in output_filenames:
            assert Path(output_filename).exists() == True
            os.system('rm '+output_filename)


    def test_task_2_part_1_optional(self): #  This test launches eog that pauses the running of the script

        os.chdir(Path(cwd))
        os.chdir(Path('../tasks/task_2'))
        output_filename = 'plot.png'
        os.system('rm '+output_filename)
        os.system('python 2_example_geometry_viewer_2d_xml_version.py')
        assert Path(output_filename).exists() == True
        os.system('rm '+output_filename)


    def test_task_2_part_3(self): #  This test launches matplotlib that pauses the running of the script

        os.chdir(Path(cwd))
        os.chdir(Path('../tasks/task_2'))
        output_filenames = ['xz_tokamak.png', 'xy_tokamak.png', 'yz_tokamak.png']
        for output_filename in output_filenames:
            os.system('rm '+output_filename)
        os.system('python 3_example_geometry_viewer_2d_tokamak.py')
        for output_filename in output_filenames:
            assert Path(output_filename).exists() == True
            os.system('rm '+output_filename)


    def test_task_2_part_4(self):

        os.chdir(Path(cwd))
        os.chdir(Path('../tasks/task_2'))
        output_filename = 'plot_3d_tokamak.vti'
        os.system('rm '+output_filename)
        os.system('python 4_example_geometry_viewer_3d_tokamak.py')
        assert Path(output_filename).exists() == True
        os.system('rm '+output_filename)
