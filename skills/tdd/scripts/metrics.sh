#!/usr/bin/env bash
# metrics.sh — what one issue's run cost, read back out of its event log (issue #108, and
# #107/ADR-0014 before it: observability is a per-run event log written by the scripts, not
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
# The log is read relative to the directory this runs in, `.tdd/events.jsonl`, the way
# event.sh writes it and the way supervise.sh already spells `.tdd/<name>.log` — the issue's
# worktree, in other words, which is where the conductor calls this from.
set -euo pipefail

# `${1:?msg}` expands $1, but aborts the shell with msg on stderr if it is unset or empty.
# The number is what the report is ABOUT: it names the file the conductor commits and the
# issue the thread belongs to, so a call that omits it has not said which run it means.
issue="${1:?usage: metrics.sh <issue-number>}"

log=".tdd/events.jsonl"

# Note the apostrophe nobody may write inside the block below: it is a single-quoted shell
# string, so a `run's` in a comment or a docstring ends the program there and python is
# handed the rest as argv. The same trap event.sh and harvest-usage.sh carry.
exec python3 -c '
import json, sys

issue, path = sys.argv[1], sys.argv[2]

# The four counts, in the order the table prints them, each with the column heading it is
# printed under. One list so the headings and the arithmetic cannot come to disagree about
# how many columns there are.
COUNTS = ["attempts", "PASS", "REJECT", "kills"]

# The per-step section prints those four and retries, in that order, for the reason in the
# header: retries answer a per-step question. Written as an extension of COUNTS rather than
# as a list of its own, so the two sections cannot come to disagree about what a kill is.
STEP_COUNTS = COUNTS + ["retries"]

# The per-step section closes with three columns that are not counts but text: the two
# `used/budget` pairs and the reason the refactor loop stopped. They are listed apart from
# STEP_COUNTS because they are tallied from a different shape of line — one mark carrying
# the numbers, rather than one line per unit counted — and rendered with a different
# alignment.
BUDGETS = ["revise", "refactor", "stopped"]

# The two time columns, printed in both sections, in this order. The heading carries the
# unit so the cell stays a bare number a reader can compare down the column. The wall column
# is named apart because it is the one cell the two sections read differently: a phase is
# summed over its attempts, so its row already carries the figure, where a step is bracketed
# by the conductor two marks and has to be read off them.
TIMES = ["wall s", "API s"]
WALL, API = TIMES

# What a row COST, in both sections and in the total: the leaf turns, the four token counts
# the stream record keeps apart, and the dollars. Each column heading travels paired with
# the field harvest-usage.sh copies onto the `usage` line (harvest-usage.sh:76-84), so the
# heading a reader sees and the number it is read off are written once, together, and cannot
# come apart. The four token counts are four columns rather than one sum because they are
# four prices: a cache read is an order of magnitude cheaper than the input it stands in
# for, and a report that added them would hide the one figure a reader can act on.
COSTS = [("turns", "num_turns"),
         ("input", "input_tokens"),
         ("output", "output_tokens"),
         ("cache read", "cache_read_input_tokens"),
         ("cache creation", "cache_creation_input_tokens"),
         ("$", "total_cost_usd")]
COST_COLUMNS = [heading for heading, _ in COSTS]

# The one cost column that is money rather than a count, so the one printed to the cent and
# summed as a float. Named once here because the renderer and the adder both ask.
DOLLARS = "$"

# The two figures the glossary keeps apart from what a row simply spent: what the run PAID
# and did not keep. Each is a pair of columns rather than one, because a reader asking how
# much a phase threw away asks it of the clock and of the bill, and one figure cannot answer
# both.
#
#   rework — what the REJECTed attempts of a step that then RECOVERED cost. A step recovered
#            when it reached its `step-done` mark, however many revises it took, so the
#            attempts the run kept are not in it: the rework of a phase is the attempts a
#            verifier turned down and nothing else.
#   waste  — what a BAILED step spent, PASS verdicts included. A step that recovered
#            contributes nothing to it, which is the half of the pair this column is here to
#            make observable: a report without it could not tell rework from everything.
#
# They are a SECTION of their own rather than four more columns of the phase section, and
# both halves of that are load-bearing. They are not what a phase spent — they are the part
# of it the run did not keep, a figure no line of the log carries and no other column of that
# row is summed the same way — so a reader comparing a phase own bill down the `$` column
# would be comparing it against two other columns of money that are subsets of it. Keeping
# them apart is what leaves each table with exactly one column answering "what did this
# cost", which is what makes either readable at all.
REWORK_WALL, REWORK_COST = "rework wall s", "rework $"
WASTE_WALL, WASTE_COST = "waste wall s", "waste $"
LOST_COLUMNS = [REWORK_WALL, REWORK_COST, WASTE_WALL, WASTE_COST]

