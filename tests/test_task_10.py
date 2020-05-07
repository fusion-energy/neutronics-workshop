
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

    # PPP not currently available
    # def test_task_10_part_1(self):

    #     os.chdir(Path(cwd))
    #     os.chdir(Path('tasks/task_10'))
    #     output_filename = 'manifest_processed/manifest_processed.brep'
    #     os.system('rm '+output_filename)
    #     os.system('geomPipeline.py manifest.json')
    #     assert Path(output_filename).exists() == True

    # def test_task_10_part_1(self):

    #     os.chdir(Path(cwd))
    #     os.chdir(Path('tasks/task_10'))
    #     output_filename = 'dagmc_notwatertight.h5m'
    #     os.system('rm '+output_filename)
    #     os.system('steps2h5m geometry_details.json 1. dagmc_notwatertight.h5m')
    #     assert Path(output_filename).exists() == True


    def test_task_10_part_2(self):

        os.chdir(Path(cwd))
        os.chdir(Path('tasks/task_10'))
        output_filename = 'dagmc.h5m'
        os.system('rm '+output_filename)
        os.system('make_watertight dagmc_notwatertight.h5m -o dagmc.h5m')
        assert Path(output_filename).exists() == True


    def test_task_10_part_3(self):

        os.chdir(Path(cwd))
        os.chdir(Path('tasks/task_10'))
        output_filename = 'cad_simulation_results.json'
        os.system('rm '+output_filename)
        os.system('python3 example_CAD_simulation.py')
        assert Path(output_filename).exists() == True
        os.system('rm '+output_filename)
