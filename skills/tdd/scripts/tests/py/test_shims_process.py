"""The one check that every top-level skills/tdd/scripts/*.sh is the canonical shim over a module under veri/."""
import importlib
import platform
import re
import shutil
import subprocess
import sys

import pytest

from conftest import INTERPRETER_VENV, SCRIPTS
from shim_audit import VENV_PREFIX


def shim(path, *lines):
    path.write_text("#!/bin/sh\n# %s — a shim.\n%s\n" % (path.name, "\n".join(lines)))


@pytest.mark.process("leaf-role.sh run through a symlink to the skills directory")
def test_a_shim_run_through_a_symlink_to_the_skills_directory_from_another_cwd_gives_its_modules_exit_code_and_stdout(
        run_cli, tmp_path):
    (tmp_path / "skills").symlink_to(SCRIPTS.parents[1], target_is_directory=True)
    (tmp_path / "elsewhere").mkdir()

    ran = subprocess.run([str(tmp_path / "skills" / "tdd" / "scripts" / "leaf-role.sh"), "verify-green-2"],
                         cwd=tmp_path / "elsewhere", stdin=subprocess.DEVNULL, capture_output=True, text=True)
    code, out, _ = run_cli(importlib.import_module("veri.leaf_role"), ["verify-green-2"])

    assert (ran.returncode, ran.stdout) == (code, out) == (0, "VERI_ACTOR=verifier VERI_PHASE=green VERI_ATTEMPT=2\n")


def python3_script(path, runs_real):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('#!/bin/sh\nexec "%s" "$@"\n' % sys.executable if runs_real else "#!/bin/sh\nexit 9\n")
    path.chmod(0o755)


def run_leaf_role(tmp_path, path_python_runs, venv_python_runs=None, venv_under_home=False):
    """leaf-role.sh develop-red on a fixed PATH whose first python3 is real or a stub exiting 9, beside a venv
    under VERI_VENV (or, VERI_VENV unset, under a scratch HOME) whose bin/python3 is real, a stub, or absent (None)."""
    python3_script(tmp_path / "path" / "python3", path_python_runs)
    home = tmp_path / "home"
    venv = home / ".veri-tools" / "venv" if venv_under_home else tmp_path / "venv"
    (venv / "bin").mkdir(parents=True)
    if venv_python_runs is not None:
        python3_script(venv / "bin" / "python3", venv_python_runs)
    env = {"PATH": "%s:/usr/bin:/bin:/usr/local/bin" % (tmp_path / "path"), "HOME": str(home)}
    if not venv_under_home:
        env["VERI_VENV"] = str(venv)

    result = subprocess.run([str(SCRIPTS / "leaf-role.sh"), "develop-red"], capture_output=True, text=True, env=env)
    return result.returncode, result.stdout, result.stderr


@pytest.mark.process("leaf-role.sh started with VERI_VENV naming a directory that has no bin/python3")
def test_issue_2106_shim_with_a_venv_lacking_python3_runs_its_module_on_the_python3_on_path(tmp_path):
    assert run_leaf_role(tmp_path, path_python_runs=True) == (
        0, "VERI_ACTOR=developer VERI_PHASE=red VERI_ATTEMPT=1\n", "")


@pytest.mark.process("leaf-role.sh started with a fixed PATH whose first python3 is a stub exiting 9")
def test_issue_2106_shim_runs_its_module_on_the_venv_python3_not_the_stub_python3_first_on_a_fixed_path(tmp_path):
    assert run_leaf_role(tmp_path, path_python_runs=False, venv_python_runs=True) == (
        0, "VERI_ACTOR=developer VERI_PHASE=red VERI_ATTEMPT=1\n", "")


@pytest.mark.process("leaf-role.sh started with VERI_VENV unset, a scratch HOME holding the venv and a stub python3 exiting 9 on PATH")
def test_issue_2106_shim_with_veri_venv_unset_finds_the_venv_python3_under_home_not_on_path(tmp_path):
    assert run_leaf_role(tmp_path, path_python_runs=False, venv_python_runs=True, venv_under_home=True) == (
        0, "VERI_ACTOR=developer VERI_PHASE=red VERI_ATTEMPT=1\n", "")


@pytest.mark.process("the canonical shim preamble run by sh on the process suites' fixed PATH and scratch HOME,"
                     " with conftest's INTERPRETER_VENV as VERI_VENV")
