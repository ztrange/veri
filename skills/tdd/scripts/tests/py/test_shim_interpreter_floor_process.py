"""Medium case for the interpreter a process case's shim runs on, whatever python3 is on PATH."""
import os
import subprocess

import pytest

from conftest import SCRIPTS


@pytest.mark.process("parse-verdict.sh started for real with a python3 reporting 3.9.6 first on PATH and no other python3")
def test_2550_a_shim_run_by_a_case_runs_on_a_python_at_the_floor_when_the_only_python3_on_path_reports_3_9_6(tmp_path):
    fake, tools, home = (tmp_path / name for name in ("fake", "tools", "home"))
    for path in (fake, tools, home):
        path.mkdir()
    python = fake / "python3"
    python.write_text('#!/bin/sh\ncase "$1" in -c) echo 3.9.6 ;; *) echo "Python 3.9.6" ;; esac\n')
    python.chmod(0o755)
    for name in ("dirname", "id"):
        (tools / name).symlink_to(next(p for p in ("/usr/bin/" + name, "/bin/" + name) if os.path.exists(p)))
    env = dict(os.environ, PATH=os.pathsep.join((str(fake), str(tools))), HOME=str(home))

    ran = subprocess.run([str(SCRIPTS / "parse-verdict.sh")], input="VERDICT: PASS\nREASON: fine\n", env=env,
                         capture_output=True, text=True)

    assert (ran.returncode, "veri needs Python 3.12 or newer" in ran.stderr) == (0, False), ran.stderr
