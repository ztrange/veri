"""The bash and Python floors a launch refuses on, each taking its message prefix."""
# hazard: runs on the python3 it may refuse, so nothing here may need more than Python 3.9.
import os
import platform
import re
import shutil
import subprocess
import sys

PROBE = 'printf "%s\\n%s\\n" "${BASH_VERSINFO[0]}" "$BASH_VERSION"'


def bash_refusal(prefix):
    path = shutil.which("bash")
    major = version = os.environ.get("VERI_BASH_MAJOR", "")
    if not major and path:
        env = {k: v for k, v in os.environ.items() if k not in ("BASH_ENV", "ENV")}
        probe = subprocess.run([path, "-c", PROBE], env=env, stdout=subprocess.PIPE, text=True)
        major, version = (probe.stdout.split("\n") + ["", ""])[:2]
        if probe.returncode:
            major = ""
    if re.fullmatch("[0-9]+", major) and int(major) >= 5:
        return 0
    sys.stderr.write(
        "%s: veri needs bash 5 or newer; this is bash %s (%s). Install it with `brew install bash` "
        "(it lands ahead of /bin/bash on PATH), or your package manager on Linux.\n" % (prefix, version, path or ""))
    return 2


def python_refusal(prefix):
    lib = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib", "venv-python.sh")
    with open(lib) as f:
        floor = re.search("^VENV_FLOOR=(.*)$", f.read(), re.M).group(1)
    version = os.environ.get("VERI_PYTHON_VERSION", "") or platform.python_version()
    major, dot, rest = version.partition(".")
    minor = rest.partition(".")[0] if dot else major
    numbers = [_bash_number(major), _bash_number(minor)]
    if None not in numbers and numbers < [int(part) for part in floor.split(".")[:2]]:
        sys.stderr.write("%s: veri needs Python %s or newer; the python3 on PATH is version %s.\n"
                         % (prefix, floor, version))
        venv = venv_dir()
        if _meets_floor(os.path.join(venv, "bin", "python3"), floor):
            sys.stderr.write("%s: the environment at %s meets it; put %s/bin first on PATH.\n" % (prefix, venv, venv))
        return 2
    return 0


def venv_dir():
    return os.environ.get("VERI_VENV", "") or os.path.join(os.environ.get("HOME", ""), ".veri-tools", "venv")


def _meets_floor(python, floor):
    check = "import sys; sys.exit(sys.version_info < (%s))" % floor.replace(".", ", ")
    try:
        return subprocess.call([python, "-c", check], stderr=subprocess.DEVNULL) == 0
    except OSError:
        return False


def _bash_number(text):
    if not re.fullmatch("[0-9]+", text):
        return None
    try:
        return int(text, 8) if len(text) > 1 and text.startswith("0") else int(text)
    except ValueError:
        return None
