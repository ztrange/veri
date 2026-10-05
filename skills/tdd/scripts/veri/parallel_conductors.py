"""parallel-conductors.sh's launcher, run in-process."""
import os
import re
import shutil
import subprocess
import sys
import tempfile
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


def _finish(code):
    os.makedirs(".tdd", exist_ok=True)
    with open(os.path.join(".tdd", "parallel.exit"), "w") as f:
        f.write("%d\n" % code)
    return code


def _whole_number(name, value, floor):
    if re.fullmatch(r"[0-9]+", value) and int(value) >= floor:
        return True
    print("parallel-conductors: %s must be a whole number >= %d: '%s'" % (name, floor, value), file=sys.stderr)
    return False


def main(argv):
    if not (_whole_number("VERI_CONDUCTOR_CTX_BUDGET", os.environ.get("VERI_CONDUCTOR_CTX_BUDGET") or "120000", 0)
            and _whole_number("VERI_PARALLEL", os.environ.get("VERI_PARALLEL", "1"), 1)
            and ("VERI_MAX_ISSUES" not in os.environ
                 or _whole_number("VERI_MAX_ISSUES", os.environ["VERI_MAX_ISSUES"], 1))):
        return _finish(2)
    rc_dir = tempfile.mkdtemp()
    code = _run()
    try:
        shutil.rmtree(rc_dir)
    except OSError:
        return 2
    return code


def _run():
    launched = []
    while True:
        solvable = subprocess.run([os.path.join(SCRIPTS, "solvable-issues.sh")], stdout=subprocess.PIPE, text=True)
        if solvable.returncode:
            print("stopped: nothing solvable", flush=True)
            return _finish(3)
        n = next((c for c in solvable.stdout.split() if c not in launched), None)
        if n is None:
            return _finish(0)
        launched.append(n)
        _launch(n)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
