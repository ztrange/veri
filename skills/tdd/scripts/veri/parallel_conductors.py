"""parallel-conductors.sh's launcher, run in-process."""
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import traceback

try:
    from github import NoAnswer, gh_json
    from json_documents import items
except ImportError:
    from .github import NoAnswer, gh_json
    from .json_documents import items

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
        self.context = 0
        self.armed = False
        self.stopped = False

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
        self._watch_context(whole)
        return alive

    def _watch_context(self, lines):
        for line in lines:
            if self.stopped:
                return
            if self.armed and b'"type":"user"' in line:
                self.armed = False
                if self.context > int(_ctx_budget()):
                    os.kill(self.sup.pid, signal.SIGTERM)
                    self.stopped = True
                continue
            if b'"type":"assistant"' not in line:
                continue
            cache_read = CACHE_READ.search(line)
            cache_creation = CACHE_CREATION.search(line) if cache_read else None
            if cache_creation:
                self.context = int(cache_read.group(1)) + int(cache_creation.group(1))
                print("context %s %d" % (self.n, self.context), flush=True)
            if b"event.sh step-done" in line:
                self.armed = True


def _prs_json():
    return gh_json("prs.json", "repos/{owner}/{repo}/pulls?state=open&per_page=100",
                   "pr", "list", "--state", "open", "--limit", "10000", "--json", "body,isDraft,url")


def _finish_prs_json():
    try:
        return _prs_json()
    except NoAnswer as error:
        return error.answer
    except FileNotFoundError:
        return ""


def _outcome(n, code, prs):
    if code == 2:
        return "killed after %ss" % _run_timeout()
    if _parked(n):
        return ""
    try:
        prs = items(prs)
    except ValueError:
        traceback.print_exc()
        return ""
    for pr in prs:
        if n in re.findall(r"\bCloses #(\d+)", pr.get("body") or ""):
            url = pr.get("html_url", pr.get("url", ""))
            if not pr.get("isDraft", pr.get("draft")):
                return "done %s" % url
            try:
                with open(os.path.join(".tdd", "wt", n, ".tdd", "events.jsonl"), "rb") as f:
                    last = f.read().removesuffix(b"\n").rsplit(b"\n", 1)[-1]
            except OSError:
                last = b""
            return "bailed %s" % url if b'"event": "bail"' in last else ""
    return ""


def _parked(n):
    return os.path.exists(os.path.join(".tdd", "parked", "%s.md" % n))


def _is_failure(got):
    return got.startswith(("killed ", "bailed "))


def _ctx_budget():
    return os.environ.get("VERI_CONDUCTOR_CTX_BUDGET") or "120000"


def _bash_arithmetic(value):
    return int(value, 8 if value.startswith("0") else 10)


def _run_timeout():
    return os.environ.get("VERI_RUN_TIMEOUT") or "14400"


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
    parallel = os.environ.get("VERI_PARALLEL", "1")
    max_issues = os.environ.get("VERI_MAX_ISSUES")
    if not (_whole_number("VERI_CONDUCTOR_CTX_BUDGET", _ctx_budget(), 0)
            and _whole_number("VERI_PARALLEL", parallel, 1)
            and (max_issues is None or _whole_number("VERI_MAX_ISSUES", max_issues, 1))):
        return _finish(2)
    rc_dir = tempfile.mkdtemp()
    code = _run(argv[:1] == ["--continue-on-bail"], int(parallel), max_issues or "0")
    try:
        shutil.rmtree(rc_dir)
    except OSError:
        return 2
    return code


def _run(continue_on_bail, parallel, max_issues):
    try:
        max_issues = _bash_arithmetic(max_issues)
    except ValueError:
        max_issues = -1
    launched, in_flight, codes = [], [], {}
    plumbing, why, stopped = False, "", ""
    while True:
        while len(in_flight) < parallel and not stopped:
            if max_issues < 0 or max_issues and len(launched) >= max_issues:
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
            try:
                prs = _prs_json()
            except NoAnswer:
                return 2
            for n in launched:
                got = _outcome(n, codes.get(n), prs)
                if got:
                    print("#%s — %s" % (n, got), flush=True)
                failed = failed or _is_failure(got)
            print("stopped: %s" % (stopped or why), flush=True)
            return _finish(2 if plumbing else 1 if failed else 3 if not launched else 0)
        done = [c for c in in_flight if not c.follow()]
        for c in done:
            in_flight.remove(c)
            codes[c.n] = c.sup.wait()
            if c.stopped:
                print("restarted %s" % c.n, flush=True)
                in_flight.append(_Conductor(c.n))
            elif _parked(c.n):
                print("parked %s" % c.n, flush=True)
            elif not continue_on_bail and not stopped:
                got = _outcome(c.n, codes[c.n], _finish_prs_json())
                if _is_failure(got):
                    stopped = "#%s %s" % (c.n, got.split()[0])
        if not done:
            time.sleep(float(os.environ.get("VERI_POLL") or "1"))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
