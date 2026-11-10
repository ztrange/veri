"""status.sh's computations, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import calendar
import contextlib
import glob
import io
import json
import os
import re
import statistics
import subprocess
import sys
import time

import run_end
from pid_file import live_conductor
from event_log import read_events, usage_totals
from ledger import ledger_path, ledger_steps
from run_dir import run_file
import tunables
from role_state import state_path
from solvable_issues import priority_label, solvable

ISO_UTC = "%Y-%m-%dT%H:%M:%SZ"

try:
    from . import github
except ImportError:
    import github


def run_activity(run, as_json=False, closed=False):
    """The activity line for one run."""
    last, attempts = None, 0
    newest = None
    events_path = run_file(run, "events.jsonl")
    events_path_exists = os.path.isfile(events_path)
    events = read_events(events_path) if events_path_exists else []
    dollars, tokens = usage_totals(events)
    ended, cause, end = run_end.run_end(run) if events_path_exists else (False, None, {})
    if end.get("event") in ("preflight-refused", "bail", "stop") and live_conductor(os.fspath(run)):
        ended, end = False, {}
    for line in events:
        newest = line
        if line.get("event") == "launch":
            if line.get("step") != (last or {}).get("step"):
                attempts = 0
            last = line
            attempts += 1

    now = int(time.time())
    if end.get("event") == "done":
        state = "done %s" % end.get("pr", "")
    elif end.get("event") == "stop":
        state = "stopped %s" % end.get("mode", "")
    elif end.get("event") == "bail":
        state = "bailed %s %s" % (end.get("phase", ""), end.get("classification", ""))
    elif end.get("event") == "preflight-refused":
        state = "refused %s" % end.get("check", "")
    elif ended:
        state = "stale"
    else:
        state = "running"
    last = last or end or newest or {"ts": now}
    if closed:
        state = "closed"
    phase, actor, leaf = last.get("phase", ""), last.get("actor", ""), last.get("name", "")
    elapsed = now - int(last["ts"])
    if as_json:
        return json.dumps({"phase": phase, "actor": actor, "leaf": leaf, "elapsed_seconds": elapsed,
                           "attempts": attempts, "dollars": round(dollars, 2), "tokens": tokens,
                           "state": state.split(" ")[0], "pr": end.get("pr", ""),
                           "bail_phase": end.get("phase", ""),
                           "classification": end.get("classification", ""),
                           "stop_mode": end.get("mode", ""),
                           "cause": cause or ""})
    return "%s  %s  %s %ds  attempt %d  $%.2f  %d tokens  %s" % (phase, actor, leaf, elapsed,
           attempts, dollars, tokens, state)


def scope_totals(name, solvable, runs, as_json=False, bare=0):
    """The scope totals line over every run's events."""
    attempted, done, bailed, wall = bare, 0, 0, 0
    dollars = 0.0
    for run in runs:
        try:
            events = read_events(run_file(run, "events.jsonl"))
            end = run_end.run_end(run)[2].get("event")
        except FileNotFoundError:
            continue
        attempted += 1
        dollars += usage_totals(events)[0]
        done += end == "done"
        bailed += end == "bail"
        timed = [e for e in events if "ts" in e]
        if timed:
            wall += int(timed[-1]["ts"]) - int(timed[0]["ts"])
    if as_json:
        return json.dumps({"name": name, "attempted": attempted, "done": done,
                           "bailed": bailed, "wall_seconds": wall, "dollars": round(dollars, 2),
                           "solvable": int(solvable) if solvable.isdigit() else solvable})
    return "scope %s  attempted %d  done %d  bailed %d  wall %ds  $%.2f  solvable %s" % (
        name, attempted, done, bailed, wall, dollars, solvable)


def issue_states():
    """{issue number: "open" | "closed"} from one gh call, empty when gh gave no answer."""
    try:
        answer = github.gh_issue_list("--state", "all", "--limit", "1000", "--json", "number,state")
        return {str(i["number"]): i["state"].lower() for i in json.loads(answer)}
    except (github.NoAnswer, ValueError, TypeError):
        return {}


def run_object(issue, title, branch, step, activity, states):
    """One run's --json object: the ledger fields, then the activity object's."""
    run = {"issue": issue, "title": title, "branch": branch, "step": step,
           "issue_state": states.get(issue, "unknown")}
    run.update(json.loads(activity) if activity else {})
    if run["issue_state"] == "closed":
        run["state"] = "closed"
    return json.dumps(run)


