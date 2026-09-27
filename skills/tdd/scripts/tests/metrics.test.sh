#!/usr/bin/env bash
# Unit tests for scripts/metrics.sh — the per-issue metrics report computed from the run's
# event log (issue #108, and #107/ADR-0014 before it: observability is a per-run event log
# written by the scripts, not a service). Zero-dependency plain-shell asserts, same idiom as
# event.test.sh and harvest-usage.test.sh, its two nearest neighbours: all three are about
# lines somebody else wrote into `.tdd/events.jsonl`.
#
# Contract under test, one case per section of the report:
#   metrics.sh <n>  → exit 0, and on stdout a row per phase of the run carrying that phase's
#                     attempts, PASS verdicts, REJECT verdicts and kills, and a row per step
#                     carrying the same four plus the stuck retries that step used and the
#                     no-verdict relaunches its verifiers spent (#219) — a count of its own,
#                     neither a retry nor a revise.
#
# The log is read relative to the directory the script runs in — `.tdd/events.jsonl`, the
# way event.sh writes it (event.sh:60) and the way supervise.sh already spells `.tdd/<name>.log`
# — so each case below writes a hand-made log into a temp directory and runs the script there.
#
# Which line of the log each of the four counts is read off, and why a kill is counted apart
# from a verdict, is metrics.sh's own header — with the writer and line number for each. It
# is not restated here: the same paragraph in two files is the same paragraph to keep
# correct twice, and a `supervise.sh:297` that moves would go stale in whichever copy
# nobody was editing.
#
# What is not pinned here is whatever `.tdd/issue-108.md` still has unchecked — budgets,
# time, cost, rework and waste, progress, the unknown-rather-than-zero rule. That list is not
# copied here: the ledger is where it is kept correct, and a copy would go stale on the step
# after the one that wrote it. And one thing this file moves that is pinned elsewhere:
# CLAUDE.md's suite count, which claude-md-counts.test.sh case 1 holds to the files on disk
# and which goes red by itself the moment this file lands uncounted.
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
  probes_run
  if [[ "${#problems[@]}" -eq 0 ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1))
    echo "FAIL - $name"
    printf '    %s\n' "${problems[@]}"
  fi
}

# report_on <name> <out-file> — close a case, quoting the whole report as a last problem when
# the case failed. The report is attached after the probes have had their say, so the output
# reads as the disagreements first and the document they were read out of last, and it is
# attached only on a failure, since a passing case has nothing to read.
report_on() {
  local name="$1" out_file="$2"
  probes_run
  [[ "${#problems[@]}" -eq 0 ]] ||
    problems+=("the report was: $(printf '%q' "$(cat "$out_file")")")
  report "$name"
}

# render <dir> <out-file> — run the script in a fixture directory, catch its report, and put
# a non-zero exit onto the caller's `problems`. Every case opens with this: the script reads
# `.tdd/events.jsonl` relative to where it runs, so a case is a directory to run in, and an
# exit other than 0 is a complaint before any probe of what was printed.
render() {
  local dir="$1" out_file="$2" status
  ( cd "$dir" && "$METRICS" 108 ) > "$out_file" 2>/dev/null
  status=$?
  [[ "$status" -eq 0 ]] ||
    problems+=("want metrics.sh to exit 0, it exited $status")
}

# probe <program> <arg>… — queue one python probe over a rendered report; `probes_run` later
# puts every line it prints onto the caller's `problems`, nothing when it prints nothing. Each
# probe below is a program that reports its disagreements on stdout and says nothing when it
# has none, so what differs between them is the program and its arguments; how the lines are
# captured, that stderr counts as a complaint too, and that an empty answer adds no empty
# problem are one rule, kept here once.
#
# Queued rather than run (#331): a `python3 -c` per assertion was 51 interpreter starts per
# run of this suite. The queue is a spool file of NUL-separated fields — the program, its
# argument count, its arguments — since a NUL is the one byte neither can hold.
probe() {
  printf '%s\0' "$1" "$(($# - 1))" "${@:2}" >> "$probe_spool"
}

# probes_run — run every queued probe in one python3, each as `python3 -c` would: its own
# globals, its own sys.argv, stdout and stderr caught together, a SystemExit ending only that
# probe. Called by report and report_on before they read `problems`, so a case's probes
# answer in the order they were queued, and the spool is emptied for the next case.
probes_run() {
  [[ -s "$probe_spool" ]] || return 0
  local said
  said="$(python3 -c '
import contextlib, io, sys, traceback
fields = open(sys.argv[1], "rb").read().decode().split("\0")[:-1]
while fields:
    program, count = fields[0], int(fields[1])
    args, fields = fields[2:2 + count], fields[2 + count:]
    sys.argv = ["-c"] + args
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        try:
            exec(compile(program, "<string>", "exec"), {"__name__": "__main__"})
        except SystemExit as stop:
            if stop.code is not None and not isinstance(stop.code, int):
                print(stop.code, file=sys.stderr)
        except BaseException:
            traceback.print_exc()
    said = buf.getvalue().rstrip("\n")
    if said:
        print(said)
' "$probe_spool" 2>&1)"
  : > "$probe_spool"
  [[ -z "$said" ]] || while IFS= read -r line; do problems+=("$line"); done <<< "$said"
}

# PROBE_PRELUDE — what every probe below opens with, so the report is split into tables, a
# row is found, a column is found and a disagreement is recorded in exactly one place each.
#
# `tables_in(path)` returns every run of consecutive table lines as a list of rows, each row
# a list of stripped cells, with the `---|---:` separator rows dropped: a report with a
# per-phase section and a per-step section has two such runs, and a blank line or a heading
# between them is what separates them.
#
# `complain(text)` puts one disagreement on `problems`, ignoring a repeat of one already
# there: several rows of one table raise the same missing-column line, and the same sentence
# twice says nothing the first did not.
#
# `table_with(tables, key)` is the first table holding a row for `key`, and `is_row` is what
# a row for a key is — its first cell, matched outright, except `total`, which matches any
# row LABELLED with the word and nothing else of substance so the report is free to head it
# `total`, `Total`, `issue total` or `totals`. Matched as a whole label rather than as a
# substring because a step name is a sentence, and a sentence that happens to say the word
# would otherwise be picked up as the row of the whole run.
#
# `column(header, name, matches, key)` is the one column of a header whose cell satisfies
# `matches`, complaining and returning None when the header gives it none or two. Locating a
# table by its ROWS and its columns by their HEADINGS is what keeps these probes from pinning
# either order.
#
# `number(cell)` is what a cell says as a figure, or None when it says no figure at all: a
# `$`, thousands commas and a trailing unit are the report's own to print or leave out, so
# every probe comparing money or seconds compares numbers and not the text around them.
#
# `money(heading)` is whether a lowercased heading cell names money rather than a count. Two
# probes ask it of two different tables — the cost section's one `$` column, and the rework
# section's money half of each pair — and a report free to head the column `$`, `cost`,
# `dollars` or `usd` is a report whose headings only one list of those words can recognise.
#
# `located(tables, key, what, find)` is the pair a probe reads a row out of — the header of
# the table `find` picked and the row in it for `key` — or `(None, None)` after complaining
# that the report has no such table, listing the rows of the tables it does have. `find` is a
# parameter because one probe looks for a table by its rows alone and another has to look for
# a table by its rows AND its subject; everything after that search is the same three lines
# in every probe, and they are here rather than three times over.
#
# `cell_in(tables, key, name, matches)` goes one step further for a probe that reads a single
# column: the stripped cell of `key`'s row under the one heading `matches` picks, or `None`
# after `located` or `column` has complained. A row too short to reach the column reads as
# an empty cell rather than a crash.
#
# It is a shell variable because that is the only way several `python3 -c` programs can share
# a definition without a file of their own. Each call site concatenates its double-quoted
# expansion with the single-quoted rest of its program, so the rest keeps the quoting it
# already had and no dollar sign of python reaches the shell: the one anchoring the separator
# regex lives in here, inside single quotes, expanded by nobody.
PROBE_PRELUDE='
import re, sys

SEPARATOR = re.compile(r"^:?-+:?$")

def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]

def tables_in(path):
    tables, current = [], []
    for line in open(path).read().splitlines():
        if line.strip().startswith("|"):
            row = cells(line)
            if not all(SEPARATOR.match(c) for c in row if c):
                current.append(row)
        elif current:
            tables.append(current)
            current = []
    if current:
        tables.append(current)
    return tables

problems = []

def complain(text):
    if text not in problems:
        problems.append(text)

TOTAL = re.compile(r"(issue |run |grand )?totals?")

def is_row(row, key):
    if not row:
        return False
    cell = row[0].strip()
    return bool(TOTAL.fullmatch(cell.lower())) if key == "total" else cell == key

def table_with(tables, key):
    for t in tables:
        if any(is_row(r, key) for r in t[1:]):
            return t
    return None

def column(header, name, matches, key):
    hit = [i for i, c in enumerate(header) if matches(c.lower())]
    if len(hit) == 1:
        return hit[0]
    complain("want exactly one column heading saying %s, the table with a row for %r is headed: %s"
             % (name, key, "|".join(header) or "nothing"))
    return None

def number(cell):
    text = cell.strip().replace("$", "").replace(",", "").rstrip("s").strip()
    try:
        return float(text)
    except ValueError:
        return None

def money(heading):
    return any(w in heading for w in ("$", "cost", "dollar", "usd"))

def outside_tables(path):
    return [l.strip() for l in open(path).read().splitlines()
            if l.strip() and not l.strip().startswith("|")]

def outcome_lines(path):
    return [l for l in outside_tables(path) if l.startswith("Outcome:")]

def quoted(said):
    return ", ".join(repr(l) for l in said) or "nothing"

def located(tables, key, what, find):
    section = find(tables, key)
    if section is None:
        labels = [", ".join(repr(r[0]) for r in t[1:] if r) for t in tables]
        complain("want %s with a row for %r, the report has tables with rows: %s"
                 % (what, key, "; ".join(labels) or "nothing"))
        return None, None
    return section[0], next(r for r in section[1:] if is_row(r, key))

def cell_in(tables, key, name, matches):
    header, row = located(tables, key, "a table", table_with)
    if row is None:
        return None
    i = column(header, name, matches, key)
    if i is None:
        return None
    return row[i].strip() if i < len(row) else ""
'

# counts_table_says <file> <noun> <columns> <key>=<n>,<n>,… — read a counts table out of the
# rendered report and complain, one line per disagreement, onto the caller's `problems`.
# <columns> is a comma-separated list of the counts the table must carry, in the order the
# expectations spell them; <noun> is what one of its rows is, for the diagnostics.
#
# The table is located by what it CARRIES rather than by a heading or a position: the first
# table in the report whose header gives every wanted count a column of its own. That leaves
# the implementation free to head its sections however it likes and to order the columns
# however it likes — what this pins is that the counts exist and are right, which is the
# step. A count named in two header cells at once gives that count no column of its own, so
# such a table is not the section and the search moves on: ambiguity is a failure rather
# than a guess.
#
# The columns are then located by reading the header row rather than by position, and rows
# are matched on their first cell against the key, so neither the column order nor the row
# order is pinned.
#
# python3 rather than awk: extract-result.sh and event.sh already exec it in production, so
# the interpreter is a dependency this repo has, and the parse is fail-closed in one place.
counts_table_says() {
  local out_file="$1" noun="$2" columns="$3"; shift 3
  probe "$PROBE_PRELUDE"'
NEEDLE = {"attempts": "attempt", "pass": "pass", "reject": "reject",
          "kills": "kill", "retries": "retr", "no-verdict": "verdict"}

noun, wanted, path = sys.argv[1], sys.argv[2].split(","), sys.argv[3]
tables = tables_in(path)

def columns(header):
    found = {}
    for i, cell in enumerate(header):
        hit = [w for w in wanted if NEEDLE[w] in cell.lower()]
        if len(hit) == 1:
            found.setdefault(hit[0], i)
    return found

problems = []
section = next((t for t in tables if len(columns(t[0])) == len(wanted)), None)
if section is None:
    headers = ["|".join(t[0]) for t in tables]
    problems.append(
        "want a table giving each of %s a column of its own, the report has tables headed: %s"
        % (", ".join(wanted), ", ".join(repr(h) for h in headers) or "nothing"))
    print("\n".join(problems))
    raise SystemExit(0)

header, body = section[0], section[1:]
column = columns(header)

labels = [r[0] for r in body if r]
for arg in sys.argv[4:]:
    key, expected = arg.split("=", 1)
    row = next((r for r in body if r and r[0].strip().lower() == key.lower()), None)
    if row is None:
        problems.append("want a row for %s %r, the table has rows for: %s"
                        % (noun, key, ", ".join(repr(l) for l in labels) or "nothing"))
        continue
    for want, number in zip(wanted, expected.split(",")):
        i = column[want]
        got = row[i] if i < len(row) else ""
        if got != number:
            problems.append("%s %r %s: want %s, got %r" % (noun, key, want, number, got))

print("\n".join(problems))
' "$noun" "$columns" "$out_file" "$@"
}

# table_says <file> <phase>=<attempts>,<pass>,<reject>,<kills> … — the per-phase section.
# It is the first table in the report carrying those four counts; the per-step section
# carries them too, but comes second and is reached by its retries column instead.
table_says() {
  local out_file="$1"; shift
  counts_table_says "$out_file" phase attempts,pass,reject,kills "$@"
}

# fixture_work <var> — make a temp directory with the `.tdd/` a fixture log lives in, and
# bind <var> to it. Each fixture gets one of its own so every case keeps the log it was
# written against, and each is registered here for the one trap that removes them all: the
# array is what lets a fixture added later be cleaned up by existing, where a trap restated
# per fixture was a list of directories to keep in sync by hand, three deep by the third one.
#
# It takes the variable's NAME and assigns it, rather than printing the directory for a
# `$(...)` to catch: a command substitution runs in a subshell, so the append below would
# happen in a shell that exits immediately and the trap here would find an empty list and
# remove nothing.
#
# The guard before `rm` is the fail-closed half — an empty array under `set -u` is not a
# reason to run `rm -rf` on an unexpanded word.
fixture_works=()
trap '[[ "${#fixture_works[@]}" -eq 0 ]] || rm -rf "${fixture_works[@]}"' EXIT

probe_spool="$(mktemp)"
fixture_works+=("$probe_spool")

fixture_work() {
  local dir
  dir="$(mktemp -d)"
  mkdir -p "$dir/.tdd"
  fixture_works+=("$dir")
  printf -v "$1" '%s' "$dir"
  fixture_log="$dir/.tdd/events.jsonl"
}

fixture_work work

# event_line <log> <ts> <actor> <phase> <step> <event> <attempt> [<trailing-json>] — one
# hand-written line of a fixture log, in the shape event.sh emits: the eight fixed context
# keys, then the payload. Hand-written rather than produced by running event.sh, so this
# suite's subject stays the reader and a change to the writer cannot quietly rewrite the
# input being read. The trailing json is the payload's own `"key": "value"` pairs and nothing
# else: the comma joining them to the context keys is added here, once, so no caller spells
# a piece of json syntax and the writer below carries no rule of its own.
event_line() {
  local log="$1"; shift
  printf '{"ts": %s, "issue": "108", "actor": "%s", "phase": "%s", "step": "%s", "event": "%s", "attempt": "%s", "skill_commit": "c0ffee1"%s}\n' \
    "$1" "$2" "$3" "$4" "$5" "$6" "${7:+, ${7}}" >> "$log"
}

# sv <step> <ts> <actor> <phase> <event> <attempt> [<trailing-json>] — a line of whichever
# fixture was made last, since `fixture_work` points `fixture_log` at the log it just made and
# each fixture below is filled in immediately after it is made. The step comes first because
# it is what a multi-step fixture varies line by line.
#
# One writer rather than one per fixture: a fixture named its own log, so a fixture added
# later owed a wrapper of its own that differed from the last only in that name, and four
# copies of one argument order were four places for it to go wrong.
sv() {
  event_line "$fixture_log" "$2" "$3" "$4" "$1" "$5" "$6" "${7:-}"
}

