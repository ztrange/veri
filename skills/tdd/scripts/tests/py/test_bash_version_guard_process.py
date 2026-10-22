"""Medium cases for the refusal veri gives on a bash older than 5 or a Python below 3.12, at make test, run-conductor.sh and leaf-launchable.sh."""
import os
import subprocess
import sys

import pytest

from conftest import ROOT, SCRIPTS

REQUIREMENT = "needs bash 5 or newer"
FLOOR = next(line.split("=", 1)[1] for line in (SCRIPTS / "lib" / "venv-python.sh").read_text().splitlines()
             if line.startswith("VENV_FLOOR="))
TODAYS_REFUSAL = "%s: veri needs Python 3.12 or newer; the python3 on PATH is version 3.11.9."


def run(argv, cwd, **env):
    base = {k: v for k, v in os.environ.items() if not k.startswith("VERI_")}
    base.update(env)
    ran = subprocess.run(argv, cwd=cwd, env=base, stdin=subprocess.DEVNULL, capture_output=True, text=True)
    return ran.returncode, ran.stdout + ran.stderr, ran.stderr


def claude_stub(tmp_path):
    stub = tmp_path / "claude"
    stub.write_text('#!/bin/sh\n: > "$LAUNCHED"\necho "2.1.0 (Claude Code)"\n')
    stub.chmod(0o755)
    return stub


def fake_venv(tmp_path, name, body):
    venv = tmp_path / name
    (venv / "bin").mkdir(parents=True)
    python = venv / "bin" / "python3"
    python.write_text('#!/bin/sh\ncase "$1" in *.py) : > "$(dirname "$0")/../used"; exec "%s" "$@" ;; esac\n' % sys.executable + body)
    python.chmod(0o755)
    return venv


VENV_OK = 'case "$*" in *platform*) echo 3.13.1 ;; esac\nexit 0\n'
VENV_OLD = 'case "$*" in *version_info*) exit 1 ;; *platform*) echo 3.11.2 ;; esac\nexit 0\n'


def conductor(tmp_path, **env):
    work = tmp_path / "work"
    work.mkdir(exist_ok=True)
    code, out, err = run([str(SCRIPTS / "run-conductor.sh"), "4242"], work, CLAUDE_BIN=str(claude_stub(tmp_path)),
                         LAUNCHED=str(work / "launched"), **env)
    return code, err, (work / "launched").exists()


def launchable(tmp_path, **env):
    code, out, err = run([str(SCRIPTS / "leaf-launchable.sh")], tmp_path, CLAUDE_BIN=str(claude_stub(tmp_path)),
                         LAUNCHED=str(tmp_path / "ll-launched"), **env)
    return code, err


@pytest.mark.process("make started for real, once with a stand-in bash 3 and once with bash 5, over the green fixture suite")
def test_make_test_refuses_before_any_suite_runs_when_the_bash_on_path_is_older_than_5_and_runs_them_when_it_is_not(tmp_path):
    green = tmp_path / "test_ends_green.py"
    green.write_text("def test_green():\n    pass\n")
    argv = ["make", "-C", str(ROOT), "test", "TESTS=" + str(green), "UNIT_TESTS="]
    old_code, old_out, _ = run(argv, ROOT, VERI_BASH_MAJOR="3")
    new_code, new_out, _ = run(argv, ROOT, VERI_BASH_MAJOR="5")
    assert old_code != 0, old_out
    assert REQUIREMENT in old_out
    assert "== pytest" not in old_out
    assert new_code == 0 and "all suites green" in new_out, new_out


@pytest.mark.process("run-conductor.sh started for real with a stand-in bash 3 and a stub claude")
def test_run_conductor_sh_refuses_with_exit_2_before_launching_anything_when_bash_is_older_than_5(tmp_path):
    code, err, launched = conductor(tmp_path, VERI_BASH_MAJOR="3")
    assert code == 2, err
    assert REQUIREMENT in err
    assert not launched


@pytest.mark.process("run-conductor.sh started for real with a stand-in python 3.11.9 and a stub claude")
def test_run_conductor_sh_refuses_with_exit_2_before_launching_anything_naming_the_python_3_12_floor_and_the_version_found_when_python3_is_older_than_3_12(tmp_path):
    code, err, launched = conductor(tmp_path, VERI_BASH_MAJOR="5", VERI_PYTHON_VERSION="3.11.9")
    assert code == 2, err
    assert "Python 3.12" in err and "3.11.9" in err
    assert not launched


@pytest.mark.process("run-conductor.sh started for real over a fake venv meeting the floor")
def test_run_conductor_sh_s_python_floor_refusal_names_veri_venv_bin_to_put_first_on_path_when_the_venv_there_meets_the_floor(tmp_path):
    venv = fake_venv(tmp_path, "venv-ok", VENV_OK)
    code, err, launched = conductor(tmp_path, VERI_BASH_MAJOR="5", VERI_PYTHON_VERSION="3.11.9", VERI_VENV=str(venv))
    assert code == 2, err
    assert str(venv / "bin") in err and "PATH" in err


