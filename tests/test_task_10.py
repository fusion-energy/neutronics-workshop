
""" test_script.py: run all the examples in the openmc workshop and check each example produces the expected results.
    The example scripts open up various plots, some of which pause / block the running of this test suite.
    The running of the tests can be manually resumed by closing matplotlib and eog windows when they pop up
    run with
    pytest test_scripts.py
"""


from pathlib import Path
import os
import unittest
import json

cwd = os.getcwd()


class test_task_10(unittest.TestCase):

    def test_task_10_part_1(self):
        # PPP not currently available so this test just checks that the brep file is present
        os.chdir(Path(cwd))
        os.chdir(Path('tasks/task_10'))
        output_filename = 'manifest_processed/manifest_processed.brep'
        assert Path(output_filename).exists() is True

    def test_task_10_part_2(self):
        # tests to see if the dagmc_notwatertight.h5m is created
        os.chdir(Path(cwd))
        os.chdir(Path('tasks/task_10'))
        output_filename = 'dagmc_notwatertight.h5m'
        os.system('rm '+output_filename)
        os.system('occ_faceter manifest_processed/manifest_processed.brep -t 0.0001 -o dagmc_notwatertight.h5m')
        assert Path(output_filename).exists() is True

    def test_task_10_part_3(self):
        # tests to see if the dagmc.h5m is created
        os.chdir(Path(cwd))
        os.chdir(Path('tasks/task_10'))
        output_filename = 'dagmc.h5m'
        os.system('rm '+output_filename)
        os.system('make_watertight dagmc_notwatertight.h5m -o dagmc.h5m')
        assert Path(output_filename).exists() is True

    def test_task_10_part_4(self):
        # tests to see if the dagmc.stl is created
        os.chdir(Path(cwd))
        os.chdir(Path('tasks/task_10'))
        output_filename = 'dagmc.stl'
        os.system('rm '+output_filename)
        os.system('mbconvert dagmc.h5m dagmc.stl')
        assert Path(output_filename).exists() is True

    def test_task_10_part_5(self):
        # tests to see if the dagmc.vtk is created
        os.chdir(Path(cwd))
        os.chdir(Path('tasks/task_10'))
        output_filename = 'dagmc.vtk'
        os.system('rm '+output_filename)
        os.system('mbconvert dagmc.h5m dagmc.vtk')
        assert Path(output_filename).exists() is True

    def test_task_10_part_6(self):
        # checks for json output file and that tbr value is above 0.01
        os.chdir(Path(cwd))
        os.chdir(Path('tasks/task_10'))
        output_filename = 'cad_simulation_results.json'
        os.system('rm '+output_filename)
        os.system('python3 example_CAD_simulation.py')
        assert Path(output_filename).exists() is True
        os.system('rm '+output_filename)
        with open('cad_simulation_results.json') as json_file:
            data = json.load(json_file)
        assert data['TBR'] > 0.01
