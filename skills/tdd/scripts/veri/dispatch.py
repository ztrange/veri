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
from role_state import state_path
import status
import timed_n_format
import tunables
import watch_runs
from ledger import ledger_path

USAGE = "usage: dispatch.sh [--target <N>]  (N a whole number >= 0; --target 0 holds dispatch: keeps watching and reporting exits, launches nothing; with no --target, N and the launch order come from .tdd/role-dev.state in the main working tree (.tdd/role-dev-<lane>.state under a VERI_LABEL of ready-for-agent:<lane>): its last n= line, overridden by an unexpired timed-n line, and each override line pulls the issue it names to the front; exit 2 if that file is unreadable, has no n= line, or has a malformed n=, timed-n or override line)"


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


def comment_bodies(issue):
    comments = json_documents.items(github.gh_rest_list(f"repos/{{owner}}/{{repo}}/issues/{issue}/comments?per_page=100"))
    return [comment["body"] for comment in comments]


def last_comment(issue):
    bodies = comment_bodies(issue)
    return bodies[-1] if bodies else ""


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


def issue_states(issues):
    listed = json.loads(github.gh_issue_list("--state", "all", "--limit", "1000", "--json", "number,state"))
    states = {str(item["number"]): item["state"] for item in listed}
    return {issue: states[issue] for issue in issues if issue in states}


class RateLimitPersists(watch_runs.QueueUnreadable):
    pass


def answered(what, read, *args):
    """<read>(*args), a gh read; no answer is an unreadable queue naming <what>. A rate limit waits for the reset
    (the caller's), but a read still rate-limited after VERI_GH_REFUSAL_RETRIES waits in a row is a RateLimitPersists."""
    retries = 0
    limited = _reads.setdefault("limited", {})
    while True:
        try:
            answer = read(*args)
            limited.pop(what, None)
            return answer
        except github.NoAnswer as failure:
            detail = " ".join((failure.detail or str(failure.answer)).split()) or "no answer"
            if ("HTTP 5" in detail or "error connecting to api.github.com" in detail) and retries < 12:
                retries += 1
                github.time.sleep(int(tunables.read("VERI_DISPATCH_RETRY_SLEEP", "5")))
                continue
            unreadable = f"dispatch.sh: reading {what} failed: {detail}\n"
            if "rate limit" in detail:
                limited[what] = limited.get(what, 0) + 1
                if limited[what] > github._wait_seconds("VERI_GH_REFUSAL_RETRIES", "3", 0):
                    raise RateLimitPersists(unreadable)
            raise watch_runs.QueueUnreadable(unreadable)


def overlap_poll():
    return tunables.read("VERI_DISPATCH_OVERLAP_POLL", "60", unless_empty="60")


# The overlap reads one dispatch process has made, emptied as main() starts: issue bodies per issue,
# PR diffs per (PR url, head sha), and the open run draft PRs with the time they were listed.
_reads = {}


def issue_paths(issue):
    """The backticked words of <issue>'s body: the repo paths it names. Read once per dispatch process."""
    bodies = _reads.setdefault("bodies", {})
    if issue not in bodies:
        bodies[issue] = answered(f"issue {issue}'s body", github.gh_issue_view, issue, "body")
    return re.findall(r"`([^`\s]+)`", bodies[issue])


def run_prs():
    """(url, number, head sha) of every open run draft PR (head tdd/…), on any machine,
    listed at most once per VERI_DISPATCH_OVERLAP_POLL seconds."""
    listed = _reads.get("listed")
    if listed is None or clock() - listed[0] >= int(overlap_poll()):
        prs = []
        for pr in answered("the open PR list", handoff_state.open_prs, "number,url,isDraft,headRefName,headRefOid,labels"):
            head = pr.get("head") or {}
            if "parked" in {label.get("name") for label in pr.get("labels") or []}:
                continue
            if pr["isDraft"] and (pr.get("headRefName") or head.get("ref") or "").startswith("tdd/"):
                prs.append((pr.get("url") or pr.get("html_url"), pr["number"], pr.get("headRefOid") or head.get("sha")))
        listed = _reads["listed"] = (clock(), prs)
    return listed[1]


def run_pr_paths():
    """{url: changed paths} of every open run draft PR, each diff read once per head sha."""
    diffs = _reads.setdefault("diffs", {})
    changed = {}
    for url, number, sha in run_prs():
        if (url, sha) not in diffs:
            diffs[(url, sha)] = answered(f"{url}'s diff", github.gh_pr_diff_names, number)
        changed[url] = diffs[(url, sha)]
    return changed


def overlap(issue, changed):
    """(path, PR url) of the first path <issue> names that an open run draft PR in <changed> changes, else None."""
    return next(((path, url) for path in issue_paths(issue) for url, files in changed.items() if path in files), None)


def say(text):
    sys.stdout.write(text)
    sys.stdout.flush()


def launchable(issue, changed, reported):
    """Whether <issue> overlaps no open run draft PR; a skip prints one line naming the issue, the path and the PR,
    once per (issue, path, PR) in <reported>, the skips this dispatch process already printed."""
    found = overlap(issue, changed)
    if found and (issue, *found) not in reported:
        reported.add((issue, *found))
        say(f"skip {issue} {found[0]} {found[1]}\n")
    return not found


