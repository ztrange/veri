#!/usr/bin/env bash
# Unit tests for scripts/metrics.sh — the per-issue metrics report computed from the run's
# event log (issue #108, and #107/ADR-0014 before it: observability is a per-run event log
# written by the scripts, not a service). Zero-dependency plain-shell asserts, same idiom as
# event.test.sh and harvest-usage.test.sh, its two nearest neighbours: all three are about
# lines somebody else wrote into `.tdd/events.jsonl`.
#
# Contract under test (this step only — the counts, per phase, and nothing else):
#   metrics.sh <n>  → exit 0, and on stdout a markdown table with one row per phase of the
#                     run, carrying that phase's attempts, its PASS verdicts, its REJECT
#                     verdicts and its kills.
#
# The log is read relative to the directory the script runs in — `.tdd/events.jsonl`, the
# way event.sh writes it (event.sh:60) and the way supervise.sh already spells `.tdd/<name>.log`
# — so the case below writes a hand-made log into a temp directory and runs the script there.
#
# Which line of the log each of the four counts is read off, and why a kill is counted apart
# from a verdict, is metrics.sh's own header — with the writer and line number for each. It
# is not restated here: the same paragraph in two files is the same paragraph to keep
# correct twice, and a `supervise.sh:297` that moves would go stale in whichever copy
# nobody was editing.
#
# What the header there does not say, because it is about this fixture: the row key is the
# log's own `phase` field rather than the leaf's name, so a developer leaf and the verifier
# that judged it land in one row. A table keyed by leaf name would have PASS and REJECT
# structurally zero for every `develop-*` row, and the case below could not tell a script
# that counted verdicts from one that did not.
#
# The fixture is built so no two columns can be confused for one another: red reads
# 2/1/0/0 and green reads 9/1/2/3, so the four columns hold four distinct pairs of numbers
# across the two rows. A script that swapped two of them cannot pass this case.
#
# The conductor's own `step-start` and `step-done` marks are in the fixture too, carrying an
# empty phase. They are neither launches nor verdicts nor exits, so they must contribute to
# nothing and must not raise a row of their own.
#
# What this case deliberately does NOT pin, because each is a step of its own in the plan:
# the per-step section, retries and budgets, time, cost, rework and waste, progress, and the
# unknown-rather-than-zero rule for a missing conductor mark. And one thing this step moves
# that is pinned elsewhere: CLAUDE.md's suite count, which claude-md-counts.test.sh case 1
# holds to the files on disk and which goes red by itself the moment this file lands
# uncounted.
#
# Run: skills/tdd/scripts/tests/metrics.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
METRICS="$HERE/../metrics.sh"
pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output says which of the counts came out wrong rather than just that one did.
# Same helper, same words, as event.test.sh's and session-cost.test.sh's.
report() {
  local name="$1"
  if [[ "${#problems[@]}" -eq 0 ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1))
    echo "FAIL - $name"
    printf '    %s\n' "${problems[@]}"
  fi
}

# table_says <file> <phase> <attempts> <pass> <reject> <kills> … — read the rendered table
# out of <file> and complain, one line per disagreement, onto the caller's `problems`.
# Takes any number of five-word row expectations after the file.
#
# The columns are located by reading the HEADER row rather than by position, because which
# order the four counts are printed in is a presentation choice this step does not pin —
# what it pins is that each count is there and is right. Ambiguity is a problem rather than
# a guess: a header cell matching two of the four words means the table did not give the
# four counts four columns, which is the thing being asserted, so it fails rather than
# silently reading one column as two.
#
# python3 rather than awk: extract-result.sh and event.sh already exec it in production, so
# the interpreter is a dependency this repo has, and the parse is fail-closed in one place.
table_says() {
  local out_file="$1"; shift
  local said
  said="$(python3 -c '
import re, sys

WANTED = ["attempts", "pass", "reject", "kills"]
NEEDLE = {"attempts": "attempt", "pass": "pass", "reject": "reject", "kills": "kill"}
SEPARATOR = re.compile(r"^:?-+:?$")

def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]

