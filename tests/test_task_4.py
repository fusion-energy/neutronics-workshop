from pathlib import Path

import pytest

from .utils import _run_task


@pytest.mark.parametrize("filename", list(Path().rglob("tasks/task_04_*/[0-9]*.py")))
def test_task(filename):

    print(f"Attempting to run {filename}")
    _, errors = _run_task(filename)
    assert errors == []
