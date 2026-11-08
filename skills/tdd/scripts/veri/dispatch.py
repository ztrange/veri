"""dispatch.sh's computations, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import subprocess
import sys
import time
from datetime import datetime

import paths
import status
import watch_runs
from ledger import ledger_path

USAGE = "usage: dispatch.sh --target <N>\n"


solvable_issues = watch_runs.solvable_issues
wait = watch_runs.wait
live_conductors = watch_runs.live_conductors


clock = time.time


def stall_window():
    return os.environ.get("VERI_DISPATCH_STALL", "3600")


def now():
    return datetime.now().isoformat(timespec="seconds")


def tdd_dir():
    return os.path.join(status.main_working_tree(), ".tdd")


def run_dir(issue):
    return os.path.join(tdd_dir(), "wt", issue)


def launch(issue):
    scripts = paths.scripts_of(__file__)
    log = os.path.join(tdd_dir(), f"conductor-{issue}.log")
    with open(log, "ab") as out:
        subprocess.Popen([os.path.join(scripts, "detach-leaf.sh"), os.path.join(scripts, "run-conductor.sh"), issue],
                         stdin=subprocess.DEVNULL, stdout=out, stderr=out)


def last_comment(issue):
    out = subprocess.run(["gh", "issue", "view", issue, "--json", "comments", "--jq", ".comments[-1].body"],
                         capture_output=True, text=True, check=True)
    return out.stdout


def queued_merges():
    out = subprocess.run(["ps", "-axo", "args="], capture_output=True, text=True, check=True)
    urls = []
    for line in out.stdout.splitlines():
        words = line.split()
        if len(words) > 2 and words[1].endswith("queued-merge.sh"):
            urls.append(words[2])
    return urls


def pr_state(pr_url):
    out = subprocess.run(["gh", "pr", "view", pr_url, "--json", "state", "--jq", ".state"],
                         capture_output=True, text=True, check=True)
    return out.stdout.strip()


def exit_line(issue):
    heading = last_comment(issue).splitlines()[0]
    if heading.startswith("### ⛔ Bailed"):
        return f"bail {issue}"
    if not heading.startswith("### ✅ Done"):
        return f"silent-exit {issue}"
    return f"done {issue} {heading.split()[-1]}"


def main(argv):
    if not argv:
        sys.stderr.write(USAGE)
        return 2
    if not stall_window().isdigit():
        sys.stderr.write(USAGE)
        return 2
    target = int(argv[1])
    previous = None
    seen = []
    merges = []
    resume_at = 0
    while True:
        live = live_conductors()
        running = queued_merges()
        for pr_url in merges:
            if pr_url not in running and pr_state(pr_url) != "MERGED":
                sys.stdout.write(f"merge-failed {pr_url}\n")
                return 0
        merges = running
        for issue in seen:
            if issue not in live:
                if not os.path.isdir(run_dir(issue)):
                    sys.stderr.write(f"run {issue} vanished: no worktree left behind\n")
                    return 2
                sys.stdout.write(exit_line(issue) + "\n")
                return 0
        stall = int(stall_window())
        for issue in seen:
            events = os.path.join(run_dir(issue), ".tdd", "events.jsonl")
            if os.path.exists(events) and clock() - os.path.getmtime(events) >= stall:
                sys.stdout.write(f"stalled {issue}\n")
                return 0
        seen = live
        ledger = previous and ledger_path(run_dir(previous), previous)
        if len(live) < target and (previous is None or os.path.exists(ledger)) \
            and clock() >= resume_at:
            try:
                previous = solvable_issues()[0]
            except watch_runs.QueueUnreadable as failure:
                if "rate limit" in str(failure):
                    resume_at = watch_runs.github.rate_limit_reset(subprocess.run)
                elif str(failure):
                    sys.stderr.write(str(failure))
                    return 2
                elif not live:
                    sys.stdout.write("queue-empty\n")
                    return 3
            else:
                launch(previous)
                with open(os.path.join(tdd_dir(), "dispatch.log"), "a") as log:
                    log.write(f"launched {previous} {now()}\n")
        wait()


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