def main_working_tree():
    listed = subprocess.run(["git", "worktree", "list", "--porcelain"],
                            capture_output=True, text=True).stdout
    first = listed.split("\n", 1)[0]
    return first[len("worktree "):] if first.startswith("worktree ") else first


def step_of_total(text):
    """"<n> of <m>": the step pending refactor, else the first open step of the ledger's <m>, or <m> when none is open."""
    records = ledger_steps(text)
    total = records[-1][0] if records else "0"
    step = next((index for index, state, _kind, pending, *_ in records if pending == "1"), None) \
        or next((index for index, state, *_ in records if state == "open"), total)
    return "%s of %s" % (step, total)


def branch_of(run):
    return subprocess.run(["git", "-C", run, "symbolic-ref", "--short", "HEAD"],
                          capture_output=True, text=True).stdout.strip()


def solvable_count(name):
    """"<count>" solvable_issues lists for scope <name>, or "?" when it gave no answer."""
    priority = priority_label()
    if priority is None:
        return "?"
    code, numbers = solvable(name, priority)
    if code == 0:
        return str(len(numbers))
    if code == 3:
        return "0"
    return "?"


USAGE = "usage: status.sh [--json] [--scope <name>] [--watch [seconds]] | status.sh --report | status.sh --recover <coord|dev> [--lane <lane>]"


def parse_args(argv):
    """(json, scope, watch seconds or None), or None for an unknown option."""
    scope, as_json, watch = tunables.read("VERI_LABEL"), False, None
    args = list(argv)
    while args:
        arg = args.pop(0)
        if arg == "--watch":
            watch = 2
            if args and re.fullmatch(r"[0-9]+", args[0]):
                watch = int(args.pop(0))
        elif arg == "--json":
            as_json = True
        elif arg == "--scope":
            scope = args.pop(0) if args else ""
        else:
            sys.stderr.write("status.sh: unknown option '%s'\n%s\n" % (arg, USAGE))
            return None
    return as_json, scope, watch


def render(as_json, scope, read_states=True):
    main_tree = main_working_tree()
    runs = sorted(glob.glob(os.path.join(main_tree, ".tdd", "wt", "*", ""))) if main_tree else []
    if not runs:
        print('{"runs": [], "scope": null}' if as_json else "no runs")
        return 3
    events, run_objects, bare = [], [], 0
    states = issue_states() if read_states else {}
    for run in runs:
        run = run.rstrip("/")
        branch = branch_of(run)
        activity = ""
        ledger = ledger_path(run, os.path.basename(run))
        has_ledger = os.path.isfile(ledger)
        text = ""
        if has_ledger:
            try:
                with open(ledger) as f:
                    text = f.read()
            except FileNotFoundError:
                has_ledger = False
        heading = text.split("\n", 1)[0]
        if heading.startswith("# Plan for #"):
            heading = heading[len("# Plan for #"):]
        parts = heading.split(" — ", 1)
        issue, title = parts[0], parts[-1]
        events_path = run_file(run, "events.jsonl")
        has_events = os.path.isfile(events_path)
        if has_events or live_conductor(run):
            try:
                activity = run_activity(run, as_json, states.get(issue) == "closed")
                if has_events:
                    events.append(run)
                else:
                    bare += 1
                if not as_json:
                    activity = "  " + activity
            except (FileNotFoundError, ValueError):
                activity = ""
                if has_events:
                    print("unreadable run %s: %s" % (run, events_path), file=sys.stderr)
        elif has_ledger:
            bare += 1
        if not has_ledger:
            if not activity:
                continue
            issue = os.path.basename(run)
        step = step_of_total(text) if has_ledger else ""
        if as_json:
            run_objects.append(run_object(issue, title, branch, step, activity, states))
            continue
        print("#%s  %s  %s  step %s%s" % (issue, title, branch, step, activity))
    scope_line = None
    if scope:
        scope_line = scope_totals(scope, solvable_count(scope), events, as_json, bare)
    if as_json:
        print('{"runs": [%s], "scope": %s}' % (",".join(run_objects), scope_line or "null"))
    elif scope_line is not None:
        print(scope_line)
    return 0


