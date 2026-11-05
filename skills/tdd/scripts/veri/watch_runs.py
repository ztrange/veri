"""watch-runs.sh's computation, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import json
import os
import subprocess
import sys
import time

import paths
import pid_file
import status


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


def rate_limit_reset():
    done = subprocess.run(["gh", "api", "rate_limit", "--jq", ".resources.core.reset"],
                          capture_output=True, text=True)
    try:
        return int(done.stdout.strip())
    except ValueError:
        return None


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


def _whole_number(text):
    return text.isascii() and text.isdigit() and int(text) >= 1


def main(argv):
    given = {}
    for i in range(0, len(argv), 2):
        flag, value = argv[i], argv[i + 1:i + 2]
        if flag not in ("--target", "--max-wait") or flag in given or not (value and _whole_number(value[0])):
            print("usage: watch-runs.sh [--target <N>] [--max-wait <seconds>]  (N, seconds: whole numbers >= 1)",
                  file=sys.stderr)
            return 2
        given[flag] = int(value[0])
    target = given.get("--target")
    max_wait = given.get("--max-wait")
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
        if target is not None and len(live) < target and time.time() >= resume_at:
            try:
                solvable = solvable_issues()
            except QueueUnreadable as failure:
                if "rate limit" not in str(failure):
                    sys.stderr.write(str(failure))
                    return 2
                resume_at = rate_limit_reset()
                if resume_at is None:
                    sys.stderr.write("gh rate limit exceeded and no reset time could be obtained\n")
                    return 2
                if deadline is not None and resume_at - time.time() > deadline - clock():
                    sys.stderr.write("gh rate limit exceeded; resets at %d, beyond --max-wait\n" % resume_at)
                    return 2
                solvable = []
            if solvable:
                print("slot-free %d/%d next %s" % (len(live), target, solvable[0]))
                return 0
        missed &= set(started) - set(live)
        for issue in started:
            if issue not in live:
                state = run_state(issue).split(" ")[0]
                if not state:
                    if pid_file.recorded_started(os.path.join(status.main_working_tree(), ".tdd", "wt", issue)):
                        continue
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