# The columns that are money rather than a count of things, so the ones printed to the cent
# and summed as floats. Named as a set because there are now three of them and the renderer
# and the adders each ask.
MONEY = {DOLLARS, REWORK_COST, WASTE_COST}

# What a figure says when no mark in the log supplies it. Not "0": see the header.
UNKNOWN = "unknown"

# Row order in either section is the order its key first appears in the log, which is the
# order the run went through them — red before green before refactor, step one before step
# two. Sorting the names instead would print the run backwards for no reason a reader could
# act on, and would sort a step by the wording of its criterion. A dict preserves the order
# its keys were first inserted in, so each of these IS that order and no second list is kept
# beside it that could come to disagree with it.
counts = {}
steps = {}

# The columns a row of either section carries: its counts and its seconds in one row, rather
# than a second table on the same key kept beside the first — the same reason `spent` below is
# one table and not one per kind of conductor mark.
PHASE_COLUMNS = COUNTS + TIMES + COST_COLUMNS
STEP_COLUMNS = STEP_COUNTS + TIMES + COST_COLUMNS

# The rework-and-waste section own table, keyed by phase like `counts` and kept beside it
# rather than inside it for the reason above the column names: these are not more of what the
# phase row reports. Its rows are raised from `counts` once the log has been read whole, so
# the two tables carry the same phases in the same order without either being consulted while
# the lines are still going past.
lost = {}

# What the conductor own marks said about each step, keyed by step like `steps` and kept
# beside it rather than inside it because these are read off marks rather than counted one
# line per unit. One table rather than one per kind of mark: a revise attempt is counted from
# its own marks, a refactor mark is read once whole, and the two brackets of the step are two
# timestamps — but all three answer "what did this step spend", all three are keyed by step,
# and two tables on one key are two tables to keep in step with each other. Each budget is
# the LAST one its marks reported — the budget the run finished under, and the same number as
# the first in every log where nobody re-exported the variable mid-run.
spent = {}

# What each ATTEMPT cost, keyed by the three fields that identify one — its step, its phase
# and its attempt number — so the developer leaf and the verifier that judged it land in one
# bucket, which is what an attempt is. Kept beside the rows rather than added into them,
# because whether an attempt is rework is not known when its lines are read: it turns on a
# verdict written after them and on a `step-done` mark written after that.
attempts_spent = {}

# The attempts a verifier turned down, in the order they were judged, and the steps that
# reached their closing mark. Rework is the intersection — a rejected attempt of a step that
# recovered — and it cannot be computed line by line, so both are collected and the sum is
# taken once the log has been read whole.
rejected = []
recovered = set()

# The run own row, a table of one rather than a row of either section above: a total belongs
# to neither key, and appended to the per-step table it would be a step whose name happened
# to be `total`, carrying a bracket and two budgets with nothing true to say. It is also the
# only row the conductor own spending can land in — that line carries no phase and no step,
# because what the conductor spends belongs to the run rather than to any leaf inside it.
totals = {"total": dict.fromkeys(COST_COLUMNS, 0)}

# Whether the log holds the conductor own closing accounting. It exists only when the
# conductor ran in print mode; a run driven from an interactive session leaves the leaf cost
# complete and the conductor own missing, so the figures mean one of two different things
# and the report says which — the same unknown-rather-than-silence rule as the cells above.
conductor_counted = False

# A row appears on first sight of its key with every column of its section at zero, so no cell
# is ever missing and the insertion order is the order the run reached the key in.
def row_in(table, key, columns):
    return table.setdefault(key, dict.fromkeys(columns, 0))

def tally(table, key, columns, count):
    row_in(table, key, columns)[count] += 1

