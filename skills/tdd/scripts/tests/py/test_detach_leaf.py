"""In-process cases for veri/detach_leaf.py, the module detach-leaf.sh is a shim over."""
import importlib
import pathlib
import subprocess
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

USAGE = "usage: detach-leaf.sh <cmd> [args…]\n"


@pytest.fixture
def detach_leaf():
    return importlib.import_module("veri.detach_leaf")


def test_main_refuses_no_argument_with_the_usage_line_and_launches_its_argv_once_returning_0_silently(
        monkeypatch, capsys, detach_leaf):
    launches = []

    class FakePopen:
        pid = 4242

        def __init__(self, args, **kwargs):
            launches.append(args)

    monkeypatch.setattr(subprocess, "Popen", FakePopen)

    code = detach_leaf.main([])
    assert (code, capsys.readouterr(), launches) == (2, ("", USAGE), [])

    code = detach_leaf.main(["true"])
    assert (code, capsys.readouterr(), launches) == (0, ("", ""), [["true"]])
