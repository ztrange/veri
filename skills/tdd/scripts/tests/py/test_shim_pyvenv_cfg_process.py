"""Cases for lib/shim-python.sh reading the venv's version from its pyvenv.cfg instead of running its python3 to ask."""
import subprocess
import sys

import pytest

from conftest import SCRIPTS


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
EXITS_9 = "#!/bin/sh\nexit 9\n"
CFG = "home = /opt/homebrew/bin\ninclude-system-site-packages = false\nversion = %s\n"


@pytest.mark.process("the canonical shim over lib/shim-python.sh with a venv python3 stub that says 3.9.6 when asked and a pyvenv.cfg saying 3.14.7")
def test_4130_a_venv_whose_pyvenv_cfg_meets_the_floor_runs_the_module_on_its_python3_without_asking_its_version(tmp_path):
    ran, _ = probe(tmp_path, CFG % "3.14.7", SAYS_3_9_6_ELSE_RUNS, EXITS_9)

    assert (ran.returncode, ran.stdout) == (7, "probe ran\n"), ran.stderr
