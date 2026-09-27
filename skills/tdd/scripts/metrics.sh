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
#   no-verdict — `relaunch` events carrying `cause=no-verdict`. verify.sh writes one each time
#              a verifier leaf exited cleanly with no VERDICT: line and is launched again
#              (issue #219): protocol compliance, `VERI_NO_VERDICT_RETRIES`, so neither a
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
# a step: the seconds every test-command run recorded, one row per tier (#342, part of PRD
# #335). timed-test-run.sh writes one `test-run` mark per run of the test command, carrying
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

# Exit 2, not the 1 a `${1:?…}` expansion aborts with — CLAUDE.md, "Exit codes are the API" (#270).
# The number is what the report is ABOUT: it names the file the conductor commits and the
# issue the thread belongs to, so a call that omits it has not said which run it means.
[[ -n "${1:-}" ]] || { echo "usage: metrics.sh <issue-number>" >&2; exit 2; }
issue="$1"

log=".tdd/events.jsonl"

# The ledger of the same issue, beside the log, and the only input that can say how many
# steps were PLANNED — see the header. Named here rather than built in python so both paths
# this reads are spelled in one place.
ledger=".tdd/issue-$issue.md"

# Note the apostrophe nobody may write inside the block below: it is a single-quoted shell
# string, so a `run's` in a comment or a docstring ends the program there and python is
# handed the rest as argv. The same trap event.sh and harvest-usage.sh carry.
exec python3 -c '
import json, re, sys

issue, path, ledger = sys.argv[1], sys.argv[2], sys.argv[3]

# The four counts, in the order the table prints them, each with the column heading it is
# printed under. One list so the headings and the arithmetic cannot come to disagree about
# how many columns there are.
COUNTS = ["attempts", "PASS", "REJECT", "kills"]

# The per-step section prints those four, retries and no-verdict relaunches, in that order, for the reason in the
# header: retries answer a per-step question. Written as an extension of COUNTS rather than
# as a list of its own, so the two sections cannot come to disagree about what a kill is.
STEP_COUNTS = COUNTS + ["retries", "no-verdict"]

# The per-step section closes with three columns that are not counts but text: the two
# `used/budget` pairs and the reason the refactor loop stopped. They are listed apart from
# STEP_COUNTS because they are tallied from a different shape of line — one mark carrying
# the numbers, rather than one line per unit counted — and rendered with a different
# alignment.
BUDGETS = ["revise", "refactor", "stopped"]

# And one more text column after them: the `spent=` carried by the `step-over-budget` mark of a step,
# empty for a step that never crossed — a `0` there would read as a crossing at nothing.
CROSSED = "crossed at"

# And the cause of a split, the `at=` a `step-split` mark carried (#452): `exhausted` for a
# spent REVISE_BUDGET, `over-budget` for a crossed cost budget. Two causes of the same plan
# growth are two facts about the run, so the report keeps the word rather than a count.
SPLIT = "split"

# The two marks above keep one attribute each, so one table says which: the mark, the column
# its cell lands in, and the attribute the cell is read from. The reading loop and the step
# row both go through it, so the cell of a mark cannot come apart from the heading it prints under.
CELL_MARKS = {"step-over-budget": (CROSSED, "spent"), "step-split": (SPLIT, "at")}
MARK_COLUMNS = [column for column, _ in CELL_MARKS.values()]

KIND = "kind"

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

# One figure of the report, as a whole number or as the word above when nothing supplied it.
# Written once because the rule it applies is one rule — ADR-0014 degrades a missing mark to
# unknown and never to zero — and three cells spelling it themselves are three places for one
# of them to reach for "0" instead.
def known(number):
    return UNKNOWN if number is None else "%d" % number

# A count that came out zero, turned into the figure it actually is. Nothing in this log
# raised the thing being counted — no step-done mark, no checkbox step — and a total of zero
# is what "nothing to count" and "nothing counted" look like alike, so the two callers that
# count marks hand their total through here and `known` then says unknown. Written once for
# the reason `known` is: it is the same reading of ADR-0014 twice, and a caller spelling it
# itself is a place for one of them to print `0` instead.
def counted(total):
    return total or None

