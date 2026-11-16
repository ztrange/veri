"""Cases for lib/shim-python.sh reading the venv's version from its pyvenv.cfg instead of running its python3 to ask."""
import re
import subprocess
import sys

import pytest

from conftest import SCRIPTS


def venv_floor():
    return re.search("^VENV_FLOOR=(.*)$", (SCRIPTS / "lib" / "venv-python.sh").read_text(), re.M).group(1)


def probe(tmp_path, cfg, venv_python, path_python):
    """The canonical shim over lib/shim-python.sh, a module printing `probe ran` and exiting 7, a venv whose pyvenv.cfg
    holds <cfg> (None: no pyvenv.cfg) and whose bin/python3 is <venv_python>, and <path_python> as the python3 on PATH."""
    (tmp_path / "lib").symlink_to(SCRIPTS / "lib", target_is_directory=True)
    shim = tmp_path / "probe.sh"
    shim.write_text('#!/bin/sh\n. "$(dirname "$0")/lib/shim-python.sh"\nexec "$py" "$(dirname "$0")/veri/probe.py" "$@"\n')
    shim.chmod(0o755)
    (tmp_path / "veri").mkdir()
    (tmp_path / "veri" / "probe.py").write_text("import sys\nprint('probe ran')\nsys.exit(7)\n")
    venv = tmp_path / "venv"
    for path, body in ((venv / "bin" / "python3", venv_python), (tmp_path / "path" / "python3", path_python)):
        path.parent.mkdir(parents=True)
        path.write_text(body)
        path.chmod(0o755)
    if cfg is not None:
        (venv / "pyvenv.cfg").write_text(cfg)
    env = {"PATH": "%s:/usr/bin:/bin" % (tmp_path / "path"), "HOME": str(tmp_path / "home"), "VERI_VENV": str(venv)}
    ran = subprocess.run([str(shim)], capture_output=True, text=True, env=env)
    return ran, shim


SAYS_3_9_6 = 'case "$1" in -c) echo 3.9.6; exit 0 ;; --version) echo "Python 3.9.6"; exit 0 ;; esac\n'
SAYS_3_9_6_ELSE_RUNS = '#!/bin/sh\n%sexec "%s" "$@"\n' % (SAYS_3_9_6, sys.executable)
SAYS_3_9_6_ELSE_EXITS_9 = "#!/bin/sh\n%sexit 9\n" % SAYS_3_9_6
EXITS_9 = "#!/bin/sh\nexit 9\n"
RUNS = '#!/bin/sh\nexec "%s" "$@"\n' % sys.executable
CFG = "home = /opt/homebrew/bin\ninclude-system-site-packages = false\nversion = %s\n"


@pytest.mark.process("the canonical shim over lib/shim-python.sh with a venv python3 stub that says 3.9.6 when asked and a pyvenv.cfg saying 3.14.7")
def test_4130_a_venv_whose_pyvenv_cfg_meets_the_floor_runs_the_module_on_its_python3_without_asking_its_version(tmp_path):
    ran, _ = probe(tmp_path, CFG % "3.14.7", SAYS_3_9_6_ELSE_RUNS, EXITS_9)

    assert (ran.returncode, ran.stdout) == (7, "probe ran\n"), ran.stderr


@pytest.mark.process("the canonical shim over lib/shim-python.sh with a venv python3 stub that says 3.9.6, no or an unparseable pyvenv.cfg")
@pytest.mark.parametrize("cfg", [None, "home = /usr/bin\n", "version = three\n", "version_info = 3.14.7.final.0\n"])
def test_4130_a_venv_with_no_parseable_pyvenv_cfg_version_is_checked_by_running_its_python3(tmp_path, cfg):
    ran, _ = probe(tmp_path, cfg, SAYS_3_9_6_ELSE_EXITS_9, RUNS)

    assert (ran.returncode, ran.stdout, ran.stderr) == (7, "probe ran\n", "")


@pytest.mark.process("the canonical shim over lib/shim-python.sh with a real venv python3 under a pyvenv.cfg saying 3.9.6 and a python3 on PATH that exits 1")
def test_4130_a_venv_whose_pyvenv_cfg_is_below_the_floor_is_passed_over_and_the_refusal_names_that_version(tmp_path):
    ran, shim = probe(tmp_path, CFG % "3.9.6", RUNS, "#!/bin/sh\nexit 1\n")

    refusal = "%s: veri needs Python %s or newer; " % (shim, venv_floor())
    assert (ran.returncode, ran.stdout, ran.stderr) == (
        2, "", "%sthe venv python3 at %s/venv/bin/python3 is version 3.9.6.\n%sthe python3 on PATH is version unknown.\n"
        % (refusal, tmp_path, refusal))
