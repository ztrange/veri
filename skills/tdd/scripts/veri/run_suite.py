"""run-suite.sh's count-line check, run in-process."""
import os
import re
import subprocess
import sys

SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read_guard(path):
    guard = {}
    with open(path) as f:
        for line in f:
            match = re.match(r"^(COUNT_LINE|COUNTLESS)='(.*)'$", line.rstrip("\n"))
            if match:
                guard[match.group(1)] = match.group(2)
    return guard


def main(argv):
    suite = argv[0]
    guard = read_guard(os.path.join(SCRIPTS, "lib", "count-line-guard.sh"))
    out = bytearray()
    with subprocess.Popen([suite], stdout=subprocess.PIPE) as proc:
        for chunk in iter(lambda: proc.stdout.read1(65536), b""):
            sys.stdout.buffer.write(chunk)
            sys.stdout.buffer.flush()
            out += chunk
    text = out.decode(errors="surrogateescape")
    lines = text.split("\n")
    last_line = lines[-2] if text.endswith("\n") else lines[-1]
    name = os.path.basename(suite)
    sys.stdout.write(guard["COUNTLESS"].replace("\\n", "\n").replace("%s", name))
    if text.strip():
        sys.stdout.write("%s: its last line was: %s\n" % (name, last_line))
    else:
        sys.stdout.write("%s: its output was empty\n" % name)
    sys.stdout.flush()
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