text = open(sys.argv[1]).read()
rows = [cells(l) for l in text.splitlines() if l.strip().startswith("|")]
rows = [r for r in rows if not all(SEPARATOR.match(c) for c in r if c)]

problems = []
if not rows:
    problems.append("want a markdown table in the output, found no line beginning with |")
    print("\n".join(problems))
    raise SystemExit(0)

header, body = rows[0], rows[1:]

column = {}
for i, cell in enumerate(header):
    hit = [w for w in WANTED if NEEDLE[w] in cell.lower()]
    if len(hit) > 1:
        problems.append(
            "header cell %r names %s at once, want one column each" % (cell, " and ".join(hit)))
    elif hit:
        column.setdefault(hit[0], i)
for want in WANTED:
    if want not in column:
        problems.append(
            "want a %s column, the header row is %r" % (want, " | ".join(header)))

labels = [r[0] for r in body if r]
for arg in sys.argv[2:]:
    phase, expected = arg.split("=", 1)
    row = next((r for r in body if r and r[0].strip().lower() == phase), None)
    if row is None:
        problems.append("want a row for phase %r, the table has rows for: %s"
                        % (phase, ", ".join(repr(l) for l in labels) or "nothing"))
        continue
    for want, number in zip(WANTED, expected.split(",")):
        if want not in column:
            continue
        i = column[want]
        got = row[i] if i < len(row) else ""
        if got != number:
            problems.append("phase %r %s: want %s, got %r" % (phase, want, number, got))

print("\n".join(problems))
' "$out_file" "$@" 2>&1)"
  [[ -z "$said" ]] || while IFS= read -r line; do problems+=("$line"); done <<< "$said"
}

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

# ev <ts> <actor> <phase> <event> <attempt> [<trailing-json>] — one hand-written line of the
# fixture log, in the shape event.sh emits: the eight fixed context keys, then the payload.
# Hand-written rather than produced by running event.sh, so this suite's subject stays the
# reader and a change to the writer cannot quietly rewrite the input being read.
step="metrics.sh renders a markdown table of per-phase counts"
ev() {
  printf '{"ts": %s, "issue": "108", "actor": "%s", "phase": "%s", "step": "%s", "event": "%s", "attempt": "%s", "skill_commit": "c0ffee1"%s}\n' \
    "$1" "$2" "$3" "$step" "$4" "$5" "${6:-}" >> "$work/.tdd/events.jsonl"
}

mkdir -p "$work/.tdd"

# The conductor's own marks, phase-less: neither launch nor verdict nor exit, so they must
# raise no row and change no count.
ev 990 conductor "" step-start ""

# Red: one developer leaf, one verifier, one PASS. 2 attempts, 1 PASS, 0 REJECT, 0 kills.
ev 1000 developer red launch 1 ', "name": "develop-red", "cmd": "run-leaf.sh", "model": ""'
ev 1100 developer red exit   1 ', "status": "0", "secs": "100"'
ev 1110 verifier  red launch 1 ', "name": "verify-red", "cmd": "run-leaf.sh", "model": ""'
ev 1130 verifier  red exit   1 ', "status": "0", "secs": "20"'
ev 1130 verifier  red verdict 1 ', "verdict": "PASS", "reason": "the case fails for the reason it was written to catch"'

