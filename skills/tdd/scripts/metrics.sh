#!/usr/bin/env bash
# metrics.sh — what one issue's run cost, read back out of its event log (ADR-0014:
# observability is a per-run event log written by the scripts, not
# a service).
#
# Usage:   metrics.sh <issue-number>
#
# The writers — event.sh for every conductor and supervisor mark, harvest-usage.sh for a
# leaf's closing accounting — leave `.tdd/events.jsonl` behind and nothing reads it. This is
# the reader. One call prints a markdown report on stdout, which the conductor both commits
# beside the ledger and pastes into the issue thread, so the report is a document rather
# than a screenful of text: a table, no colour, nothing that depends on a terminal.
#
# It reports, for now, the four COUNTS of each phase of the run:
#
#   attempts — `launch` events. supervise.sh writes exactly one per leaf it supervises,
#              outside its retry loop (supervise.sh:297), so a launch IS an attempt.
#   PASS / REJECT — `verdict` events, carrying the word verify.sh parsed out of the
#              verifier's answer (verify.sh:239). Only a verifier writes one.
#   kills    — `exit` events whose `status` is `2`: this codebase's no-answer-could-be-
#              obtained code, which supervise.sh reaches for one reason only — the watchdog
#              giving up on a leaf that never answered (supervise.sh:318). Counted apart
#              from the verdicts because a kill is liveness and a verdict is methodology,
#              the same two axes CLAUDE.md keeps exit 1 and exit 2 on.
#
# The row key is the log's own `phase` field, which event.sh writes on every line
# (event.sh:52), so grouping by it invents nothing: a developer leaf and the verifier that
# judged it share a phase, and that is what makes all four counts meaningful in one row. A
# line with no phase — the conductor's own `step-start` and `step-done` marks — is none of
# the three events counted here and raises no row.
#
# A second section prints the same counts keyed by the log's `step` field instead, plus one
# count the phase section has no column for:
#
#   retries  — `retry` events. supervise.sh writes one per relaunch of a leaf that went
#              quiet, INSIDE its retry loop (supervise.sh:311) where `launch` is written
#              outside it. So retries are neither a second reading of attempts nor of kills:
#              a leaf retried twice and then killed is one attempt, two retries, one kill.
#              It is the liveness budget spent, `VERI_STUCK_RETRIES`, and that is a per-step
#              question — which step cost the watchdog its patience — which is why the
#              column is here and not in the phase section.
#   no-verdict — `relaunch` events carrying `cause=no-verdict`. verify.sh writes one each time
#              a verifier leaf exited cleanly with no VERDICT: line and is launched again:
#              protocol compliance, `VERI_NO_VERDICT_RETRIES`, so neither a
#              retry (liveness) nor a revise (verdict).
#
# Every line carries a step, the conductor's marks included, so the section is keyed by
# something always present; a phase, by contrast, is absent on exactly those marks.
#
# That same per-step section carries the two BUDGETS a step spent, for the same reason
# retries are there: which budget a step ran through is a question about the step. Both are
# printed as one `used/budget` cell, the spelling the house already uses —
# refactor-budget.sh prints `refactor 2/5`, SKILL.md narrates a revise as
# `attempt <k>/<REVISE_BUDGET>` — so a reader sees the pair rather than two numbers to
# divide.
#
#   revise   — `revise` events, one written by the conductor per revise attempt
#              (SKILL.md:875), each carrying the budget that attempt was counted against.
#              Counting the marks is what makes this a reading of the VERDICT axis and not
#              of the liveness one: a leaf relaunched by the watchdog writes `retry`, never
#              `revise`.
#   refactor — the conductor's single `refactor` mark for the step, carrying the transforms
#              applied, the budget, and why the loop stopped. One refactor leaf spends the
#              whole budget of the step (ADR-0017), so the transforms are what that leaf
#              reported applying rather than a count of launches, and there is exactly one
#              such mark per step.
#
# Each budget travels in its own mark rather than being read out of the environment: the
# report is rendered wherever the file is committed, which need not be the shell the run was
# configured in.
#
# A step whose log carries neither mark spent nothing the log recorded, and its cells say
# `unknown` rather than `0` — ADR-0014: a missing conductor mark degrades a figure to
# unknown, never to zero, because `0/3` reads as "this step needed no revise" and that is a
# different claim from "nobody wrote it down".
#
# A third group of columns, in both sections, is TIME — the axis a reader reaches for before
# money, and the one the other three counts are a proxy for:
#
#   wall / API per phase — summed over that phase's attempts. Wall is the `secs`
#              supervise.sh writes on every `exit` (supervise.sh:355), the wall seconds of
#              one attempt; API is `duration_api_ms` off the leaf's own closing record, which
#              harvest-usage.sh copies into the `usage` line (harvest-usage.sh:80) —
#              milliseconds there, seconds here. The two are read off two different lines on
#              purpose: a killed leaf writes an `exit` and no `usage` at all, so a wall
#              figure summed from `usage` would be short by exactly the attempts that went
#              quiet, which are the ones a reader most wants to see.
#   wall per step — the conductor's `step-start` to its `step-done`: the stretch of the run
#              the step OCCUPIED, rather than the sum of what ran inside it. The gap between
#              the two is the conductor's own reading, committing and narrating, which
#              belongs to the step and to no attempt in it. A step whose log is missing
#              either mark says `unknown`, by the rule above.
#   issue wall — printed on a line of its own rather than in either table, because it belongs
#              to no phase and no step: the log's first event to the `done` or `bail` mark
#              that ended the run.
#
# Two more figures belong to no row, and print beside the issue wall for the reason it is
# there: they are of the whole run.
#
#   progress — the steps that reached their `step-done` mark, of the steps the PLAN has. The
#              first is read off the log; the second cannot be, because a run that bailed
#              never reached the steps after the one it died on and their names appear
#              nowhere in it. It is read off the ledger the conductor commits,
#              `.tdd/issue-<n>.md`, counting the checkbox steps in the grammar
#              next-unchecked.sh reads (next-unchecked.sh:16) — ticked or not, since what is
#              wanted is how many were planned. A run with no ledger beside its log says
#              `unknown` for the second number, by the rule above.
#   outcome  — how the run ENDED, off the mark that ended it: a `done` carrying the draft PR,
#              which is what issue success is, or a `bail` carrying the cause and the
#              `system`/`process` classification classify-bail.sh gave it (SKILL.md:949).
#              The two failures are never collapsed, for the reason CLAUDE.md keeps exit 1
#              and exit 2 apart: a system failure is the plumbing breaking and a process one
#              is the methodology speaking, and a reader deciding what to do next needs to
#              know which. A log whose run has not ended says `unknown` rather than either.
#
# A fourth group is COST, in both sections and in a total of its own: the leaf's turns, the
# four token counts and the dollars, all six read off the same `usage` line the API seconds
# come from (harvest-usage.sh:76-84). Four token columns rather than one sum, because they
# are four prices — a cache read costs a tenth of the input it stands in for — and a report
# that added them would hide the figure a reader can act on.
#
# The total is a table of one row rather than a row appended to either section: a run total
# is keyed by neither a phase nor a step, and in the per-step table it would be a step whose
# name happened to be `total`, carrying a bracket and two budgets with nothing true to say.
# It is also the only row the conductor's own spending can land in — that `usage` line
# carries no phase and no step, what the conductor spends belonging to the run rather than
# to any leaf inside it. That line exists only when the conductor ran in print mode, so a
# line beside the issue wall says whether the figures have it or are the leaves alone: the
# same claim the `unknown` cells make, about a figure that has no cell to make it in.
#
# A fifth section is TIME AGAIN, read off a different mark and keyed by neither a phase nor
# a step: the seconds every test-command run recorded, one row per tier.
# timed-test-run.sh writes one `test-run` mark per run of the test command, carrying
# the tier it used, the suites it covered and the wall seconds it took, and this section
# lists those seconds per tier in the order the log carries them — a trend, which is what
# makes "is this run typical" a question a reader can answer by eye.
#
# The figures are the marks own and never the `secs` an `exit` carries: a leaf wall second is
# the whole leaf, reading and writing and thinking included, and what this section is about is
# the test command alone.
#
# The log is read relative to the directory this runs in, `.tdd/events.jsonl`, the way
# event.sh writes it and the way supervise.sh already spells `.tdd/<name>.log` — the issue's
# worktree, in other words, which is where the conductor calls this from.
set -euo pipefail

