"""ledger-growth.sh's check, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import re
import subprocess
import sys

import entry
import event
import git
import tunables

from event_log import read_events
from ledger import ADDED_MARK, CRITERION_TAG, STEP_RE, added_file, body, carries_mark, is_added, ledger_steps, open_step_line, read_ledger, replace_ledger

RETIRED = ("VERI_STEP_GROWTH is retired: unset it; VERI_STEP_GROWTH_PERCENT (default 50) caps ⟦added⟧ steps"
           " as a percent of the verified plan's steps")
USAGE = ("usage: ledger-growth.sh <plan-ledger-file> <ledger-file> | plan-sha"
         " | record-existing <ledger-file> | record-rewrite <pre-rewrite-ledger-file> <ledger-file>"
         " | reopen <ledger-file> <needle> <change> | split <ledger-file>")


def step_texts(text):
    steps = []
    for line in text.split("\n"):
        match = STEP_RE.fullmatch(line)
        if match:
            steps.append(body(match.group(4) or ""))
    return steps


def added_steps(ledger):
    try:
        with open(added_file(ledger), "rb") as f:
            return step_texts(f.read().decode(errors="surrogateescape"))
    except FileNotFoundError:
        return []


def recorded_steps(ledger):
    log = os.path.join(os.path.dirname(ledger), "events.jsonl")
    try:
        events = read_events(log, skip_unreadable=True)
    except FileNotFoundError:
        return added_steps(ledger)
    return added_steps(ledger) + [step for event in events
            if event.get("event") == "step-added" and event.get("actor") == "add-ledger-step"
            and isinstance(event.get("step"), str)
            for step in step_texts(event["step"])]


PLAN_BASELINE_RE = re.compile(r"[0-9a-f]+ plan: (scope|rewrite)\b")


def plan_sha(log):
    for line in log.split("\n"):
        if PLAN_BASELINE_RE.match(line):
            return line.split(" ", 1)[0]
    return None


def git_out(directory, *args):
    return subprocess.run(["git", "-C", directory, *args], check=True, stdout=subprocess.PIPE,
                          text=True, errors="surrogateescape").stdout


def record_lines(steps):
    return "".join(open_step_line(step) + "\n" for step in steps).encode(errors="surrogateescape")


def record_existing(ledger):
    added = added_file(ledger)
    if os.path.exists(added):
        print(f"ledger-growth.sh: {os.path.basename(added)} already exists", file=sys.stderr)
        return 2
    directory = os.path.dirname(os.path.abspath(ledger))
    try:
        sha = plan_sha(git_out(directory, "log", "--format=%H %s"))
        if sha is None:
            print("ledger-growth.sh: no plan commit in the ledger's history", file=sys.stderr)
            return 2
        planned = set(step_texts(git_out(directory, "show", f"{sha}:./{os.path.basename(ledger)}")))
        steps = step_texts(read_ledger(ledger))
    except (OSError, subprocess.CalledProcessError) as error:
        print(f"ledger-growth.sh: cannot read {ledger}: {error}", file=sys.stderr)
        return 2
    with open(added, "wb") as f:
        f.write(record_lines(step for step in steps if step not in planned))
    return 0


def record_rewrite(pre, ledger):
    try:
        pre_text, text = read_ledger(pre), read_ledger(ledger)
        before = set(step_texts(pre_text))
        steps = step_texts(text)
        recorded = set(recorded_steps(ledger))
        with open(added_file(ledger), "ab") as f:
            f.write(record_lines(step for step in steps if step not in before
                                 and step not in recorded))
    except OSError as error:
        return unreadable(error)
    record_rewordings(ledger, pre_text, text)
    return 0


def record_rewordings(ledger, pre_text, text):
    """One `step-reworded from=<old> to=<new>` event per ledger position whose step text (as events name a step) the
    rewrite changed, when both ledgers hold the same number of steps; none otherwise, since positions pair only when
    nothing was inserted or removed. Written beside the ledger's `.tdd/`, for the issue its file name carries; a failed
    write is the event call's own stderr line and never changes the exit code."""
    old, new = [step.text for step in ledger_steps(pre_text)], [step.text for step in ledger_steps(text)]
    if len(old) != len(new):
        return
    issue = re.fullmatch(r"issue-(\d+)\.md", os.path.basename(ledger))
    run_context = event.context(tunables.with_values(VERI_ISSUE=issue.group(1)) if issue else tunables.environment())
    run = os.path.dirname(os.path.dirname(os.path.abspath(ledger)))
    for was, now in zip(old, new):
        if was != now:
            event.mark(run, run_context, "step-reworded", ["from=" + was, "to=" + now])