# ev <ts> <actor> <phase> <event> <attempt> [<trailing-json>] — a line of the first fixture,
# whose step never varies.
step="metrics.sh renders a markdown table of per-phase counts"
ev() {
  sv "$step" "$@"
}

# The first fixture: one step, two phases — a run whose Green was rejected twice and whose
# leaves were killed three times. Its case reads the per-phase section.
#
# The row key there is the log's own `phase` field rather than the leaf's name, so a
# developer leaf and the verifier that judged it land in one row. A table keyed by leaf name
# would have PASS and REJECT structurally zero for every `develop-*` row, and this case could
# not tell a script that counted verdicts from one that did not.
#
# The fixture is built so no two columns can be confused for one another: red reads 2/1/0/0
# and green reads 9/1/2/3, so the four columns hold four distinct pairs of numbers across the
# two rows. A script that swapped two of them cannot pass this case.
#
# The conductor's own `step-start` and `step-done` marks are in it too, carrying an empty
# phase. They are neither launches nor verdicts nor exits, so they must contribute to nothing
# and must not raise a row of their own.

# The conductor's own marks, phase-less: neither launch nor verdict nor exit, so they must
# raise no row and change no count.
ev 990 conductor "" step-start ""

# Red: one developer leaf, one verifier, one PASS. 2 attempts, 1 PASS, 0 REJECT, 0 kills.
ev 1000 developer red launch 1 '"name": "develop-red", "cmd": "run-leaf.sh", "model": ""'
ev 1100 developer red exit   1 '"status": "0", "secs": "100"'
ev 1110 verifier  red launch 1 '"name": "verify-red", "cmd": "run-leaf.sh", "model": ""'
ev 1130 verifier  red exit   1 '"status": "0", "secs": "20"'
ev 1130 verifier  red verdict 1 '"verdict": "PASS", "reason": "the case fails for the reason it was written to catch"'

# Green: two REJECTs and the revises that answered them, three killed leaves in the middle,
# and a PASS at the end. 9 attempts, 1 PASS, 2 REJECT, 3 kills.
ev 1200 developer green launch 1 '"name": "develop-green", "cmd": "run-leaf.sh", "model": ""'
ev 1300 developer green exit   1 '"status": "0", "secs": "100"'
ev 1310 verifier  green launch 1 '"name": "verify-green", "cmd": "run-leaf.sh", "model": ""'
ev 1330 verifier  green exit   1 '"status": "0", "secs": "20"'
ev 1330 verifier  green verdict 1 '"verdict": "REJECT", "reason": "the production change is wider than the case asks for"'
ev 1340 developer green launch 2 '"name": "revise-green-2", "cmd": "run-leaf.sh", "model": ""'
ev 1400 developer green exit   2 '"status": "0", "secs": "60"'
ev 1410 verifier  green launch 2 '"name": "verify-green", "cmd": "run-leaf.sh", "model": ""'
ev 1430 verifier  green exit   2 '"status": "0", "secs": "20"'
ev 1430 verifier  green verdict 2 '"verdict": "REJECT", "reason": "a second criterion was pinned in passing"'
ev 1440 developer green launch 3 '"name": "revise-green-3", "cmd": "run-leaf.sh", "model": ""'
ev 1500 developer green exit   3 '"status": "2", "cause": "no heartbeat for 300s (window 120s)", "secs": "60"'
ev 1510 developer green launch 3 '"name": "revise-green-3", "cmd": "run-leaf.sh", "model": ""'
ev 1570 developer green exit   3 '"status": "2", "cause": "no heartbeat for 300s (window 120s)", "secs": "60"'
ev 1580 developer green launch 3 '"name": "revise-green-3", "cmd": "run-leaf.sh", "model": ""'
ev 1640 developer green exit   3 '"status": "2", "cause": "hard timeout 1200s exceeded", "secs": "60"'
ev 1650 developer green launch 3 '"name": "revise-green-3", "cmd": "run-leaf.sh", "model": ""'
ev 1700 developer green exit   3 '"status": "0", "secs": "50"'
ev 1710 verifier  green launch 3 '"name": "verify-green", "cmd": "run-leaf.sh", "model": ""'
ev 1730 verifier  green exit   3 '"status": "0", "secs": "20"'
ev 1730 verifier  green verdict 3 '"verdict": "PASS", "reason": "the step is now pinned and no wider"'

ev 1740 conductor "" step-done ""


name="a two-phase log renders one row per phase with its attempts, PASS, REJECT and kills"
problems=()

out_file="$work/report.md"
render "$work" "$out_file"

table_says "$out_file" red=2,1,0,0 green=9,1,2,3

report_on "$name" "$out_file"


# step_table_says <file> <step>=<attempts>,<pass>,<reject>,<kills>,<retries> … — the
# per-step section, located by its stuck-retries column, since only that section has those
# counts. Rows are matched on their first cell against the step's own name, the string
# event.sh writes into every line's `step` field.
step_table_says() {
  local out_file="$1"; shift
  counts_table_says "$out_file" step attempts,pass,reject,kills,retries "$@"
}

# A second fixture, in a directory of its own so the case above keeps the log it was written
# against. Two steps, because one step could not tell a per-step section from a per-issue
# total: the two rows are what make the section's key observable.
#
# The lines are written with `sv`, which takes the step as its first argument since the step
# is the thing this fixture varies.
fixture_work step_work

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
render "$step_work" "$step_out"

step_table_says "$step_out" "$one=4,2,0,0,0" "$two=9,1,2,3,4"

report_on "$name" "$step_out"


# budgets_say <file> <step-one> <step-two> <label>=<cell> … — the third section's subject:
# the two budgets a step spends, and whether the refactor loop stopped because it ran out of
# one. The expectations are read against BOTH steps' rows, `<label>` naming which figure is
# wanted for the diagnostics and `<cell>` the exact cell text; the arguments for the second
# step follow a literal `--`.
#
# The `used/budget` spelling is the house's own, not this suite's invention:
# refactor-budget.sh prints `refactor 2/5` and SKILL.md narrates a revise as
# `attempt <k>/<REVISE_BUDGET>`, so the pair travels as one cell. What is NOT pinned is
# where that cell sits: the row is found by its step name in any table carrying both steps,
# and each value by scanning that row's cells, so neither column order nor the heading is
# fixed.
#
# Whether the loop stopped by budget is pinned as a column whose heading says `stop`, and
# only in the two ways it can be observed at all: the two steps must not say the same thing
# — a constant is not a report — and the step that did run out must mention the budget in
# its heading-plus-cell, which passes both a `budget` cell under a `stopped by` heading and
# a `yes` under `stopped by budget`.
budgets_say() {
  local out_file="$1" one="$2" two="$3"; shift 3
  probe "$PROBE_PRELUDE"'
path, steps = sys.argv[1], (sys.argv[2], sys.argv[3])
tables = tables_in(path)

# The expectations, one list per step, split on the literal `--` that separates them.
wanted, rest = [[]], sys.argv[4:]
for arg in rest:
    if arg == "--":
        wanted.append([])
    else:
        wanted[-1].append(arg.split("=", 1))

def row_for(table, step):
    return next((r for r in table[1:] if r and r[0].strip() == step), None)

section = next((t for t in tables
                if all(row_for(t, s) is not None for s in steps)), None)
if section is None:
    labels = [", ".join(repr(r[0]) for r in t[1:] if r) for t in tables]
    problems.append(
        "want one table with a row for each of %s, the report has tables with rows: %s"
        % (" and ".join(repr(s) for s in steps), "; ".join(labels) or "nothing"))
    print("\n".join(problems))
    raise SystemExit(0)

header = section[0]
rows = [row_for(section, s) for s in steps]

for step, row, expectations in zip(steps, rows, wanted):
    for label, value in expectations:
        if value not in [c.strip() for c in row[1:]]:
            problems.append("step %r %s: want a cell %r, the row has cells: %s"
                            % (step, label, value,
                               ", ".join(repr(c) for c in row[1:]) or "nothing"))

stop = [i for i, c in enumerate(header) if "stop" in c.lower()]
if len(stop) != 1:
    problems.append(
        "want exactly one column heading saying whether the refactor loop stopped, the table is headed: %s"
        % ("|".join(header) or "nothing"))
else:
    i = stop[0]
    said = [r[i].strip() if i < len(r) else "" for r in rows]
    if said[0] == said[1]:
        problems.append(
            "the two steps stopped differently, the column says %r for both" % said[0])
    if "budget" not in ("%s %s" % (header[i], said[1])).lower():
        problems.append(
            "step %r spent its refactor budget, its %r cell says %r — neither mentions the budget"
            % (steps[1], header[i], said[1]))

print("\n".join(problems))
' "$out_file" "$one" "$two" "$@"
}

# A third fixture, in its own directory for the same reason the second has one: the cases
# above keep the logs they were written against.
#
# Two steps again, and here they are what makes the figures observable at all — a report
# that printed one constant per column would satisfy a one-step fixture. The first step is
# revised once of a budget of three and its refactor stops with work left undone; the second
# spends both budgets to the last unit and stops because the refactor budget ran out.
#
# The four cells are four distinct strings — 1/3, 2/5, 3/3, 5/5 — so a report that printed
# the revise figure in the refactor column, or one step's row in the other's place, cannot
# pass. `3` rather than the default `2` for REVISE_BUDGET, and both budgets read off the log
# line rather than the environment: the report is rendered wherever the file is committed,
# which is not necessarily the shell the run was configured in.
#
# Two marks in the fixture are the conductor's, and only one of them exists today:
#   `revise budget=<REVISE_BUDGET>` is prescribed at SKILL.md:875, one per revise attempt,
#   carrying the budget that attempt was counted against.
#   `refactor transforms=<n> budget=<VERI_REFACTOR_BUDGET> stopped=<why>` is the mark the
#   refactor narration owes (SKILL.md's "Narrate + branch" already tells the conductor to
#   say all three, against `git rev-list --count`, so the mark is that sentence written to
#   the log as well as to the thread). A run whose conductor never writes it has no figure
#   to report, which is the unknown-rather-than-zero rule a later step of the ledger owns —
#   this case is about a run that did write it.
fixture_work budget_work

frugal="the table reports revise attempts used of REVISE_BUDGET and refactor transforms used"
spendthrift="the table reports wall seconds and API seconds per phase and per step"

# Step one: one REJECT answered by one revise of three, then a refactor that applied two
# transforms of five and stopped with nothing structural left to tidy.
sv "$frugal" 4000 conductor ""       step-start ""
sv "$frugal" 4010 developer red      launch  1 '"name": "develop-red"'
sv "$frugal" 4100 developer red      exit    1 '"status": "0", "secs": "90"'
sv "$frugal" 4110 verifier  red      launch  1 '"name": "verify-red"'
sv "$frugal" 4130 verifier  red      exit    1 '"status": "0", "secs": "20"'
sv "$frugal" 4130 verifier  red      verdict 1 '"verdict": "PASS", "reason": "the case fails as written"'
sv "$frugal" 4200 developer green    launch  1 '"name": "develop-green"'
sv "$frugal" 4300 developer green    exit    1 '"status": "0", "secs": "100"'
sv "$frugal" 4310 verifier  green    launch  1 '"name": "verify-green"'
sv "$frugal" 4330 verifier  green    exit    1 '"status": "0", "secs": "20"'
sv "$frugal" 4330 verifier  green    verdict 1 '"verdict": "REJECT", "reason": "the production change is wider than the case asks for"'
sv "$frugal" 4340 conductor green    revise  1 '"budget": "3"'
sv "$frugal" 4350 developer green    launch  2 '"name": "revise-green-1"'
sv "$frugal" 4410 developer green    exit    2 '"status": "0", "secs": "60"'
sv "$frugal" 4420 verifier  green    launch  2 '"name": "verify-green"'
sv "$frugal" 4440 verifier  green    exit    2 '"status": "0", "secs": "20"'
sv "$frugal" 4440 verifier  green    verdict 2 '"verdict": "PASS", "reason": "the step is pinned and no wider"'
sv "$frugal" 4450 developer refactor launch  1 '"name": "develop-refactor"'
sv "$frugal" 4600 developer refactor exit    1 '"status": "0", "secs": "150"'
sv "$frugal" 4610 conductor refactor refactor "" '"transforms": "2", "budget": "5", "stopped": "nothing left to tidy"'
sv "$frugal" 4620 verifier  refactor launch  1 '"name": "verify-refactor"'
sv "$frugal" 4640 verifier  refactor exit    1 '"status": "0", "secs": "20"'
sv "$frugal" 4640 verifier  refactor verdict 1 '"verdict": "PASS", "reason": "behaviour is preserved"'
sv "$frugal" 4650 conductor ""       step-done ""

# Step two: three REJECTs and the three revises that answered them — the whole budget — and
# a refactor that applied five transforms of five and stopped because that budget was spent.
sv "$spendthrift" 5000 conductor ""       step-start ""
sv "$spendthrift" 5010 developer red      launch  1 '"name": "develop-red"'
sv "$spendthrift" 5100 developer red      exit    1 '"status": "0", "secs": "90"'
sv "$spendthrift" 5110 verifier  red      launch  1 '"name": "verify-red"'
sv "$spendthrift" 5130 verifier  red      exit    1 '"status": "0", "secs": "20"'
sv "$spendthrift" 5130 verifier  red      verdict 1 '"verdict": "PASS", "reason": "the case fails as written"'
sv "$spendthrift" 5200 developer green    launch  1 '"name": "develop-green"'
sv "$spendthrift" 5300 developer green    exit    1 '"status": "0", "secs": "100"'
sv "$spendthrift" 5310 verifier  green    launch  1 '"name": "verify-green"'
sv "$spendthrift" 5330 verifier  green    exit    1 '"status": "0", "secs": "20"'
sv "$spendthrift" 5330 verifier  green    verdict 1 '"verdict": "REJECT", "reason": "the production change is wider than the case asks for"'
sv "$spendthrift" 5340 conductor green    revise  1 '"budget": "3"'
sv "$spendthrift" 5350 developer green    launch  2 '"name": "revise-green-1"'
sv "$spendthrift" 5410 developer green    exit    2 '"status": "0", "secs": "60"'
sv "$spendthrift" 5420 verifier  green    launch  2 '"name": "verify-green"'
sv "$spendthrift" 5440 verifier  green    exit    2 '"status": "0", "secs": "20"'
sv "$spendthrift" 5440 verifier  green    verdict 2 '"verdict": "REJECT", "reason": "a second criterion was pinned in passing"'
sv "$spendthrift" 5450 conductor green    revise  2 '"budget": "3"'
sv "$spendthrift" 5460 developer green    launch  3 '"name": "revise-green-2"'
sv "$spendthrift" 5520 developer green    exit    3 '"status": "0", "secs": "60"'
sv "$spendthrift" 5530 verifier  green    launch  3 '"name": "verify-green"'
sv "$spendthrift" 5550 verifier  green    exit    3 '"status": "0", "secs": "20"'
sv "$spendthrift" 5550 verifier  green    verdict 3 '"verdict": "REJECT", "reason": "the case was weakened rather than answered"'
sv "$spendthrift" 5560 conductor green    revise  3 '"budget": "3"'
sv "$spendthrift" 5570 developer green    launch  4 '"name": "revise-green-3"'
sv "$spendthrift" 5630 developer green    exit    4 '"status": "0", "secs": "60"'
sv "$spendthrift" 5640 verifier  green    launch  4 '"name": "verify-green"'
sv "$spendthrift" 5660 verifier  green    exit    4 '"status": "0", "secs": "20"'
sv "$spendthrift" 5660 verifier  green    verdict 4 '"verdict": "PASS", "reason": "the step is pinned and no wider"'
sv "$spendthrift" 5670 developer refactor launch  1 '"name": "develop-refactor"'
sv "$spendthrift" 5900 developer refactor exit    1 '"status": "0", "secs": "230"'
sv "$spendthrift" 5910 conductor refactor refactor "" '"transforms": "5", "budget": "5", "stopped": "budget"'
sv "$spendthrift" 5920 verifier  refactor launch  1 '"name": "verify-refactor"'
sv "$spendthrift" 5940 verifier  refactor exit    1 '"status": "0", "secs": "20"'
sv "$spendthrift" 5940 verifier  refactor verdict 1 '"verdict": "PASS", "reason": "behaviour is preserved"'
sv "$spendthrift" 5950 conductor ""       step-done ""


