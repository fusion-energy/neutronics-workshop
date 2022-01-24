
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

# No module named 'openmc_model'
    def test_task_13(self):
        for notebook in Path().rglob("tasks/task_13_*/*.ipynb"):
            print(notebook)
            nb, errors = _notebook_run(notebook)
            assert errors == []
