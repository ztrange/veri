"""The bash and Python floors a launch refuses on, each taking its message prefix."""
# hazard: runs on the python3 it may refuse, so nothing here may need more than Python 3.9.
import os
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