name="each step's row says the revise attempts and refactor transforms it used of their budgets, and whether the refactor loop stopped by budget"
problems=()

budget_out="$budget_work/report.md"
render "$budget_work" "$budget_out"

budgets_say "$budget_out" "$frugal" "$spendthrift" \
  revise=1/3 refactor=2/5 -- revise=3/3 refactor=5/5

report_on "$name" "$budget_out"


# times_say <file> <key>=<wall>,<api> … — the fourth section's subject: how long the run
# took. Each expectation names a row — a phase row or a step row, the two sections are
# searched alike — and the wall seconds and API seconds that row must carry.
#
# The table is located by the ROW, not by a heading or a position: the first table holding a
# row whose first cell is the key. Its wall column and its API column are then found by
# their headings, exactly one each, so neither column order nor the wording around the two
# words is pinned. A trailing `s` on a cell is accepted and stripped — `210` and `210s` are
# the same figure, and which one the report prints is not this step.
#
# Complaints are deduplicated because two rows of one table raise the same missing-column
# line, and the same sentence twice says nothing the first did not.
times_say() {
  local out_file="$1"; shift
  probe "$PROBE_PRELUDE"'
path = sys.argv[1]
tables = tables_in(path)

def seconds(cell):
    cell = cell.strip()
    return cell[:-1] if cell.endswith("s") else cell

for arg in sys.argv[2:]:
    key, expected = arg.split("=", 1)
    header, row = located(tables, key, "a table", table_with)
    if row is None:
        continue
    for word, number in zip(("wall", "api"), expected.split(",")):
        i = column(header, word, lambda c: word in c, key)
        if i is None:
            continue
        got = row[i] if i < len(row) else ""
        if seconds(got) != number:
            complain("%r %s seconds: want %s, got %r" % (key, word, number, got))

print("\n".join(problems))
' "$out_file" "$@"
}

# issue_wall_says <file> <seconds> — the one figure that belongs to no row: the whole issue
# from its first event to the mark that ended it. It is looked for on a line OUTSIDE the
# tables, since it is a total of the run rather than of a phase or a step, and matched on
# the number alone — the prose around it is the implementation to word.
issue_wall_says() {
  local out_file="$1" want="$2"
  probe '
import re, sys

path, want = sys.argv[1], sys.argv[2]
lines = [l for l in open(path).read().splitlines()
         if l.strip() and not l.strip().startswith("|")]

if any(re.search(r"(?<![0-9.])%s(?![0-9.])" % re.escape(want), l) for l in lines):
    raise SystemExit(0)

print("want a line outside the tables reporting the issue wall of %s seconds, the report says outside them: %s"
      % (want, ", ".join(repr(l.strip()) for l in lines) or "nothing"))
' "$out_file" "$want"
}

# issue_wall_line_says <file> <seconds> — issue_wall_says held to the one line that owns the
# figure: the wall-clock seconds must be on the "Wall time for the issue:" line itself, not
# merely somewhere outside the tables, where a wrong issue wall would pass so long as the
# number turned up on another line (#486).
issue_wall_line_says() {
  local out_file="$1" want="$2"
  probe '
import re, sys

path, want = sys.argv[1], sys.argv[2]
lines = [l.strip() for l in open(path).read().splitlines()
         if l.strip() and not l.strip().startswith("|")]
walls = [l for l in lines if l.startswith("Wall time for the issue:")]

if not walls:
    print("want a line starting \"Wall time for the issue:\", the report has none")
elif re.search(r"(?<![0-9.])%s(?![0-9.])" % re.escape(want), walls[0]) is None:
    print("want the issue wall to be the %s wall-clock seconds, it says: %r" % (want, walls[0]))
' "$out_file" "$want"
}

# A fourth fixture, in its own directory for the reason the others have one: each case keeps
# the log it was written against.
#
# Two steps, so a per-step figure is observable as something other than the issue total, and
# two phases in each, so a per-phase figure is observable as something other than a per-step
# one. Every figure the case reads is a distinct number — 210, 155, 390, 240, 400, 175, 600,
# 220, 1700 — so a report that printed wall where API belongs, or one row in the place of
# the other, cannot pass.
#
# Which line each figure is read off is the shape of the log, not a choice of this suite:
#
#   wall per phase — the `secs` supervise.sh writes on every `exit` (supervise.sh:355), the
#     wall seconds of one attempt. Summed over the phase. It is the `exit` and not the
#     `usage` line because a killed leaf writes one and no usage at all — the 70-second kill
#     in step two is in the fixture to say so, and a phase wall summed from `usage` is 70
#     seconds short of the number below.
#   API per phase — `duration_api_ms` off the leaf own closing record, which harvest-usage.sh
#     turns into the `usage` line. Milliseconds there, seconds here.
#   wall per step — `step-start` to `step-done`, the conductor two marks, which is the
#     stretch of the run the step occupied rather than the sum of what ran inside it: step
#     one spent 230 seconds of attempts inside a 400-second step.
#   issue wall — the first event of the log to the `done` mark that closed the run.
fixture_work time_work

# `usage_json <api-ms>` — the payload of one `usage` line, in the shape harvest-usage.sh
# emits (harvest-usage.sh:76-84): the leaf own four numbers and its four token counts, under
# the stream record own key names. Only `duration_api_ms` varies per call; the rest are
# there because a reader of this fixture should see the line a real run writes, and because
# a later step reads the other seven off the same line.
usage_json() {
  printf '"duration_ms": "0", "duration_api_ms": "%s", "num_turns": "9", "total_cost_usd": "0.5", "input_tokens": "1000", "output_tokens": "2000", "cache_read_input_tokens": "3000", "cache_creation_input_tokens": "4000"' "$1"
}

brisk="the table reports wall seconds and API seconds per phase and per step"
slow="the table reports turns, the four token counts and dollars per phase"

# Step one: red and green, each a developer leaf and a verifier, all four accounted for.
# red 90+20 = 110 wall, 70+15 = 85 API. green 100+20 = 120 wall, 80+10 = 90 API.
# The step itself ran 7000 to 7400 — 400 seconds — with 230 seconds of attempts inside it.
sv "$brisk" 7000 conductor ""    step-start ""
sv "$brisk" 7010 developer red   launch  1 '"name": "develop-red"'
sv "$brisk" 7100 developer red   exit    1 '"status": "0", "secs": "90"'
sv "$brisk" 7100 developer red   usage   1 "$(usage_json 70000)"
sv "$brisk" 7110 verifier  red   launch  1 '"name": "verify-red"'
sv "$brisk" 7130 verifier  red   exit    1 '"status": "0", "secs": "20"'
sv "$brisk" 7130 verifier  red   usage   1 "$(usage_json 15000)"
sv "$brisk" 7130 verifier  red   verdict 1 '"verdict": "PASS", "reason": "the case fails as written"'
sv "$brisk" 7200 developer green launch  1 '"name": "develop-green"'
sv "$brisk" 7300 developer green exit    1 '"status": "0", "secs": "100"'
sv "$brisk" 7300 developer green usage   1 "$(usage_json 80000)"
sv "$brisk" 7310 verifier  green launch  1 '"name": "verify-green"'
sv "$brisk" 7330 verifier  green exit    1 '"status": "0", "secs": "20"'
sv "$brisk" 7330 verifier  green usage   1 "$(usage_json 10000)"
sv "$brisk" 7330 verifier  green verdict 1 '"verdict": "PASS", "reason": "the step is pinned and no wider"'
sv "$brisk" 7400 conductor ""    step-done ""

# Step two: a rejected Green, a leaf the watchdog killed — 70 wall seconds and no usage line
# at all, which is what makes the two sources of wall time tell apart — and a revise that
# passed. red 80+20 = 100 wall, 60+10 = 70 API. green 100+20+70+60+20 = 270 wall,
# 85+10+45+10 = 150 API. The step ran 8000 to 8600 — 600 seconds.
sv "$slow" 8000 conductor ""    step-start ""
sv "$slow" 8010 developer red   launch  1 '"name": "develop-red"'
sv "$slow" 8100 developer red   exit    1 '"status": "0", "secs": "80"'
sv "$slow" 8100 developer red   usage   1 "$(usage_json 60000)"
sv "$slow" 8110 verifier  red   launch  1 '"name": "verify-red"'
sv "$slow" 8130 verifier  red   exit    1 '"status": "0", "secs": "20"'
sv "$slow" 8130 verifier  red   usage   1 "$(usage_json 10000)"
sv "$slow" 8130 verifier  red   verdict 1 '"verdict": "PASS", "reason": "the case fails as written"'
sv "$slow" 8200 developer green launch  1 '"name": "develop-green"'
sv "$slow" 8300 developer green exit    1 '"status": "0", "secs": "100"'
sv "$slow" 8300 developer green usage   1 "$(usage_json 85000)"
sv "$slow" 8310 verifier  green launch  1 '"name": "verify-green"'
sv "$slow" 8330 verifier  green exit    1 '"status": "0", "secs": "20"'
sv "$slow" 8330 verifier  green usage   1 "$(usage_json 10000)"
sv "$slow" 8330 verifier  green verdict 1 '"verdict": "REJECT", "reason": "the production change is wider than the case asks for"'
sv "$slow" 8340 conductor green revise  1 '"budget": "3"'
sv "$slow" 8350 developer green launch  2 '"name": "revise-green-1"'
sv "$slow" 8420 developer green exit    2 '"status": "2", "cause": "no heartbeat for 300s (window 120s)", "secs": "70"'
sv "$slow" 8430 developer green launch  2 '"name": "revise-green-1"'
sv "$slow" 8490 developer green exit    2 '"status": "0", "secs": "60"'
sv "$slow" 8490 developer green usage   2 "$(usage_json 45000)"
sv "$slow" 8500 verifier  green launch  2 '"name": "verify-green"'
sv "$slow" 8520 verifier  green exit    2 '"status": "0", "secs": "20"'
sv "$slow" 8520 verifier  green usage   2 "$(usage_json 10000)"
sv "$slow" 8520 verifier  green verdict 2 '"verdict": "PASS", "reason": "the step is pinned and no wider"'
sv "$slow" 8600 conductor ""    step-done ""

# The mark that closed the run, 1700 seconds after its first event.
sv "$slow" 8700 conductor ""    done       "" '"pr": "https://github.com/ztrange/veri/pull/999"'


name="the phase and step rows carry their wall and API seconds, and the report gives the issue wall from its first event to done"
problems=()

time_out="$time_work/report.md"
render "$time_work" "$time_out"

times_say "$time_out" red=210,155 green=390,240 "$brisk=400,175" "$slow=600,220"
issue_wall_says "$time_out" 1700

report_on "$name" "$time_out"

# costs_say <file> <key>=<turns>,<input>,<output>,<cache read>,<cache creation>,<dollars> …
# — the fifth section's subject: what the run cost. Each expectation names a row — a phase
# row, a step row or the total, the sections are searched alike, the way times_say searches
# them — and the six figures that row must carry.
#
# The six are the ones the closing record of a leaf reports and harvest-usage.sh copies onto
# the `usage` line (harvest-usage.sh:76-84): `num_turns`, the four `usage.*` token counts
# under their own names, and `total_cost_usd`. Which line they are read off is the shape of
# the log and not a choice of this suite; what a row of the report holds is the sum over the
# attempts grouped into it.
#
# The table is located by the ROW and its columns by their HEADINGS, exactly one each, so
# neither column order nor the wording around the words is pinned — only that each figure
# has a column of its own and a heading that names it. The cells are compared as NUMBERS
# after `$` and thousands commas are stripped, and dollars to the cent: `1.3`, `1.30` and
# `$1.30` are the same figure, and which one the report prints is not this step.
#
# The total is the one row matched loosely — any row whose first cell says `total` — because
# the word is the whole of what identifies it, where a phase row and a step row are named by
# strings the log itself carries.
#
# Complaints are deduplicated for times_say's reason: several rows of one table raise the
# same missing-column line, and the same sentence twice says nothing the first did not.
costs_say() {
  local out_file="$1"; shift
  probe "$PROBE_PRELUDE"'
path = sys.argv[1]
tables = tables_in(path)

# Each figure wanted, as the name it is complained about under and a predicate over one
# heading cell. Predicates rather than substrings because two of the four token counts are
# spelled with the same first word: a heading is the cache-read column when it says read,
# and the plain input column only when it says input and none of the cache words.
def turns(c):        return "turn" in c
def input_(c):       return "input" in c and not any(w in c for w in ("cache", "read", "creat", "writ"))
def output(c):       return "output" in c
def cache_read(c):   return "read" in c
def cache_create(c): return "creat" in c or "writ" in c

WANTED = [("turns", turns), ("input tokens", input_), ("output tokens", output),
          ("cache read tokens", cache_read), ("cache creation tokens", cache_create),
          ("dollars", money)]

for arg in sys.argv[2:]:
    key, expected = arg.split("=", 1)
    header, row = located(tables, key, "a table", table_with)
    if row is None:
        continue
    for (name, matches), want in zip(WANTED, expected.split(",")):
        i = column(header, name, matches, key)
        if i is None:
            continue
        got = row[i] if i < len(row) else ""
        said = number(got)
        if said is None or abs(said - float(want)) > 0.005:
            complain("%r %s: want %s, got %r" % (key, name, want, got))

print("\n".join(problems))
' "$out_file" "$@"
}

# conductor_says <report-without> <report-with> — the line that says whether the figures
# above include the conductor own cost.
#
# It is looked for OUTSIDE the tables, the way the issue wall is: the claim is about every
# figure in the report rather than about a row of it. Both reports are read at once because
# a line saying "whether" is only observable as a line that says something ELSE when the
# answer changes — a sentence printed unconditionally answers nothing, the same reason the
# refactor `stopped` column above is read against two steps rather than one.
#
# The two reports differ in exactly one thing: whether the log holds a `usage` line of the
# conductor own. That line exists only when the conductor ran in print mode, with a closing
# record of its own to harvest, so a run driven from an interactive session leaves the leaf
# cost complete and the conductor own missing — and the report has to say which of the two a
# reader is holding.
#
# What is pinned is that the report has one such line, that the two answers are not the same
# sentence, and that the one whose log has no conductor usage reads as a DENIAL while the one
# whose log has it does not. The denial is recognised by a whole word — `not`, `no`,
# `without`, `excluded`, `excluding`, `missing` — so the wording, the punctuation and the
# order of the sentence stay the implementation own.
conductor_says() {
  probe '
import re, sys

DENIAL = re.compile(r"\b(not|no|without|excluded|excluding|missing)\b")

problems = []

def conductor_line(path, label):
    said = [l.strip() for l in open(path).read().splitlines()
            if l.strip() and not l.strip().startswith("|") and "conductor" in l.lower()]
    if len(said) == 1:
        return said[0]
    problems.append(
        "want exactly one line outside the tables saying whether the conductor own cost is "
        "included, the report of the log %s has %d: %s"
        % (label, len(said), ", ".join(repr(l) for l in said) or "nothing"))
    return None

without = conductor_line(sys.argv[1], "with no conductor usage line")
with_ = conductor_line(sys.argv[2], "with one")

if without is not None and with_ is not None:
    if without == with_:
        problems.append(
            "the log with a conductor usage line and the log without one say the same thing: %r"
            % without)
    if not DENIAL.search(without.lower()):
        problems.append(
            "the log has no conductor usage, so its line must say the conductor own cost is "
            "left out, it says: %r" % without)
    if DENIAL.search(with_.lower()):
        problems.append(
            "the log has the conductor own usage, so its line must not deny it, it says: %r"
            % with_)

print("\n".join(problems))
' "$@"
}

