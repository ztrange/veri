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
    refused = entry.no_arguments(argv, USAGE)
    if refused is not None:
        return refused
    if os.environ.get("CLAUDE_CODE_REMOTE") != "true":
        return 0
    venv = tunables.venv_dir()
    code = _build(venv)
    if code:
        return code
    env_file = os.environ.get("CLAUDE_ENV_FILE")
    line = 'export PATH="' + venv + '/bin:$PATH"\n'
    if env_file and line not in _read(env_file).splitlines(True):
        with open(env_file, "a") as out:
            out.write(line)
    return 0


def _build(venv):
    """Install veri's environment at venv unless its stamp names the current lock, with the first candidate at or above
    the floor, else one uv installs; 0, or 2 with neither."""
    stamp = os.path.join(venv, ".veri-lock-sha256")
    lock = _lock_sha256()
    if _read(stamp) == lock:
        return 0
    floor = launch_floor.python_floor()
    tried = [(name, _version(name)) for name in _candidates(floor)]
    python = next((name for name, version in tried if _meets(version, floor)), None)
    if python is None and _uv("python", "install", floor) is not None:
        python = _uv("python", "find", floor).strip()
    if python is None:
        return entry.refuse(*[(name + " is version " + version + ".") if version else ("no " + name + " on PATH.")
                              for name, version in tried],
                            prefix="cloud-setup: veri needs Python " + floor + " or newer; ")
    _install(python, venv)
    os.makedirs(venv, exist_ok=True)
    with open(stamp, "w") as out:
        out.write(lock)
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


def _uv(*args):
    """uv's stdout for args, or None when uv is not on PATH; a uv that fails raises."""
    path = shutil.which("uv")
    if not path:
        return None
    return subprocess.run([path] + list(args), stdout=subprocess.PIPE, universal_newlines=True, check=True).stdout


def _install(python, venv):
    """Create the environment at venv with python when it has no bin/python3,
    then run veri's make install-dev into it."""
    if not os.path.exists(os.path.join(venv, "bin", "python3")):
        subprocess.run([python, "-m", "venv", venv], check=True)
    subprocess.run(["make", "-C", ROOT, "install-dev"], env=tunables.with_values(VERI_VENV=venv), check=True)


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
