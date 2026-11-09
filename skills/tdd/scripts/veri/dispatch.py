"""dispatch.sh's computations, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import json
import glob
import os
import re
import subprocess
import sys
import time
from datetime import datetime

import github
import handoff_state
import json_documents
import paths
import status
import tunables
import watch_runs
from ledger import ledger_path

USAGE = "usage: dispatch.sh --target <N>"


solvable_issues = watch_runs.solvable_issues
wait = watch_runs.wait
live_conductors = watch_runs.live_conductors


clock = time.time


def stall_window():
    return tunables.read("VERI_DISPATCH_STALL", "3600")


def restart_pending(issue):
    """True while a restart is in flight: the marker holds the restarter's pid;
    a dead pid is a stale marker, so the exit is reported. A marker not yet
    holding a pid (restart-conductor.sh is mid-write) counts as in flight."""
    try:
        with open(os.path.join(run_dir(issue), ".tdd", "restart-pending")) as f:
            text = f.read().strip()
    except FileNotFoundError:
        return False
    if not text.isdigit():
        return True
    try:
        os.kill(int(text), 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def now():
    return datetime.now().isoformat(timespec="seconds")


def tdd_dir():
    return os.path.join(status.main_working_tree(), ".tdd")


def run_dir(issue):
    return os.path.join(tdd_dir(), "wt", issue)


def launch(issue):
    scripts = paths.scripts_of(__file__)
    for script, log_name in (("run-conductor.sh", f"conductor-{issue}.log"), ("restart-conductor.sh", f"restart-{issue}.log")):
        with open(os.path.join(tdd_dir(), log_name), "ab") as out:
            subprocess.Popen([os.path.join(scripts, "detach-leaf.sh"), os.path.join(scripts, script), issue],
                             stdin=subprocess.DEVNULL, stdout=out, stderr=out)


def last_comment(issue):
    comments = json_documents.items(github.gh_rest_list(f"repos/{{owner}}/{{repo}}/issues/{issue}/comments?per_page=100"))
    return comments[-1]["body"] if comments else ""


def queued_merges():
    out = subprocess.run(["ps", "-axo", "args="], capture_output=True, text=True, check=True)
    urls = []
    mine = os.path.realpath(os.path.join(paths.scripts_of(__file__), "queued-merge.sh"))
    py_mine = os.path.realpath(os.path.join(paths.scripts_of(__file__), "veri", "queued_merge.py"))
    for line in out.stdout.splitlines():
        words = line.split()
        if len(words) < 3:
            continue
        script = os.path.realpath(words[1])
        if script == mine or (script == py_mine and os.path.basename(words[0]).startswith("python")):
            urls.append(words[2])
    return urls


def pr_state(pr_url):
    owner, repo, number = pr_url.split("/")[-4], pr_url.split("/")[-3], pr_url.split("/")[-1]
    pull = json.loads(github.gh_api(f"repos/{owner}/{repo}/pulls/{number}").stdout)
    if "merged" not in pull:
        return "UNRESOLVED"
    return "MERGED" if pull["merged"] else pull["state"].upper()


def issue_paths(issue):
    """The backticked words of <issue>'s body: the repo paths it names."""
    return re.findall(r"`([^`\s]+)`", github.gh_issue_view(issue, "body"))


def run_pr_paths():
    """{url: changed paths} of every open run draft PR (head tdd/…), on any machine."""
    changed = {}
    for pr in handoff_state.open_prs("number,url,isDraft,headRefName"):
        head = pr.get("headRefName") or (pr.get("head") or {}).get("ref") or ""
        if pr["isDraft"] and head.startswith("tdd/"):
            diff = subprocess.run(["gh", "pr", "diff", str(pr["number"]), "--name-only"],
                                  capture_output=True, text=True)
            changed[pr.get("url") or pr.get("html_url")] = diff.stdout.split()
    return changed


def overlap(issue, changed):
    """(path, PR url) of the first path <issue> names that an open run draft PR in <changed> changes, else None."""
    return next(((path, url) for path in issue_paths(issue) for url, files in changed.items() if path in files), None)


def launchable(issue, changed):
    """Whether <issue> overlaps no open run draft PR; a skip prints one line naming the issue, the path and the PR."""
    found = overlap(issue, changed)
    if found:
        sys.stdout.write(f"skip {issue} {found[0]} {found[1]}\n")
    return not found


def exit_line(issue):
    heading = next(iter(last_comment(issue).splitlines()), "")
    if heading.startswith("### ⛔ Bailed"):
        return f"bail {issue}"
    if not heading.startswith("### ✅ Done"):
        return f"silent-exit {issue}"
    return f"done {issue} {heading.split()[-1]}"


def parse_args(argv):
    if (
        not argv
        or not stall_window().isdigit()
        or len(argv) != 2
        or argv[0] != "--target"
        or not argv[1].isdigit()
        or int(argv[1]) == 0
    ):
        return None
    return int(argv[1])


def main(argv):
    target = parse_args(argv)
    if target is None:
        sys.stderr.write(USAGE + "\n")
        return 2
    previous = None
    seen = []
    absent = []
    pending = []
    merges = []
    resume_at = 0
    while True:
        live = live_conductors()
        running = queued_merges()
        for pr_url in merges:
            if pr_url not in running and pr_state(pr_url) not in ("MERGED", "UNRESOLVED"):
                sys.stdout.write(f"merge-failed {pr_url}\n")
                return 0
        merges = running
        for issue in seen:
            if issue not in live:
                if not os.path.isdir(run_dir(issue)):
                    pending = [p for p in pending if p != issue]
                    if issue in absent:
                        sys.stderr.write(f"run {issue} vanished: no worktree left behind\n")
                        return 2
                    absent.append(issue)
                    continue
                if restart_pending(issue):
                    if issue not in pending:
                        pending.append(issue)
                    continue
                sys.stdout.write(exit_line(issue) + "\n")
                return 0
        stall = int(stall_window())
        for issue in seen:
            tdd = os.path.join(run_dir(issue), ".tdd")
            events = os.path.join(tdd, "events.jsonl")
            log = os.path.join(tdd, f"conductor-{issue}.log")
            if os.path.exists(events) and clock() - max(
                    os.path.getmtime(f)
                    for f in (events, log, *glob.glob(os.path.join(tdd, "*.out")))
                    if os.path.exists(f)) >= stall:
                sys.stdout.write(f"stalled {issue}\n")
                return 0
        absent = [issue for issue in absent if issue not in live]
        pending = [issue for issue in pending if issue not in live and issue not in absent]
        seen = live + absent + pending
        ledger = previous and ledger_path(run_dir(previous), previous)
        held = len(live) + len(pending)
        if held < target:
            wt = os.path.join(tdd_dir(), "wt")
            held = len(live) + len(set(pending) | {
                i for i in (os.listdir(wt) if os.path.isdir(wt) else [])
                if i not in live and restart_pending(i)})
        if held < target and (previous is None or os.path.exists(ledger)) \
            and clock() >= resume_at:
            try:
                queue = solvable_issues()
                changed = run_pr_paths()
                free = [issue for issue in queue if launchable(issue, changed)]
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
                if free:
                    previous = free[0]
                    launch(previous)
                    with open(os.path.join(tdd_dir(), "dispatch.log"), "a") as log:
                        log.write(f"launched {previous} {now()}\n")
        wait()


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