# A fifth fixture, in its own directory for the reason the others have one: each case keeps
# the log it was written against.
#
# Two steps of two phases each, so a per-phase figure is observable as something other than a
# per-step one and both as something other than the total. Every figure the case reads is a
# distinct number, and no two rows share one, so a report that printed one token count in
# another column, or one row in another row place, cannot pass.
fixture_work cost_work

# `cost_json <turns> <dollars> <input> <output> <cache-read> <cache-creation>` — the payload
# of one `usage` line, in the shape harvest-usage.sh emits (harvest-usage.sh:76-84). It is a
# writer of its own beside `usage_json` above rather than an argument added to it: that one
# varies the API milliseconds its case reads and holds the rest constant, this one varies the
# six its case reads and holds the two durations constant, and a single writer taking eight
# arguments would make every call site of both spell the two figures its own case is not
# about.
cost_json() {
  printf '"duration_ms": "0", "duration_api_ms": "0", "num_turns": "%s", "total_cost_usd": "%s", "input_tokens": "%s", "output_tokens": "%s", "cache_read_input_tokens": "%s", "cache_creation_input_tokens": "%s"' \
    "$1" "$2" "$3" "$4" "$5" "$6"
}

cheap="the table reports turns, the four token counts and dollars per step"
dear="a step recovered after a REJECT contributes its rejected attempts to rework"

# Step one, the cheap one. Its red is 3+2 = 5 turns, 0.10+0.05 = 0.15 dollars, 150 input,
# 230 output, 1500 cache read and 500 cache creation; its green 11 turns, 0.60 dollars, 420
# input, 670 output, 4900 cache read and 1200 cache creation. The step is the two together:
# 16 turns, 0.75 dollars, 570 input, 900 output, 6400 cache read, 1700 cache creation.
sv "$cheap" 9000 conductor ""    step-start ""
sv "$cheap" 9010 developer red   launch  1 '"name": "develop-red"'
sv "$cheap" 9100 developer red   exit    1 '"status": "0", "secs": "90"'
sv "$cheap" 9100 developer red   usage   1 "$(cost_json 3 0.10 100 200 1000 400)"
sv "$cheap" 9110 verifier  red   launch  1 '"name": "verify-red"'
sv "$cheap" 9130 verifier  red   exit    1 '"status": "0", "secs": "20"'
sv "$cheap" 9130 verifier  red   usage   1 "$(cost_json 2 0.05 50 30 500 100)"
sv "$cheap" 9130 verifier  red   verdict 1 '"verdict": "PASS", "reason": "the case fails as written"'
sv "$cheap" 9200 developer green launch  1 '"name": "develop-green"'
sv "$cheap" 9300 developer green exit    1 '"status": "0", "secs": "100"'
sv "$cheap" 9300 developer green usage   1 "$(cost_json 7 0.40 300 600 4000 900)"
sv "$cheap" 9310 verifier  green launch  1 '"name": "verify-green"'
sv "$cheap" 9330 verifier  green exit    1 '"status": "0", "secs": "20"'
sv "$cheap" 9330 verifier  green usage   1 "$(cost_json 4 0.20 120 70 900 300)"
sv "$cheap" 9330 verifier  green verdict 1 '"verdict": "PASS", "reason": "the step is pinned and no wider"'
sv "$cheap" 9400 conductor ""    step-done ""

# Step two, the dear one: 8 turns, 0.30 dollars, 250 input, 400 output, 2900 cache read and
# 800 cache creation in red; 12 turns, 0.70 dollars, 590 input, 910 output, 7100 cache read
# and 1900 cache creation in green. The step is 20 turns, 1.00 dollars, 840 input, 1310
# output, 10000 cache read, 2700 cache creation.
#
# Across the two steps, red is 13 turns, 0.45 dollars, 400 input, 630 output, 4400 cache read
# and 1300 cache creation; green is 23 turns, 1.30 dollars, 1010 input, 1580 output, 12000
# cache read and 3100 cache creation; and the whole run is 36 turns, 1.75 dollars, 1410
# input, 2210 output, 16400 cache read and 4400 cache creation.
sv "$dear" 9500 conductor ""    step-start ""
sv "$dear" 9510 developer red   launch  1 '"name": "develop-red"'
sv "$dear" 9600 developer red   exit    1 '"status": "0", "secs": "90"'
sv "$dear" 9600 developer red   usage   1 "$(cost_json 6 0.25 210 340 2200 600)"
sv "$dear" 9610 verifier  red   launch  1 '"name": "verify-red"'
sv "$dear" 9630 verifier  red   exit    1 '"status": "0", "secs": "20"'
sv "$dear" 9630 verifier  red   usage   1 "$(cost_json 2 0.05 40 60 700 200)"
sv "$dear" 9630 verifier  red   verdict 1 '"verdict": "PASS", "reason": "the case fails as written"'
sv "$dear" 9700 developer green launch  1 '"name": "develop-green"'
sv "$dear" 9800 developer green exit    1 '"status": "0", "secs": "100"'
sv "$dear" 9800 developer green usage   1 "$(cost_json 9 0.55 500 800 6000 1500)"
sv "$dear" 9810 verifier  green launch  1 '"name": "verify-green"'
sv "$dear" 9830 verifier  green exit    1 '"status": "0", "secs": "20"'
sv "$dear" 9830 verifier  green usage   1 "$(cost_json 3 0.15 90 110 1100 400)"
sv "$dear" 9830 verifier  green verdict 1 '"verdict": "PASS", "reason": "the step is pinned and no wider"'
sv "$dear" 9900 conductor ""    step-done ""
sv "$dear" 9910 conductor ""    done      "" '"pr": "https://github.com/ztrange/veri/pull/999"'

# A sixth fixture, the same run driven in print mode: one leaf and, beside it, the
# conductor own closing accounting as a `usage` line of its own — actor `conductor`, and no
# phase and no step, because the conductor own spending belongs to the run rather than to any
# leaf inside it. It is here only so the line the case reads has something to say the other
# way round; what the figures do with it is a later step.
fixture_work printed_work

printed="the table reports turns, the four token counts and dollars per step"

sv "$printed" 9000 conductor ""    step-start ""
sv "$printed" 9010 developer red   launch  1 '"name": "develop-red"'
sv "$printed" 9100 developer red   exit    1 '"status": "0", "secs": "90"'
sv "$printed" 9100 developer red   usage   1 "$(cost_json 3 0.10 100 200 1000 400)"
sv "$printed" 9110 conductor ""    step-done ""
event_line "$fixture_log" 9200 conductor "" "" usage "" "$(cost_json 12 0.90 800 400 20000 2500)"


name="every phase row, step row and the total carry their turns, four token counts and dollars, and a line says whether the conductor own cost is in them"
problems=()

cost_out="$cost_work/report.md"
printed_out="$printed_work/report.md"
render "$cost_work" "$cost_out"
render "$printed_work" "$printed_out"

costs_say "$cost_out" \
  red=13,400,630,4400,1300,0.45 \
  green=23,1010,1580,12000,3100,1.30 \
  "$cheap=16,570,900,6400,1700,0.75" \
  "$dear=20,840,1310,10000,2700,1.00" \
  total=36,1410,2210,16400,4400,1.75
conductor_says "$cost_out" "$printed_out"

report_on "$name" "$cost_out"

# rework_and_waste_say <file> <phase>=<rework wall>,<rework $>,<waste wall>,<waste $> … —
# the report section whose subject is what a phase spent that the run did not keep.
#
# Rework and waste are the glossary's two, and each is read here as the two figures the spec
# pairs it with: the wall seconds of the attempts that went into it, and the dollars those
# attempts cost.
#
# The table is located by its ROWS AND ITS SUBJECT — the first table that has a row for the
# phase and a heading saying `rework` — where the probes above locate theirs by rows alone.
# That is the one thing this case has to say about layout, and it says it because rework is
# necessarily a SECOND figure about the same key: a report with a per-phase section already
# has a table with a `red` row, so "the table with a red row" no longer names one table. What
# stays unpinned is everything those probes leave unpinned — section headings, column order,
# row order, and whether these figures ride in the phase table or a table of their own.
#
# Within it, which column is which is decided by the heading and not by position: of the
# headings naming a kind, the money one is the one that says `$`, `cost`, `dollar` or `usd`,
# and the time one is the rest — narrowed to a `wall` heading when there is more than one, so
# a rework API column is a figure this case is not about rather than a reason to fail.
#
# The cells are compared as NUMBERS after `$`, thousands commas and a trailing unit are
# stripped, and to the cent, for costs_say's reason: `0.5`, `0.50` and `$0.50` are one
# figure, and which of them the report prints is not this step.
rework_and_waste_say() {
  local out_file="$1"; shift
  probe "$PROBE_PRELUDE"'
path = sys.argv[1]
tables = tables_in(path)

def lost_table(tables, key):
    for t in tables:
        if any("rework" in c.lower() for c in t[0]) and any(is_row(r, key) for r in t[1:]):
            return t
    return None

def pick(header, kind, want_money, name, key):
    hits = [i for i, c in enumerate(header) if kind in c.lower()]
    monied = [i for i in hits if money(header[i].lower())]
    if want_money:
        chosen = monied
    else:
        rest = [i for i in hits if i not in monied]
        walls = [i for i in rest if "wall" in header[i].lower()]
        chosen = walls or rest
    if len(chosen) == 1:
        return chosen[0]
    complain("want exactly one column heading saying %s, the table reporting rework with a "
             "row for %r is headed: %s" % (name, key, "|".join(header) or "nothing"))
    return None

WANTED = [("rework", False, "rework wall seconds"),
          ("rework", True,  "rework dollars"),
          ("waste",  False, "waste wall seconds"),
          ("waste",  True,  "waste dollars")]

for arg in sys.argv[2:]:
    key, expected = arg.split("=", 1)
    header, row = located(tables, key, "a table reporting rework", lost_table)
    if row is None:
        continue
    for (kind, want_money, name), want in zip(WANTED, expected.split(",")):
        i = pick(header, kind, want_money, name, key)
        if i is None:
            continue
        got = row[i] if i < len(row) else ""
        said = number(got)
        if said is None or abs(said - float(want)) > 0.005:
            complain("%r %s: want %s, got %r" % (key, name, want, got))

print("\n".join(problems))
' "$out_file" "$@"
}

# A seventh fixture, in its own directory for the reason the others have one: each case keeps
# the log it was written against.
#
# It is a run of two steps that BOTH reached their `step-done` mark — nothing in it bailed —
# so every figure it reports is about the half of the glossary this step pins: a step that
# recovered. One of the two was never rejected and one was rejected once and then passed, so
# the rework figure is observable as something other than "every attempt of the run" and the
# waste figure as something other than "whatever rework is not".
#
# The rejected attempt of the recovered step is attempt 1 of its green: the developer leaf
# that wrote the code (100 wall seconds, $0.40) and the blind verifier that turned it down
# (20 seconds, $0.10). Those two are what the REJECT cost, so green's rework is 120 seconds
# and $0.50 — and the revise that followed, which the run kept, is not in it. Red was never
# rejected anywhere in the run, so its rework is 0 and $0.00.
#
# Waste is 0 everywhere, in both phases, because waste is what a BAILED step spent and this
# log holds no bail: a step that recovered contributes nothing to it, PASS verdicts and
# REJECTed attempts alike. That half of the case is the reason the fixture ends on a `done`
# mark rather than simply stopping.
fixture_work rework_work

unrejected="rework and waste are both empty in a step nothing rejected"
recovered="a step recovered after a REJECT contributes its rejected attempts to rework"

# The step nothing rejected: two phases, one attempt each, both PASS.
sv "$unrejected" 100 conductor ""    step-start ""
sv "$unrejected" 110 developer red   launch  1 '"name": "develop-red"'
sv "$unrejected" 200 developer red   exit    1 '"status": "0", "secs": "90"'
sv "$unrejected" 200 developer red   usage   1 "$(cost_json 3 0.11 100 200 1000 400)"
sv "$unrejected" 210 verifier  red   launch  1 '"name": "verify-red"'
sv "$unrejected" 230 verifier  red   exit    1 '"status": "0", "secs": "20"'
sv "$unrejected" 230 verifier  red   usage   1 "$(cost_json 2 0.07 50 30 500 100)"
sv "$unrejected" 230 verifier  red   verdict 1 '"verdict": "PASS", "reason": "the case fails as written"'
sv "$unrejected" 300 developer green launch  1 '"name": "develop-green"'
sv "$unrejected" 380 developer green exit    1 '"status": "0", "secs": "80"'
sv "$unrejected" 380 developer green usage   1 "$(cost_json 7 0.22 300 600 4000 900)"
sv "$unrejected" 385 verifier  green launch  1 '"name": "verify-green"'
sv "$unrejected" 395 verifier  green exit    1 '"status": "0", "secs": "10"'
sv "$unrejected" 395 verifier  green usage   1 "$(cost_json 4 0.13 120 70 900 300)"
sv "$unrejected" 395 verifier  green verdict 1 '"verdict": "PASS", "reason": "the step is pinned and no wider"'
sv "$unrejected" 400 conductor ""    step-done ""

# The step that recovered: its red passed first time, its green was rejected once — the two
# leaves of that attempt are green rework, 120 seconds and $0.50 — and the revise that
# followed passed, so the step reached its `step-done` mark and wasted nothing.
sv "$recovered" 500 conductor ""    step-start ""
sv "$recovered" 510 developer red   launch  1 '"name": "develop-red"'
sv "$recovered" 540 developer red   exit    1 '"status": "0", "secs": "30"'
sv "$recovered" 540 developer red   usage   1 "$(cost_json 3 0.03 100 200 1000 400)"
sv "$recovered" 550 verifier  red   launch  1 '"name": "verify-red"'
sv "$recovered" 560 verifier  red   exit    1 '"status": "0", "secs": "10"'
sv "$recovered" 560 verifier  red   usage   1 "$(cost_json 2 0.02 50 30 500 100)"
sv "$recovered" 560 verifier  red   verdict 1 '"verdict": "PASS", "reason": "the case fails as written"'
sv "$recovered" 600 developer green launch  1 '"name": "develop-green"'
sv "$recovered" 700 developer green exit    1 '"status": "0", "secs": "100"'
sv "$recovered" 700 developer green usage   1 "$(cost_json 9 0.40 500 800 6000 1500)"
sv "$recovered" 710 verifier  green launch  1 '"name": "verify-green"'
sv "$recovered" 730 verifier  green exit    1 '"status": "0", "secs": "20"'
sv "$recovered" 730 verifier  green usage   1 "$(cost_json 3 0.10 90 110 1100 400)"
sv "$recovered" 730 verifier  green verdict 1 '"verdict": "REJECT", "reason": "the production change is wider than the case asks for"'
sv "$recovered" 740 conductor green revise  1 '"budget": "3"'
sv "$recovered" 750 developer green launch  2 '"name": "revise-green-1"'
sv "$recovered" 810 developer green exit    2 '"status": "0", "secs": "60"'
sv "$recovered" 810 developer green usage   2 "$(cost_json 5 0.24 200 300 2000 700)"
sv "$recovered" 820 verifier  green launch  2 '"name": "verify-green"'
sv "$recovered" 840 verifier  green exit    2 '"status": "0", "secs": "20"'
sv "$recovered" 840 verifier  green usage   2 "$(cost_json 2 0.06 60 40 600 200)"
sv "$recovered" 840 verifier  green verdict 2 '"verdict": "PASS", "reason": "the step is pinned and no wider"'
sv "$recovered" 900 conductor ""    step-done ""
sv "$recovered" 910 conductor ""    done      "" '"pr": "https://github.com/ztrange/veri/pull/999"'


name="a step recovered after a REJECT puts its rejected attempts into its phase rework and nothing into waste"
problems=()