def reopen(ledger, needle, change):
    try:
        lines = read_ledger(ledger).split("\n")
    except OSError as error:
        return unreadable(error)
    hits = [(i, STEP_RE.fullmatch(line)) for i, line in enumerate(lines)
            if STEP_RE.fullmatch(line) and needle in line]
    if not hits:
        print(f"ledger-growth.sh: no step matches: {needle}", file=sys.stderr)
        return 3
    if len(hits) > 1:
        print(f"ledger-growth.sh: needle matches {len(hits)} steps: {needle}", file=sys.stderr)
        for _, match in hits:
            print(f"  {match.group(4)}", file=sys.stderr)
        return 2
    i, match = hits[0]
    step_body = body(match.group(4))
    if not carries_mark(step_body, "skill-edit"):
        print(f"ledger-growth.sh: not a skill-edit step: {step_body}", file=sys.stderr)
        return 2
    if match.group(2) == " ":
        print(f"ledger-growth.sh: step is not ticked: {step_body}", file=sys.stderr)
        return 3
    head, tag, k = step_body.rpartition(" " + CRITERION_TAG)
    head = head.removesuffix(" " + ADDED_MARK)
    step = f"{head} change: {change} {ADDED_MARK}{tag}{k}"
    lines[i] = open_step_line(step)
    replace_ledger(ledger, "\n".join(lines))
    with open(added_file(ledger), "ab") as f:
        f.write(record_lines([step]))
    return 0


