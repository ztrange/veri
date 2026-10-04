"""profile.sh's per-case timing, run in-process."""
import os
import re
import subprocess
import sys

TRACED = 'PS4=\'+${EPOCHREALTIME} ${LINENO} \'; set -x; . "$0"'


def run_traced(suite):
    subprocess.run(["bash", "-c", TRACED, suite], stdin=subprocess.DEVNULL,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def sort_lines(lines):
    done = subprocess.run(["sort", "-rn"], input="".join(lines), text=True, stdout=subprocess.PIPE)
    sys.stdout.write(done.stdout)
    return done.returncode


def main(argv):
    threshold = os.environ.get("VERI_PROFILE_THRESHOLD") or "1"
    if not re.fullmatch(r"[0-9]+(\.[0-9]+)?", threshold):
        print("profile.sh: VERI_PROFILE_THRESHOLD must be a number of seconds, got '%s'" % threshold,
              file=sys.stderr)
        return 2
    for suite in argv:
        run_traced(suite)
        print("profile.sh: %s: no pass=/fail= increment in its trace" % suite, file=sys.stderr)
        return 2
    return sort_lines([])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
