"""profile.sh's per-case timing, run in-process."""
import os
import re
import subprocess
import sys
import tempfile

TRACED = 'PS4=\'+${EPOCHREALTIME} ${LINENO} \'; set -x; . "$0"'


def run_traced(suite, trace):
    try:
        held = os.dup(9)
    except OSError:
        held = None
    fd = os.open(trace, os.O_WRONLY | os.O_TRUNC)
    os.dup2(fd, 9)
    os.close(fd)
    try:
        subprocess.run(["bash", "-c", TRACED, suite], stdin=subprocess.DEVNULL,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, pass_fds=(9,))
    finally:
        if held is None:
            os.close(9)
        else:
            os.dup2(held, 9)
            os.close(held)
    with open(trace) as fd:
        return fd.read().splitlines()


def cases(suite, trace_lines, threshold):
    lines = []
    n = 0
    start = first = None
    for line in trace_lines:
        fields = line.split()
        stamp = fields[0][2:]
        if start is None:
            start = stamp
        lineno = fields[1]
        if first is None:
            first = lineno
        if re.fullmatch(r"(pass|fail)=[0-9]+", fields[2]):
            if int(fields[2].split("=")[1]) > 0:
                n += 1
                secs = float(stamp) - float(start)
                if secs >= float(threshold):
                    lines.append("%.6f %s case %d L%d-%d\n" % (secs, suite, n, int(first), int(lineno)))
                start = stamp
                first = None
    return n, lines


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
    fd, trace = tempfile.mkstemp()
    os.close(fd)
    try:
        lines = []
        for suite in argv:
            n, found = cases(suite, run_traced(suite, trace), threshold)
            if not n:
                print("profile.sh: %s: no pass=/fail= increment in its trace" % suite, file=sys.stderr)
                return 2
            lines += found
        return sort_lines(lines)
    finally:
        os.remove(trace)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