def growth_cap(percent, planned):
    """The most ⟦added⟧ steps a ledger may hold: `percent` of the `planned` steps of the verified plan, rounded up."""
    return -(-percent * planned // 100)


def unreadable(error):
    print(f"ledger-growth.sh: {error.filename}: {error.strerror}", file=sys.stderr)
    return 2


SCOPE_RE = re.compile(r"[0-9a-f]+ plan: scope\b")


def counted_steps(text):
    """The ledger's steps that count toward its size: every step line but a ⟦suite-repair⟧, ⟦ci-repair⟧ or ⟦branch-repair⟧ one."""
    return [step for step in ledger_steps(text)
            if not any(carries_mark(step.text, mark) for mark in ("suite-repair", "ci-repair", "branch-repair"))]


def split(ledger):
    """`split <ledger-file>`: the growth of the ledger past ⌈VERI_STEP_GROWTH_PERCENT × P ÷ 100⌉ over P, the steps of
    the ledger at the oldest `plan: scope` commit of its history; exit 0 reporting it, 3 within the bound, 2 (one
    stderr line, nothing on stdout) when no answer can be had."""
    percent = growth_percent()
    if percent is None:
        return 2
    directory, name = os.path.dirname(os.path.abspath(ledger)), os.path.basename(ledger)
    try:
        steps = counted_steps(read_ledger(ledger))
        log = git.out("log", "--format=%H %s", "--", name, cwd=directory)
        scopes = [line.split(" ", 1)[0] for line in log.split("\n") if SCOPE_RE.match(line)]
        if not scopes:
            print(f"ledger-growth.sh: no plan: scope commit in the history of {name}", file=sys.stderr)
            return 2
        planned = len(counted_steps(git.out("show", f"{scopes[-1]}:./{name}", cwd=directory)))
    except OSError as error:
        return unreadable(error)
    except git.GitFailed as error:
        print(f"ledger-growth.sh: {error}: {' '.join(error.stderr.split())}", file=sys.stderr)
        return 2
    bound = growth_cap(int(percent), planned)
    if len(steps) - planned <= bound:
        return 3
    print(f"plan grew from {planned} to {len(steps)} steps, past the growth bound of {bound}"
          f" (VERI_STEP_GROWTH_PERCENT {percent}% of {planned}, rounded up)")
    print(split_point([int(step.criterion) for step in steps if step.criterion]))
    return 0


def split_point(criteria):
    """Where the steps serving `criteria` (one number per tagged counted step) split best: the boundary between two
    consecutive criterion numbers that leaves the two sides' step counts closest, the earlier on a tie."""
    numbers = sorted(set(criteria))
    if not numbers:
        return "no split point: no criterion tag"
    if len(numbers) == 1:
        return f"no split point: every counted step serves criterion {numbers[0]}"
    sides = [(sum(k <= number for k in criteria), i) for i, number in enumerate(numbers[:-1])]
    here, i = min(sides, key=lambda side: (abs(2 * side[0] - len(criteria)), side[1]))
    return (f"split suggested after criterion {numbers[i]}: criteria {numbers[0]}–{numbers[i]} ({here} steps) here,"
            f" criteria {numbers[i + 1]}–{numbers[-1]} ({len(criteria) - here} steps) in a follow-up issue")


def growth_percent():
    """VERI_STEP_GROWTH_PERCENT as given, or None after one stderr line when it is malformed or the retired
    VERI_STEP_GROWTH is set."""
    if tunables.is_set("VERI_STEP_GROWTH"):
        print("ledger-growth.sh: " + RETIRED, file=sys.stderr)
        return None
    percent = tunables.get("VERI_STEP_GROWTH_PERCENT")
    if not tunables.parses("VERI_STEP_GROWTH_PERCENT", percent):
        print(f"ledger-growth.sh: VERI_STEP_GROWTH_PERCENT must be a whole number >= 0: {percent}", file=sys.stderr)
        return None
    return percent


def main(argv):
    if argv[:1] == ["split"]:
        if len(argv) != 2 or not argv[1]:
            print("usage: ledger-growth.sh split <ledger-file>", file=sys.stderr)
            return 2
        return split(argv[1])
    if len(argv) == 2 and argv[0] == "record-existing":
        return record_existing(argv[1])
    if len(argv) == 3 and argv[0] == "record-rewrite":
        return record_rewrite(argv[1], argv[2])
    if len(argv) == 4 and argv[0] == "reopen":
        return reopen(*argv[1:])
    if argv == ["plan-sha"]:
        sha = plan_sha(sys.stdin.read())
        if sha is None:
            print("ledger-growth.sh: no plan commit in the log", file=sys.stderr)
            return 2
        print(sha)
        return 0
    if len(argv) != 2 or not argv[0] or not argv[1]:
        print(USAGE, file=sys.stderr)
        return 2
    try:
        plan_steps = step_texts(read_ledger(argv[0]))
        steps = step_texts(read_ledger(argv[1]))
    except OSError as error:
        return unreadable(error)
    planned = set(plan_steps)
    percent = growth_percent()
    if percent is None:
        return 2
    budget = growth_cap(int(percent), len(plan_steps))
    try:
        recorded = recorded_steps(argv[1])
    except OSError as error:
        return unreadable(error)
    unrecorded_new = [step for step in steps if step not in planned
                      and step not in recorded]
    off = [step for step in unrecorded_new if not is_added(step)]
    for step in off:
        print(f"ledger-growth.sh: step added without ⟦added⟧: {step}", file=sys.stderr)
    unrecorded = [step for step in unrecorded_new if is_added(step)]
    for step in unrecorded:
        print(f"ledger-growth.sh: step added without an add-ledger-step.sh record: {step}", file=sys.stderr)
    over = sum(is_added(step) for step in steps) > budget
    if over:
        print(f"ledger-growth.sh: more than {budget} ⟦added⟧ steps"
              f" (VERI_STEP_GROWTH_PERCENT {percent}% of {len(plan_steps)} planned steps, rounded up)", file=sys.stderr)
    return 1 if off or unrecorded or over else 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