rework_out="$rework_work/report.md"
render "$rework_work" "$rework_out"

rework_and_waste_say "$rework_out" red=0,0.00,0,0.00 green=120,0.50,0,0.00

report_on "$name" "$rework_out"

# An eighth fixture, in its own directory like the others: the half of the glossary the
# seventh cannot show. It is a run of two steps of which the second BAILED — it never reached
# a `step-done` mark and the log ends on the conductor's `bail` — so every figure it reports
# is about a step the run did not keep.
#
# The bailed step's red PASSED before its green went wrong, and that is the point of the
# case: waste is what the bailed step spent, PASS verdicts included, so the 120 seconds and
# $0.50 of a red nobody ever turned down are waste all the same. A script reading waste off
# the REJECTs would report red as empty.
#
# Its green was rejected twice — attempt 1 (60 + 20 seconds, $0.20 + $0.05) and the revise
# after it (50 + 10 seconds, $0.10 + $0.05) — for 140 seconds and $0.40. Those REJECTs must
# contribute NOTHING to rework: an attempt is rework only in a step that recovered, and this
# one did not, so a script that counted every REJECT as rework would report green twice over.
#
# The step that landed first is in the log so that neither figure is "everything the run
# spent": red spent 160 seconds across the two steps and green 190, and neither waste figure
# is either number.
fixture_work bail_work

landed="the first step of the run reached its step-done mark"
bailed="a bailed step contributes every attempt to waste"

# The step that landed: one attempt per phase, both PASS, closed by `step-done`. It
# contributes to neither figure.
sv "$landed" 7000 conductor ""    step-start ""
sv "$landed" 7010 developer red   launch  1 '"name": "develop-red"'
sv "$landed" 7040 developer red   exit    1 '"status": "0", "secs": "30"'
sv "$landed" 7040 developer red   usage   1 "$(cost_json 3 0.03 100 200 1000 400)"
sv "$landed" 7050 verifier  red   launch  1 '"name": "verify-red"'
sv "$landed" 7060 verifier  red   exit    1 '"status": "0", "secs": "10"'
sv "$landed" 7060 verifier  red   usage   1 "$(cost_json 2 0.02 50 30 500 100)"
sv "$landed" 7060 verifier  red   verdict 1 '"verdict": "PASS", "reason": "the case fails as written"'
sv "$landed" 7100 developer green launch  1 '"name": "develop-green"'
sv "$landed" 7140 developer green exit    1 '"status": "0", "secs": "40"'
sv "$landed" 7140 developer green usage   1 "$(cost_json 4 0.05 120 70 900 300)"
sv "$landed" 7150 verifier  green launch  1 '"name": "verify-green"'
sv "$landed" 7160 verifier  green exit    1 '"status": "0", "secs": "10"'
sv "$landed" 7160 verifier  green usage   1 "$(cost_json 2 0.01 60 40 600 200)"
sv "$landed" 7160 verifier  green verdict 1 '"verdict": "PASS", "reason": "the step is pinned and no wider"'
sv "$landed" 7200 conductor ""    step-done ""

# The step that bailed: a red that PASSED — 120 seconds and $0.50 of waste — and a green
# rejected twice, 140 seconds and $0.40 of waste and no rework, since no `step-done` follows.
sv "$bailed" 7300 conductor ""    step-start ""
sv "$bailed" 7310 developer red   launch  1 '"name": "develop-red"'
sv "$bailed" 7410 developer red   exit    1 '"status": "0", "secs": "100"'
sv "$bailed" 7410 developer red   usage   1 "$(cost_json 6 0.40 300 600 4000 900)"
sv "$bailed" 7420 verifier  red   launch  1 '"name": "verify-red"'
sv "$bailed" 7440 verifier  red   exit    1 '"status": "0", "secs": "20"'
sv "$bailed" 7440 verifier  red   usage   1 "$(cost_json 3 0.10 90 110 1100 400)"
sv "$bailed" 7440 verifier  red   verdict 1 '"verdict": "PASS", "reason": "the case fails as written"'
sv "$bailed" 7500 developer green launch  1 '"name": "develop-green"'
sv "$bailed" 7560 developer green exit    1 '"status": "0", "secs": "60"'
sv "$bailed" 7560 developer green usage   1 "$(cost_json 5 0.20 200 300 2000 700)"
sv "$bailed" 7570 verifier  green launch  1 '"name": "verify-green"'
sv "$bailed" 7590 verifier  green exit    1 '"status": "0", "secs": "20"'
sv "$bailed" 7590 verifier  green usage   1 "$(cost_json 2 0.05 60 40 600 200)"
sv "$bailed" 7590 verifier  green verdict 1 '"verdict": "REJECT", "reason": "the production change is wider than the case asks for"'
sv "$bailed" 7600 conductor green revise  1 '"budget": "3"'
sv "$bailed" 7610 developer green launch  2 '"name": "revise-green-1"'
sv "$bailed" 7660 developer green exit    2 '"status": "0", "secs": "50"'
sv "$bailed" 7660 developer green usage   2 "$(cost_json 4 0.10 150 250 1700 600)"
sv "$bailed" 7670 verifier  green launch  2 '"name": "verify-green"'
sv "$bailed" 7680 verifier  green exit    2 '"status": "0", "secs": "10"'
sv "$bailed" 7680 verifier  green usage   2 "$(cost_json 2 0.05 60 40 600 200)"
sv "$bailed" 7680 verifier  green verdict 2 '"verdict": "REJECT", "reason": "the production change is still wider than the case asks for"'
sv "$bailed" 7700 conductor green bail    "" '"cause": "revise-budget", "classification": "process"'


name="a bailed step puts every attempt, PASS verdicts included, into its phase waste and nothing into rework"
problems=()

bail_out="$bail_work/report.md"
render "$bail_work" "$bail_out"

rework_and_waste_say "$bail_out" red=0,0.00,120,0.50 green=0,0.00,140,0.40

report_on "$name" "$bail_out"


# progress_says <file> <done> <planned> — the progress figure: how many steps of the plan the
# run finished. Looked for OUTSIDE the tables, the way the issue wall is, because it belongs
# to no phase and no step: it is a figure of the whole run.
#
# The pair is matched as the two numbers in that order with nothing but non-digits between
# them, on a line that names steps, so `1 of 3`, `1/3` and `steps done: 1 of 3` all read
# alike and only the ORDER of the pair is pinned — which of the two is the numerator is the
# whole of what the figure claims, and the wording around it is the implementation's own.
#
# The line has to say `step` because that is the noun the figure counts, not a choice of
# words: without it, a report printing no progress at all could be passed by two numbers that
# happened to fall side by side in some other sentence.
progress_says() {
  probe "$PROBE_PRELUDE"'
path, done, planned = sys.argv[1], sys.argv[2], sys.argv[3]
pair = re.compile(r"(?<![0-9.])%s(?![0-9.])\D{1,20}(?<![0-9.])%s(?![0-9.])"
                  % (re.escape(done), re.escape(planned)))
lines = outside_tables(path)

if not any(pair.search(l) and "step" in l.lower() for l in lines):
    complain("want a line outside the tables saying %s steps of %s planned were done, the "
             "report says outside them: %s" % (done, planned, quoted(lines)))

print("\n".join(problems))
' "$@"
}

# outcome_says <file> <outcome> — how the run ENDED, as the report says it outside the tables.
# <outcome> is `system` or `process` for a bail of that classification — the word
# classify-bail.sh decided and the conductor put on the `bail` mark (SKILL.md:949) — or `pr`
# for a run that reached a draft PR, which is what issue success is.
#
# A bail report must carry a line calling the run a bail AND naming its classification, and
# no line anywhere outside the tables may name the OTHER one. That second half is what makes
# the split observable: a report printing one of the two constantly would pass a case that
# only ever read the bail it was handed, and "a bail split system or process" is exactly the
# claim such a report would not be making.
#
# A run that landed is read the other way round — no line may call it a bail, and some line
# must name the PR — so the three answers are three different sentences rather than one
# printed unconditionally.
#
# The words matched are the glossary's own nouns for the outcome — bail, system failure,
# process failure, a draft PR — so what is pinned is which of them the report reaches for,
# never how it words the sentence they sit in.
outcome_says() {
  probe "$PROBE_PRELUDE"'
path, want = sys.argv[1], sys.argv[2]
lines = outside_tables(path)

def says(line, word):
    return re.search(r"\b%s\b" % word, line.lower()) is not None

bails = [l for l in lines if says(l, "bail(ed|s)?")]

if want == "pr":
    if bails:
        complain("the run reached a draft PR, so no line outside the tables may call it a "
                 "bail, these do: %s" % quoted(bails))
    if not any(re.search(r"\b(pr|pull request|draft)\b", l.lower()) for l in lines):
        complain("want a line outside the tables naming the draft PR the run reached, the "
                 "report says outside them: %s" % quoted(lines))
else:
    other = "process" if want == "system" else "system"
    if not any(says(l, want) for l in bails):
        complain("want a line outside the tables calling the run a bail and classifying it "
                 "a %s failure, the report says outside them: %s" % (want, quoted(lines)))
    wrong = [l for l in lines if says(l, other)]
    if wrong:
        complain("the bail was classified %s, so no line outside the tables may call it %s, "
                 "these do: %s" % (want, other, quoted(wrong)))

print("\n".join(problems))
' "$@"
}

# plan_of <ticked step>… -- <open step>… — write the ledger beside the log of whichever
# fixture was made last, in the checkbox grammar next-unchecked.sh reads (next-unchecked.sh:16),
# with the steps before the `--` ticked and the ones after it still open.
#
# The ledger is a second input to the report, and the only one that can say how many steps
# were PLANNED: a run that bailed never reached the steps after the one it died on, so its
# log holds no line mentioning them at all, and a planned count read off the log would be
# whatever the run got through — the one number a progress figure must not be. The file is
# `.tdd/issue-108.md`, the ledger the conductor commits for this issue, which is the file the
# issue number on the command line names.
plan_of() {
  local ledger="${fixture_log%events.jsonl}issue-108.md" box="[x]" step
  : > "$ledger"
  for step in "$@"; do
    if [[ "$step" == "--" ]]; then
      box="[ ]"
      continue
    fi
    printf -- '- %s %s\n' "$box" "$step" >> "$ledger"
  done
}

# A ninth fixture, in its own directory for the reason the others have one: each case keeps
# the log it was written against. It, and the two after it, are the three answers this case's
# one question has — a bail the plumbing caused, a bail the methodology caused, and a run that
# landed — because a report that said the same thing about all three would be answering none
# of them.
#
# This one is a plan of three steps whose first landed and whose second was killed stuck: the
# conductor's `bail` mark carries the cause and the `system` classification classify-bail.sh
# gave it (classify-bail.sh:15). One step reached its `step-done` mark, so the progress figure
# is 1 of 3 — and the third step appears nowhere in the log, which is what the ledger is here
# to supply.
#
# The log carries the conductor's marks and no leaf lines at all. Both figures this case reads
# are read off those marks, so a fixture with attempts under them would only be adding rows to
# tables no probe here looks at.
fixture_work system_work

landed_first="the table reports steps done of planned"
killed="the table reports the issue outcome, a bail split system or process"

sv "$landed_first" 11000 conductor ""    step-start ""
sv "$landed_first" 11100 conductor ""    step-done  ""
sv "$killed"       11200 conductor ""    step-start ""
sv "$killed"       11300 conductor green bail       "" '"cause": "killed-stuck", "classification": "system"'

plan_of "$landed_first" -- "$killed" "a third step the run never reached"

# A tenth fixture: the other classification, and a second pair of progress numbers. Two of a
# four-step plan landed and the third exhausted its revise budget, which classify-bail.sh
# calls a `process` failure (classify-bail.sh:18) — the methodology spoke, where the fixture
# above is the plumbing breaking. 2 of 4, so neither number this case reads is shared with the
# fixture above and a report that hard-coded either cannot pass both.
fixture_work process_work

first_landed="the table reports steps done of planned, the first step"
second_landed="the table reports steps done of planned, the second step"
exhausted="the issue outcome is a bail split system or process"

sv "$first_landed"  12000 conductor ""    step-start ""
sv "$first_landed"  12100 conductor ""    step-done  ""
sv "$second_landed" 12200 conductor ""    step-start ""
sv "$second_landed" 12300 conductor ""    step-done  ""
sv "$exhausted"     12400 conductor ""    step-start ""
sv "$exhausted"     12500 conductor green bail       "" '"cause": "revise-exhausted", "classification": "process"'

plan_of "$first_landed" "$second_landed" -- "$exhausted" "a fourth step the run never reached"

# An eleventh fixture: the outcome that is not a bail. Every step of a two-step plan reached
# its `step-done` mark and the run ended on the conductor's `done` mark carrying the draft PR,
# which is what issue success is. Its progress figure is 2 of 2 — the one reading that says
# the run finished — and its outcome line must name neither classification, since there was no
# bail to classify.
fixture_work landed_work

opener="the table reports steps done of planned, of a run that landed"
closer="the issue outcome of a run that landed is its draft PR"

sv "$opener" 13000 conductor "" step-start ""
sv "$opener" 13100 conductor "" step-done  ""
sv "$closer" 13200 conductor "" step-start ""
sv "$closer" 13300 conductor "" step-done  ""
sv "$closer" 13400 conductor "" done       "" '"pr": "https://github.com/ztrange/veri/pull/999"'

plan_of "$opener" "$closer"


name="the report says how many steps of the plan were done and how the run ended, naming a bail's classification and a landed run's PR"
problems=()

system_out="$system_work/report.md"
process_out="$process_work/report.md"
landed_out="$landed_work/report.md"
render "$system_work" "$system_out"
render "$process_work" "$process_out"
render "$landed_work" "$landed_out"

progress_says "$system_out" 1 3
progress_says "$process_out" 2 4
progress_says "$landed_out" 2 2

outcome_says "$system_out" system
outcome_says "$process_out" process
outcome_says "$landed_out" pr

report_on "$name" "$system_out"


# The eleventh fixture again, read for its wall rather than its outcome: its log is exactly one
# run, and that run ended on a `done` mark 400 seconds after its first event. The wall is read
# off the same mark the outcome line is (issue #236), so a log that says the run landed must
# also give the run a length — `unknown` there would be the report failing to read a mark the
# log carries.
name="a log of exactly one run that ended in a done mark renders its issue wall as a number, not unknown"
problems=()

issue_wall_says "$landed_out" 400

report_on "$name" "$landed_out"

# A twelfth fixture: a log with no step mark in it at all. Its leaves ran, named their step and
# spent what they spent, but the conductor's own `step-start` and `step-done` marks were never
# written — the ADR-0014 case where a figure's input is missing rather than zero.
#
# The steps-done figure is read off `step-done` marks and off nothing else, so in this log it
# has no input: `0 of 2` would claim the run finished none of its two steps, which is a
# different claim from "nobody wrote it down" — the same distance `0/3` puts between "needed
# no revise" and "unrecorded". The planned half is a number, off the ledger beside the log,
# so a report reading `unknown of 2` is saying the missing half and only the missing half.
fixture_work unmarked_work

unmarked="a figure a missing conductor mark makes unreadable renders as unknown"
second_planned="a second step the log's marks never mention"

sv "$unmarked" 14000 developer red   launch 1 '"name": "develop-red", "cmd": "run-leaf.sh", "model": ""'
sv "$unmarked" 14100 developer red   exit   1 '"status": "0", "secs": "100"'
sv "$unmarked" 14110 verifier  red   launch 1 '"name": "verify-red", "cmd": "run-leaf.sh", "model": ""'
sv "$unmarked" 14130 verifier  red   exit   1 '"status": "0", "secs": "20"'
sv "$unmarked" 14130 verifier  red   verdict 1 '"verdict": "PASS", "reason": "the case fails for the reason it was written to catch"'

plan_of -- "$unmarked" "$second_planned"


name="a steps-done figure no step mark in the log supplies says unknown, not zero"
problems=()