# The seconds between two marks of the log, or None when either is missing, which `known`
# above then says is unknown. A stretch of the run is bracketed by two marks — the step by
# its `step-start` and `step-done`, the issue by its first line and the mark that ended it —
# so the arithmetic and the pair of conditions on it are the same for both.
def span(start, end):
    return None if start is None or end is None else end - start

# The reading of one clock off a mark of the log — `ts` or `awake` — or None when there is no mark,
# or the mark carries no reading of that clock, which `span` above then carries through. The
# awake clock reads as None throughout a log not every line of which carries it (`clocked`
# below), so no figure mixes the two clocks.
def reading(mark, clock):
    if mark is None or (clock == "awake" and not clocked):
        return None
    return mark.get(clock)

# The seconds between two marks as a figure measures them (#486): on the awake clock when both
# carry a reading, so time the machine spent asleep is not counted as work, and on `ts`
# otherwise. Written once because the step wall and the issue wall apply the one rule, and two
# spellings of it are two places for one of them to mix the clocks.
def awake_span_or_wall(start, end):
    awake = span(reading(start, "awake"), reading(end, "awake"))
    return awake if awake is not None else span(reading(start, "ts"), reading(end, "ts"))

# A checkbox step of the ledger, ticked or not — the same grammar next-unchecked.sh reads
# (next-unchecked.sh:16), matched leaving the state inside the box open, because what is
# wanted is how many steps the plan HAS, not how many are still to do.
STEP_BOX = re.compile(r"^[ \t]*- \[[ xX]\] .")

# How many steps the plan has, off the ledger beside the log, or None when there is no
# ledger to read or it holds no checkbox step at all — both of them a count nothing supplied,
# which `counted` above is what says so for the second.
def planned_steps(path):
    try:
        with open(path) as f:
            found = sum(1 for line in f if STEP_BOX.match(line))
    except OSError:
        return None
    return counted(found)

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
# marks kept whole (#486) — but all three answer "what did this step spend", all three are keyed by step,
# and two tables on one key are two tables to keep in step with each other. Each budget is
# the LAST one its marks reported — the budget the run finished under, and the same number as
# the first in every log where nobody re-exported the variable mid-run.
spent = {}

passes = {}
open_passes = {}

def open_pass(step):
    return open_passes.setdefault(step, {"verdict": "", "revise": 0, WALL: 0, DOLLARS: 0.0})

# What each ATTEMPT cost, keyed by the three fields that identify one — its step, its phase
# and its attempt number — so the developer leaf and the verifier that judged it land in one
# bucket, which is what an attempt is. Kept beside the rows rather than added into them,
# because whether an attempt is rework is not known when its lines are read: it turns on a
# verdict written after them and on a `step-done` mark written after that.
attempts_spent = {}

# The attempts a verifier turned down, each as the step it belongs to, the phase it was
# rejected in and its own bucket, and the steps that reached their closing mark. Rework is
# the intersection — a rejected attempt of a step that recovered — and it cannot be computed
# line by line, so both are collected and the sum is taken once the log has been read whole.
# The bucket itself travels rather than the key it is filed under, because it is the same
# dict the lines still to come go on adding into: by the end of the log it holds the whole of
# what that attempt spent, and nothing has to go and look it up again.
rejected = []
recovered = set()

# The seconds each tier of test-command run recorded, keyed by tier and holding one figure
# per `test-run` mark in the order the log carries them — a list rather than a row of counts,
# because what this section reports is a trend and a trend read out of order is not one. Its
# own table rather than a column of either section above, for the reason the total has one:
# a tier is neither a phase nor a step, and one test-command run happens inside both.
tier_runs = {}

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