def test_issue_2106_interpreter_venv_gives_a_shim_on_a_fixed_path_and_scratch_home_a_python3_at_the_3_12_floor(tmp_path):
    shim = tmp_path / "probe.sh"
    shim.write_text('#!/bin/sh\n%s\nexec "$py" "$(dirname "$0")/probe.py"\n' % "\n".join(VENV_PREFIX))
    shim.chmod(0o755)
    (tmp_path / "probe.py").write_text("import sys\nprint('%d.%d' % sys.version_info[:2])\n")
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV}

    ran = subprocess.run([str(shim)], capture_output=True, text=True, env=env)

    assert tuple(int(part) for part in ran.stdout.split(".")) >= (3, 12), (ran.stdout, ran.stderr)


@pytest.mark.process("the floor-checking canonical shim started with a venv python3 stub reporting 3.9 and a real python3 on PATH")
def test_issue_2106_shim_runs_its_module_on_the_path_python3_when_the_venv_python3_reports_3_9(tmp_path):
    (tmp_path / "lib").symlink_to(SCRIPTS / "lib", target_is_directory=True)
    shim = tmp_path / "probe.sh"
    shim.write_text('#!/bin/sh\n. "$(dirname "$0")/lib/shim-python.sh"\nexec "$py" "$(dirname "$0")/veri/probe.py" "$@"\n')
    shim.chmod(0o755)
    (tmp_path / "veri").mkdir()
    (tmp_path / "veri" / "probe.py").write_text("print('probe ran')\n")
    python3_script(tmp_path / "path" / "python3", True)
    venv_python = tmp_path / "venv" / "bin" / "python3"
    venv_python.parent.mkdir(parents=True)
    venv_python.write_text('#!/bin/sh\n[ "$1" = --version ] && { echo "Python 3.9.6"; exit 0; }\nexit 9\n')
    venv_python.chmod(0o755)
    env = {"PATH": "%s:/usr/bin:/bin" % (tmp_path / "path"), "HOME": str(tmp_path / "home"), "VERI_VENV": str(tmp_path / "venv")}

    ran = subprocess.run([str(shim)], capture_output=True, text=True, env=env)

    assert (ran.returncode, ran.stdout) == (0, "probe ran\n"), ran.stderr


def python3_reporting_3_9(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('#!/bin/sh\n[ "$1" = --version ] && { echo "Python 3.9.6"; exit 0; }\nexit 9\n')
    path.chmod(0o755)


@pytest.mark.process("leaf-role.sh started with a venv python3 and a PATH python3 that both report 3.9")
def test_issue_2106_shim_with_both_python3s_below_the_floor_exits_2_without_its_module_naming_each_interpreter_its_source_and_version(tmp_path):
    python3_reporting_3_9(tmp_path / "path" / "python3")
    python3_reporting_3_9(tmp_path / "venv" / "bin" / "python3")
    env = {"PATH": "%s:/usr/bin:/bin" % (tmp_path / "path"), "HOME": str(tmp_path / "home"), "VERI_VENV": str(tmp_path / "venv")}

    ran = subprocess.run([str(SCRIPTS / "leaf-role.sh"), "develop-red"], capture_output=True, text=True, env=env)

    named = [line for line in ran.stderr.splitlines() if "3.9.6" in line]
    assert (ran.returncode, ran.stdout, [("venv" in line, "PATH" in line) for line in named]) == (
        2, "", [(True, False), (False, True)]), ran.stderr


def venv_floor():
    return re.search("^VENV_FLOOR=(.*)$", (SCRIPTS / "lib" / "venv-python.sh").read_text(), re.M).group(1)


def path_with_dirname(directory):
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "dirname").symlink_to(shutil.which("dirname"))
    return str(directory)


@pytest.mark.process("leaf-role.sh started with no venv python3 and a PATH holding only dirname")
def test_issue_2106_shim_with_no_venv_python3_and_none_on_path_exits_2_naming_where_it_looked_for_each(tmp_path):
    env = {"PATH": path_with_dirname(tmp_path / "path"), "HOME": str(tmp_path / "home"), "VERI_VENV": str(tmp_path / "venv")}

    ran = subprocess.run([str(SCRIPTS / "leaf-role.sh"), "develop-red"], capture_output=True, text=True, env=env)

    refusal = "%s: veri needs Python %s or newer; " % (SCRIPTS / "leaf-role.sh", venv_floor())
    assert (ran.returncode, ran.stdout, ran.stderr) == (
        2, "", "%sno venv python3 at %s/venv/bin/python3.\n%sno python3 on PATH.\n" % (refusal, tmp_path, refusal))


