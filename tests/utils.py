
import sys

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert.preprocessors.execute import CellExecutionError


def _notebook_run(path):
    """
    Execute a notebook via nbconvert and collect output.
    :returns (parsed nb object, execution errors)
    """
    kernel_name = 'python%d' % sys.version_info[0]
    errors = []

    with open(path) as f:
        nb = nbformat.read(f, as_version=4)
        nb.metadata.get('kernelspec', {})['name'] = kernel_name
        # 1000s to match the timeout used for the book build in _config.yml.
        # The Windows and Mac OS OpenMC wheels are built without OpenMP so
        # their simulations are single threaded, and several of the notebooks
        # take longer than the previous 300s on those platforms.
        ep = ExecutePreprocessor(kernel_name=kernel_name, timeout=1000) #, allow_errors=True

        try:
            ep.preprocess(nb, {'metadata': {'path': path.parent}})
            print(f'running notebook from this path {path.parent}')

        except CellExecutionError as e: 
            if "SKIP" in e.traceback:
                print(str(e.traceback).split("\n")[-2])
            else:
                raise e

    return nb, errors