# Green: two REJECTs and the revises that answered them, three killed leaves in the middle,
# and a PASS at the end. 9 attempts, 1 PASS, 2 REJECT, 3 kills.
ev 1200 developer green launch 1 ', "name": "develop-green", "cmd": "run-leaf.sh", "model": ""'
ev 1300 developer green exit   1 ', "status": "0", "secs": "100"'
ev 1310 verifier  green launch 1 ', "name": "verify-green", "cmd": "run-leaf.sh", "model": ""'
ev 1330 verifier  green exit   1 ', "status": "0", "secs": "20"'
ev 1330 verifier  green verdict 1 ', "verdict": "REJECT", "reason": "the production change is wider than the case asks for"'
ev 1340 developer green launch 2 ', "name": "revise-green-2", "cmd": "run-leaf.sh", "model": ""'
ev 1400 developer green exit   2 ', "status": "0", "secs": "60"'
ev 1410 verifier  green launch 2 ', "name": "verify-green", "cmd": "run-leaf.sh", "model": ""'
ev 1430 verifier  green exit   2 ', "status": "0", "secs": "20"'
ev 1430 verifier  green verdict 2 ', "verdict": "REJECT", "reason": "a second criterion was pinned in passing"'
ev 1440 developer green launch 3 ', "name": "revise-green-3", "cmd": "run-leaf.sh", "model": ""'
ev 1500 developer green exit   3 ', "status": "2", "cause": "no heartbeat for 300s (window 120s)", "secs": "60"'
ev 1510 developer green launch 3 ', "name": "revise-green-3", "cmd": "run-leaf.sh", "model": ""'
ev 1570 developer green exit   3 ', "status": "2", "cause": "no heartbeat for 300s (window 120s)", "secs": "60"'
ev 1580 developer green launch 3 ', "name": "revise-green-3", "cmd": "run-leaf.sh", "model": ""'
ev 1640 developer green exit   3 ', "status": "2", "cause": "hard timeout 1200s exceeded", "secs": "60"'
ev 1650 developer green launch 3 ', "name": "revise-green-3", "cmd": "run-leaf.sh", "model": ""'
ev 1700 developer green exit   3 ', "status": "0", "secs": "50"'
ev 1710 verifier  green launch 3 ', "name": "verify-green", "cmd": "run-leaf.sh", "model": ""'
ev 1730 verifier  green exit   3 ', "status": "0", "secs": "20"'
ev 1730 verifier  green verdict 3 ', "verdict": "PASS", "reason": "the step is now pinned and no wider"'

ev 1740 conductor "" step-done ""


name="a two-phase log renders one row per phase with its attempts, PASS, REJECT and kills"
problems=()

out_file="$work/report.md"
( cd "$work" && "$METRICS" 108 ) > "$out_file" 2>/dev/null
status=$?

[[ "$status" -eq 0 ]] ||
  problems+=("want metrics.sh to exit 0, it exited $status")

table_says "$out_file" red=2,1,0,0 green=9,1,2,3

[[ "${#problems[@]}" -eq 0 ]] ||
  problems+=("the report was: $(printf '%q' "$(cat "$out_file")")")

report "$name"


# step_table_says <file> <step>=<attempts>,<pass>,<reject>,<kills>,<retries> … — read the
# PER-STEP section out of the rendered report and complain, one line per disagreement, onto
# the caller's `problems`.
#
# The section is located by what it carries rather than by a heading or a position: the
# report's tables are searched for one that has a stuck-retries column, since only the
# per-step section has those counts. That leaves the implementation free to head the section
# however it likes and to order the columns however it likes — what this pins is that the
# per-step counts exist and are right, which is the step. Rows are then matched on their
# first cell against the step's own name, the string event.sh writes into every line's
# `step` field.
#
# Same shape, same fail-closed parse, and the same reason for python3 over awk, as
# table_says above.
step_table_says() {
  local out_file="$1"; shift
  local said
  said="$(python3 -c '
import re, sys

WANTED = ["attempts", "pass", "reject", "kills", "retries"]
NEEDLE = {"attempts": "attempt", "pass": "pass", "reject": "reject",
          "kills": "kill", "retries": "retr"}
SEPARATOR = re.compile(r"^:?-+:?$")

def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]

# Every run of consecutive table lines is one table: a report with a per-phase section and a
# per-step section has two, and a blank line or a heading between them is what separates
# them.
tables, current = [], []
for line in open(sys.argv[1]).read().splitlines():
    if line.strip().startswith("|"):
        row = cells(line)
        if not all(SEPARATOR.match(c) for c in row if c):
            current.append(row)
    elif current:
        tables.append(current)
        current = []
