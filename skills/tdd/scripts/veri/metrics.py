"""metrics.sh's report, rendered in-process."""
import os
import sys

from event_log import read_events
from ledger import ledger_steps

USAGE = "usage: metrics.sh <issue-number>"


COUNTS = ["attempts", "PASS", "REJECT", "kills"]

STEP_COUNTS = COUNTS + ["retries", "no-verdict"]

BUDGETS = ["revise", "refactor", "stopped"]

CROSSED = "crossed at"

SPLIT = "split"

CELL_MARKS = {"step-over-budget": (CROSSED, "spent"), "step-split": (SPLIT, "at")}
MARK_COLUMNS = [column for column, _ in CELL_MARKS.values()]

KIND = "kind"

TIMES = ["wall s", "API s"]
WALL, API = TIMES

COSTS = [("turns", "num_turns"),
         ("input", "input_tokens"),
         ("output", "output_tokens"),
         ("cache read", "cache_read_input_tokens"),
         ("cache creation", "cache_creation_input_tokens"),
         ("$", "total_cost_usd")]
COST_COLUMNS = [heading for heading, _ in COSTS]

DOLLARS = "$"

REWORK_WALL, REWORK_COST = "rework wall s", "rework $"
WASTE_WALL, WASTE_COST = "waste wall s", "waste $"
LOST_COLUMNS = [REWORK_WALL, REWORK_COST, WASTE_WALL, WASTE_COST]

MONEY = {DOLLARS, REWORK_COST, WASTE_COST}

UNKNOWN = "unknown"