@pytest.mark.process("leaf-role.sh started with a venv python3 and a PATH python3 that both exit 1 printing nothing")
def test_issue_2106_shim_with_both_python3s_exiting_1_silently_exits_2_naming_each_interpreter_and_an_unknown_version(tmp_path):
    for python3 in (tmp_path / "path" / "python3", tmp_path / "venv" / "bin" / "python3"):
        python3.parent.mkdir(parents=True, exist_ok=True)
        python3.write_text("#!/bin/sh\nexit 1\n")
        python3.chmod(0o755)
    env = {"PATH": path_with_dirname(tmp_path / "path"), "HOME": str(tmp_path / "home"), "VERI_VENV": str(tmp_path / "venv")}

    ran = subprocess.run([str(SCRIPTS / "leaf-role.sh"), "develop-red"], capture_output=True, text=True, env=env)

    refusal = "%s: veri needs Python %s or newer; " % (SCRIPTS / "leaf-role.sh", venv_floor())
    assert (ran.returncode, ran.stdout, ran.stderr) == (
        2, "", "%sthe venv python3 at %s/venv/bin/python3 is version unknown.\n%sthe python3 on PATH is version unknown.\n"
        % (refusal, tmp_path, refusal))


def floor_probe(tmp_path, floor_line):
    """The canonical shim over lib/shim-python.sh beside a copy of lib/venv-python.sh whose VENV_FLOOR line is
    floor_line (None drops the file), a venv without python3 and a real python3 on PATH."""
    (tmp_path / "lib").mkdir()
    shutil.copy(SCRIPTS / "lib" / "shim-python.sh", tmp_path / "lib" / "shim-python.sh")
    if floor_line is not None:
        lib = (SCRIPTS / "lib" / "venv-python.sh").read_text()
        (tmp_path / "lib" / "venv-python.sh").write_text(re.sub("^VENV_FLOOR=.*$", floor_line, lib, count=1, flags=re.M))
    shim = tmp_path / "probe.sh"
    shim.write_text('#!/bin/sh\n. "$(dirname "$0")/lib/shim-python.sh"\nexec "$py" "$(dirname "$0")/veri/probe.py" "$@"\n')
    shim.chmod(0o755)
    (tmp_path / "veri").mkdir()
    (tmp_path / "veri" / "probe.py").write_text("print('probe ran')\n")
    python3_script(tmp_path / "path" / "python3", True)
    env = {"PATH": "%s:/usr/bin:/bin" % (tmp_path / "path"), "HOME": str(tmp_path / "home"), "VERI_VENV": str(tmp_path / "venv")}
    return subprocess.run([str(shim)], capture_output=True, text=True, env=env), shim


@pytest.mark.process("the floor-checking canonical shim beside a venv-python.sh whose VENV_FLOOR is 3.99, a real python3 on PATH")
def test_issue_2106_shim_refuses_by_the_venv_floor_in_lib_venv_python_sh_not_a_floor_of_its_own(tmp_path):
    ran, shim = floor_probe(tmp_path, "VENV_FLOOR=3.99")

    refusal = "%s: veri needs Python 3.99 or newer; " % shim
    assert (ran.returncode, ran.stdout, ran.stderr) == (
        2, "", "%sno venv python3 at %s/venv/bin/python3.\n%sthe python3 on PATH is version %s.\n"
        % (refusal, tmp_path, refusal, platform.python_version()))


@pytest.mark.process("the floor-checking canonical shim with no lib/venv-python.sh beside it, or one whose VENV_FLOOR is no version")
@pytest.mark.parametrize("floor_line", [None, "VENV_FLOOR=3.12 # floor", 'VENV_FLOOR="3.12"'])
def test_issue_2106_shim_without_a_readable_venv_floor_exits_2_naming_lib_venv_python_sh(tmp_path, floor_line):
    ran, shim = floor_probe(tmp_path, floor_line)

    assert (ran.returncode, ran.stdout, ran.stderr.splitlines()[-1:]) == (
        2, "", ["%s: cannot read VENV_FLOOR from %s/lib/venv-python.sh." % (shim, tmp_path)])


@pytest.mark.process("leaf-role.sh started by sh as a bare name from the scripts directory, a real python3 on PATH")
def test_issue_2106_shim_started_by_a_name_without_a_slash_finds_its_lib_in_the_current_directory(tmp_path):
    python3_script(tmp_path / "path" / "python3", True)
    env = {"PATH": "%s:/usr/bin:/bin" % (tmp_path / "path"), "HOME": str(tmp_path / "home"), "VERI_VENV": str(tmp_path / "venv")}

    ran = subprocess.run(["sh", "leaf-role.sh", "develop-red"], capture_output=True, text=True, env=env, cwd=SCRIPTS)

    assert (ran.returncode, ran.stdout, ran.stderr) == (0, "VERI_ACTOR=developer VERI_PHASE=red VERI_ATTEMPT=1\n", "")