unmarked_out="$unmarked_work/report.md"
render "$unmarked_work" "$unmarked_out"

progress_says "$unmarked_out" unknown 2

report_on "$name" "$unmarked_out"


# A thirteenth fixture: a step whose criterion earlier work already satisfied. Such a step takes
# the pin path (SKILL.md, the verify-pin PASS branch): the conductor marks it `pin` and the step
# is done with no Green and no Refactor, so no `step-done` mark is ever written for it. The first
# step of this two-step plan closed the ordinary way and the second closed on its pin, so both
# are done and the figure is 2 of 2 — `1 of 2` would be the report counting only one of the two
# marks a step can finish on.
fixture_work pinned_work

closed="a step that closed on its step-done mark"
pinned="a step that closed on its pin mark, already satisfied"

sv "$closed" 15000 conductor ""  step-start ""
sv "$closed" 15100 conductor ""  step-done  ""
sv "$pinned" 15200 conductor ""  step-start ""
sv "$pinned" 15300 conductor pin pin        ""

plan_of "$closed" "$pinned"


name="a step that ended in a pin mark and no step-done mark counts as done in the steps-done figure"
problems=()

pinned_out="$pinned_work/report.md"
render "$pinned_work" "$pinned_out"

progress_says "$pinned_out" 2 2

report_on "$name" "$pinned_out"


# A fourteenth fixture: issue #228's own run, in the shape it had. Two of its three steps were
# already satisfied and closed on their `pin` marks, and the third closed on `step-done`, so all
# three are done — the committed report said `1 of 3`, the one mark it counted.
fixture_work two_pins_work

first_pin="a first step already satisfied, closed on its pin mark"
second_pin="a second step already satisfied, closed on its pin mark"
last_done="a third step that closed on its step-done mark"

sv "$first_pin"  16000 conductor ""  step-start ""
sv "$first_pin"  16100 conductor pin pin        ""
sv "$second_pin" 16200 conductor ""  step-start ""
sv "$second_pin" 16300 conductor pin pin        ""
sv "$last_done"  16400 conductor ""  step-start ""
sv "$last_done"  16500 conductor ""  step-done  ""

plan_of "$first_pin" "$second_pin" "$last_done"


name="a log with two pin marks and one step-done mark for three ledger steps reports 3 of 3 planned"
problems=()

two_pins_out="$two_pins_work/report.md"
render "$two_pins_work" "$two_pins_out"

progress_says "$two_pins_out" 3 3

report_on "$name" "$two_pins_out"


# A fifteenth fixture: a log with no `pin` mark in it, so the pin branch has nothing to read and
# the figure is what `step-done` alone says. Two steps closed the ordinary way; the third was
# started and ran a leaf but never reached a closing mark of either kind, so it is not done —
# `2 of 3`, and `3 of 3` would be a closing mark counted that the log never wrote.
fixture_work unpinned_work

first_done="a first step that closed on its step-done mark"
second_done="a second step that closed on its step-done mark"
unclosed="a third step started and never closed"

sv "$first_done"  17000 conductor ""  step-start ""
sv "$first_done"  17100 conductor ""  step-done  ""
sv "$second_done" 17200 conductor ""  step-start ""
sv "$second_done" 17300 conductor ""  step-done  ""
sv "$unclosed"    17400 conductor ""  step-start ""
sv "$unclosed"    17500 developer red launch 1 '"name": "develop-red", "cmd": "run-leaf.sh", "model": ""'

plan_of "$first_done" "$second_done" -- "$unclosed"


name="a log whose steps end only in step-done marks, with no pin mark, counts only those steps as done"
problems=()

unpinned_out="$unpinned_work/report.md"
render "$unpinned_work" "$unpinned_out"

progress_says "$unpinned_out" 2 3

report_on "$name" "$unpinned_out"


# A sixteenth fixture: one issue run twice in one log. The first run bailed on a poisoned
# baseline and left its `bail` mark behind — `.tdd/events.jsonl` is per-worktree state that
# survives into the next run — and the second run resumed and landed its draft PR. The mark
# that ended the issue is the last one, so the outcome is the PR, not the earlier bail (#229).
fixture_work rerun_work

bailed_then_landed="a step whose first run bailed and whose resumed run landed"

sv "$bailed_then_landed" 18000 conductor ""  step-start ""
sv "$bailed_then_landed" 18100 conductor ""  bail       "" '"cause": "poisoned-baseline", "classification": "system"'
sv "$bailed_then_landed" 18200 conductor ""  resume     ""
sv "$bailed_then_landed" 18300 conductor ""  step-done  ""
sv "$bailed_then_landed" 18400 conductor ""  done       "" '"pr": "https://github.com/ztrange/veri/pull/998"'

plan_of "$bailed_then_landed"


name="a log with a bail mark followed by a resume and a done reports the run as landed, naming the PR"
problems=()

rerun_out="$rerun_work/report.md"
render "$rerun_work" "$rerun_out"

outcome_says "$rerun_out" pr

report_on "$name" "$rerun_out"


# The same log, read for its wall: the run the `done` mark ends began at the last `resume`
# (18200), not at the log's first event (18000), so the issue wall is 200 s, not 400 (#229).
name="on a log with a bail, a resume and a done the issue wall runs from the last resume to the done mark"
problems=()

issue_wall_says "$rerun_out" 200

report_on "$name" "$rerun_out"


# The same log, read for the words around that figure: the sentence has to say where the wall
# starts, and on a resumed run that is the last `resume` — not "the first event of the log",
# which the figure stopped being on #229 while the sentence went on claiming it (#248).
name="on a resumed run the issue-wall sentence says the wall starts at the last resume, not at the log's first event"
problems=()

probe '
import sys

path = sys.argv[1]
walls = [l.strip() for l in open(path).read().splitlines()
         if l.strip().startswith("Wall time for the issue:")]

if not walls:
    print("want a line starting \"Wall time for the issue:\", the report has none")
    raise SystemExit(0)

wall = walls[0]
if "the last `resume`" not in wall:
    print("want the issue-wall sentence to name the last `resume` as where the wall starts, it says: %r" % wall)
if "from the first event of the log" in wall:
    print("want the issue-wall sentence to stop claiming the wall runs \"from the first event of the log\", it says: %r" % wall)
' "$rerun_out"

report_on "$name" "$rerun_out"


# A seventeenth fixture: one run and no `resume` in its log, so nothing moves the opening end
# of the wall off the first event (19000) and the one `bail` mark (19250) is the whole of the
# outcome. The wall is 250 s and the outcome a system bail, as it was before #229.
fixture_work single_run_work

only_run="a step of a log that holds one run and no resume"

sv "$only_run" 19000 conductor ""    step-start ""
sv "$only_run" 19150 conductor ""    step-done  ""
sv "$only_run" 19250 conductor green bail       "" '"cause": "killed-stuck", "classification": "system"'

plan_of "$only_run"


name="a log with no resume walls the issue from its first event and takes its outcome from its single ending mark"
problems=()

single_run_out="$single_run_work/report.md"
render "$single_run_work" "$single_run_out"

issue_wall_says "$single_run_out" 250
outcome_says "$single_run_out" system

report_on "$name" "$single_run_out"


# The same log, read for the words around its figure: with no `resume` to move it, the wall
# starts at the log's first event, and the sentence has to say so (#248).
name="on a run with no resume the issue-wall sentence says the wall starts at the log's first event"
problems=()

probe '
import sys

path = sys.argv[1]
walls = [l.strip() for l in open(path).read().splitlines()
         if l.strip().startswith("Wall time for the issue:")]

if not walls:
    print("want a line starting \"Wall time for the issue:\", the report has none")
    raise SystemExit(0)

wall = walls[0]
if "the first event of the log" not in wall:
    print("want the issue-wall sentence to name the first event of the log as where the wall starts, it says: %r" % wall)
' "$single_run_out"

report_on "$name" "$single_run_out"


# An eighteenth fixture: one issue run twice again, but with leaves in both runs, so a figure
# summed over the whole log is observable as something other than one summed over the last
# run alone. Red was tried and rejected before the bail, and tried again and passed after the
# resume. Over the whole log red is 4 attempts, 1 PASS, 1 REJECT, 210 wall seconds, 10 turns,
# 1111/2222/3333/4444 tokens and $0.80; over the last run alone it would be 2, 1, 0, 90, 5,
# 1001/2002/3003/4004 and $0.45 — no figure the same, so a report scoped to the last run cannot
# pass (#229).
fixture_work accrued_work

accrued="a step whose leaves ran in both the bailed run and the resumed one"

sv "$accrued" 20000 conductor ""  step-start ""
sv "$accrued" 20010 developer red launch  1 '"name": "develop-red"'
sv "$accrued" 20110 developer red exit    1 '"status": "0", "secs": "100"'
sv "$accrued" 20110 developer red usage   1 "$(cost_json 3 0.25 100 200 300 400)"
sv "$accrued" 20120 verifier  red launch  1 '"name": "verify-red"'
sv "$accrued" 20140 verifier  red exit    1 '"status": "0", "secs": "20"'
sv "$accrued" 20140 verifier  red usage   1 "$(cost_json 2 0.10 10 20 30 40)"
sv "$accrued" 20140 verifier  red verdict 1 '"verdict": "REJECT", "reason": "the case fails for a reason it was not written to catch"'
sv "$accrued" 20200 conductor ""  bail    "" '"cause": "poisoned-baseline", "classification": "system"'
sv "$accrued" 20300 conductor ""  resume  ""
sv "$accrued" 20310 developer red launch  2 '"name": "develop-red"'
sv "$accrued" 20370 developer red exit    2 '"status": "0", "secs": "60"'
sv "$accrued" 20370 developer red usage   2 "$(cost_json 4 0.40 1000 2000 3000 4000)"
sv "$accrued" 20380 verifier  red launch  2 '"name": "verify-red"'
sv "$accrued" 20410 verifier  red exit    2 '"status": "0", "secs": "30"'
sv "$accrued" 20410 verifier  red usage   2 "$(cost_json 1 0.05 1 2 3 4)"
sv "$accrued" 20410 verifier  red verdict 2 '"verdict": "PASS", "reason": "the case fails as written"'
sv "$accrued" 20500 conductor ""  step-done ""
sv "$accrued" 20600 conductor ""  done    "" '"pr": "https://github.com/ztrange/veri/pull/997"'

plan_of "$accrued"


name="on a log with a bail, a resume and a done the counts, wall seconds and costs are summed over both runs"
problems=()

accrued_out="$accrued_work/report.md"
render "$accrued_work" "$accrued_out"

table_says "$accrued_out" red=4,1,1,0
times_say "$accrued_out" red=210
costs_say "$accrued_out" red=10,1111,2222,3333,4444,0.80 total=10,1111,2222,3333,4444,0.80

report_on "$name" "$accrued_out"


# A fixture for the no-verdict relaunch count (issue #219). verify.sh writes a `relaunch` mark
# with `cause=no-verdict` each time a verifier leaf exited cleanly with no VERDICT: line and is
# launched again — neither supervise.sh's `retry` (a leaf that never answered) nor a `revise`
# (a verdict that was REJECT). The step below spends all three, as three distinct figures: two
# no-verdict relaunches, one stuck retry, one revise of three, so a report that counted a
# relaunch as a retry, or printed one figure in another's column, cannot pass.
# 6 attempts, 1 PASS, 1 REJECT, 0 kills, 1 stuck retry, 2 no-verdict relaunches.
fixture_work relaunch_work

relaunched="a verifier that ended its turn without a verdict is relaunched"
sv "$relaunched" 30000 conductor ""    step-start ""
sv "$relaunched" 30010 developer green launch   1 '"name": "develop-green"'
sv "$relaunched" 30100 developer green exit     1 '"status": "0", "secs": "90"'
sv "$relaunched" 30110 verifier  green launch   1 '"name": "verify-green"'
sv "$relaunched" 30130 verifier  green exit     1 '"status": "0", "secs": "20"'
sv "$relaunched" 30130 verifier  green relaunch 1 '"cause": "no-verdict"'
sv "$relaunched" 30140 verifier  green launch   1 '"name": "verify-green"'
sv "$relaunched" 30160 verifier  green exit     1 '"status": "0", "secs": "20"'
sv "$relaunched" 30160 verifier  green relaunch 1 '"cause": "no-verdict"'
sv "$relaunched" 30170 verifier  green launch   1 '"name": "verify-green"'
sv "$relaunched" 30190 verifier  green exit     1 '"status": "0", "secs": "20"'
sv "$relaunched" 30190 verifier  green verdict  1 '"verdict": "REJECT", "reason": "the change is wider than the case"'
sv "$relaunched" 30200 conductor green revise   1 '"budget": "3"'
sv "$relaunched" 30210 developer green launch   2 '"name": "revise-green-2"'
sv "$relaunched" 30270 developer green retry    2 '"cause": "no heartbeat for 300s (window 120s)"'
sv "$relaunched" 30330 developer green exit     2 '"status": "0", "secs": "120"'
sv "$relaunched" 30340 verifier  green launch   2 '"name": "verify-green"'
sv "$relaunched" 30360 verifier  green exit     2 '"status": "0", "secs": "20"'
sv "$relaunched" 30360 verifier  green verdict  2 '"verdict": "PASS", "reason": "the step is pinned and no wider"'
sv "$relaunched" 30370 conductor ""    step-done ""


name="a step whose verifier was relaunched for no verdict reports those relaunches as their own count, apart from its retries and revises"
problems=()

relaunch_out="$relaunch_work/report.md"
render "$relaunch_work" "$relaunch_out"

counts_table_says "$relaunch_out" step attempts,pass,reject,kills,retries,no-verdict "$relaunched=6,1,1,0,1,2"

report_on "$name" "$relaunch_out"


# stopped_says <file> <step>=<cell> … — the one refactor figure that is a word rather than a
# pair: why the loop stopped. Each expectation names a step row and the exact text its
# `stop` column must carry. The table is found by the row and the column by its heading, as
# everywhere above, so neither order is pinned.
stopped_says() {
  local out_file="$1"; shift
  probe "$PROBE_PRELUDE"'
path = sys.argv[1]
tables = tables_in(path)

for arg in sys.argv[2:]:
    key, expected = arg.split("=", 1)
    got = cell_in(tables, key, "why the refactor loop stopped", lambda c: "stop" in c)
    if got is None:
        continue
    if got != expected:
        complain("step %r stopped: want %r, got %r" % (key, expected, got))

print("\n".join(problems))
' "$out_file" "$@"
}

# A fixture for the two ways refactor-triage.sh lets the loop end without an error (#250):
# exit 3, nothing structural left, is `stopped=nothing-structural`; exit 0, structural
# candidates remain and a follow-up owes them, is `stopped=structural-owed`. Two steps, one
# of each, so a report that collapsed both into one word — the `triage` #250 split — or put
# one step's reason in the other's row cannot pass. Each step launches one refactor leaf, since a
# step with no leaf launched raises no row to read.
fixture_work triage_work

tidied="a refactor whose triage found nothing structural left"
owing="a refactor whose triage left structural candidates owed"

sv "$tidied" 40000 conductor ""       step-start ""
sv "$tidied" 40002 developer refactor launch  1 '"name": "develop-refactor"'
sv "$tidied" 40008 developer refactor exit    1 '"status": "0", "secs": "6"'
sv "$tidied" 40010 conductor refactor refactor "" '"transforms": "1", "budget": "5", "stopped": "nothing-structural"'
sv "$tidied" 40020 conductor ""       step-done ""
sv "$owing"  41000 conductor ""       step-start ""
sv "$owing"  41002 developer refactor launch  1 '"name": "develop-refactor"'
sv "$owing"  41008 developer refactor exit    1 '"status": "0", "secs": "6"'
sv "$owing"  41010 conductor refactor refactor "" '"transforms": "3", "budget": "5", "stopped": "structural-owed"'
sv "$owing"  41020 conductor ""       step-done ""


name="a step whose triage found nothing structural and one that owes structural candidates each report their own stopped value"
problems=()

