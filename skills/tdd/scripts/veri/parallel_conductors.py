"""parallel-conductors.sh's launcher, run in-process."""
import os
import re
import subprocess
import sys
import time

SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_READ = re.compile(rb'"cache_read_input_tokens":([0-9]+)')
CACHE_CREATION = re.compile(rb'"cache_creation_input_tokens":([0-9]+)')


def _lines(sup, path):
    part = b""
    with open(path, "rb") as log:
        while True:
            alive = sup.poll() is None
            chunk = part + log.read()
            *whole, part = chunk.split(b"\n")
            yield from whole
            if not alive:
                return
            time.sleep(1)


def _watch_context(n, lines):
    for line in lines:
        if b'"type":"assistant"' not in line:
            continue
        cache_read = CACHE_READ.search(line)
        cache_creation = CACHE_CREATION.search(line) if cache_read else None
        if cache_creation:
            print("context %s %d" % (n, int(cache_read.group(1)) + int(cache_creation.group(1))), flush=True)


def _launch(n):
    log = os.path.join(".tdd", "conductor-%s.log" % n)
    sup = subprocess.Popen([os.path.join(SCRIPTS, "supervise.sh"), "conductor-%s" % n,
                            os.path.join(SCRIPTS, "run-conductor.sh"), n], stdout=subprocess.DEVNULL)
    _watch_context(n, _lines(sup, log))
    return sup.wait()


def main(argv):
    launched = []
    while True:
        solvable = subprocess.run([os.path.join(SCRIPTS, "solvable-issues.sh")], stdout=subprocess.PIPE, text=True)
        if solvable.returncode:
            print("stopped: nothing solvable", flush=True)
            return 3
        n = next((c for c in solvable.stdout.split() if c not in launched), None)
        if n is None:
            return 0
        launched.append(n)
        _launch(n)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