def json_document(scope=None, read_states=True):
    """(exit code, the --json document) as main(["--json"]) would print it."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = render(True, tunables.read("VERI_LABEL") if scope is None else scope, read_states)
    return code, out.getvalue()


def watch_loop(seconds, as_json, scope):
    while True:
        frame = io.StringIO()
        with contextlib.redirect_stdout(frame):
            render(as_json, scope)
        sys.stdout.write("\033[H\033[2J%s\n" % frame.getvalue().rstrip("\n"))
        sys.stdout.flush()
        time.sleep(seconds)


def read_snapshot():
    with open(os.path.join(main_working_tree(), ".tdd", "report-cache.json")) as f:
        return json.load(f)


def snapshot_time():
    return calendar.timegm(time.strptime(read_snapshot()["fetched_at"], ISO_UTC))


def snapshot_age():
    return time.time() - snapshot_time()


def local_hhmm(epoch):
    return time.strftime("%H:%M", time.localtime(epoch))


def snapshot_line():
    try:
        age = snapshot_age()
    except OSError:
        return "no snapshot"
    minutes = int(age) // 60
    return "snapshot %dh %dm old, fetched %s" % (divmod(minutes, 60) + (local_hhmm(snapshot_time()),))


def eta_range(count):
    walls = []
    for _path, events in journals():
        done = [e for e in events if e.get("event") == "done"]
        if done:
            walls.append(int(done[-1]["awake"]) - int(events[0]["awake"]))
    if len(walls) < 3:
        return "no rate yet"
    low, _mid, high = statistics.quantiles(walls, n=4, method="inclusive")
    return "%s–%s" % tuple("%dh %dm" % divmod(int(w * count) // 60, 60) for w in (low, high))


def opted_in_issues():
    label = tunables.read("VERI_LABEL", "ready-for-agent")
    issues = read_snapshot()["issues"]
    return label, issues, [i for i in issues if i["state"] == "OPEN" and label in [x["name"] for x in i["labels"]]]


def queue_counts():
    try:
        label, issues, opted_in = opted_in_issues()
    except OSError:
        return ""
    state = {i["number"]: i["state"] for i in issues}
    text = "\n%d %s" % (len(opted_in), label)
    last = status_last_queue()
    if label in last:
        text += " %+d" % (len(opted_in) - last[label])
    if opted_in:
        text += "\nETA " + eta_range(len(opted_in))
    for i in opted_in:
        for b in i["blockedBy"]:
            if state.get(b) == "OPEN":
                text += "\n#%d blocked by #%d" % (i["number"], b)
    return text


def status_last_path():
    return os.path.join(main_working_tree(), ".tdd", "status-last")


def status_last():
    try:
        with open(status_last_path()) as f:
            return json.load(f)
    except OSError:
        return None


def status_last_queue():
    return (status_last() or {}).get("queue", {})


def status_last_time():
    last = status_last()
    return None if last is None else calendar.timegm(time.strptime(last["time"], ISO_UTC))


def landed_lines():
    root = main_working_tree()
    since = status_last_time()
    lines = git_tags(root, "%(refname:short)  %(creatordate:format-local:%Y-%m-%d %H:%M)  %(contents:subject)")
    if since is not None:
        cut = tags_created_since(root, since)
        lines = [l for l in lines if l.split()[0] in cut]
    return "\n".join(lines) or "none"


def git_tags(root, fmt):
    return subprocess.run(["git", "-C", root, "tag", "--list", "--format=" + fmt],
                          capture_output=True, text=True).stdout.splitlines()


def tags_created_since(root, since):
    return {l.split()[1] for l in git_tags(root, "%(creatordate:unix) %(refname:short)") if int(l.split()[0]) >= since}


def journals():
    import event
    sample = event.journal_path(main_working_tree(), "0")
    for path in sorted(glob.glob(os.path.join(os.path.dirname(sample), "*.jsonl"))) if sample else []:
        with open(path) as f:
            yield path, [json.loads(l) for l in f if l.strip()]


def run_name(path):
    return "#" + os.path.basename(path)[:-len(".jsonl")]


def conductor_alive(start):
    pid = int(start["pid"])
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return subprocess.run(["ps", "-o", "lstart=", "-p", str(pid)], capture_output=True, text=True).stdout.strip() == start["started"]


def sum_since(events, since, value=lambda e: 1):
    return sum(value(e) for e in events if e["ts"] > since)


def running_lines():
    blocks = []
    since = status_last_time()
    for path, events in journals():
        def of(kind):
            return [e for e in events if e.get("event") == kind]
        starts = of("conductor-start")
        if starts and conductor_alive(starts[-1]):
            name = run_name(path)
            name += " %dm" % ((int(events[-1]["awake"]) - int(events[0]["awake"])) // 60)
            plans = of("plan")
            if plans:
                name += " %d/%s" % (len(of("step-done")), plans[-1]["steps"])
                if since is not None:
                    name += " +%d" % sum_since(of("step-done"), since)
            launches = of("launch")
            if launches:
                phase = launches[-1]["phase"]
                tries = sum(1 for e in launches if e["phase"] == phase)
                name += " %s attempt %d" % (phase, tries)
            verdicts = [e["verdict"] for e in of("verdict")]
            if verdicts:
                name += " PASS %d REJECT %d" % (verdicts.count("PASS"), verdicts.count("REJECT"))
            usage = of("usage")
            dollars = sum(float(e["total_cost_usd"]) for e in usage)
            if dollars:
                name += " | total | $%.2f" % dollars
                if since is not None:
                    name += " +$%.2f" % sum_since(usage, since, lambda e: float(e["total_cost_usd"]))
            models = {}
            for e in launches:
                if "model" in e:
                    models["revise" if e["name"].startswith("revise") else e["actor"]] = e["model"]
            name += "".join(" %s %s" % (r, m) for r, m in models.items())
            passes = of("refactor") + of("structural-pass")
            if passes:
                landed = [int(e.get("transforms", 0)) for e in passes]
                name += " refactor %d passes %d transforms %d landed nothing" % (
                    len(passes), sum(landed), landed.count(0))
                reasons = {}
                for e in passes:
                    if "stopped" in e:
                        reasons[e["stopped"]] = reasons.get(e["stopped"], 0) + 1
                name += "".join(" %s %d" % (r, n) for r, n in reasons.items())
            blocks.append(name)
    return "\n".join(blocks) or "none"


def waiting_lines():
    since = status_last_time() or 0
    lines = []
    for path, events in journals():
        for e in events:
            if e.get("event") == "bail" and e["ts"] > since:
                lines.append("%s %s" % (run_name(path), e["cause"]))
        pr = None
        for e in events:
            if e.get("event") == "done" and "pr" in e:
                pr = e["pr"]
            elif e.get("event") == "merged":
                pr = None
        if pr is not None:
            lines.append("%s PR %s ready to merge" % (run_name(path), pr))
    return "\n".join(lines) or "none"


def unjournaled_notes():
    from pid_file import recorded_alive
    seen = {os.path.basename(p)[:-len(".jsonl")] for p, _ in journals()}
    notes = []
    for wt in sorted(glob.glob(os.path.join(main_working_tree(), ".tdd", "wt", "*"))):
        n = os.path.basename(wt)
        if n not in seen and recorded_alive(wt):
            notes.append("\nNote: #%s is running with no journal" % n)
    return "".join(notes)


def refresh_running():
    pids = subprocess.run(["pgrep", "-f", "report-cache.sh refresh"], capture_output=True, text=True).stdout.split()
    if not pids:
        return False
    own = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "report-cache.sh")
    listing = subprocess.run(["ps", "-p", ",".join(pids), "-o", "pid=,command="], capture_output=True, text=True).stdout
    for m in re.finditer(r"(\S*/report-cache\.sh) refresh", listing):
        if m.group(1) == own:
            return True
    return False


def refresh_if_stale():
    try:
        age = snapshot_age()
    except OSError:
        return
    if age > int(tunables.read("VERI_SNAPSHOT_MAX_AGE", "60")) and not refresh_running():
        script = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "report-cache.sh")
        subprocess.Popen([script, "refresh"], start_new_session=True, stdin=subprocess.DEVNULL,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def zone_line():
    now = time.localtime(time.time())
    since = status_last_time()
    window = "" if since is None else "%s → %s " % (local_hhmm(since), local_hhmm(time.time()))
    minutes = abs(now.tm_gmtoff) // 60 % 60
    offset = "%d%s" % (abs(now.tm_gmtoff) // 3600, ":%02d" % minutes if minutes else "")
    return window + "%s (UTC%s%s)" % (now.tm_zone, "−" if now.tm_gmtoff < 0 else "+", offset)


RECOVER_HEADINGS = ["Runs", "Bailed", "PRs", "Merge lock", "State", "Pending decisions", "Pending messages"]


def recover_runs():
    from pid_file import recorded_alive
    lines = []
    for run in glob.glob(os.path.join(main_working_tree(), ".tdd", "wt", "*")):
        n = os.path.basename(run)
        with open(ledger_path(run, n)) as f:
            heading = f.readline().rstrip("\n")
        title = heading.split(" — ", 1)[-1]
        lines.append("#%s %s %s" % (n, title, recorded_alive(run) or "dead"))
    return lines


def recover_bailed():
    from classify_bail import CATEGORIES
    lines = []
    for path, events in journals():
        if events and events[-1].get("event") == "bail":
            cause = events[-1].get("cause", "")
            lines.append("%s %s" % (run_name(path), CATEGORIES.get(cause, cause)))
    return lines


def recover_prs():
    answer = github.gh_probe("api", "repos/{owner}/{repo}/pulls?state=open")
    if answer.returncode != 0:
        raise OSError("status.sh --recover: GitHub refused the open pull request read: %s" % answer.stderr.strip())
    lines = []
    for pr in json.loads(answer.stdout):
        closes = re.search(r"[Cc]loses #(\d+)", pr["body"] or "")
        state = "draft" if pr["draft"] else "ready"
        single = github.gh_probe("api", "repos/{owner}/{repo}/pulls/%d" % pr["number"])
        if single.returncode != 0:
            raise OSError("status.sh --recover: GitHub refused the single pull request read for #%d: %s"
                          % (pr["number"], single.stderr.strip()))
        try:
            mergeable = json.loads(single.stdout)["mergeable_state"]
        except ValueError:
            raise OSError("status.sh --recover: GitHub returned an unreadable single pull request read for #%d"
                          % pr["number"])
        lines.append("#%d %s %s %s" % (pr["number"], "#" + closes.group(1) if closes else "-", state, mergeable))
    return lines


def recover_lock():
    holder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "merge-lock.sh")
    out = subprocess.run([holder, "holder"], capture_output=True, text=True).stdout.strip()
    if out.startswith("stale"):
        return ["stale"]
    return [out or "free"]


def read_role_state(role, lane=None):
    try:
        with open(state_path(main_working_tree(), role, lane)) as f:
            return f.read().splitlines()
    except FileNotFoundError:
        return []


def recover_items(role, lane, prefix):
    return [line for line in read_role_state(role, lane) if line.startswith(prefix)]


def recover_state(role, lane=None):
    fields = dict(line.partition("=")[::2] for line in read_role_state(role, lane))
    return ["%s %s" % (key, fields[key]) for key in ("n", "lane") if key in fields] + recover_items(
        role, lane, ("timed-n ", "override "))


def recover(role, lane=None):
    if role not in ("coord", "dev"):
        print("usage: status.sh --recover <coord|dev> [--lane <lane>]", file=sys.stderr)
        return 2
    bodies = {"Runs": recover_runs, "Bailed": recover_bailed, "PRs": recover_prs, "Merge lock": recover_lock,
              "State": lambda: recover_state(role, lane),
              "Pending decisions": lambda: recover_items(role, lane, "decision "),
              "Pending messages": lambda: recover_items(role, lane, "message ")}
    try:
        sections = [(heading, bodies[heading]()) for heading in RECOVER_HEADINGS]
    except OSError as refused:
        print(refused, file=sys.stderr)
        return 2
    for heading, lines in sections:
        print(heading)
        print("\n".join(lines) or "none")
    return 0


def main(argv):
    if len(argv) == 2 and argv[0] == "--recover":
        return recover(argv[1])
    if len(argv) == 4 and argv[0] == "--recover" and argv[2] == "--lane":
        return recover(argv[1], argv[3])
    if list(argv) == ["--report"]:
        refresh_if_stale()
        print("%s\nLanded\n%s\n\nRunning\n%s\n\nQueue\n%s%s\n\nWaiting\n%s" % (zone_line(), landed_lines(), running_lines(), snapshot_line(), queue_counts(), waiting_lines()) + unjournaled_notes())
        queue = {}
        try:
            label, _issues, opted_in = opted_in_issues()
            queue[label] = len(opted_in)
        except OSError:
            pass
        os.makedirs(os.path.dirname(status_last_path()), exist_ok=True)
        with open(status_last_path(), "w") as f:
            json.dump({"time": time.strftime(ISO_UTC, time.gmtime()), "queue": queue}, f)
        return 0
    parsed = parse_args(argv)
    if parsed is None:
        return 2
    as_json, scope, watch = parsed
    if watch is not None:
        watch_loop(watch, as_json, scope)
    return render(as_json, scope)


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
