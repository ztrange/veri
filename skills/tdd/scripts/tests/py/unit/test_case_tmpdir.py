"""The per-case temporary directory the autouse hermetic_environment fixture sets up."""
import _io
import builtins
import io
import os
import pathlib
import posix
import sys
import tempfile

import pytest

import conftest
from conftest import SCRIPTS

pytest_plugins = ["pytester"]


def test_2246_case_runs_with_tmpdir_and_tempdir_set_to_one_directory_beside_tmp_path(tmp_path):
    case_dir = pathlib.Path(os.environ["TMPDIR"])

    assert tempfile.tempdir == str(case_dir)
    assert case_dir.parent == tmp_path.parent
    assert case_dir != tmp_path
    assert not case_dir.is_relative_to(tmp_path)
    assert pathlib.Path(tempfile.gettempdir()) == case_dir
    fd = os.open(case_dir / "probe", os.O_CREAT | os.O_WRONLY)
    os.close(fd)


PLANTED = '''
import os
import pathlib
import subprocess

import pytest


@pytest.mark.process("run-conductor.sh started for real, its stub claude SIGKILLing the launcher, git faked failing")
def test_a_conductor_killed_before_its_cleanup(tmp_path):
    claude = tmp_path / "claude"
    claude.write_text("#!/bin/sh\\nkill -9 $PPID\\n")
    claude.chmod(0o755)
    fake = tmp_path / "bin"
    fake.mkdir()
    (fake / "git").write_text("#!/bin/sh\\nexit 128\\n")
    (fake / "git").chmod(0o755)
    work = tmp_path / "work"
    (work / ".git").mkdir(parents=True)
    floor = tmp_path / "floor"
    floor.mkdir()
    (floor / "python3").symlink_to(%(python)r)
    env = dict(os.environ, CLAUDE_BIN=str(claude), PATH="%%s:%%s:%%s" %% (fake, floor, os.environ["PATH"]))
    ran = subprocess.run([%(conductor)r, "4242"], cwd=work, env=env,
                         stdin=subprocess.DEVNULL, capture_output=True, text=True)

    assert ran.returncode == -9, ran.stderr
    assert list(pathlib.Path(os.environ["TMPDIR"]).glob("veri-run-4242-*")), ran.stderr
'''


@pytest.mark.process("run-conductor.sh started for real from a planted case under conftest, its stub claude SIGKILLing the launcher so its veri-run-4242-* directory is never removed")
def test_2246_a_conductor_killed_before_its_cleanup_leaves_its_veri_run_directory_in_the_case_tmpdir_and_the_inherited_tmpdir_unchanged(
        pytester, monkeypatch, tmp_path):
    inherited = tmp_path / "inherited"
    inherited.mkdir()
    monkeypatch.setenv("TMPDIR", str(inherited))
    monkeypatch.setattr(tempfile, "tempdir", str(inherited))
    monkeypatch.setattr(builtins, "open", _io.open)
    monkeypatch.setattr(io, "open", _io.open)
    monkeypatch.setattr(os, "open", posix.open)
    monkeypatch.setattr(os, "mkdir", posix.mkdir)
    pytester.makepyfile(test_planted=PLANTED % {"conductor": str(SCRIPTS / "run-conductor.sh"), "python": sys.executable})

    result = pytester.runpytest_inprocess("-p", "no:cacheprovider", plugins=[conftest])

    result.assert_outcomes(passed=1)
    assert sorted(os.listdir(inherited)) == []
