
import sys

import jupytext
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert.preprocessors.execute import CellExecutionError


def _run_task(path):
    """
    Read a percent format task script with jupytext and execute it as a notebook.
    :returns (parsed nb object, execution errors)
    """
    kernel_name = 'python%d' % sys.version_info[0]
    errors = []

    nb = jupytext.read(path)
    # The Windows and Mac OS OpenMC wheels are built without OpenMP so their
    # simulations are single threaded, and several of the tasks take longer
    # than the previous 300s on those platforms.
    ep = ExecutePreprocessor(kernel_name=kernel_name, timeout=1000) #, allow_errors=True

    try:
        ep.preprocess(nb, {'metadata': {'path': path.parent}})
        print(f'running task from this path {path.parent}')

    except CellExecutionError as e:
        if "SKIP" in e.traceback:
            print(str(e.traceback).split("\n")[-2])
        else:
            raise e

    return nb, errors