def render(issue, path, ledger):
    def known(number):
        return UNKNOWN if number is None else "%d" % number

    def counted(total):
        return total or None

    def span(start, end):
        return None if start is None or end is None else end - start

    def reading(mark, clock):
        if mark is None or (clock == "awake" and not clocked):
            return None
        return mark.get(clock)

    def wall_and_awake_spans(start, end):
        return (span(reading(start, "ts"), reading(end, "ts")),
                span(reading(start, "awake"), reading(end, "awake")))

    def awake_span_or_wall(start, end):
        wall, awake = wall_and_awake_spans(start, end)
        return wall if awake is None or wall < awake else awake

    def planned_steps(path):
        try:
            with open(path, "rb") as f:
                text = f.read().replace(b"\0", b"").decode(errors="surrogateescape")
        except OSError:
            return None
        records = "".join("\t".join(record) + "\n" for record in ledger_steps(text))
        return counted(len(records.encode(errors="surrogateescape").decode().splitlines()))

    counts = {}
    steps = {}

    PHASE_COLUMNS = COUNTS + TIMES + COST_COLUMNS
    STEP_COLUMNS = STEP_COUNTS + TIMES + COST_COLUMNS

    lost = {}

    ROLES = ("developer", "verifier")
    by_model = {}

    spent = {}

    def step_mark(step):
        return spent.setdefault(step, {})

    passes = {}
    open_passes = {}

    def open_pass(step):
        return open_passes.setdefault(step, {"verdict": "", "revise": 0, WALL: 0, DOLLARS: 0.0})

    def settle_pass(step, current):
        if current["verdict"] == "PASS" and current.get("marked"):
            open_passes.pop(step)

    attempts_spent = {}

    rejected = []
    recovered = set()

    tier_runs = {}

    totals = {"total": dict.fromkeys(COST_COLUMNS, 0)}

    conductor_counted = False

    def row_in(table, key, columns):
        return table.setdefault(key, dict.fromkeys(columns, 0))

    def tally(table, key, columns, count):
        row_in(table, key, columns)[count] += 1

    def model_row(line):
        actor = line.get("actor")
        if actor not in ROLES:
            return None
        attempt = (line.get("step", ""), line.get("phase", ""), line.get("attempt", ""), actor)
        return row_in(by_model, (actor, models.get(attempt, "")), PHASE_COLUMNS)

    def rows_for(phase, step, line):
        rows = [r for r in [model_row(line)] if r is not None]
        if phase:
            rows.append(row_in(counts, phase, PHASE_COLUMNS))
        if step:
            rows.append(row_in(steps, step, STEP_COLUMNS))
        return rows

    def add_seconds(phase, step, line, column, seconds):
        for row_of in rows_for(phase, step, line):
            row_of[column] += seconds

    def attempt_in(phase, step, attempt):
        if not phase or not step:
            return None
        return attempts_spent.setdefault((step, phase, attempt), {WALL: 0, DOLLARS: 0.0})

    def add_cost(phase, step, line):
        rows = rows_for(phase, step, line) + [totals["total"]]
        for heading, field in COSTS:
            reported = line.get(field) or 0
            amount = float(reported) if heading in MONEY else int(reported)
            for row_of in rows:
                row_of[heading] += amount

    opening = None

    ending = None

    structural = None

    launched = {}

    marks = read_events(path)
    clocked = bool(marks) and all("awake" in mark for mark in marks)
    models = {(mark.get("step", ""), mark.get("phase", ""), mark.get("attempt", ""), mark.get("actor")):
              mark["model"] for mark in marks if mark.get("event") == "usage" and "model" in mark}

    for line in marks:
        event = line.get("event", "")
        step = line.get("step", "")
        phase = line.get("phase", "")
        ts = line.get("ts")
        if opening is None or event == "resume":
            opening = line
        if event == "resume" and ending is not None and ending.get("event") == "stop":
            ending = None
        if event in ("done", "bail", "stop"):
            ending = line
        if event == "structural-pass":
            structural = line
        if event in ("step-start", "step-done") and step:
            step_mark(step)[event] = line
            if event == "step-done":
                recovered.add(step)
            continue
        if event == "test-run":
            seconds = line.get("seconds")
            if seconds not in (None, ""):
                tier_runs.setdefault(line.get("tier") or UNKNOWN, []).append(str(seconds))
            continue
        if event == "pin" and step:
            recovered.add(step)
            step_mark(step)[KIND] = "pin"
        elif event == "verdict" and phase == "pin" and line.get("verdict") == "PASS" and step:
            step_mark(step).setdefault(KIND, "already-satisfied")
        attempt_no = line.get("attempt", "")
        attempt = attempt_in(phase, step, attempt_no)
        if event == "launch":
            launched[(step, phase, attempt_no)] = line
        if event == "exit":
            awake = span(reading(launched.get((step, phase, attempt_no)), "awake"),
                         reading(line, "awake"))
            seconds = int(awake if awake is not None else (line.get("secs") or 0))
            add_seconds(phase, step, line, "wall s", seconds)
            if attempt is not None:
                attempt[WALL] += seconds
            if phase == "refactor":
                open_pass(step)[WALL] += seconds
        elif event == "usage":
            add_seconds(phase, step, line, "API s",
                        int(line.get("duration_api_ms") or 0) // 1000)
            add_cost(phase, step, line)
            dollars = float(line.get("total_cost_usd") or 0)
            if attempt is not None:
                attempt[DOLLARS] += dollars
            if phase == "refactor":
                open_pass(step)[DOLLARS] += dollars
            if line.get("actor") == "conductor":
                conductor_counted = True
        elif event == "verdict" and line.get("verdict") == "REJECT" and attempt is not None:
            rejected.append((step, phase, attempt))
        if event == "verdict" and phase == "refactor":
            current = open_pass(step)
            current["verdict"] = line.get("verdict", "")
            settle_pass(step, current)
        if event == "revise" and step:
            per_phase = step_mark(step).setdefault("revise phases", {})
            per_phase[phase] = (per_phase.get(phase, (0, ""))[0] + 1, line.get("budget", ""))
            if phase == "refactor":
                open_pass(step)["revise"] += 1
            continue
        if event == "refactor" and step:
            mark = step_mark(step)
            mark["transforms"] = line.get("transforms", "")
            mark["refactor"] = line.get("budget", "")
            mark["stopped"] = line.get("stopped", "")
            current = open_pass(step)
            passes[(step, line.get("pass", ""))] = (line, current)
            current["marked"] = True
            settle_pass(step, current)
            continue
        if event in CELL_MARKS and step:
            column, attribute = CELL_MARKS[event]
            step_mark(step)[column] = line.get(attribute, "")
            continue
        if event == "launch":
            count = "attempts"
        elif event == "verdict" and line.get("verdict") in ("PASS", "REJECT"):
            count = line["verdict"]
        elif event == "exit" and line.get("status") == "2":
            count = "kills"
        elif event == "retry":
            count = "retries"
        elif event == "relaunch" and line.get("cause") == "no-verdict":
            count = "no-verdict"
        else:
            continue
        if phase and count in COUNTS:
            tally(counts, phase, PHASE_COLUMNS, count)
        model = model_row(line) if count in COUNTS else None
        if model is not None:
            model[count] += 1
        if step:
            tally(steps, step, STEP_COLUMNS, count)

    for phase in counts:
        row_in(lost, phase, LOST_COLUMNS)

    def lose(phase, attempt, wall_column, cost_column):
        row_of = row_in(lost, phase, LOST_COLUMNS)
        row_of[wall_column] += attempt[WALL]
        row_of[cost_column] += attempt[DOLLARS]

    for step, phase, attempt in rejected:
        if step in recovered:
            lose(phase, attempt, REWORK_WALL, REWORK_COST)

    for (step, phase, _attempt_no), attempt in attempts_spent.items():
        if step not in recovered:
            lose(phase, attempt, WASTE_WALL, WASTE_COST)

    def row(cells):
        print("| " + " | ".join(cells) + " |")

    def figure(column, value):
        return "%.2f" % value if column in MONEY else "%d" % value

    def refactor_spent(mark):
        return "%s/%s" % (mark["transforms"], mark.get("budget", "?"))

    def step_wall(step):
        mark = spent.get(step, {})
        return known(awake_span_or_wall(mark.get("step-start"), mark.get("step-done")))

    def budget_cells(step):
        mark = spent.get(step, {})
        phases = mark.get("revise phases", {})
        named = len(phases) > 1
        revise = ", ".join(("%s " % phase if named else "") + "%d/%s" % (count, budget or "?")
                           for phase, (count, budget) in phases.items()) or UNKNOWN
        if mark.get("refactor"):
            refactor = "%s/%s" % (mark.get("transforms") or "?", mark["refactor"])
        else:
            refactor = UNKNOWN
        return [revise, refactor, mark.get("stopped") or UNKNOWN]

    def step_cells(step):
        mark = spent.get(step, {})
        return [step_wall(step)] + budget_cells(step) + [mark.get(column, "") for column in MARK_COLUMNS] + [mark.get(KIND, "full")]

    def table_head(heading, key_column, columns, aligns):
        print()
        print(heading)
        print()
        row([key_column] + columns)
        row(["---"] + aligns)

    def section(heading, key_column, columns, table, text=None):
        headings, cells_for = text or ((), None)
        headings = list(headings)
        table_head(heading, key_column, columns + headings,
                   ["---:"] * len(columns) + ["---"] * len(headings))
        for key, row_counts in table.items():
            cells = [key] + [figure(c, row_counts[c]) for c in columns]
            row(cells + (cells_for(key) if cells_for else []))

    def tier_section(heading, key_column):
        width = max([len(runs) for runs in tier_runs.values()] or [0])
        table_head(heading, key_column,
                   ["run %d s" % (i + 1) for i in range(width)], ["---:"] * width)
        for tier, runs in tier_runs.items():
            row([tier] + runs + [""] * (width - len(runs)))

    print("### 📊 Metrics — issue %s" % issue)
    print()
    wall_span, awake_span = wall_and_awake_spans(opening, ending)
    print("Wall time for the issue: %s s, from the last `resume`, or the first event of the log when "
          "there is none, to the mark that ended the run."
          % known(awake_span_or_wall(opening, ending)))
    if awake_span is not None and wall_span is not None:
        print("Seconds the machine was not running inside that span: %s s, excluded from it."
              % max(0, wall_span - awake_span))
    if not clocked:
        print("Every figure in this report is wall-clock: the log carries no awake-clock reading, "
              "so time the machine spent asleep is counted in them.")
    planned = planned_steps(ledger)
    print("Steps done: %s of %s planned."
          % (known(counted(len(recovered))), known(planned)))
    if ending is None:
        print("Outcome: %s — the log carries no mark ending the run." % UNKNOWN)
    elif ending.get("event") == "done":
        print("Outcome: the run landed — its draft PR is %s."
              % (ending.get("pr") or UNKNOWN))
    elif ending.get("event") == "stop":
        print("Outcome: the run was stopped — mode %s, at %s."
              % (ending.get("mode") or UNKNOWN, ending.get("at") or UNKNOWN))
    else:
        print("Outcome: the run bailed — %s, a %s failure."
              % (ending.get("cause") or UNKNOWN, ending.get("classification") or UNKNOWN))
    print("Cost is every leaf of the run, and the conductor own %s."
          % ("closing accounting with them, which this log carries"
             if conductor_counted else
             "spending is not in it: this log carries no usage record of the conductor own"))
    if models:
        print("Models requested: %s; models that answered: %s."
              % (", ".join("%s %s" % (knob, os.environ.get(knob) or "unset")
                           for knob in ["VERI_MODEL", "VERI_MODEL_DEVELOPER", "VERI_MODEL_VERIFIER"]),
                 ", ".join(sorted({m for answered in models.values() for m in answered.split(",") if m}))))
    section("#### By phase", "phase", PHASE_COLUMNS, counts)
    if models or any(mark.get("event") == "launch" and "model" in mark for mark in marks):
        table_head("#### By model", "role", ["model"] + PHASE_COLUMNS, ["---"] + ["---:"] * len(PHASE_COLUMNS))
        for (role, model), row_counts in by_model.items():
            row([role, model or "not recorded"] + [figure(c, row_counts[c]) for c in PHASE_COLUMNS])
    section("#### Rework and waste, by phase", "phase", LOST_COLUMNS, lost)
    section("#### By step", "step", STEP_COUNTS + [API] + COST_COLUMNS, steps,
            ([WALL] + BUDGETS + MARK_COLUMNS + [KIND], step_cells))
    print()
    print("The figure comparable across runs is turns, the same measurement on any model; dollars "
          "are not comparable, the same measurement only at the same VERI_MODEL, "
          "VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.")
    if passes:
        table_head("#### By refactor pass", "step", ["pass", "refactor", "stopped", "verdict", "revise", WALL, DOLLARS],
                   ["---:", "---:", "---", "---", "---:", "---:", "---:"])
        for (step, index), (mark, spent_by) in passes.items():
            row([step, index, refactor_spent(mark), mark["stopped"],
                 spent_by["verdict"], str(spent_by["revise"]), figure(WALL, spent_by[WALL]), figure(DOLLARS, spent_by[DOLLARS])])
    if structural is None and ending is not None and ending.get("event") == "done":
        structural = {"stopped": "not marked"}
    if structural is not None:
        stopped = structural.get("stopped", "?")
        if "transforms" not in structural:
            print()
            print("#### Structural pass")
            print()
            print("Stopped: %s" % stopped)
        else:
            table_head("#### Structural pass", "pass", ["refactor", "stopped"], ["---:", "---"])
            row(["issue", refactor_spent(structural), stopped])
        inconsistent = None
        if "stopped" not in structural:
            inconsistent = "the mark carries no stopped"
        elif "transforms" in structural:
            if "budget" not in structural:
                inconsistent = "transforms=%s without a budget" % structural["transforms"]
            elif structural["stopped"] == "budget-spent" and int(structural["transforms"]) < int(structural["budget"]):
                inconsistent = ("stopped=budget-spent, but transforms=%s is below budget=%s"
                                % (structural["transforms"], structural["budget"]))
            elif structural["stopped"] not in ("candidates-done", "budget-spent", "nothing-structural"):
                inconsistent = ("stopped=%s is not one of candidates-done, budget-spent, nothing-structural"
                                % structural["stopped"])
        if inconsistent is not None:
            print()
            print("Inconsistent mark: %s" % inconsistent)
    tier_section("#### Test-command seconds, by tier", "tier")
    section("#### Total", "run", COST_COLUMNS, totals)


def main(argv):
    if not argv or not argv[0]:
        sys.stderr.write(USAGE + "\n")
        return 2
    issue = argv[0]
    render(issue, ".tdd/events.jsonl", ".tdd/issue-%s.md" % issue)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