if current:
    tables.append(current)

def columns(header):
    found = {}
    for i, cell in enumerate(header):
        hit = [w for w in WANTED if NEEDLE[w] in cell.lower()]
        if len(hit) == 1:
            found.setdefault(hit[0], i)
    return found

problems = []
section = None
for table in tables:
    if "retries" in columns(table[0]):
        section = table
        break

if section is None:
    headers = ["|".join(t[0]) for t in tables]
    problems.append(
        "want a table with a stuck-retries column, the report has tables headed: %s"
        % (", ".join(repr(h) for h in headers) or "nothing"))
    print("\n".join(problems))
    raise SystemExit(0)

header, body = section[0], section[1:]
column = columns(header)
for i, cell in enumerate(header):
    hit = [w for w in WANTED if NEEDLE[w] in cell.lower()]
    if len(hit) > 1:
        problems.append(
            "header cell %r names %s at once, want one column each" % (cell, " and ".join(hit)))
for want in WANTED:
    if want not in column:
        problems.append("want a %s column in the per-step section, its header row is %r"
                        % (want, " | ".join(header)))

labels = [r[0] for r in body if r]
for arg in sys.argv[2:]:
    step, expected = arg.split("=", 1)
    row = next((r for r in body if r and r[0].strip().lower() == step.lower()), None)
    if row is None:
        problems.append("want a row for step %r in the per-step section, its rows are: %s"
                        % (step, ", ".join(repr(l) for l in labels) or "nothing"))
        continue
    for want, number in zip(WANTED, expected.split(",")):
        if want not in column:
            continue
        i = column[want]
        got = row[i] if i < len(row) else ""
        if got != number:
            problems.append("step %r %s: want %s, got %r" % (step, want, number, got))

print("\n".join(problems))
' "$out_file" "$@" 2>&1)"
  [[ -z "$said" ]] || while IFS= read -r line; do problems+=("$line"); done <<< "$said"
}

# A second fixture, in a directory of its own so the case above keeps the log it was written
# against. Two steps, because one step could not tell a per-step section from a per-issue
# total: the two rows are what make the section's key observable.
#
# `sv <step> <ts> <actor> <phase> <event> <attempt> [<trailing-json>]` is `ev` with the step
# as its first argument, since the step is the thing this fixture varies. Same line shape,
# hand-written for the same reason.
step_work="$(mktemp -d)"
trap 'rm -rf "$work" "$step_work"' EXIT
mkdir -p "$step_work/.tdd"

sv() {
  printf '{"ts": %s, "issue": "108", "actor": "%s", "phase": "%s", "step": "%s", "event": "%s", "attempt": "%s", "skill_commit": "c0ffee1"%s}\n' \
    "$2" "$3" "$4" "$1" "$5" "$6" "${7:+, ${7}}" >> "$step_work/.tdd/events.jsonl"
}

one="metrics.sh renders a markdown table of per-phase counts"
two="the table carries a per-step section with the same counts"

# Step one, clean: red and green each a developer leaf, a verifier and a PASS.
# 4 attempts, 2 PASS, 0 REJECT, 0 kills, 0 stuck retries.
sv "$one" 2000 conductor ""    step-start ""
sv "$one" 2010 developer red   launch  1 '"name": "develop-red"'
sv "$one" 2100 developer red   exit    1 '"status": "0", "secs": "90"'
sv "$one" 2110 verifier  red   launch  1 '"name": "verify-red"'
sv "$one" 2130 verifier  red   exit    1 '"status": "0", "secs": "20"'
sv "$one" 2130 verifier  red   verdict 1 '"verdict": "PASS", "reason": "the case fails as written"'
sv "$one" 2200 developer green launch  1 '"name": "develop-green"'
sv "$one" 2300 developer green exit    1 '"status": "0", "secs": "100"'
sv "$one" 2310 verifier  green launch  1 '"name": "verify-green"'
sv "$one" 2330 verifier  green exit    1 '"status": "0", "secs": "20"'
sv "$one" 2330 verifier  green verdict 1 '"verdict": "PASS", "reason": "the step is pinned and no wider"'
sv "$one" 2340 conductor ""    step-done ""

