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
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, pass_fds=(9,),
                       env={**os.environ, "BASH_XTRACEFD": "9"})
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
    start = first = ""
    seen = {}
    for line in trace_lines:
        if not re.match(r"\+\+[^+]", line):
            continue
        fields = line.split()
        stamp = fields[0][2:]
        if stamp and not start:
            start = stamp
        lineno = fields[1]
        if not first:
            first = lineno
        counter = len(fields) == 3 and re.fullmatch(r"(pass|fail)=([0-9]+)", fields[2])
        if counter:
            name, value = counter[1], int(counter[2])
            if value > seen.get(name, 0):
                n += 1
                secs = float(stamp) - float(start)
                if secs >= threshold:
                    lines.append("%.6f %s case %d L%d-%d\n" % (secs, suite, n, int(first), int(lineno)))
                start = stamp
                first = ""
            seen[name] = value
    return n, lines


def sort_lines(lines):
    done = subprocess.run(["sort", "-rn"], input="".join(lines), text=True, stdout=subprocess.PIPE)
    sys.stdout.write(done.stdout)
    return done.returncode if 0 <= done.returncode <= 3 else 2


def main(argv):
    threshold = os.environ.get("VERI_PROFILE_THRESHOLD") or "1"
    if not re.fullmatch(r"[0-9]+(\.[0-9]+)?", threshold):
        print("profile.sh: VERI_PROFILE_THRESHOLD must be a number of seconds, got '%s'" % threshold,
              file=sys.stderr)
        return 2
    seconds = float(threshold)
    fd, trace = tempfile.mkstemp()
    os.close(fd)
    try:
        lines = []
        for suite in argv:
            n, found = cases(suite, run_traced(suite, trace), seconds)
            if not n:
                print("profile.sh: %s: no pass=/fail= increment in its trace" % suite, file=sys.stderr)
                sort_lines(lines)
                return 2
            lines += found
        return sort_lines(lines)
    finally:
        os.remove(trace)


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