# The rows one leaf line belongs to: the row of its phase and the row of its step, each
# raised on first sight. Which table goes with which set of columns is written here once, so
# the two additions below cannot come to disagree about it, and a line missing either key —
# a phase-less conductor mark, and the conductor own usage, which carries neither — simply
# lands in one row or in none.
def rows_for(phase, step):
    rows = []
    if phase:
        rows.append(row_in(counts, phase, PHASE_COLUMNS))
    if step:
        rows.append(row_in(steps, step, STEP_COLUMNS))
    return rows

# Seconds land in both sections from one call, the way a count does below: the line is the
# same attempt whichever way it is grouped. A count rises by one per line, these rise by
# whatever the line reports.
def add_seconds(phase, step, column, seconds):
    for row_of in rows_for(phase, step):
        row_of[column] += seconds

# One attempt own bucket, raised on first sight. An attempt with no phase or no step is not
# one a verdict can be written about, so it gets no bucket and cannot become rework.
def attempt_in(phase, step, attempt):
    if not phase or not step:
        return None
    return attempts_spent.setdefault((step, phase, attempt),
                                     {REWORK_WALL: 0, REWORK_COST: 0.0})

# What one `usage` line spent, into the row of its phase, the row of its step and the total.
# The total is in the list unconditionally where the other two are not: a line with neither
# key — the conductor own — is still spending of the run, and that is exactly the figure the
# line below `conductor_counted` is about.
def add_cost(phase, step, line):
    rows = rows_for(phase, step) + [totals["total"]]
    for heading, field in COSTS:
        reported = line.get(field) or 0
        amount = float(reported) if heading in MONEY else int(reported)
        for row_of in rows:
            row_of[heading] += amount

# The two ends of the whole run. `first` is the first line of the log whatever it is, since
# the mark that opens a run is the conductor own and a log missing it still started
# somewhere; `last` is the mark that ended it, either outcome, and stays None in a log of a
# run that has not ended.
first, last = None, None

