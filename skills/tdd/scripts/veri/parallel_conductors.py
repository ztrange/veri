"""parallel-conductors.sh's launcher, run in-process."""
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASSED_THROUGH = ("VERI_HEARTBEAT", "VERI_TIMEOUT", "VERI_STUCK_RETRIES", "VERI_POLL")
CACHE_READ = re.compile(rb'"cache_read_input_tokens":([0-9]+)')
CACHE_CREATION = re.compile(rb'"cache_creation_input_tokens":([0-9]+)')


class _Conductor:
    def __init__(self, n):
        self.n = n
        self.log = os.path.join(".tdd", "conductor-%s.log" % n)
        try:
            os.remove(self.log)
        except FileNotFoundError:
            pass
        words = ["%s=%s" % (name, os.environ[name]) for name in PASSED_THROUGH if name in os.environ]
        run_timeout = _run_timeout()
        env = dict(os.environ, VERI_HEARTBEAT=run_timeout, VERI_TIMEOUT=run_timeout, VERI_STUCK_RETRIES="0")
        self.sup = subprocess.Popen([os.path.join(SCRIPTS, "supervise.sh"), "conductor-%s" % n, "env",
                                     *[w for name in PASSED_THROUGH for w in ("-u", name)], *words,
                                     os.path.join(SCRIPTS, "run-conductor.sh"), n],
                                    stdout=subprocess.DEVNULL, env=env)
        self.read = 0
        self.part = b""

    def follow(self):
        alive = self.sup.poll() is None
        try:
            with open(self.log, "rb") as log:
                log.seek(self.read)
                chunk = log.read()
        except FileNotFoundError:
            chunk = b""
        self.read += len(chunk)
        *whole, self.part = (self.part + chunk).split(b"\n")
        _watch_context(self.n, whole)
        return alive


def _run_timeout():
    return os.environ.get("VERI_RUN_TIMEOUT") or "14400"


def _watch_context(n, lines):
    for line in lines:
        if b'"type":"assistant"' not in line:
            continue
        cache_read = CACHE_READ.search(line)
        cache_creation = CACHE_CREATION.search(line) if cache_read else None
        if cache_creation:
            print("context %s %d" % (n, int(cache_read.group(1)) + int(cache_creation.group(1))), flush=True)


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


def _exclude_tdd():
    git = subprocess.run(["git", "rev-parse", "--git-common-dir"], stdout=subprocess.PIPE, text=True)
    if git.returncode:
        return False
    exclude = os.path.join(git.stdout.rstrip("\n"), "info", "exclude")
    try:
        with open(exclude, "rb") as f:
            text = f.read()
    except FileNotFoundError:
        text = b""
    if b".tdd/*" in text.split(b"\n"):
        return True
    os.makedirs(os.path.dirname(exclude), exist_ok=True)
    with open(exclude, "ab") as f:
        f.write((b"\n" if text and not text.endswith(b"\n") else b"") + b".tdd/*\n")
    return True


def main(argv):
    if not _exclude_tdd():
        return 2
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
    parallel = int(os.environ.get("VERI_PARALLEL", "1"))
    max_issues = int(os.environ.get("VERI_MAX_ISSUES", "0"))
    launched, in_flight, codes = [], [], {}
    plumbing, why = False, ""
    while True:
        while len(in_flight) < parallel:
            if max_issues and len(launched) >= max_issues:
                why = "VERI_MAX_ISSUES reached"
                break
            solvable = subprocess.run([os.path.join(SCRIPTS, "solvable-issues.sh")], stdout=subprocess.PIPE, text=True)
            why = "nothing solvable"
            if solvable.returncode == 2:
                plumbing, why = True, "solvable-issues.sh could not answer"
            if solvable.returncode:
                break
            n = next((c for c in solvable.stdout.split() if c not in launched), None)
            if n is None:
                break
            launched.append(n)
            in_flight.append(_Conductor(n))
        if not in_flight:
            failed = False
            for n in launched:
                if codes.get(n) == 2:
                    print("#%s — killed after %ss" % (n, _run_timeout()), flush=True)
                    failed = True
            print("stopped: %s" % why, flush=True)
            return _finish(2 if plumbing else 1 if failed else 3 if not launched else 0)
        done = [c for c in in_flight if not c.follow()]
        for c in done:
            in_flight.remove(c)
            codes[c.n] = c.sup.wait()
        if not done:
            time.sleep(1)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
