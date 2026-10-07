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
    if not major:
        env = {k: v for k, v in os.environ.items() if k not in ("BASH_ENV", "ENV")}
        major, version = subprocess.check_output([path, "-c", PROBE], env=env, text=True).split("\n")[:2]
    if re.fullmatch("[0-9]+", major) and int(major) >= 5:
        return 0
    sys.stderr.write(
        "%s: veri needs bash 5 or newer; this is bash %s (%s). Install it with `brew install bash` "
        "(it lands ahead of /bin/bash on PATH), or your package manager on Linux.\n" % (prefix, version, path))
    return 2
