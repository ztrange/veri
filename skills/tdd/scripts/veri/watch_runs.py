"""watch-runs.sh's computation, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import json
import os
import subprocess
import sys
import time

import github
import paths
import pid_file
import status
import tunables

USAGE = "usage: watch-runs.sh [--target <N>] [--max-wait <seconds>]  (N, seconds: whole numbers >= 1)"


def _runs():
    _, document = status.json_document(read_states=False)
    return json.loads(document)["runs"]


def _starting():
    return pid_file.starting_runs(status.main_working_tree())


def live_conductors():
    live = [str(run["issue"]) for run in _runs() if run.get("state") == "running"]
    return live + [issue for issue in dict.fromkeys(_starting()) if issue not in live]


def run_state(issue):
    for run in _runs():
        if str(run["issue"]) == issue:
            return run.get("state", "")
    return ""


class QueueUnreadable(Exception):
    pass


def solvable_issues():
    script = os.path.join(paths.scripts_of(__file__), "veri", "..", "solvable-issues.sh")
    done = subprocess.run([script, "--not-running"], capture_output=True, text=True)
    if done.returncode != 0:
        raise QueueUnreadable(done.stderr)
    return [line.split()[0] for line in done.stdout.splitlines() if line.strip()]


_pause = 2


def wait():
    time.sleep(_pause)


def clock():
    return time.monotonic()


def _seen_path():
    return os.path.join(status.main_working_tree(), ".tdd", "watch-seen-live")


def _seen():
    try:
        with open(_seen_path()) as f:
            return f.read().split()
    except Exception:
        return []


def _remember(issues):
    try:
        os.makedirs(os.path.dirname(_seen_path()), exist_ok=True)
        with open(_seen_path(), "w") as f:
            f.write("".join(issue + "\n" for issue in issues))
    except Exception:
        pass


def _report_exit(issue, state, live=()):
    kept = [i for i in _seen() if i != issue]
    _remember(kept + [i for i in live if i not in kept])
    print("exited %s %s" % (issue, state))
    return 0


def _restart_pending(issue):
    try:
        path = os.path.join(status.main_working_tree(), ".tdd", "wt", issue, ".tdd", "restart-pending")
        with open(path) as f:
            os.kill(int(f.read().strip()), 0)
        return True
    except Exception:
        return False


def _whole_number(text):
    return text.isascii() and text.isdigit() and int(text) >= 1


def main(argv):
    given = {}
    for i in range(0, len(argv), 2):
        flag, value = argv[i], argv[i + 1:i + 2]
        if flag not in ("--target", "--max-wait") or flag in given or not (value and _whole_number(value[0])):
            print(USAGE, file=sys.stderr)
            return 2
        given[flag] = int(value[0])
    target = given.get("--target")
    max_wait = given.get("--max-wait")
    interval = tunables.read("VERI_WATCH_QUEUE_INTERVAL", "60")
    if not _whole_number(interval):
        print("VERI_WATCH_QUEUE_INTERVAL must be a whole number >= 1, got %r" % interval, file=sys.stderr)
        return 2
    interval = int(interval)
    started = live_conductors()
    seen = _seen()
    for issue in seen:
        if issue not in started:
            state = run_state(issue).split(" ")[0]
            return _report_exit(issue, state, started)
    _remember(started)
    if not given and not started:
        print("nothing to watch")
        return 3
    global _pause
    _pause = 2 if max_wait is None else min(2, max_wait)
    deadline = clock() + max_wait if max_wait is not None else None
    missed = set()
    resume_at = 0
    while True:
        wait()
        live = live_conductors()
        arrived = [issue for issue in live if issue not in started]
        if arrived:
            started += arrived
            _remember(started)
        if target is not None and len(live) < target and time.time() >= resume_at:
            try:
                solvable = solvable_issues()
            except QueueUnreadable as failure:
                if "rate limit" not in str(failure):
                    sys.stderr.write(str(failure))
                    return 2
                resume_at = github.rate_limit_reset(subprocess.run)
                if resume_at is not None:
                    resume_at = max(resume_at, time.time() + interval)
                if resume_at is None:
                    sys.stderr.write("gh rate limit exceeded and no reset time could be obtained\n")
                    return 2
                if deadline is not None and resume_at - time.time() > deadline - clock():
                    sys.stderr.write("gh rate limit exceeded; resets at %d, beyond --max-wait\n" % resume_at)
                    return 2
                solvable = []
            else:
                resume_at = time.time() + interval
            if solvable:
                print("slot-free %d/%d next %s" % (len(live), target, solvable[0]))
                return 0
        missed &= set(started) - set(live)
        for issue in started:
            if issue not in live:
                if _restart_pending(issue):
                    continue
                state = run_state(issue).split(" ")[0]
                if state == "running":
                    continue
                if not state and pid_file.recorded_started(
                        os.path.join(status.main_working_tree(), ".tdd", "wt", issue)):
                    continue
                if not state:
                    if issue in pid_file.conductor_processes():
                        continue
                    if issue not in missed:
                        missed.add(issue)
                        continue
                    print("vanished %s" % issue)
                    return 2
                return _report_exit(issue, state)
        if deadline is not None and clock() >= deadline:
            print("timeout")
            return 3


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
