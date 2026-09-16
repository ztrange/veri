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

# The budget readings, keyed by step like `steps` and kept beside it rather than inside it
# because a revise attempt is counted from its own marks while a refactor mark is read once,
# whole. `revises` counts the marks, `budgets` holds the last budget each kind of mark
# reported for the step — last rather than first because it is the budget the run finished
# under, and the two are the same number in every log where nobody re-exported the variable
# mid-run.
revises = {}
budgets = {}

def tally(table, key, columns, count):
    if key not in table:
        table[key] = dict.fromkeys(columns, 0)
    table[key][count] += 1

with open(path) as f:
    for raw in f:
        raw = raw.strip()
        if not raw:
            continue
        line = json.loads(raw)
        event = line.get("event", "")
        step = line.get("step", "")
        # The conductor budget marks first, and they fall through to nothing below: a
        # `revise` is not a leaf launch, so counting it as an attempt would double-count the
        # revise leaf that the mark is followed by.
        if event == "revise" and step:
            revises[step] = revises.get(step, 0) + 1
            budgets.setdefault(step, {})["revise"] = line.get("budget", "")
            continue
        if event == "refactor" and step:
            mark = budgets.setdefault(step, {})
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
        phase = line.get("phase", "")
        if phase and count in COUNTS:
            tally(counts, phase, COUNTS, count)
        if step:
            tally(steps, step, STEP_COUNTS, count)

def row(cells):
    print("| " + " | ".join(cells) + " |")

def budget_cells(step):
    mark = budgets.get(step, {})
    used = revises.get(step)
    revise = "%d/%s" % (used, mark.get("revise") or "?") if used else UNKNOWN
    if mark.get("refactor"):
        refactor = "%s/%s" % (mark.get("transforms") or "?", mark["refactor"])
    else:
        refactor = UNKNOWN
    return [revise, refactor, mark.get("stopped") or UNKNOWN]

def section(heading, key_column, columns, table, extra=()):
    extra = list(extra)
    print()
    print(heading)
    print()
    row([key_column] + columns + extra)
    row(["---"] + ["---:"] * len(columns) + ["---"] * len(extra))
    for key, row_counts in table.items():
        cells = [key] + ["%d" % row_counts[c] for c in columns]
        row(cells + (budget_cells(key) if extra else []))

print("### 📊 Metrics — issue %s" % issue)
section("#### By phase", "phase", COUNTS, counts)
section("#### By step", "step", STEP_COUNTS, steps, BUDGETS)
' "$issue" "$log"