triage_out="$triage_work/report.md"
render "$triage_work" "$triage_out"

stopped_says "$triage_out" "$tidied=nothing-structural" "$owing=structural-owed"

report_on "$name" "$triage_out"


# crossed_says <file> <step>=<cell> … — the step table's crossing column (#452): what a step
# had spent when it crossed its cost budget, read off its `step-over-budget` mark's `spent=`.
# An expectation with a figure is compared as a number, so the report is free to print a `$`
# or a trailing zero; an empty expectation wants the cell empty, since a step that never
# crossed has no figure and a `0` there would read as a crossing at nothing. The column is
# found by a heading saying `over` or `cross`, and nothing else in the table says either.
crossed_says() {
  local out_file="$1"; shift
  probe "$PROBE_PRELUDE"'
path = sys.argv[1]
tables = tables_in(path)

for arg in sys.argv[2:]:
    key, expected = arg.split("=", 1)
    got = cell_in(tables, key, "what the step had spent when it crossed its cost budget",
                  lambda c: "over" in c or "cross" in c)
    if got is None:
        continue
    if expected == "":
        if got != "":
            complain("step %r never crossed: want the cell empty, got %r" % (key, got))
    elif number(got) != float(expected):
        complain("step %r crossed: want spent %s, got %r" % (key, expected, got))

print("\n".join(problems))
' "$out_file" "$@"
}

# A fixture for the crossing column (#452): two steps, one whose log carries the conductor's
# `step-over-budget spent=12.40 budget=10.00` mark and one whose log carries none. Each
# launches one leaf, since a step with no leaf launched raises no row to read. The crossing
# figure is one no other cell of that row holds, so a column that printed the budget, or a
# cost summed off the usage lines, cannot pass.
fixture_work crossing_work

crossed="a step that crossed its cost budget"
under="a step that stayed under its cost budget"

sv "$crossed" 42000 conductor ""    step-start ""
sv "$crossed" 42002 developer green launch  1 '"name": "develop-green"'
sv "$crossed" 42008 developer green exit    1 '"status": "0", "secs": "6"'
sv "$crossed" 42010 conductor ""    step-over-budget "" '"spent": "12.40", "budget": "10.00"'
sv "$crossed" 42020 conductor ""    step-done ""
sv "$under"   43000 conductor ""    step-start ""
sv "$under"   43002 developer green launch  1 '"name": "develop-green"'
sv "$under"   43008 developer green exit    1 '"status": "0", "secs": "6"'
sv "$under"   43020 conductor ""    step-done ""

name="#452 the By step table reports the spent= a step's step-over-budget carried, and leaves that column empty for a step that did not cross"
problems=()

crossing_out="$crossing_work/report.md"
render "$crossing_work" "$crossing_out"

crossed_says "$crossing_out" "$crossed=12.40" "$under="

report_on "$name" "$crossing_out"


# Two causes of a split (#452): a spent REVISE_BUDGET writes `step-split at=exhausted` (#408),
# a crossed cost budget `step-split at=over-budget`. The two fixtures below are the same log
# byte for byte but for that one value, so whatever tells their reports apart can only be the
# `at=` of the split — and a report that reads both the same has lost which cause grew the plan.
split_log() {
  sv "$split_step" 44000 conductor ""    step-start ""
  sv "$split_step" 44002 developer green launch  1 '"name": "develop-green"'
  sv "$split_step" 44008 developer green exit    1 '"status": "0", "secs": "6"'
  sv "$split_step" 44010 conductor ""    step-split "" "\"at\": \"$1\""
}

split_step="a step whose plan grew by a split"

fixture_work split_exhausted_work
split_log exhausted
fixture_work split_over_work
split_log over-budget

name="#452 a log whose step-split carries at=over-budget and one whose step-split carries at=exhausted render different reports"
problems=()

split_exhausted_out="$split_exhausted_work/report.md"
split_over_out="$split_over_work/report.md"
render "$split_exhausted_work" "$split_exhausted_out"
render "$split_over_work" "$split_over_out"

cmp -s "$split_exhausted_out" "$split_over_out" &&
  problems+=("the at=over-budget and at=exhausted logs rendered byte-identical reports")

report_on "$name" "$split_over_out"


# tier_seconds_say <file> <tier>=<s>,<s>,… … — the per-tier section of the `test-run` marks
# timed-test-run.sh leaves behind (#342, part of PRD #335). Each expectation names a tier and
# the seconds its runs recorded, in the order the log carries them, and every one of those
# figures must appear in that tier's row in that order.
#
# A subsequence rather than the row's numbers outright, for the reason every other probe here
# locates a column by its heading: what the step asks for is that the recorded seconds are
# listed per tier, so a section free to carry a count, a median or a usual beside them is one
# this case must not forbid. The ORDER is pinned, since a trend read out of order is not one.
#
# The table is found by its rows, as everywhere above — the first one carrying a row whose
# key is the tier — so neither the section's heading nor its position in the report is pinned.
tier_seconds_say() {
  local out_file="$1"; shift
  probe "$PROBE_PRELUDE"'
path = sys.argv[1]
tables = tables_in(path)

# Whether `wanted` runs through `got` in order, other figures allowed between them.
def in_order(wanted, got):
    remaining = iter(got)
    return all(any(figure == want for figure in remaining) for want in wanted)

for arg in sys.argv[2:]:
    key, expected = arg.split("=", 1)
    wanted = [float(s) for s in expected.split(",")]
    header, row = located(tables, key, "a per-tier table", table_with)
    if row is None:
        continue
    got = [figure for figure in (number(c) for c in row[1:]) if figure is not None]
    if not in_order(wanted, got):
        complain("tier %r seconds: want %s in its row, in that order, got %s"
                 % (key, wanted, got))

print("\n".join(problems))
' "$out_file" "$@"
}

# A fixture for the per-tier section: one step of one phase whose leaves ran the test command
# six times, three at the `fast` tier and three at `all`, interleaved the way a run interleaves
# them. The seconds are fabricated and no clock produced them — `test-run` carries the figure
# it was written with, so nothing here waits on wall time.
#
# The two tiers read 4, 6, 5 and 120, 100, 140: neither list is sorted, so a section that
# ordered the figures rather than trending them cannot pass, and no figure of one tier appears
# in the other, so a section that pooled both tiers into one row cannot either.
#
# The step's own `exit` marks carry `secs` too, and are what make the case say something: they
# are 30 and 900 seconds, in neither tier's list, so a section reading its figures off the
# wall seconds supervise.sh writes rather than off the `test-run` marks reports numbers this
# case does not want.
fixture_work tier_work

timed="metrics.sh prints a per-tier section of the test-run events' recorded seconds"

sv "$timed" 50000 conductor ""        step-start ""
sv "$timed" 50002 developer green     launch  1 '"name": "develop-green"'
sv "$timed" 50010 developer green     test-run 1 '"tier": "fast", "suites": "metrics.test.sh", "seconds": "4"'
sv "$timed" 50020 developer green     test-run 1 '"tier": "all", "suites": "all", "seconds": "120"'
sv "$timed" 50032 developer green     exit    1 '"status": "0", "secs": "30"'
sv "$timed" 50040 verifier  green     launch  1 '"name": "verify-green"'
sv "$timed" 50050 verifier  green     test-run 1 '"tier": "fast", "suites": "metrics.test.sh", "seconds": "6"'
sv "$timed" 50060 verifier  green     test-run 1 '"tier": "all", "suites": "all", "seconds": "100"'
sv "$timed" 50070 verifier  green     test-run 1 '"tier": "fast", "suites": "metrics.test.sh", "seconds": "5"'
sv "$timed" 50080 verifier  green     test-run 1 '"tier": "all", "suites": "all", "seconds": "140"'
sv "$timed" 50940 verifier  green     exit    1 '"status": "0", "secs": "900"'
sv "$timed" 50940 verifier  green     verdict 1 '"verdict": "PASS", "reason": "the step is pinned and no wider"'
sv "$timed" 50950 conductor ""        step-done ""


name="the report carries a per-tier section listing each tier's test-run seconds in log order"
problems=()

tier_out="$tier_work/report.md"
render "$tier_work" "$tier_out"

tier_seconds_say "$tier_out" fast=4,6,5 all=120,100,140

report_on "$name" "$tier_out"


# A fixture for a run the operator stopped (#390): its log's ending mark is the `stop
# mode=at-ledger at=green` the conductor writes on *Stopping* (SKILL.md), and no `done` or
# `bail` follows it. The stop lands at 60340, 340 s after the log's first event, so an issue
# wall ended anywhere else — or left unknown — is not the figure this case wants. The mode and
# the boundary are two different words, and the Outcome line has to name both.
fixture_work stopped_work

halted="a step of a run the operator stopped at the ledger"

sv "$halted" 60000 conductor ""    step-start ""
sv "$halted" 60200 conductor ""    step-done  ""
sv "$halted" 60340 conductor green stop       "" '"mode": "at-ledger", "at": "green"'

plan_of "$halted"


name="a log whose ending mark is stop prints an Outcome line naming the mode and the at boundary, and ends the issue wall at the stop"
problems=()

stopped_out="$stopped_work/report.md"
render "$stopped_work" "$stopped_out"

issue_wall_says "$stopped_out" 340
probe "$PROBE_PRELUDE"'
path = sys.argv[1]
outcomes = outcome_lines(path)

if not any("at-ledger" in l and re.search(r"\bgreen\b", l) for l in outcomes):
    complain("want an Outcome line naming the stop mode at-ledger and the at boundary green, "
             "the report has: %s" % quoted(outcomes))

print("\n".join(problems))
' "$stopped_out"

report_on "$name" "$stopped_out"


# A fixture for a stopped run the operator resumed (#390): a `stop` is not terminal the way
# `done` and `bail` are, so the `resume` after it clears the ending, and with no `done` or
# `bail` since, the run has not ended — its Outcome is the no-ending-mark one, not the stop.
fixture_work resumed_stop_work

picked_up="a step of a stopped run the operator resumed"

sv "$picked_up" 70000 conductor ""  step-start ""
sv "$picked_up" 70100 conductor red stop       "" '"mode": "at-leaf", "at": "red"'
sv "$picked_up" 70200 conductor ""  resume     ""
sv "$picked_up" 70300 conductor ""  step-start ""

plan_of "$picked_up"


name="a resume mark after a stop mark makes the report print the no-ending-mark Outcome for a run that has not ended since"
problems=()

resumed_stop_out="$resumed_stop_work/report.md"
render "$resumed_stop_work" "$resumed_stop_out"

probe "$PROBE_PRELUDE"'
path = sys.argv[1]
outcomes = outcome_lines(path)

if not any("no mark ending the run" in l for l in outcomes):
    complain("want an Outcome line saying the log carries no mark ending the run, "
             "the report has: %s" % quoted(outcomes))
stale = [l for l in outcomes if "stop" in l or "at-leaf" in l]
if stale:
    complain("the resume cleared the stop, so no Outcome line may still name it, these do: %s"
             % quoted(stale))

print("\n".join(problems))
' "$resumed_stop_out"

report_on "$name" "$resumed_stop_out"


# A fixture whose machine slept (#486): every line carries the `awake` reading event.sh writes
# beside `ts`, and between the step-done (ts 80100, awake 5100) and the done mark (ts 90217,
# awake 5217) the wall clock moved 10,117 s where the awake clock moved 117. So the issue ran
# 217 awake seconds inside a 10,217-second wall span, and the 10,000 between them are the
# seconds the machine was not running — three distinct numbers, so a report that printed the
# wall span, or named no excluded figure, cannot pass.
fixture_work slept_work

slept="a step of a run the machine slept through"

sv "$slept" 80000 conductor ""  step-start "" '"awake": 5000'
sv "$slept" 80100 conductor ""  step-done  "" '"awake": 5100'
sv "$slept" 90217 conductor ""  done       "" '"awake": 5217, "pr": "https://github.com/ztrange/veri/pull/998"'

plan_of "$slept"


name="#486 given a log whose wall timestamps span a gap its awake readings do not, the issue wall excludes the gap and a figure beside it names the excluded seconds"
problems=()

slept_out="$slept_work/report.md"
render "$slept_work" "$slept_out"

probe '
import re, sys

path = sys.argv[1]
lines = [l.strip() for l in open(path).read().splitlines()
         if l.strip() and not l.strip().startswith("|")]
walls = [l for l in lines if l.startswith("Wall time for the issue:")]

def names(line, number):
    return re.search(r"(?<![0-9.])%s(?![0-9.])" % number, line) is not None

if not walls:
    print("want a line starting \"Wall time for the issue:\", the report has none")
    raise SystemExit(0)

wall = walls[0]
if not names(wall, "217") or names(wall, "10217"):
    print("want the issue wall to be the 217 awake seconds, not the 10217-second wall span, it says: %r" % wall)
if not any(names(l, "10000") for l in lines):
    print("want a line outside the tables naming the 10000 seconds the machine was not running, the report says outside them: %s"
          % ", ".join(repr(l) for l in lines))
' "$slept_out"

report_on "$name" "$slept_out"


# A fixture whose machine slept INSIDE a step (#486): between the Red leaf's launch (ts 60010,
# awake 3010) and its exit (ts 70050, awake 3050) the wall clock moved 10,040 s where the awake
# clock moved 40. The step's own marks, step-start (ts 60000, awake 3000) and step-done (ts
# 70100, awake 3100), so bracket 100 awake seconds inside a 10,100-second wall span — two
# distinct numbers, so a step wall read off `ts` cannot pass.
fixture_work step_slept_work

step_slept="a step the machine slept through"

sv "$step_slept" 60000 conductor ""  step-start "" '"awake": 3000'
sv "$step_slept" 60010 developer red launch     1  '"awake": 3010, "name": "develop-red"'
sv "$step_slept" 70050 developer red exit       1  '"awake": 3050, "status": "0", "secs": "40"'
sv "$step_slept" 70100 conductor ""  step-done  "" '"awake": 3100'
sv "$step_slept" 70150 conductor ""  done       "" '"awake": 3150, "pr": "https://github.com/ztrange/veri/pull/997"'

plan_of "$step_slept"


name="#486 a step's wall is read off the awake readings of its step-start and step-done, so a sleep gap inside the step is not counted in it"
problems=()

step_slept_out="$step_slept_work/report.md"
render "$step_slept_work" "$step_slept_out"

times_say "$step_slept_out" "$step_slept=100"

report_on "$name" "$step_slept_out"


# A fixture whose machine slept INSIDE a leaf's attempt (#486): between the Red leaf's launch
# (ts 50010, awake 2010) and its exit (ts 60050, awake 2050) the wall clock moved 10,040 s
# where the awake clock moved 40. The exit's `secs` is the 10,040 wall seconds a supervise.sh
# measuring on the wall clock wrote, so the only place the 40 is to be found is the two awake
# readings — a phase wall summed off `secs` cannot pass.
fixture_work phase_slept_work

phase_slept="a leaf attempt the machine slept through"

sv "$phase_slept" 50000 conductor ""  step-start "" '"awake": 2000'
sv "$phase_slept" 50010 developer red launch     1  '"awake": 2010, "name": "develop-red"'
sv "$phase_slept" 60050 developer red exit       1  '"awake": 2050, "status": "0", "secs": "10040"'
sv "$phase_slept" 60100 conductor ""  step-done  "" '"awake": 2100'
sv "$phase_slept" 60150 conductor ""  done       "" '"awake": 2150, "pr": "https://github.com/ztrange/veri/pull/996"'

plan_of "$phase_slept"


name="#486 a phase's wall is read off the awake readings of each attempt's launch and exit, so a sleep gap inside a leaf's attempt is not counted in it"
problems=()

phase_slept_out="$phase_slept_work/report.md"
render "$phase_slept_work" "$phase_slept_out"

times_say "$phase_slept_out" red=40

report_on "$name" "$phase_slept_out"


