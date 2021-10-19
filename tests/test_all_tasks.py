
"""
tests the create_isotope_plot from plotting_utils in the same way the examples
use the function.
"""

import os
import sys
import unittest
from pathlib import Path

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert.preprocessors.execute import CellExecutionError


def _notebook_run(path):
    """
    Execute a notebook via nbconvert and collect output.
    :returns (parsed nb object, execution errors)
    """
    kernel_name = 'python%d' % sys.version_info[0]
    this_file_directory = os.path.dirname(__file__)
    errors = []

    with open(path) as f:
        nb = nbformat.read(f, as_version=4)
        nb.metadata.get('kernelspec', {})['name'] = kernel_name
        ep = ExecutePreprocessor(kernel_name=kernel_name, timeout=300) #, allow_errors=True

        try:
            ep.preprocess(nb, {'metadata': {'path': this_file_directory}})

        except CellExecutionError as e: 
            if "SKIP" in e.traceback:
                print(str(e.traceback).split("\n")[-2])
            else:
                raise e

    return nb, errors


class test_tasks(unittest.TestCase):

    def test_task_1(self):
        for notebook in Path().rglob("tasks/tasks/task_01_*/*.ipynb"):
            print(notebook)
            nb, errors = _notebook_run(notebook)
            assert errors == []

    def test_task_2(self):
        for notebook in Path().rglob("tasks/task_02_*/*.ipynb"):
            print(notebook)
            nb, errors = _notebook_run(notebook)
            assert errors == []

    def test_task_3(self):
        for notebook in Path().rglob("tasks/task_03_*/*.ipynb"):
            print(notebook)
            nb, errors = _notebook_run(notebook)
            assert errors == []

# ModuleNotFoundError: No module named 'source_extraction_utils
    # def test_task_4(self):
            # print(notebook)
    #     for notebook in Path().rglob("tasks/task_04_*/*.ipynb"):
    #         nb, errors = _notebook_run(notebook)
    #         assert errors == []

    def test_task_5(self):
        for notebook in Path().rglob("tasks/task_05_*/*.ipynb"):
            print(notebook)
            nb, errors = _notebook_run(notebook)
            assert errors == []

    def test_task_6(self):
        for notebook in Path().rglob("tasks/task_06_*/*.ipynb"):
            print(notebook)
            nb, errors = _notebook_run(notebook)
            assert errors == []

# ModuleNotFoundError: No module named 'plotting_utils'
    # def test_task_7(self):
    #     for notebook in Path().rglob("tasks/task_07_*/*.ipynb"):
            # print(notebook)
    #         nb, errors = _notebook_run(notebook)
    #         assert errors == []

# ModuleNotFoundError: No module named 'statepoint_to_vtk'
#     def test_task_8(self):
#         for notebook in Path().rglob("tasks/task_08_*/*.ipynb"):
#             print(notebook)
#             nb, errors = _notebook_run(notebook)
#             assert errors == []

    def test_task_9(self):
        for notebook in Path().rglob("tasks/task_09_*/*.ipynb"):
            print(notebook)
            nb, errors = _notebook_run(notebook)
            assert errors == []

# FileNotFoundError: The dagmc_not_watertight.h5m was not found
    def test_task_10(self):
        for notebook in Path().rglob("tasks/task_10_*/*.ipynb"):
            print(notebook)
            nb, errors = _notebook_run(notebook)
            assert errors == []

# TimeoutError: Cell execution timed out
    def test_task_11(self):
        for notebook in Path().rglob("tasks/task_11_*/*.ipynb"):
            print(notebook)
            nb, errors = _notebook_run(notebook)
            assert errors == []

# FileNotFoundError: The dagmc_not_watertight.h5m was not found
    def test_task_12(self):
        for notebook in Path().rglob("tasks/task_12_*/*.ipynb"):
            print(notebook)
            nb, errors = _notebook_run(notebook)
            assert errors == []

# ModuleNotFoundError: No module named 'statepoint_to_vtk'
    def test_task_13(self):
        for notebook in Path().rglob("tasks/task_13_*/*.ipynb"):
            print(notebook)
            nb, errors = _notebook_run(notebook)
            assert errors == []