# One attempt own bucket, raised on first sight, keyed by the two columns a row carries the
# same figures under: what a bucket holds is what the attempt SPENT, which is what it will
# contribute if it later turns out to be rework, and naming it `rework` here would have said
# it already was. An attempt with no phase or no step is not one a verdict can be written
# about, so it gets no bucket and cannot become rework.
def attempt_in(phase, step, attempt):
    if not phase or not step:
        return None
    return attempts_spent.setdefault((step, phase, attempt), {WALL: 0, DOLLARS: 0.0})

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

# Where the last run in the log began: its last `resume`, or the first line of the log, whatever
# it is, when there is none, since the mark that opens a run is the conductor own and a log
# missing it still started somewhere. It is the opening end of the issue wall, whose closing
# end is the mark below — a log holding several runs of one issue walls only the last (#229).
# Kept whole, as `ending` is, because the issue wall reads two clocks off it: its `ts` and the
# awake-clock reading event.sh writes beside it (#486).
opening = None

# The mark that ended the run, any outcome, and None in the log of a run that has not
# ended. Kept whole rather than as its timestamp beside itself: the issue wall reads its `ts`
# and the outcome line reads its payload — the PR a `done` carries, the cause and
# classification a `bail` does, the mode and boundary a `stop` does — and two names for one
# mark is one of them going stale.
ending = None

# Each attempt `launch` mark, keyed as `attempts_spent` is, so its `exit` can read the
# attempt span off the awake clock (#486).
launched = {}

# Whether every line of the log carries an awake-clock reading (#486). A log with none was
# written before event.sh recorded one, and a log with only some gained it partway; in either
# case every figure below is wall-clock — a figure taking one end off each clock, or summing
# attempts measured on different clocks, is on no clock at all — and the report says so
# rather than letting a reader take them for awake time. Settled before the loop below because
# the attempt sums there are added line by line, before the last line is seen.
with open(path) as f:
    marks = [json.loads(raw) for raw in f if raw.strip()]
clocked = bool(marks) and all("awake" in mark for mark in marks)

