import os
import pathlib
import subprocess
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


def pytest_configure(config):
    config.option.importmode = "append"


@pytest.fixture
def fake_processes(monkeypatch):
    def install():
        calls = []

        def record(args, *_, **__):
            calls.append(" ".join([os.path.basename(str(args[0]))] + [str(a) for a in args[1:]]))
            return subprocess.CompletedProcess(args, 0, "", "")

        for name in ("run", "Popen", "call", "check_call", "check_output"):
            monkeypatch.setattr(subprocess, name, record)
        return calls

    return install
