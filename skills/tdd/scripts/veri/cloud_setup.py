"""cloud-setup.sh's computations, run in-process."""
# hazard: runs on a python3 below VENV_FLOOR, so nothing here may need more than Python 3.9.
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import hashlib
import os
import shutil
import subprocess
import sys

import entry
import launch_floor
import paths
import tunables

ROOT = os.path.realpath(os.path.join(paths.resolved_scripts_of(__file__), "..", "..", ".."))

USAGE = "usage: cloud-setup.sh"


def main(argv):
    if os.environ.get("CLAUDE_CODE_REMOTE") != "true":
        return 0
    venv = tunables.venv_dir()
    stamp = os.path.join(venv, ".veri-lock-sha256")
    lock = _lock_sha256()
    if _read(stamp) != lock:
        floor = launch_floor.python_floor()
        python = next(name for name in _candidates(floor) if _meets(_version(name), floor))
        _install(python, venv)
        os.makedirs(venv, exist_ok=True)
        with open(stamp, "w") as out:
            out.write(lock)
    env_file = os.environ.get("CLAUDE_ENV_FILE")
    line = 'export PATH="' + venv + '/bin:$PATH"\n'
    if env_file and line not in _read(env_file).splitlines(True):
        with open(env_file, "a") as out:
            out.write(line)
    return 0


def _lock_sha256():
    with open(os.path.join(ROOT, "requirements-dev.txt"), "rb") as lock:
        return hashlib.sha256(lock.read()).hexdigest()


def _read(path):
    """The text of the file at path, or "" when there is none."""
    try:
        with open(path) as text:
            return text.read()
    except FileNotFoundError:
        return ""


def _candidates(floor):
    """python3, then python3.13 down to the floor's minor: venv_builder's order in lib/venv-python.sh."""
    return ["python3"] + ["python3.%d" % minor for minor in range(13, int(floor.split(".")[1]) - 1, -1)]


def _meets(version, floor):
    if not version:
        return False
    return [int(part) for part in version.split(".")[:2]] >= [int(part) for part in floor.split(".")[:2]]


def _version(name):
    """The Python version the interpreter `name` on PATH reports, or None when it is not on PATH or gives none."""
    path = shutil.which(name)
    if not path:
        return None
    probe = subprocess.run([path, "-c", "import platform; print(platform.python_version())"],
                           stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, universal_newlines=True)
    return probe.stdout.strip() if probe.returncode == 0 else None


def _install(python, venv):
    """Create the environment at venv with python when it has no bin/python3, then run veri's make install-dev into it."""
    if not os.path.exists(os.path.join(venv, "bin", "python3")):
        subprocess.run([python, "-m", "venv", venv], check=True)
    subprocess.run(["make", "-C", ROOT, "install-dev"], env=dict(os.environ, VERI_VENV=venv), check=True)


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