source "$(cd "$(dirname "$0")" && pwd)/lib/exit-contract.sh"
USAGE="usage: metrics.sh <issue-number>"

require_args 1 "$@"
issue="$1"

log=".tdd/events.jsonl"

ledger=".tdd/issue-$issue.md"

ledger_steps="$(cd "$(dirname "$0")" && pwd)/ledger-steps.sh"

lib="$(cd "$(dirname "$0")" && pwd)/lib"

# hazard: the python block is one single-quoted string, so an apostrophe inside it ends it.
PYTHONPATH="$lib" exec python3 -c '
import os, subprocess, sys
from event_log import read_events

issue, path, ledger, ledger_steps = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]

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
        with open(path) as f:
            records = subprocess.run([ledger_steps], stdin=f, capture_output=True,
                                     text=True).stdout
    except OSError:
        return None
    return counted(len(records.splitlines()))

counts = {}
steps = {}

PHASE_COLUMNS = COUNTS + TIMES + COST_COLUMNS
STEP_COLUMNS = STEP_COUNTS + TIMES + COST_COLUMNS

lost = {}

ROLES = ("developer", "verifier")
by_model = {}

spent = {}

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
        spent.setdefault(step, {})[event] = line
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
        spent.setdefault(step, {})[KIND] = "pin"
    elif event == "verdict" and phase == "pin" and line.get("verdict") == "PASS" and step:
        spent.setdefault(step, {}).setdefault(KIND, "already-satisfied")
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
        per_phase = spent.setdefault(step, {}).setdefault("revise phases", {})
        per_phase[phase] = (per_phase.get(phase, (0, ""))[0] + 1, line.get("budget", ""))
        if phase == "refactor":
            open_pass(step)["revise"] += 1
        continue
    if event == "refactor" and step:
        mark = spent.setdefault(step, {})
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
        spent.setdefault(step, {})[column] = line.get(attribute, "")
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
    return "%s/%s" % (mark["transforms"], mark["budget"])

def step_wall(step):
    mark = spent.get(step, {})
    return known(awake_span_or_wall(mark.get("step-start"), mark.get("step-done")))

def budget_cells(step):
    mark = spent.get(step, {})
    phases = mark.get("revise phases", {})
    if len(phases) > 1:
        revise = ", ".join("%s %d/%s" % (phase, count, budget or "?")
                           for phase, (count, budget) in phases.items())
    elif phases:
        (count, budget), = phases.values()
        revise = "%d/%s" % (count, budget or "?")
    else:
        revise = UNKNOWN
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
if structural is not None and "transforms" not in structural:
    print()
    print("#### Structural pass")
    print()
    print("Stopped: %s" % structural["stopped"])
elif structural is not None:
    table_head("#### Structural pass", "pass", ["refactor", "stopped"], ["---:", "---"])
    row(["issue", refactor_spent(structural), structural["stopped"]])
tier_section("#### Test-command seconds, by tier", "tier")
section("#### Total", "run", COST_COLUMNS, totals)
' "$issue" "$log" "$ledger" "$ledger_steps"