# Step two, the expensive one: a rejected Green, three leaves the watchdog killed — two of
# them after retrying, one of them twice — and a second REJECT at the end.
# 9 attempts, 1 PASS, 2 REJECT, 3 kills, 4 stuck retries.
#
# The `retry` marks are supervise.sh's own (supervise.sh:311): one per relaunch of a leaf
# that went quiet, written INSIDE its retry loop where `launch` is written outside it. That
# is what makes retries a count of their own rather than a second reading of attempts or of
# kills — and why the five numbers above are five distinct pairs across the two rows, so a
# section that printed any one column in another's place cannot pass.
sv "$two" 2400 conductor ""    step-start ""
sv "$two" 2410 developer red   launch  1 '"name": "develop-red"'
sv "$two" 2500 developer red   exit    1 '"status": "0", "secs": "90"'
sv "$two" 2510 verifier  red   launch  1 '"name": "verify-red"'
sv "$two" 2530 verifier  red   exit    1 '"status": "0", "secs": "20"'
sv "$two" 2530 verifier  red   verdict 1 '"verdict": "PASS", "reason": "the case fails as written"'
sv "$two" 2600 developer green launch  1 '"name": "develop-green"'
sv "$two" 2700 developer green exit    1 '"status": "0", "secs": "100"'
sv "$two" 2710 verifier  green launch  1 '"name": "verify-green"'
sv "$two" 2730 verifier  green exit    1 '"status": "0", "secs": "20"'
sv "$two" 2730 verifier  green verdict 1 '"verdict": "REJECT", "reason": "the production change is wider than the case asks for"'
sv "$two" 2740 developer green launch  2 '"name": "revise-green-2"'
sv "$two" 2800 developer green retry   2 '"cause": "no heartbeat for 300s (window 120s)"'
sv "$two" 2860 developer green exit    2 '"status": "2", "cause": "no heartbeat for 300s (window 120s)", "secs": "120"'
sv "$two" 2870 developer green launch  2 '"name": "revise-green-2"'
sv "$two" 2930 developer green retry   2 '"cause": "no heartbeat for 300s (window 120s)"'
sv "$two" 2990 developer green retry   2 '"cause": "hard timeout 1200s exceeded"'
sv "$two" 3050 developer green exit    2 '"status": "2", "cause": "hard timeout 1200s exceeded", "secs": "180"'
sv "$two" 3060 developer green launch  2 '"name": "revise-green-2"'
sv "$two" 3120 developer green retry   2 '"cause": "no heartbeat for 300s (window 120s)"'
sv "$two" 3180 developer green exit    2 '"status": "2", "cause": "no heartbeat for 300s (window 120s)", "secs": "120"'
sv "$two" 3190 developer green launch  2 '"name": "revise-green-2"'
sv "$two" 3250 developer green exit    2 '"status": "0", "secs": "60"'
sv "$two" 3260 verifier  green launch  2 '"name": "verify-green"'
sv "$two" 3280 verifier  green exit    2 '"status": "0", "secs": "20"'
sv "$two" 3280 verifier  green verdict 2 '"verdict": "REJECT", "reason": "a second criterion was pinned in passing"'


name="a two-step log renders a per-step section with each step's counts and stuck retries"
problems=()

step_out="$step_work/report.md"
( cd "$step_work" && "$METRICS" 108 ) > "$step_out" 2>/dev/null
status=$?

[[ "$status" -eq 0 ]] ||
  problems+=("want metrics.sh to exit 0, it exited $status")

step_table_says "$step_out" "$one=4,2,0,0,0" "$two=9,1,2,3,4"

[[ "${#problems[@]}" -eq 0 ]] ||
  problems+=("the report was: $(printf '%q' "$(cat "$step_out")")")

report "$name"


echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
