"""status.sh's computations, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import calendar
import contextlib
import glob
import io
import json
import os
import re
import subprocess
import sys
import time

import decision_log
import event_log
import github
import markdown_sections
import paths
import pid_file
import role_state
import run_dir
import run_end
import stack_branch
import stack_green
import tunables
from event import journals, run_name
from event_log import read_events, usage_totals
from ledger import ledger_steps
from pid_file import conductor_alive, live_conductor
from run_activity import activity
from solvable_issues import priority_label, solvable

ISO_UTC = "%Y-%m-%dT%H:%M:%SZ"


def run_activity(run, as_json=False, closed=False):
    """The activity line for one run."""
    a = activity(run, closed)
    if as_json:
        return json.dumps({"phase": a.phase, "actor": a.actor, "leaf": a.leaf, "elapsed_seconds": a.elapsed_seconds,
                           "attempts": a.attempts, "dollars": round(a.dollars, 2), "tokens": a.tokens,
                           "state": a.state, "pr": a.pr, "bail_phase": a.bail_phase,
                           "classification": a.classification, "stop_mode": a.stop_mode, "cause": a.cause})
    return "%s  %s  %s %ds  attempt %d  $%.2f  %d tokens  %s" % (a.phase, a.actor, a.leaf, a.elapsed_seconds,
           a.attempts, a.dollars, a.tokens, a.detail)


def scope_totals(name, solvable, runs, as_json=False, bare=0):
    """The scope totals line over every run's events."""
    attempted, done, bailed, wall = bare, 0, 0, 0
    dollars = 0.0
    for run in runs:
        try:
            events = read_events(event_log.path(run))
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


def step_of_total(text):
    """"<n> of <m>": the step pending refactor, else the first open step of the ledger's <m>, or <m> when none is open."""
    records = ledger_steps(text)
    total = records[-1].number if records else "0"
    step = next((r.number for r in records if r.pending == "1"), None) \
        or next((r.number for r in records if r.state == "open" and r.kind != "human-owed"), total)
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


USAGE = "usage: status.sh [--json] [--scope <name>] [--watch [seconds]] | status.sh --report | status.sh --recover dev [--lane <lane>]"


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


def render(as_json, scope, read_states=True, stack=False):
    """Print every run (and, with <stack> and <as_json>, the stack's figures under a `stack` key where a stack is
    named); the exit code."""
    main_tree = run_dir.main_tree(missing="")
    member = stack_member(main_tree) if stack and as_json else ""
    runs = sorted(glob.glob(os.path.join(run_dir.worktrees(main_tree), "*", ""))) if main_tree else []
    if not runs:
        print('{"runs": [], "scope": null%s}' % member if as_json else "no runs")
        return 3
    events, run_objects, bare = [], [], 0
    states = issue_states() if read_states else {}
    for run in runs:
        run = run.rstrip("/")
        branch = branch_of(run)
        activity = ""
        ledger = run_dir.ledger(run, os.path.basename(run))
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
        has_events = os.path.isfile(event_log.path(run))
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
                    print("unreadable run %s: %s" % (run, event_log.path(run)), file=sys.stderr)
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
        print('{"runs": [%s], "scope": %s%s}' % (",".join(run_objects), scope_line or "null", member))
    elif scope_line is not None:
        print(scope_line)
    return 0