@pytest.mark.process("run-conductor.sh started for real with no venv at VERI_VENV")
def test_run_conductor_sh_s_python_floor_refusal_with_no_venv_at_veri_venv_exits_2_with_today_s_message_and_names_no_venv_path(tmp_path):
    code, err, launched = conductor(tmp_path, VERI_BASH_MAJOR="5", VERI_PYTHON_VERSION="3.11.9",
                                    VERI_VENV=str(tmp_path / "no-venv"))
    assert code == 2, err
    assert err.strip() == TODAYS_REFUSAL % "run-conductor"
    assert str(tmp_path / "no-venv") not in err


@pytest.mark.process("leaf-launchable.sh started for real, with a stand-in bash 3 and with bash 5, over a stub claude")
def test_leaf_launchable_sh_refuses_with_exit_2_when_bash_is_older_than_5_and_still_answers_0_for_a_launchable_binary_on_bash_5(tmp_path):
    code, err = launchable(tmp_path, VERI_BASH_MAJOR="3")
    assert code == 2, err
    assert REQUIREMENT in err
    assert launchable(tmp_path, VERI_BASH_MAJOR="5")[0] == 0


@pytest.mark.process("leaf-launchable.sh started for real over a fake venv meeting the floor")
def test_leaf_launchable_sh_s_python_floor_refusal_names_veri_venv_bin_to_put_first_on_path_when_the_venv_there_meets_the_floor(tmp_path):
    venv = fake_venv(tmp_path, "venv-ok", VENV_OK)
    code, err = launchable(tmp_path, VERI_BASH_MAJOR="5", VERI_PYTHON_VERSION="3.11.9", VERI_VENV=str(venv))
    assert code == 2, err
    assert str(venv / "bin") in err and "PATH" in err


@pytest.mark.process("run-conductor.sh and leaf-launchable.sh started for real over a fake venv below the floor")
def test_run_conductor_sh_s_and_leaf_launchable_sh_s_python_floor_refusals_with_a_venv_at_veri_venv_below_the_floor_too_exit_2_with_today_s_message_and_name_no_venv_path(tmp_path):
    venv = fake_venv(tmp_path, "venv-old", VENV_OLD)
    env = dict(VERI_BASH_MAJOR="5", VERI_PYTHON_VERSION="3.11.9", VERI_VENV=str(venv))
    rc_code, rc_err, _ = conductor(tmp_path, **env)
    ll_code, ll_err = launchable(tmp_path, **env)
    assert (rc_code, rc_err.strip()) == (2, TODAYS_REFUSAL % "run-conductor")
    assert (ll_code, ll_err.strip()) == (2, TODAYS_REFUSAL % "leaf-launchable")
    assert str(venv) not in rc_err + ll_err


def bash_major(path):
    ran = subprocess.run([path, "-c", 'echo "${BASH_VERSINFO[0]}"'], capture_output=True, text=True)
    return int(ran.stdout.strip() or 99)


@pytest.mark.skipif(not os.access("/bin/bash", os.X_OK) or bash_major("/bin/bash") >= 5, reason="no bash older than 5 at /bin/bash")
@pytest.mark.process("leaf-launchable.sh started for real with /bin/bash first on PATH")
def test_on_a_real_bash_older_than_5_bin_bash_leaf_launchable_sh_refuses_with_exit_2(tmp_path):
    old = tmp_path / "old-bash"
    old.mkdir()
    (old / "bash").symlink_to("/bin/bash")
    env = {k: v for k, v in os.environ.items() if k != "VERI_BASH_MAJOR"}
    code, err = launchable(tmp_path, PATH=str(old) + os.pathsep + env["PATH"])
    assert code == 2 and REQUIREMENT in err, err


def python_below_floor(path):
    if not os.access(path, os.X_OK):
        return False
    major, minor = (int(n) for n in FLOOR.split("."))
    ran = subprocess.run([path, "-c", "import sys; sys.exit(sys.version_info < (%d, %d))" % (major, minor)],
                         capture_output=True)
    return ran.returncode != 0


@pytest.mark.skipif(not python_below_floor("/usr/bin/python3"), reason="no python3 below the floor at /usr/bin/python3")
@pytest.mark.process("leaf-launchable.sh started for real with /usr/bin/python3 first on PATH")
def test_on_a_real_python3_below_the_floor_first_on_path_usr_bin_python3_leaf_launchable_sh_refuses_with_exit_2_naming_the_floor_and_its_version(tmp_path):
    old = tmp_path / "old-python"
    old.mkdir()
    (old / "python3").symlink_to("/usr/bin/python3")
    version = subprocess.run(["/usr/bin/python3", "-c", "import platform; print(platform.python_version())"],
                             capture_output=True, text=True).stdout.strip()
    code, err = launchable(tmp_path, VERI_BASH_MAJOR="5", VERI_VENV=str(tmp_path / "no-venv"),
                           PATH=str(old) + os.pathsep + os.environ["PATH"])
    want = "veri needs Python %s or newer; the python3 on PATH is version %s." % (FLOOR, version)
    assert code == 2 and want in err, err


@pytest.mark.process("leaf-launchable.sh started for real over a fake venv meeting the floor that runs modules on the real interpreter")
def test_2106_leaf_launchable_sh_runs_its_module_on_the_venv_at_veri_venv_and_answers_0_for_a_launchable_binary(tmp_path):
    venv = fake_venv(tmp_path, "venv-ok", VENV_OK)
    code, err = launchable(tmp_path, VERI_BASH_MAJOR="5", VERI_VENV=str(venv))
    assert code == 0, err
    assert (venv / "used").exists()
