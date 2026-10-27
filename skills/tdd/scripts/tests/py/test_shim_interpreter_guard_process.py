"""Medium case for the guard that fails a process case launching a shim whose interpreter is left to PATH's python3."""
import os
import subprocess

import pytest

from conftest import INTERPRETER_VENV, SCRIPTS


@pytest.mark.process("parse-verdict.sh started for real, once without a usable venv and once with one")
def test_2550_the_guard_fails_a_case_launching_a_shim_with_no_venv_and_only_a_3_9_6_python3_on_path(tmp_path):
    fake, tools, home = (tmp_path / name for name in ("fake", "tools", "home"))
    for path in (fake, tools, home):
        path.mkdir()
    python = fake / "python3"
    python.write_text('#!/bin/sh\ncase "$1" in -c) echo 3.9.6 ;; *) echo "Python 3.9.6" ;; esac\n')
    python.chmod(0o755)
    for name in ("dirname", "id"):
        (tools / name).symlink_to(next(p for p in ("/usr/bin/" + name, "/bin/" + name) if os.path.exists(p)))
    bare = {k: v for k, v in os.environ.items() if k != "VERI_VENV"}
    bare.update(PATH=os.pathsep.join((str(fake), str(tools))), HOME=str(home))
    shim = str(SCRIPTS / "parse-verdict.sh")

    with pytest.raises(AssertionError, match="parse-verdict.sh"):
        subprocess.run([shim], input="VERDICT: PASS\nREASON: fine\n", env=bare, capture_output=True, text=True)

    ran = subprocess.run([shim], input="VERDICT: PASS\nREASON: fine\n", env=dict(bare, VERI_VENV=INTERPRETER_VENV),
                         capture_output=True, text=True)
    assert ran.returncode == 0, ran.stderr