for line in marks:
    event = line.get("event", "")
    step = line.get("step", "")
    phase = line.get("phase", "")
    ts = line.get("ts")
    if opening is None or event == "resume":
        opening = line
    # A `stop` is not terminal the way `done` and `bail` are: the run it paused may be
    # resumed, and a resumed run has not ended until a mark after its `resume` says so.
    if event == "resume" and ending is not None and ending.get("event") == "stop":
        ending = None
    if event in ("done", "bail", "stop"):
        ending = line
    # The two brackets of a step, read before anything classifies the line below, since
    # neither is a leaf event and both would otherwise fall through to nothing.
    if event in ("step-start", "step-done") and step:
        spent.setdefault(step, {})[event] = line
        if event == "step-done":
            recovered.add(step)
        continue
    # The seconds one test-command run recorded, off the mark timed-test-run.sh writes
    # for it. Read before the leaf events below and falling through to none of them: a
    # `test-run` is not a launch, an exit or a verdict, and the seconds it carries are
    # the test command own rather than any attempt.
    #
    # The figure travels as the text the mark carries rather than as a number parsed and
    # printed again, so a run recorded as `4` is listed as `4` and this section invents
    # no precision the writer did not claim. A mark with no seconds at all supplies no
    # figure and raises no row of its own.
    if event == "test-run":
        seconds = line.get("seconds")
        if seconds not in (None, ""):
            tier_runs.setdefault(line.get("tier") or UNKNOWN, []).append(str(seconds))
        continue
    # A step whose criterion earlier work already satisfied is done on its `pin` mark and
    # never writes `step-done` (SKILL.md, the verify-pin PASS branch).
    if event == "pin" and step:
        recovered.add(step)
        spent.setdefault(step, {})[KIND] = "pin"
    elif event == "verdict" and phase == "pin" and line.get("verdict") == "PASS" and step:
        spent.setdefault(step, {}).setdefault(KIND, "already-satisfied")
    # Time, off the two lines that carry it. An `exit` is also where a kill is counted
    # below, so this adds and lets the line fall through rather than classifying it.
    attempt_no = line.get("attempt", "")
    attempt = attempt_in(phase, step, attempt_no)
    if event == "launch":
        launched[(step, phase, attempt_no)] = line
    if event == "exit":
        # On the awake clock when the attempt launch and exit both carry a reading, so a
        # sleep inside the attempt is not counted as work (#486); off `secs` otherwise.
        awake = span(reading(launched.get((step, phase, attempt_no)), "awake"),
                     reading(line, "awake"))
        seconds = int(awake if awake is not None else (line.get("secs") or 0))
        add_seconds(phase, step, "wall s", seconds)
        if attempt is not None:
            attempt[WALL] += seconds
        if phase == "refactor":
            open_pass(step)[WALL] += seconds
    elif event == "usage":
        add_seconds(phase, step, "API s",
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
        if current["verdict"] == "PASS" and current.get("marked"):
            open_passes.pop(step)
    # The conductor budget marks next, and they fall through to nothing below: a
    # `revise` is not a leaf launch, so counting it as an attempt would double-count the
    # revise leaf that the mark is followed by.
    if event == "revise" and step:
        # REVISE_BUDGET is per phase, so the attempts are kept per phase: a step
        # revised in two phases spent two budgets, not one (#488).
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
        if current["verdict"]:
            open_passes.pop(step)
        continue
    # The cost-budget crossing and the cause of a split (#452): what the step had spent when
    # it crossed, kept as the figure rather than a flag, since a crossing at $12 and one at $28
    # are different findings, and the `at=` its split carried.
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

# What one attempt the run did not keep contributes, under whichever pair of columns is
# losing it. The pair travels as a parameter rather than the kind of loss, because what the
# two kinds disagree about is which attempts they are told about — the condition each loop
# below applies — and not what an attempt contributes once told: both are the wall seconds
# and the dollars of the same bucket. Written once so the two can never come to disagree
# about that, leaving each loop as its own condition and nothing else.
def lose(phase, attempt, wall_column, cost_column):
    row_of = row_in(lost, phase, LOST_COLUMNS)
    row_of[wall_column] += attempt[WALL]
    row_of[cost_column] += attempt[DOLLARS]

for step, phase, attempt in rejected:
    if step in recovered:
        lose(phase, attempt, REWORK_WALL, REWORK_COST)

# Waste, the other half of the same pair and the same one condition read the other way: a
# step that never reached its closing mark is a step the run did not keep, so EVERY attempt
# it made is waste — the PASSing ones too, since a Red nobody turned down is still a Red
# nobody kept. It is read off `attempts_spent` rather than off `rejected` for exactly that
# reason: a verdict says which attempts are rework, and nothing about which are waste.
for (step, phase, _attempt_no), attempt in attempts_spent.items():
    if step not in recovered:
        lose(phase, attempt, WASTE_WALL, WASTE_COST)

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

# `section` takes one reader for its text columns, and the step section has two groups of
# them: this is the one, so the cells cannot come apart from the order the headings print in.
def step_cells(step):
    mark = spent.get(step, {})
    return [step_wall(step)] + budget_cells(step) + [mark.get(column, "") for column in MARK_COLUMNS] + [mark.get(KIND, "full")]

# The lines every table in this report opens with: a blank line, the heading, another blank,
# the header row and the markdown alignment row under it. Both renderers below go through it
# rather than spelling it out twice, so the frame of a table is laid out in one place however
# many tables the report grows. The alignments come in per column because they are the one part
# that differs between them: a column of figures is right-aligned and a column of words is not.
def table_head(heading, key_column, columns, aligns):
    print()
    print(heading)
    print()
    row([key_column] + columns)
    row(["---"] + aligns)

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
    table_head(heading, key_column, columns + headings,
               ["---:"] * len(columns) + ["---"] * len(headings))
    for key, row_counts in table.items():
        cells = [key] + [figure(c, row_counts[c]) for c in columns]
        row(cells + (cells_for(key) if cells_for else []))

# The per-tier section, rendered by itself rather than through `section` above: every other
# table has one cell per column of a fixed list, where a row here has one cell per run that
# tier made, and how many that is is a fact about the log rather than about the report.
#
# The header is widened to the busiest tier and the shorter rows are padded with empty cells,
# so the table stays rectangular: a row carrying more cells than the header has columns is a
# row whose extra figures GitHub markdown drops on the floor, and this report is pasted into
# an issue thread to be read there.
def tier_section(heading, key_column):
    width = max([len(runs) for runs in tier_runs.values()] or [0])
    table_head(heading, key_column,
               ["run %d s" % (i + 1) for i in range(width)], ["---:"] * width)
    for tier, runs in tier_runs.items():
        row([tier] + runs + [""] * (width - len(runs)))

print("### 📊 Metrics — issue %s" % issue)
print()
# Outside the tables, because it is a figure of the whole run and not of a row in either.
# Measured on the awake clock when both ends carry a reading (#486), so time the machine
# spent asleep is not counted as work; the wall-clock span is kept only to name the seconds
# it excluded, on the line beside it.
wall_span = span(reading(opening, "ts"), reading(ending, "ts"))
awake_span = span(reading(opening, "awake"), reading(ending, "awake"))
print("Wall time for the issue: %s s, from the last `resume`, or the first event of the log when "
      "there is none, to the mark that ended the run."
      % known(awake_span_or_wall(opening, ending)))
if awake_span is not None and wall_span is not None:
    print("Seconds the machine was not running inside that span: %s s, excluded from it."
          % (wall_span - awake_span))
if not clocked:
    print("Every figure in this report is wall-clock: the log carries no awake-clock reading, "
          "so time the machine spent asleep is counted in them.")
# Beside the line above, and outside the tables for the same reason: progress is a figure of
# the run and of no row in either. The steps done are the ones that reached their closing
# mark — a step that took a revise to get there is one of them, since what the figure counts
# is steps finished and not attempts — and the count of the plan comes off the ledger, which
# is the only input that still names the steps a bailed run never reached.
#
# A log carrying no closing mark at all supplies the first number no more than a missing
# ledger supplies the second, which is why the count of the steps that reached one goes
# through `counted` on its way to `known`, exactly as the count off the ledger does.
planned = planned_steps(ledger)
print("Steps done: %s of %s planned."
      % (known(counted(len(recovered))), known(planned)))
# And how the run ended, beside the two figures above: the same mark that closed the issue
# wall, read for its payload rather than its timestamp. A bail names its classification
# because system and process are two different things for a reader to do next.
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
# Outside the tables for the same reason as the lines above, and beside them: it qualifies
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
        ([WALL] + BUDGETS + MARK_COLUMNS + [KIND], step_cells))
print()
print("The figure comparable across runs is turns, the same measurement on any model; dollars "
      "are not comparable, the same measurement only at the same VERI_MODEL, "
      "VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.")
if passes:
    table_head("#### By refactor pass", "step", ["pass", "refactor", "stopped", "verdict", "revise", WALL, DOLLARS],
               ["---:", "---:", "---", "---", "---:", "---:", "---:"])
    for (step, index), (mark, spent_by) in passes.items():
        row([step, index, "%s/%s" % (mark["transforms"], mark["budget"]), mark["stopped"],
             spent_by["verdict"], str(spent_by["revise"]), figure(WALL, spent_by[WALL]), figure(DOLLARS, spent_by[DOLLARS])])
# After the two sections keyed by the run own structure and before the total, because it is
# keyed by neither: the seconds of the test command itself, per tier, in log order.
tier_section("#### Test-command seconds, by tier", "tier")
section("#### Total", "run", COST_COLUMNS, totals)
' "$issue" "$log" "$ledger"