def exit_line(issue):
    body = last_comment(issue)
    if not body.startswith(("### ⛔ Bailed", "### ✅ Done")):
        bodies = comment_bodies(issue)
        if len(bodies) > 1:
            body = bodies[-2]
    heading = next(iter(body.splitlines()), "")
    if heading.startswith("### ⛔ Bailed"):
        return f"bail {issue}"
    if not heading.startswith("### ✅ Done"):
        return f"silent-exit {issue}"
    return f"done {issue} {heading.split()[-1]}"


def parse_args(argv):
    if (
        not argv
        or not stall_window().isdigit()
        or not overlap_poll().isdigit()
        or len(argv) != 2
        or argv[0] != "--target"
        or not argv[1].isdigit()
    ):
        return None
    return int(argv[1])


class MalformedOverride(Exception):
    pass


class MalformedState(Exception):
    pass


def last_n(lines):
    ns = [line for line in lines if line.startswith("n=")]
    if not ns:
        raise MalformedState("no n= line")
    try:
        return int(ns[-1][2:])
    except ValueError:
        raise MalformedState(f"malformed n line: {ns[-1]}")


def timed_n(line):
    try:
        return timed_n_format.parse(line.split(None, 3)[3])
    except (IndexError, ValueError):
        raise MalformedState(f"malformed timed-n line: {line}")


def prioritize(free, lines):
    named_before = set()
    for line in lines:
        if not line.startswith("override "):
            continue
        fields = line.split(None, 3)
        if len(fields) < 4:
            raise MalformedOverride(line)
        named = re.search(r"\d+", fields[3])
        if named and named.group() in free and named.group() not in named_before:
            named_before.add(named.group())
            free.remove(named.group())
            free.insert(0, named.group())
    return free


def lane():
    return tunables.lane_of(tunables.read("VERI_LABEL", "ready-for-agent", unless_empty="ready-for-agent"))


def state_file():
    return state_path(status.main_working_tree(), "dev", lane())


def main(argv):
    if not argv:
        state = state_file()
        if not os.path.isfile(state) or not os.access(state, os.R_OK):
            sys.stderr.write(f"dispatch.sh: cannot read {state}\n")
            return 2
    target = parse_args(argv) if argv else 0
    if target is None:
        sys.stderr.write(USAGE + "\n")
        return 2
    if not tunables.read("VERI_DISPATCH_RETRY_SLEEP", "5").isdigit():
        sys.stderr.write("dispatch.sh: VERI_DISPATCH_RETRY_SLEEP must be a whole number of seconds\n")
        return 2
    previous = None
    seen = []
    absent = []
    pending = []
    merges = []
    resume_at = 0
    reported = set()
    missing = {}
    held_at = None
    _reads.clear()
    while True:
        live = live_conductors()
        running = queued_merges()
        for pr_url in merges:
            if pr_url not in running and pr_state(pr_url) not in ("MERGED", "UNRESOLVED"):
                say(f"merge-failed {pr_url}\n")
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
                line = exit_line(issue)
                if line.startswith("silent-exit") and clock() - missing.setdefault(issue, clock()) < 30:
                    if issue not in pending:
                        pending.append(issue)
                    continue
                say(line + "\n")
                return 0
        if not argv:
            lines = status.read_role_state("dev", lane())
            try:
                target = last_n(lines)
                for line in lines:
                    if line.startswith("timed-n "):
                        value, expiry = timed_n(line)
                        if clock() < expiry:
                            target = value
            except MalformedState as why:
                sys.stderr.write(f"dispatch.sh: {why} in {state_file()}\n")
                return 2
        stall = int(stall_window())
        states = None
        for issue in seen:
            tdd = os.path.join(run_dir(issue), ".tdd")
            events = os.path.join(tdd, "events.jsonl")
            if os.path.exists(events) and clock() - max(
                    os.path.getmtime(f)
                    for f in (events, *glob.glob(os.path.join(tdd, "*.out")),
                              *glob.glob(os.path.join(tdd, "*.log")))
                    if os.path.exists(f)) >= stall:
                if states is None:
                    try:
                        states = answered("issue states", issue_states, seen)
                    except watch_runs.QueueUnreadable as failure:
                        sys.stderr.write(str(failure))
                        return 2
                if states.get(issue) == "CLOSED":
                    continue
                say(f"stalled {issue}\n")
                return 0
        for issue in live:
            missing.pop(issue, None)
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
            and clock() >= resume_at and (held_at is None or clock() - held_at >= int(overlap_poll())):
            try:
                queue = solvable_issues()
                changed = run_pr_paths()
                free = [issue for issue in queue if launchable(issue, changed, reported)]
                free = prioritize(free, status.read_role_state("dev", lane()))
            except MalformedOverride as line:
                sys.stderr.write(f"dispatch.sh: malformed override line in {state_file()}: {line}\n")
                return 2
            except watch_runs.QueueUnreadable as failure:
                if "rate limit" in str(failure) and not isinstance(failure, RateLimitPersists):
                    resume_at = watch_runs.github.rate_limit_reset(subprocess.run)
                elif str(failure):
                    sys.stderr.write(str(failure))
                    return 2
                elif not live:
                    say("queue-empty\n")
                    return 3
            else:
                held_at = clock() if queue and not free else None
                if free:
                    previous = free[0]
                    launch(previous)
                    with open(os.path.join(tdd_dir(), "dispatch.log"), "a") as log:
                        log.write(f"launched {previous} {now()}\n")
        wait()


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