def stack_member(root):
    """`, "stack": {...}`, the stack's figures as --json carries them, every one null when the stack could not be read
    (the reason on stderr); "" where no stack is named."""
    try:
        span = stack_span(root)
    except stack_branch.Refused as refused:
        print("status.sh: the stack could not be read: %s" % refused, file=sys.stderr)
        return ', "stack": ' + json.dumps(stack_figures(root, None))
    return ', "stack": ' + json.dumps(stack_figures(root, span)) if span else ""


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
    with open(run_dir.main_file(run_dir.main_tree(missing=""), "report-cache.json")) as f:
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
    import statistics
    low, _mid, high = statistics.quantiles(walls, n=4, method="inclusive")
    return "%s–%s" % tuple("%dh %dm" % divmod(int(w * count) // 60, 60) for w in (low, high))


def opted_in_issues():
    label = tunables.get("VERI_LABEL")
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
    return run_dir.main_file(run_dir.main_tree(missing=""), "status-last")


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
    root = run_dir.main_tree(missing="")
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


def sum_since(events, since, value=lambda e: 1):
    return sum(value(e) for e in events if e["ts"] > since)


def running_lines():
    blocks = []
    since = status_last_time()
    for path, events in journals():
        def of(kind, events=events):
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


def main_subjects(ref="main"):
    return subject_log(ref).stdout.splitlines()


def subject_log(ref):
    """`git log <ref> --format=%s` in the main tree, as the CompletedProcess."""
    return subprocess.run(["git", "-C", run_dir.main_tree(missing=""), "log", ref, "--format=%s"],
                          capture_output=True, text=True)


SLICE_WINDOW = 24 * 3600  # the landed count's window: slices merged in the last 24 hours


def stack_script(root, name):
    """(exit code, stdout) of the sibling script <name> run in <root>, bounded by VERI_GIT_NETWORK_TIMEOUT (exit 2
    when it is killed there); its stderr is passed on when it exits 2, so a figure it leaves unread says why."""
    ran = github.bounded_group([os.path.join(paths.SCRIPTS, name)], limit_name="VERI_GIT_NETWORK_TIMEOUT", cwd=root,
                               stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    code = 2 if isinstance(ran, github.TimedOut) else ran.returncode
    if code == 2:
        sys.stderr.write(ran.stderr or "status.sh: %s gave no answer\n" % name)
    return code, ran.stdout or ""


def tracking_pull(stack, default):
    """The url of the one open pull request from <stack> to <default>, None when none is open; github.NoAnswer when
    GitHub gave none or two or more are open. Read only: unlike stack-pr.sh, it never opens one."""
    pulls = github.stack_pulls(stack, default)
    if len(pulls) > 1:
        raise github.NoAnswer("", "%d open pull requests track %s" % (len(pulls), stack))
    return pulls[0].html_url if pulls else None


def landed_slices(stack, default, since):
    """The issue numbers (strings) named by `Closes #<n>` in the slice pull requests (head `<stack>-slice-*`, in this
    repository) merged into <default> at or after epoch <since>: the closed pull requests onto <default>, newest
    updated first, read 100 to a page until a page ends updated before <since> (a merge updates its pull request, so
    none after it merged later), at most github.PULL_PAGES pages. github.NoAnswer for a failed read, an answer not a
    list of pull requests, or pages past the bound."""
    found = set()
    for page in range(1, github.PULL_PAGES + 1):
        run = github.gh_api("repos/{owner}/{repo}/pulls?state=closed&base=%s&sort=updated&direction=desc"
                            "&per_page=100&page=%d" % (default, page), stderr=subprocess.PIPE)
        if run.returncode:
            raise github.NoAnswer("", "reading the slices merged into %s: %s" % (
                default, " ".join((run.stderr or "").split())[:200] or "exit %d" % run.returncode))
        try:
            items = json.loads(run.stdout or "")
        except ValueError:
            items = None
        if not isinstance(items, list) or not all(isinstance(raw, dict) for raw in items):
            raise github.NoAnswer("", "the slices merged into %s: the answer is not a list of pull requests" % default)
        found.update(n for raw in items if landed_slice(raw, stack, default, since)
                     for n in github.closed_issues(raw.get("body") or ""))
        if len(items) < 100 or (items and epoch_of(items[-1].get("updated_at"), since) < since):
            return found
    raise github.NoAnswer("", "the slices merged into %s ran past %d pages of 100" % (default, github.PULL_PAGES))


FIGURES = ("branch", "joined", "tested", "landed", "tracking_pr", "frozen")


def stack_figures(root, span):
    """The stack's figures for <span> (stack_span's answer, None when the stack could not be read), keyed by FIGURES:
    None for a figure that could not be read; tracking_pr the open tracking pull request's url, False when none is
    open; frozen {sha, run_url} when stack-red.sh exits 0, False when it exits 3."""
    if span is None:
        return dict.fromkeys(FIGURES)
    stack, default, commits = span
    issues = [stack_green.named(subject) for _, subject in commits]
    code, said = stack_script(root, "stack-green.sh")
    shas = [sha for sha, _ in commits]
    cut = said.split()[0] if code == 0 and said.split() else None
    figures = {"branch": stack, "joined": len(set().union(*issues)),
               "tested": 0 if code == 3 else len(set().union(*issues[:shas.index(cut) + 1])) if cut in shas else None}
    try:
        figures["landed"] = len(landed_slices(stack, default, time.time() - SLICE_WINDOW))
    except (github.NoAnswer, ValueError) as no:
        figures["landed"] = unread_figure("landed", no)
    try:
        figures["tracking_pr"] = tracking_pull(stack, default) or False
    except github.NoAnswer as no:
        figures["tracking_pr"] = unread_figure("tracking", no)
    code, said = stack_script(root, "stack-red.sh")
    red = said.split()
    figures["frozen"] = {"sha": red[0], "run_url": red[1]} if code == 0 and len(red) > 1 else False if code == 3 else None
    return figures


def landed_slice(raw, stack, default, since):
    """Whether pull request record <raw> is a slice of <stack> (head `<stack>-slice-*` in the base repository) merged
    into <default> at or after epoch <since>."""
    head, base = raw.get("head") or {}, raw.get("base") or {}
    if not (isinstance(head, dict) and isinstance(base, dict)):
        return False
    return (base.get("ref") == default and str(head.get("ref") or "").startswith(stack + "-slice-")
            and ((head.get("repo") or {}).get("full_name") or None) == ((base.get("repo") or {}).get("full_name") or 0)
            and epoch_of(raw.get("merged_at"), since - 1) >= since)


def epoch_of(stamp, otherwise):
    """The epoch of GitHub's UTC time <stamp>, <otherwise> when it is not a string."""
    return calendar.timegm(time.strptime(stamp, ISO_UTC)) if isinstance(stamp, str) else otherwise


def stack_lines(figures):
    """The Stack section's lines for <figures> (stack_figures' answer): a figure that could not be read prints `?`,
    never 0."""
    lines = ["%s: joined %s, tested %s, landed %s in 24h" % tuple(shown(figures[key]) for key in FIGURES[:4])]
    if figures["tracking_pr"] is not False:
        lines.append("tracking: " + shown(figures["tracking_pr"]))
    if figures["frozen"] is not False:
        lines.append("frozen: " + ("?" if figures["frozen"] is None else "%(sha)s %(run_url)s" % figures["frozen"]))
    return lines


def shown(figure):
    """A stack figure as the report prints it: `?` for one that could not be read (None)."""
    return "?" if figure is None else str(figure)


def unread_figure(what, no):
    """None, the stack figure <what> that could not be read, said on stderr with GitHub's reason (<no>)."""
    detail = no.detail or no.answer if isinstance(no, github.NoAnswer) else str(no)
    print("status.sh: the stack's %s figure could not be read: %s" % (what, " ".join(str(detail).split())[:200]),
          file=sys.stderr)
    return None


def stack_absent(stack):
    """Whether origin holds no branch <stack> as the main tree last fetched it: `git rev-parse --verify` of its
    remote-tracking ref says it is absent (exit 1), not that it could not be read."""
    return subprocess.run(["git", "-C", run_dir.main_tree(missing=""), "rev-parse", "--verify", "--quiet",
                           "refs/remotes/origin/" + stack], capture_output=True, text=True).returncode == 1


def stack_span(root):
    """stack_branch.ahead(<root>): (stack, default, commits of origin/<default>..origin/<stack>), None when <root> is
    no main tree or its CLAUDE.md names no stack; stack_branch.Refused when the stack cannot be read."""
    return stack_branch.ahead(root) if root else None


def waiting_lines(stack=None, unread=None):
    """Waiting: the bails since status-last, each run whose done pull request has no `(#n)` subject on local main nor,
    with <stack> named, on origin/<stack> (a joined run is not waiting for a merge), and the decisions since. Where the
    stack's subjects could not be read (<unread> says why, or its git log fails), such a run is listed as merge state
    unknown, never as ready to merge and never left out."""
    since = status_last_time() or 0
    lines = []
    subjects = main_subjects()
    if stack and unread is None:
        log = subject_log("origin/" + stack)
        if log.returncode and not stack_absent(stack):
            unread = "git log origin/%s failed (exit %d)" % (stack, log.returncode)
        subjects += log.stdout.splitlines()
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
        name = run_name(path)
        numbers = {name, "#" + str(pr).rsplit("/", 1)[-1]}
        if pr is not None and not any(t.endswith("(%s)" % n) for t in subjects for n in numbers):
            lines.append("%s PR %s merge state unknown: %s" % (name, pr, unread) if unread
                         else "%s PR %s ready to merge" % (name, pr))
    for record in decision_log.read(run_dir.main_tree(missing="")):
        if decision_log.epoch(record) >= since:
            shown = {key: printed_field(record[key]) for key in ("question", "decision", "rule")}
            lines.append(("owner decided" if record["by"] == "owner" else "decided")
                         + ": %(question)s → %(decision)s (rule: %(rule)s)" % shown)
    return "\n".join(lines) or "none"


PRINTED_FIELD_MAX = 300


def printed_field(text):
    """A decision log field as the report prints it: each character that does not print (a newline, an escape) written
    as its Python escape, so a record stays one line and draws nothing; cut at PRINTED_FIELD_MAX, the cut shown by …."""
    text = "".join(c if c.isprintable() else repr(c)[1:-1] for c in text)
    return text if len(text) <= PRINTED_FIELD_MAX else text[:PRINTED_FIELD_MAX] + "…"


def unjournaled_notes():
    from pid_file import recorded_alive
    seen = {os.path.basename(p)[:-len(".jsonl")] for p, _ in journals()}
    notes = []
    for wt in sorted(glob.glob(os.path.join(run_dir.worktrees(run_dir.main_tree(missing="")), "*"))):
        n = os.path.basename(wt)
        if n not in seen and recorded_alive(wt):
            notes.append("\nNote: #%s is running with no journal" % n)
    return "".join(notes)


def refresh_running():
    pids = pid_file.pids_matching("report-cache.sh refresh")
    if not pids:
        return False
    own = os.path.join(paths.resolved_scripts_of(__file__), "report-cache.sh")
    listing = pid_file.commands_of(pids)
    for m in re.finditer(r"(\S*/report-cache\.sh) refresh", listing):
        if m.group(1) == own:
            return True
    return False


def refresh_if_stale():
    try:
        age = snapshot_age()
    except OSError:
        return
    if age > int(tunables.get("VERI_SNAPSHOT_MAX_AGE")) and not refresh_running():
        script = os.path.join(paths.resolved_scripts_of(__file__), "report-cache.sh")
        subprocess.Popen([script, "refresh"], start_new_session=True, stdin=subprocess.DEVNULL,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def zone_line():
    now = time.localtime(time.time())
    since = status_last_time()
    window = "" if since is None else "%s → %s " % (local_hhmm(since), local_hhmm(time.time()))
    minutes = abs(now.tm_gmtoff) // 60 % 60
    offset = "%d%s" % (abs(now.tm_gmtoff) // 3600, ":%02d" % minutes if minutes else "")
    return window + "%s (UTC%s%s)" % (now.tm_zone, "−" if now.tm_gmtoff < 0 else "+", offset)


RECOVER_HEADINGS = ["Runs", "Bailed", "PRs", "Merge lock", "State", "Pending decisions", "Pending messages", "Questions",
                    "Unasked questions", "Answered questions"]


def recover_runs():
    from pid_file import recorded_alive
    lines = []
    for run in glob.glob(os.path.join(run_dir.worktrees(run_dir.main_tree(missing="")), "*")):
        n = os.path.basename(run)
        try:
            with open(run_dir.ledger(run, n)) as f:
                heading = f.readline().rstrip("\n")
        except FileNotFoundError:
            continue
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


def refused_read_check(answer, what):
    if answer.returncode != 0:
        raise OSError("status.sh --recover: GitHub refused the %s: %s" % (what, answer.stderr.strip()))


def recover_prs():
    answer = github.gh_probe("api", "repos/{owner}/{repo}/pulls?state=open")
    refused_read_check(answer, "open pull request read")
    lines = []
    for pr in json.loads(answer.stdout):
        closes = github.closed_issues(pr["body"], loose=True)
        state = "draft" if pr["draft"] else "ready"
        single = github.gh_probe("api", "repos/{owner}/{repo}/pulls/%d" % pr["number"])
        refused_read_check(single, "single pull request read for #%d" % pr["number"])
        try:
            mergeable = json.loads(single.stdout)["mergeable_state"] or "unknown"
        except (ValueError, KeyError) as error:
            raise OSError("status.sh --recover: GitHub returned an unreadable single pull request read for #%d"
                          % pr["number"]) from error
        lines.append("#%d %s %s %s" % (pr["number"], "#" + closes[0] if closes else "-", state, mergeable))
    return lines


def recover_lock():
    holder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "merge-lock.sh")
    out = subprocess.run([holder, "holder"], capture_output=True, text=True).stdout.strip()
    if out.startswith("stale"):
        return ["stale"]
    return [out or "free"]


def recover_items(role, lane, *kinds):
    return role_state.State(role_state.read_lines(role, lane) or []).items(*kinds)


def recover_state(role, lane=None):
    lines = role_state.read_lines(role, lane)
    if lines is None:
        return ["no state file"]
    state = role_state.State(lines)
    return ["%s %s" % (key, state.field(key)) for key in ("n", "lane", "auto") if state.field(key) is not None] + state.items(
        "timed-n", "override")


ASKED_LINE = re.compile(r"## Asked \S+")


def question_state(path):
    """Which recovery section lists the question file <path>: "Answered questions" when it has an `## Answer` line,
    else "Questions" when it has an `## Asked <session-id>` line (asked, open) or cannot be read, else "Unasked
    questions" (written, never asked). The file is read once, and a line inside a code fence is no heading
    (`markdown_sections.unfenced`, the rule record-answer.sh reads the file by)."""
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            text = f.read()
    except OSError:
        return "Questions"
    lines = [line.rstrip() for _, line in markdown_sections.unfenced(text)]
    if "## Answer" in lines:
        return "Answered questions"
    return "Questions" if any(ASKED_LINE.fullmatch(line) for line in lines) else "Unasked questions"


QUESTION_SECTIONS = ("Questions", "Unasked questions", "Answered questions")


def recover_questions(lane):
    """{section: paths}: the lane's question files sorted into recovery's three question sections, each file judged
    once by `question_state`, so it is in exactly one: each regular `.tdd/questions/<lane>-*.md` (`main-*` with no
    lane), by its `.tdd/questions/<name>` path, sorted by name. One bad entry never stops recovery: a directory or
    dangling link is skipped, and a file that cannot be read is listed under Questions."""
    directory = os.path.join(run_dir.main_tree(missing=""), ".tdd", "questions")
    sections = {section: [] for section in QUESTION_SECTIONS}
    for path in sorted(glob.glob(os.path.join(directory, "%s-*.md" % (lane or "main")))):
        if os.path.isfile(path):
            sections[question_state(path)].append(os.path.join(".tdd", "questions", os.path.basename(path)))
    return sections


def recover(role, lane=None):
    if role != "dev":
        print("usage: status.sh --recover dev [--lane <lane>]", file=sys.stderr)
        return 2
    questions = recover_questions(lane)
    bodies = {"Runs": recover_runs, "Bailed": recover_bailed, "PRs": recover_prs, "Merge lock": recover_lock,
              "State": lambda: recover_state(role, lane),
              "Pending decisions": lambda: recover_items(role, lane, "decision"),
              "Pending messages": lambda: recover_items(role, lane, "message"),
              **{section: lambda section=section: questions[section] for section in QUESTION_SECTIONS}}
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
        # The window's next start is taken before the decision log is read, and written floored to the second, which
        # the decisions are compared against with >=: one recorded at a boundary may be listed twice, never zero times.
        read_at = time.time()
        span, unread = None, None
        try:
            span = stack_span(run_dir.main_tree(missing=""))
        except stack_branch.Refused as refused:
            unread = "the stack could not be read: %s" % refused
        try:
            waiting = waiting_lines(span[0] if span else None, unread)
        except decision_log.Malformed as bad:
            print("status.sh: %s is not a decision record" % bad.where, file=sys.stderr)
            return 2
        except decision_log.Unreadable as bad:
            print("status.sh: cannot read the decision log %s: %s" % (bad.path, bad.reason), file=sys.stderr)
            return 2
        if unread:
            print("status.sh: " + unread, file=sys.stderr)
        stack = "\n\nStack\n" + "\n".join(stack_lines(stack_figures(run_dir.main_tree(missing=""), span))) if span or unread else ""
        print("%s\nLanded\n%s%s\n\nRunning\n%s\n\nQueue\n%s%s\n\nWaiting\n%s" % (zone_line(), landed_lines(), stack, running_lines(), snapshot_line(), queue_counts(), waiting) + unjournaled_notes())
        queue = {}
        try:
            label, _issues, opted_in = opted_in_issues()
            queue[label] = len(opted_in)
        except OSError:
            pass
        os.makedirs(os.path.dirname(status_last_path()), exist_ok=True)
        with open(status_last_path(), "w") as f:
            json.dump({"time": time.strftime(ISO_UTC, time.gmtime(read_at)), "queue": queue}, f)
        return 0
    parsed = parse_args(argv)
    if parsed is None:
        return 2
    as_json, scope, watch = parsed
    if watch is not None:
        watch_loop(watch, as_json, scope)
    return render(as_json, scope, stack=True)


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
