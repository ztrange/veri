import os
import pathlib
import shutil
import subprocess

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]

PROBES = r'''
source "$LIB"
probe() { printf '%s|%s|%s\n' "$1" "$(venv_dir)" "$(venv_python)"; }
VERI_VENV="$VENV" probe executable
VERI_VENV="$ABSENT" probe absent
/bin/chmod -x "$VENV/bin/python3"
VERI_VENV="$VENV" probe not-executable
unset VERI_VENV
probe unset
'''


@pytest.mark.process("bash sources lib/venv-python.sh")
def test_venv_dir_is_veri_venv_or_home_default_and_venv_python_is_its_executable_python3_else_path_python3(tmp_path):
    home, path, venv, absent = (tmp_path / name for name in ("home", "path", "venv", "absent"))
    default = home / ".veri-tools" / "venv"
    for directory in (path, venv / "bin", default / "bin"):
        directory.mkdir(parents=True)
    stubs = (path / "python3", venv / "bin" / "python3", default / "bin" / "python3")
    for stub in stubs:
        stub.write_text("#!/bin/sh\n")
        stub.chmod(0o755)
    env = {"HOME": str(home), "PATH": str(path), "LIB": str(SCRIPTS / "lib" / "venv-python.sh"),
           "VENV": str(venv), "ABSENT": str(absent)}
    done = subprocess.run([shutil.which("bash"), "-c", PROBES], env=env, capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    assert done.stdout.splitlines() == [
        "executable|%s|%s" % (venv, venv / "bin" / "python3"),
        "absent|%s|%s" % (absent, path / "python3"),
        "not-executable|%s|%s" % (venv, path / "python3"),
        "unset|%s|%s" % (default, default / "bin" / "python3"),
    ]