# A fixture written before the awake clock existed (#486): no line carries an `awake` reading,
# so the only clock the log has is `ts`. The issue spans 150 wall seconds (ts 40000 to 40150),
# the step 100 (step-start 40000 to step-done 40100) and the Red attempt 40 (its exit's `secs`)
# — three distinct numbers, each the wall-clock figure the report printed before #486. And
# since none of them was measured on the awake clock, the report owes a line outside the
# tables saying they are wall-clock, so a reader does not take them for awake time.
# wall_clock_says <file> yes|no — whether a line outside the tables says the report's figures
# are wall-clock (#486): owed when no event carried an awake reading, false when they did.
# Matched on the phrase alone, the rest of the line being the implementation's to word.
wall_clock_says() {
  local out_file="$1" want="$2"
  probe '
import re, sys

path, want = sys.argv[1], sys.argv[2]
lines = [l.strip() for l in open(path).read().splitlines()
         if l.strip() and not l.strip().startswith("|")]
said = [l for l in lines if re.search(r"wall[- ]clock", l, re.I)]

if want == "yes" and not said:
    print("want a line outside the tables saying the figures are wall-clock, the report says outside them: %s"
          % ", ".join(repr(l) for l in lines))
if want == "no" and said:
    print("want no line saying the figures are wall-clock, the report says: %s"
          % ", ".join(repr(l) for l in said))
' "$out_file" "$want"
}

fixture_work unclocked_work

unclocked="a step of a run logged before the awake clock"

sv "$unclocked" 40000 conductor ""  step-start ""
sv "$unclocked" 40010 developer red launch     1  '"name": "develop-red"'
sv "$unclocked" 40050 developer red exit       1  '"status": "0", "secs": "40"'
sv "$unclocked" 40100 conductor ""  step-done  ""
sv "$unclocked" 40150 conductor ""  done       "" '"pr": "https://github.com/ztrange/veri/pull/995"'

plan_of "$unclocked"


name="#486 given a log with no awake readings at all, every figure is the wall-clock one and the report says the figures are wall-clock"
problems=()

unclocked_out="$unclocked_work/report.md"
render "$unclocked_work" "$unclocked_out"

times_say "$unclocked_out" "$unclocked=100" red=40
issue_wall_line_says "$unclocked_out" 150

wall_clock_says "$unclocked_out" yes

report_on "$name" "$unclocked_out"


# The other side of the case above (#486): the step_slept fixture carries an awake reading on
# every line, so its figures were measured on the awake clock and a line calling them
# wall-clock would be false.
name="#486 given a log with awake readings, the report does not say the figures are wall-clock"
problems=()

clocked_out="$step_slept_work/clocked-report.md"
render "$step_slept_work" "$clocked_out"

wall_clock_says "$clocked_out" no

report_on "$name" "$clocked_out"


# A fixture half written before the awake clock existed (#486): the step opened and its first
# Red attempt ran with no `awake` reading, and from the second attempt on every line carries
# one. The second attempt slept: launch (ts 30050, awake 1050) to exit (ts 40090, awake 1090)
# is 10,040 wall seconds and 40 awake ones. Summing the first attempt's 30 wall seconds with
# the second's 40 awake ones gives 70, a figure on no clock at all; on the one clock both
# attempts carry it is 30 + 10,040 = 10,070. The step (30000 to 40100) and the issue (30000
# to 40150) are 10,100 and 10,150 on that clock — every figure a distinct number — and since
# they are wall-clock, the report owes the line saying so.
fixture_work mixed_work

mixed="a step of a run whose log gained the awake clock partway"

sv "$mixed" 30000 conductor ""  step-start ""
sv "$mixed" 30010 developer red launch     1  '"name": "develop-red"'
sv "$mixed" 30040 developer red exit       1  '"status": "2", "cause": "no heartbeat for 300s (window 120s)", "secs": "30"'
sv "$mixed" 30050 developer red launch     2  '"awake": 1050, "name": "develop-red"'
sv "$mixed" 40090 developer red exit       2  '"awake": 1090, "status": "0", "secs": "10040"'
sv "$mixed" 40100 conductor ""  step-done  "" '"awake": 1100'
sv "$mixed" 40150 conductor ""  done       "" '"awake": 1150, "pr": "https://github.com/ztrange/veri/pull/994"'

plan_of "$mixed"


name="#486 given a log where only some events carry an awake reading, no figure mixes the two clocks and the report says the figures are wall-clock"
problems=()

mixed_out="$mixed_work/report.md"
render "$mixed_work" "$mixed_out"

times_say "$mixed_out" "$mixed=10100" red=10070
issue_wall_line_says "$mixed_out" 10150

wall_clock_says "$mixed_out" yes

report_on "$name" "$mixed_out"


# An empty log carries no awake-clock reading at all, so it is the no-reading case at its
# limit: a report of it says its figures are wall-clock, as one of a log written before the
# awake clock does. "Every line carries a reading" is vacuously true of no lines, which is the
# answer this case is here to refuse.
fixture_work empty_work
: > "$fixture_log"

name="#486 given an empty log, the report says its figures are wall-clock"
problems=()

empty_out="$empty_work/report.md"
render "$empty_work" "$empty_out"

wall_clock_says "$empty_out" yes

report_on "$name" "$empty_out"


# revise_cell_says <file> <step> <phase>=<used>/<budget> … — the step's revise cell in the
# `#### By step` table, read as its `<phase> <used>/<budget>` entries, must be exactly the
# ones given. REVISE_BUDGET is per phase, so the cell carries one entry per revised phase;
# what separates the entries, and their order, is the report's own to choose.
revise_cell_says() {
  local out_file="$1" step="$2"; shift 2
  probe "$PROBE_PRELUDE"'
path, step = sys.argv[1], sys.argv[2]
want = set(tuple(re.split(r"[=/]", arg)) for arg in sys.argv[3:])
header, row = located(tables_in(path), step, "a table", table_with)
if row is not None:
    i = column(header, "the revise attempts", lambda c: "revise" in c, step)
    if i is not None:
        cell = row[i] if i < len(row) else ""
        got = set(re.findall(r"([a-z]+) ([0-9]+)/([0-9?]+)", cell))
        if got != want:
            complain("step %r revise cell: want one entry per phase %s, got %r"
                     % (step, " ".join(sorted(sys.argv[3:])), cell))
print("\n".join(problems))
' "$out_file" "$step" "$@"
}

# A step revised in two phases: Red twice and Refactor once, each against a REVISE_BUDGET of
# three. Three revises in all, which a step-wide counter renders `3/3` — a budget spent that
# no phase spent. Three rather than two so this case is only about the split, not about the
# overrun the split cures. One leaf launch besides the marks, since a step raises a row of
# the table only by a counted leaf event and the cell is read off that row.
fixture_work phased_work
phased="a step revised in Red and in Refactor"
sv "$phased" 9000 conductor ""       step-start ""
sv "$phased" 9010 developer red      launch  1 '"name": "develop-red"'
sv "$phased" 9100 conductor red      revise  1 '"budget": "3"'
sv "$phased" 9200 conductor red      revise  2 '"budget": "3"'
sv "$phased" 9300 conductor refactor revise  1 '"budget": "3"'
sv "$phased" 9400 conductor ""       step-done ""

name="#488 a step revised in two phases renders its revise cell as one <phase> <used>/<budget> entry per phase"
problems=()

phased_out="$phased_work/report.md"
render "$phased_work" "$phased_out"

revise_cell_says "$phased_out" "$phased" red=2/3 refactor=1/3

report_on "$name" "$phased_out"


# revise_cell_within_budget <file> <step> — no `<used>/<budget>` count anywhere in the step's
# revise cell may exceed its budget, whether it sits in a phase entry or stands alone.
revise_cell_within_budget() {
  probe "$PROBE_PRELUDE"'
path, step = sys.argv[1], sys.argv[2]
header, row = located(tables_in(path), step, "a table", table_with)
if row is not None:
    i = column(header, "the revise attempts", lambda c: "revise" in c, step)
    if i is not None:
        cell = row[i] if i < len(row) else ""
        over = [u + "/" + b for u, b in re.findall(r"([0-9]+)/([0-9]+)", cell) if int(u) > int(b)]
        if over:
            complain("step %r revise cell: counts above the budget %s in %r"
                     % (step, " ".join(over), cell))
print("\n".join(problems))
' "$1" "$2"
}

# A step that revised Red once and Refactor once under a REVISE_BUDGET of two. Two revises in
# all, which a step-wide counter renders `2/2` — a budget spent that neither phase spent.
fixture_work twice_work
twice="a step revised once in Red and once in Refactor"
sv "$twice" 9500 conductor ""       step-start ""
sv "$twice" 9510 developer red      launch  1 '"name": "develop-red"'
sv "$twice" 9600 conductor red      revise  1 '"budget": "2"'
sv "$twice" 9700 conductor refactor revise  1 '"budget": "2"'
sv "$twice" 9800 conductor ""       step-done ""

name="#488 a step revised once in each of two phases renders each as 1/2, no count above the budget"
problems=()

twice_out="$twice_work/report.md"
render "$twice_work" "$twice_out"

revise_cell_says "$twice_out" "$twice" red=1/2 refactor=1/2
revise_cell_within_budget "$twice_out" "$twice"

report_on "$name" "$twice_out"


# revise_cell_spent <file> <step> <phase> <budget> — the step's revise cell reads
# `<budget>/<budget>`, the phase named before it or not: a step revised in one phase only has
# no second phase to tell it from, which is why the step-wide spelling `3/3` still stands.
revise_cell_spent() {
  probe "$PROBE_PRELUDE"'
path, step, phase, budget = sys.argv[1:5]
header, row = located(tables_in(path), step, "a table", table_with)
if row is not None:
    i = column(header, "the revise attempts", lambda c: "revise" in c, step)
    if i is not None:
        cell = (row[i] if i < len(row) else "").strip()
        if not re.fullmatch(r"(%s )?%s/%s" % (re.escape(phase), budget, budget), cell):
            complain("step %r revise cell: want %s/%s, spent in %s, got %r"
                     % (step, budget, budget, phase, cell))
print("\n".join(problems))
' "$@"
}

# A step that revised Red twice under a REVISE_BUDGET of two, and nothing else: the budget
# genuinely spent, in one phase. Splitting the cell per phase must not turn it into less.
fixture_work spent_work
spent="a step that spent its revise budget in Red"
sv "$spent" 9900 conductor ""  step-start ""
sv "$spent" 9910 developer red launch  1 '"name": "develop-red"'
sv "$spent" 9920 conductor red revise  1 '"budget": "2"'
sv "$spent" 9930 conductor red revise  2 '"budget": "2"'
sv "$spent" 9940 conductor ""  step-done ""

name="#488 a step that revised one phase REVISE_BUDGET times renders that phase as 2/2"
problems=()

spent_out="$spent_work/report.md"
render "$spent_work" "$spent_out"

revise_cell_spent "$spent_out" "$spent" red 2

report_on "$name" "$spent_out"


# revise_cell_is <file> <step> <want> — the step's revise cell reads exactly <want>.
revise_cell_is() {
  probe "$PROBE_PRELUDE"'
path, step, want = sys.argv[1:4]
header, row = located(tables_in(path), step, "a table", table_with)
if row is not None:
    i = column(header, "the revise attempts", lambda c: "revise" in c, step)
    if i is not None:
        cell = (row[i] if i < len(row) else "").strip()
        if cell != want:
            complain("step %r revise cell: want %r, got %r" % (step, want, cell))
print("\n".join(problems))
' "$@"
}

# A step that was never revised: a leaf launched, no `revise` mark. ADR-0014 keeps a figure no
# mark supplied at `unknown` rather than `0`, and splitting the cell per phase must not turn an
# absent phase list into an empty cell, a `0/?`, or anything else.
fixture_work unrevised_work
unrevised="a step with no revise marks"
sv "$unrevised" 10000 conductor ""  step-start ""
sv "$unrevised" 10010 developer red launch  1 '"name": "develop-red"'
sv "$unrevised" 10020 conductor ""  step-done ""

name="#488 a step with no revise marks renders its revise cell as unknown, as before"
problems=()

unrevised_out="$unrevised_work/report.md"
render "$unrevised_work" "$unrevised_out"

revise_cell_is "$unrevised_out" "$unrevised" unknown

report_on "$name" "$unrevised_out"


# kind_cell_is <file> <step> <want> — the step's By-step kind cell reads exactly <want>.
kind_cell_is() {
  probe "$PROBE_PRELUDE"'
path, step, want = sys.argv[1:4]
cell = cell_in(tables_in(path), step, "the kind", lambda c: "kind" in c)
if cell is not None and cell != want:
    complain("step %r kind cell: want %r, got %r" % (step, want, cell))
print("\n".join(problems))
' "$@"
}

# full_step <step> <ts> — the marks of a step that ran Red → Green → Refactor, each phase
# launched once and passed, from <ts> on.
full_step() {
  local step=$1 t=$2
  sv "$step" "$t"          conductor ""       step-start ""
  sv "$step" $((t + 10))  developer red      launch  1 '"name": "develop-red"'
  sv "$step" $((t + 20))  verifier  red      launch  1 '"name": "verify-red"'
  sv "$step" $((t + 30))  verifier  red      verdict 1 '"verdict": "PASS", "reason": "fails for the reason it names"'
  sv "$step" $((t + 40))  developer green    launch  1 '"name": "develop-green"'
  sv "$step" $((t + 50))  verifier  green    launch  1 '"name": "verify-green"'
  sv "$step" $((t + 60))  verifier  green    verdict 1 '"verdict": "PASS", "reason": "the step is pinned and no wider"'
  sv "$step" $((t + 70))  developer refactor launch  1 '"name": "develop-refactor"'
  sv "$step" $((t + 80))  verifier  refactor launch  1 '"name": "verify-refactor"'
  sv "$step" $((t + 90))  verifier  refactor verdict 1 '"verdict": "PASS", "reason": "behaviour unchanged"'
  sv "$step" $((t + 100)) conductor ""       step-done ""
}

# A step that ran Red → Green → Refactor and closed on `step-done`, beside one whose red leaf
# found the criterion already satisfied and which closed on its `pin` mark (#454).
fixture_work kinds_work
full="a step that ran red, green and refactor"
pinned_kind="a step that closed on its pin mark"
full_step "$full" 18000
sv "$pinned_kind" 18200 conductor ""  step-start ""
sv "$pinned_kind" 18210 developer red launch  1 '"name": "develop-red"'
sv "$pinned_kind" 18220 verifier  pin launch  1 '"name": "verdict-pin"'
sv "$pinned_kind" 18230 verifier  pin verdict 1 '"verdict": "PASS", "reason": "already satisfied"'
sv "$pinned_kind" 18240 conductor pin pin     ""

name="#454 the By-step kind cell reads pin for a step with a pin mark and full for a Red-Green-Refactor step"
problems=()

kinds_out="$kinds_work/report.md"
render "$kinds_work" "$kinds_out"

kind_cell_is "$kinds_out" "$full" full
kind_cell_is "$kinds_out" "$pinned_kind" pin

report_on "$name" "$kinds_out"


# A full step beside one whose verify-pin verdict passed but which never wrote a `pin` mark.
fixture_work satisfied_work
full="a step that ran red, green and refactor"
satisfied="a step whose red leaf found its criterion already satisfied"
full_step "$full" 19000
sv "$satisfied" 19200 conductor ""  step-start ""
sv "$satisfied" 19210 developer red launch  1 '"name": "develop-red"'
sv "$satisfied" 19220 verifier  pin launch  1 '"name": "verdict-pin"'
sv "$satisfied" 19230 verifier  pin verdict 1 '"verdict": "PASS", "reason": "already satisfied"'

name="#454 the By-step kind cell reads already-satisfied for a verify-pin PASS with no pin mark and full for a full step"
problems=()

sat_out="$satisfied_work/report.md"
render "$satisfied_work" "$sat_out"

kind_cell_is "$sat_out" "$full" full
kind_cell_is "$sat_out" "$satisfied" already-satisfied

report_on "$name" "$sat_out"


echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
