from pathlib import Path

import pytest

from .utils import _notebook_run


@pytest.mark.parametrize("filename", Path().rglob("tasks/task_17_*/*.ipynb"))
def test_task(filename):

    print(f"Attempting to run {filename}")
    _, errors = _notebook_run(filename)
    assert errors == []