with open(path) as f:
    for raw in f:
        raw = raw.strip()
        if not raw:
            continue
        line = json.loads(raw)
        event = line.get("event", "")
        step = line.get("step", "")
        phase = line.get("phase", "")
        ts = line.get("ts")
        if first is None:
            first = ts
        if event in ("done", "bail"):
            last = ts
        # The two brackets of a step, read before anything classifies the line below, since
        # neither is a leaf event and both would otherwise fall through to nothing.
        if event in ("step-start", "step-done") and step:
            spent.setdefault(step, {})[event] = ts
            if event == "step-done":
                recovered.add(step)
            continue
        # Time, off the two lines that carry it. An `exit` is also where a kill is counted
        # below, so this adds and lets the line fall through rather than classifying it.
        attempt = attempt_in(phase, step, line.get("attempt", ""))
        if event == "exit":
            seconds = int(line.get("secs") or 0)
            add_seconds(phase, step, "wall s", seconds)
            if attempt is not None:
                attempt[REWORK_WALL] += seconds
        elif event == "usage":
            add_seconds(phase, step, "API s",
                        int(line.get("duration_api_ms") or 0) // 1000)
            add_cost(phase, step, line)
            if attempt is not None:
                attempt[REWORK_COST] += float(line.get("total_cost_usd") or 0)
            if line.get("actor") == "conductor":
                conductor_counted = True
        elif event == "verdict" and line.get("verdict") == "REJECT" and attempt is not None:
            rejected.append((step, phase, line.get("attempt", "")))
        # The conductor budget marks next, and they fall through to nothing below: a
        # `revise` is not a leaf launch, so counting it as an attempt would double-count the
        # revise leaf that the mark is followed by.
        if event == "revise" and step:
            mark = spent.setdefault(step, {})
            mark["revises"] = mark.get("revises", 0) + 1
            mark["revise"] = line.get("budget", "")
            continue
        if event == "refactor" and step:
            mark = spent.setdefault(step, {})
            mark["transforms"] = line.get("transforms", "")
            mark["refactor"] = line.get("budget", "")
            mark["stopped"] = line.get("stopped", "")
            continue
        if event == "launch":
            count = "attempts"
        elif event == "verdict" and line.get("verdict") in ("PASS", "REJECT"):
            count = line["verdict"]
        elif event == "exit" and line.get("status") == "2":
            count = "kills"
        elif event == "retry":
            count = "retries"
        else:
            continue
        # One classification, two tables: the line is the same event whichever way it is
        # grouped, so reading `event` twice is the way the two sections come to disagree.
        # A phase-less line still raises no phase row, and a retry has no phase column to
        # land in.
        if phase and count in COUNTS:
            tally(counts, phase, PHASE_COLUMNS, count)
        if step:
            tally(steps, step, STEP_COLUMNS, count)

# Rework, once the log has been read whole: every rejected attempt of a step that reached its
# closing mark, into the row of the phase it was rejected in. The two conditions are what the
# glossary pairs — a REJECT is what makes an attempt rework, and recovering is what keeps it
# out of waste — so neither can be applied while the lines are still going past.
for phase in counts:
    row_in(lost, phase, LOST_COLUMNS)

for key in rejected:
    step, phase, _ = key
    if step not in recovered:
        continue
    attempt = attempts_spent[key]
    row_of = row_in(lost, phase, LOST_COLUMNS)
    row_of[REWORK_WALL] += attempt[REWORK_WALL]
    row_of[REWORK_COST] += attempt[REWORK_COST]

def row(cells):
    print("| " + " | ".join(cells) + " |")

# One cell of a counted column. Everything in both sections is a whole number of things
# counted except the dollars, which are money and are printed to the cent — a run that spent
# 1.75 dollars printed as `1` or as `1.75000000000000002` is a figure a reader has to go and
# check somewhere else.
def figure(column, value):
    return "%.2f" % value if column in MONEY else "%d" % value

def step_wall(step):
    mark = spent.get(step, {})
    start, done = mark.get("step-start"), mark.get("step-done")
    if start is None or done is None:
        return UNKNOWN
    return "%d" % (done - start)

def budget_cells(step):
    mark = spent.get(step, {})
    used = mark.get("revises")
    revise = "%d/%s" % (used, mark.get("revise") or "?") if used else UNKNOWN
    if mark.get("refactor"):
        refactor = "%s/%s" % (mark.get("transforms") or "?", mark["refactor"])
    else:
        refactor = UNKNOWN
    return [revise, refactor, mark.get("stopped") or UNKNOWN]

# `section` takes one reader for its text columns, and the step section has two groups of
# them: this is the one, so the cells cannot come apart from the order the headings print in.
def step_cells(step):
    return [step_wall(step)] + budget_cells(step)

# `text` is a section of non-count columns, as the pair (headings, a function mapping a row
# key to that rows cells under them). One parameter rather than two because headings with
# nothing filling them is a table of blanks and cells with no heading land nowhere, so the
# pair is what makes it impossible to pass one and forget the other. It is also what keeps
# this renderer from naming a budget: the section that has such columns hands in its own
# reader, where before the headings doubled as a flag for whether to call a function this
# function reached out of the module for by name.
def section(heading, key_column, columns, table, text=None):
    headings, cells_for = text or ((), None)
    headings = list(headings)
    print()
    print(heading)
    print()
    row([key_column] + columns + headings)
    row(["---"] + ["---:"] * len(columns) + ["---"] * len(headings))
    for key, row_counts in table.items():
        cells = [key] + [figure(c, row_counts[c]) for c in columns]
        row(cells + (cells_for(key) if cells_for else []))

print("### 📊 Metrics — issue %s" % issue)
print()
# Outside the tables, because it is a figure of the whole run and not of a row in either.
print("Wall time for the issue: %s s, from the first event of the log to the mark that "
      "ended the run."
      % (UNKNOWN if first is None or last is None else "%d" % (last - first)))
# Outside the tables for the same reason as the line above, and beside it: it qualifies
# every cost figure in the report rather than any one row of it.
print("Cost is every leaf of the run, and the conductor own %s."
      % ("closing accounting with them, which this log carries"
         if conductor_counted else
         "spending is not in it: this log carries no usage record of the conductor own"))
# Every column of the phase section is a figure its row already carries, so it is printed
# from the same list the row was raised with and needs no reader of its own. The step
# section hands one in for its wall cell and its budgets, the three it cannot read off a row.
section("#### By phase", "phase", PHASE_COLUMNS, counts)
# Beside the phase section and after it, because every row it has is a row that one has:
# a reader reaches "what did this phase throw away" by way of what it spent.
section("#### Rework and waste, by phase", "phase", LOST_COLUMNS, lost)
section("#### By step", "step", STEP_COUNTS + [API] + COST_COLUMNS, steps,
        ([WALL] + BUDGETS, step_cells))
section("#### Total", "run", COST_COLUMNS, totals)
' "$issue" "$log"
