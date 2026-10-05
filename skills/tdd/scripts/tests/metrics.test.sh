#!/usr/bin/env bash
# Unit tests for scripts/metrics.sh — the per-issue metrics report computed from the run's
# event log.
#
# Contract under test:
#   metrics.sh <n>  → exit 0, and on stdout a row per phase of the run carrying that phase's
#                     attempts, PASS verdicts, REJECT verdicts and kills, and a row per step
#                     carrying the same four plus the stuck retries that step used and the
#                     no-verdict relaunches its verifiers spent.
#   the log         → `.tdd/events.jsonl`, read relative to the directory the script runs in.
#
# Run: skills/tdd/scripts/tests/metrics.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
METRICS="$HERE/../metrics.sh"

source "$HERE/lib/harness.sh"

report_on() {
  local name="$1" out_file="$2"
  probes_run
  [[ "${#problems[@]}" -eq 0 ]] ||
    problems+=("the report was: $(printf '%q' "$(cat "$out_file")")")
  report "$name"
}

render() {
  local dir="$1" out_file="$2" status
  ( cd "$dir" && "$METRICS" 108 ) > "$out_file" 2>/dev/null
  status=$?
  [[ "$status" -eq 0 ]] ||
    problems+=("want metrics.sh to exit 0, it exited $status")
}

probe() {
  printf '%s\0' "$1" "$(($# - 1))" "${@:2}" >> "$probe_spool"
}

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

table_says() {
  local out_file="$1"; shift
  counts_table_says "$out_file" phase attempts,pass,reject,kills "$@"
}

fixture_works=()
on_exit '[[ "${#fixture_works[@]}" -eq 0 ]] || rm -rf "${fixture_works[@]}"'

probe_spool="$(mktemp)"
fixture_works+=("$probe_spool")

fixture_work() {
  local dir
  dir="$(scratch_dir)"
  mkdir -p "$dir/.tdd"
  fixture_works+=("$dir")
  printf -v "$1" '%s' "$dir"
  fixture_log="$dir/.tdd/events.jsonl"
}

fixture_work work

event_line() {
  local log="$1"; shift
  printf '{"ts": %s, "issue": "108", "actor": "%s", "phase": "%s", "step": "%s", "event": "%s", "attempt": "%s", "skill_commit": "c0ffee1"%s}\n' \
    "$1" "$2" "$3" "$4" "$5" "$6" "${7:+, ${7}}" >> "$log"
}

sv() {
  event_line "$fixture_log" "$2" "$3" "$4" "$1" "$5" "$6" "${7:-}"
}

step="metrics.sh renders a markdown table of per-phase counts"
ev() {
  sv "$step" "$@"
}


ev 990 conductor "" step-start ""

ev 1000 developer red launch 1 '"name": "develop-red", "cmd": "run-leaf.sh", "model": ""'
ev 1100 developer red exit   1 '"status": "0", "secs": "100"'
ev 1110 verifier  red launch 1 '"name": "verify-red", "cmd": "run-leaf.sh", "model": ""'
ev 1130 verifier  red exit   1 '"status": "0", "secs": "20"'
ev 1130 verifier  red verdict 1 '"verdict": "PASS", "reason": "the case fails for the reason it was written to catch"'

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


step_table_says() {
  local out_file="$1"; shift
  counts_table_says "$out_file" step attempts,pass,reject,kills,retries "$@"
}

fixture_work step_work

one="metrics.sh renders a markdown table of per-phase counts"
two="the table carries a per-step section with the same counts"

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

fixture_work budget_work

frugal="the table reports revise attempts used of REVISE_BUDGET and refactor transforms used"
spendthrift="the table reports wall seconds and API seconds per phase and per step"

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

fixture_work time_work

usage_json() {
  printf '"duration_ms": "0", "duration_api_ms": "%s", "num_turns": "9", "total_cost_usd": "0.5", "input_tokens": "1000", "output_tokens": "2000", "cache_read_input_tokens": "3000", "cache_creation_input_tokens": "4000"' "$1"
}

brisk="the table reports wall seconds and API seconds per phase and per step"
slow="the table reports turns, the four token counts and dollars per phase"

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

sv "$slow" 8700 conductor ""    done       "" '"pr": "https://github.com/ztrange/veri/pull/999"'


name="the phase and step rows carry their wall and API seconds, and the report gives the issue wall from its first event to done"
problems=()

time_out="$time_work/report.md"
render "$time_work" "$time_out"

times_say "$time_out" red=210,155 green=390,240 "$brisk=400,175" "$slow=600,220"
issue_wall_says "$time_out" 1700

report_on "$name" "$time_out"

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

fixture_work cost_work

cost_json() {
  printf '"duration_ms": "0", "duration_api_ms": "0", "num_turns": "%s", "total_cost_usd": "%s", "input_tokens": "%s", "output_tokens": "%s", "cache_read_input_tokens": "%s", "cache_creation_input_tokens": "%s"' \
    "$1" "$2" "$3" "$4" "$5" "$6"
}

cheap="the table reports turns, the four token counts and dollars per step"
dear="a step recovered after a REJECT contributes its rejected attempts to rework"

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

fixture_work rework_work

unrejected="rework and waste are both empty in a step nothing rejected"
recovered="a step recovered after a REJECT contributes its rejected attempts to rework"

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

fixture_work bail_work

landed="the first step of the run reached its step-done mark"
bailed="a bailed step contributes every attempt to waste"

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

fixture_work system_work

landed_first="the table reports steps done of planned"
killed="the table reports the issue outcome, a bail split system or process"

sv "$landed_first" 11000 conductor ""    step-start ""
sv "$landed_first" 11100 conductor ""    step-done  ""
sv "$killed"       11200 conductor ""    step-start ""
sv "$killed"       11300 conductor green bail       "" '"cause": "killed-stuck", "classification": "system"'

plan_of "$landed_first" -- "$killed" "a third step the run never reached"

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


name="a log of exactly one run that ended in a done mark renders its issue wall as a number, not unknown"
problems=()

issue_wall_says "$landed_out" 400

report_on "$name" "$landed_out"

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


name="on a log with a bail, a resume and a done the issue wall runs from the last resume to the done mark"
problems=()

issue_wall_says "$rerun_out" 200

report_on "$name" "$rerun_out"


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


name="#643 given a log with a real suspend, the not-running line still names the suspend's seconds and the issue wall is the awake span"
problems=()

probe '
import re, sys

lines = [l.strip() for l in open(sys.argv[1]).read().splitlines()]
stopped = [l for l in lines if l.startswith("Seconds the machine was not running inside that span:")]
walls = [l for l in lines if l.startswith("Wall time for the issue:")]

if not stopped:
    print("want a line starting \"Seconds the machine was not running inside that span:\", the report has none")
elif not stopped[0].startswith("Seconds the machine was not running inside that span: 10000 s,"):
    print("want the not-running line to say 10000 s, it says: %r" % stopped[0])
if not walls:
    print("want a line starting \"Wall time for the issue:\", the report has none")
elif re.match(r"Wall time for the issue: 217 s\b", walls[0]) is None:
    print("want the issue wall to be the 217-second awake span, it says: %r" % walls[0])
' "$slept_out"

report_on "$name" "$slept_out"


NOT_RUNNING_ZERO='
import sys

lines = [l.strip() for l in open(sys.argv[1]).read().splitlines()]
stopped = [l for l in lines if l.startswith("Seconds the machine was not running inside that span:")]

if not stopped:
    print("want a line starting \"Seconds the machine was not running inside that span:\", the report has none")
elif not stopped[0].startswith("Seconds the machine was not running inside that span: 0 s,"):
    print("want the not-running line to say 0 s, it says: %r" % stopped[0])
'

fixture_work level_clocks_work

level_clocks="a step of a run whose awake clock kept pace with its wall clock"

sv "$level_clocks" 70000 conductor ""  step-start "" '"awake": 4000'
sv "$level_clocks" 70100 conductor ""  step-done  "" '"awake": 4100'
sv "$level_clocks" 70217 conductor ""  done       "" '"awake": 4217, "pr": "https://github.com/ztrange/veri/pull/993"'

plan_of "$level_clocks"


name="#643 given a log whose awake clock advanced exactly as far as its wall clock over the issue span, the not-running line says 0 s"
problems=()

level_clocks_out="$level_clocks_work/report.md"
render "$level_clocks_work" "$level_clocks_out"

probe "$NOT_RUNNING_ZERO" "$level_clocks_out"

report_on "$name" "$level_clocks_out"


fixture_work ahead_clocks_work

ahead_clocks="a step of a run whose awake clock ran one second ahead of its wall clock"

sv "$ahead_clocks" 70000 conductor ""  step-start "" '"awake": 4000'
sv "$ahead_clocks" 70100 conductor ""  step-done  "" '"awake": 4100'
sv "$ahead_clocks" 70217 conductor ""  done       "" '"awake": 4218, "pr": "https://github.com/ztrange/veri/pull/994"'

plan_of "$ahead_clocks"


name="#643 given a log whose awake clock advanced one second further than its wall clock over the issue span, the not-running line says 0 s, never a negative number"
problems=()

ahead_clocks_out="$ahead_clocks_work/report.md"
render "$ahead_clocks_work" "$ahead_clocks_out"

probe "$NOT_RUNNING_ZERO" "$ahead_clocks_out"

report_on "$name" "$ahead_clocks_out"


name="#643 given a log whose awake clock advanced one second further than its wall clock over the issue span, the issue wall is no larger than the wall-clock span"
problems=()

probe '
import re, sys

lines = [l.strip() for l in open(sys.argv[1]).read().splitlines()]
walls = [l for l in lines if l.startswith("Wall time for the issue:")]

if not walls:
    print("want a line starting \"Wall time for the issue:\", the report has none")
    raise SystemExit(0)

seconds = re.match(r"Wall time for the issue: ([0-9]+) s", walls[0])
if seconds is None or int(seconds.group(1)) > 217:
    print("want the issue wall no larger than the 217-second wall span, it says: %r" % walls[0])
' "$ahead_clocks_out"

report_on "$name" "$ahead_clocks_out"


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


name="#486 given a log with awake readings, the report does not say the figures are wall-clock"
problems=()

clocked_out="$step_slept_work/clocked-report.md"
render "$step_slept_work" "$clocked_out"

wall_clock_says "$clocked_out" no

report_on "$name" "$clocked_out"


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


fixture_work empty_work
: > "$fixture_log"

name="#486 given an empty log, the report says its figures are wall-clock"
problems=()

empty_out="$empty_work/report.md"
render "$empty_work" "$empty_out"

wall_clock_says "$empty_out" yes

report_on "$name" "$empty_out"


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


kind_cell_is() {
  probe "$PROBE_PRELUDE"'
path, step, want = sys.argv[1:4]
cell = cell_in(tables_in(path), step, "the kind", lambda c: "kind" in c)
if cell is not None and cell != want:
    complain("step %r kind cell: want %r, got %r" % (step, want, cell))
print("\n".join(problems))
' "$@"
}

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

satisfied_red() {
  local step=$1 t=$2
  sv "$step" "$t"         conductor ""  step-start ""
  sv "$step" $((t + 10)) developer red launch  1 '"name": "develop-red"'
  sv "$step" $((t + 20)) verifier  pin launch  1 '"name": "verdict-pin"'
  sv "$step" $((t + 30)) verifier  pin verdict 1 '"verdict": "PASS", "reason": "already satisfied"'
}

fixture_work kinds_work
full="a step that ran red, green and refactor"
pinned_kind="a step that closed on its pin mark"
full_step "$full" 18000
satisfied_red "$pinned_kind" 18200
sv "$pinned_kind" 18240 conductor pin pin     ""

name="#454 the By-step kind cell reads pin for a step with a pin mark and full for a Red-Green-Refactor step"
problems=()

kinds_out="$kinds_work/report.md"
render "$kinds_work" "$kinds_out"

kind_cell_is "$kinds_out" "$full" full
kind_cell_is "$kinds_out" "$pinned_kind" pin

report_on "$name" "$kinds_out"


fixture_work satisfied_work
full="a step that ran red, green and refactor"
satisfied="a step whose red leaf found its criterion already satisfied"
full_step "$full" 19000
satisfied_red "$satisfied" 19200

name="#454 the By-step kind cell reads already-satisfied for a verify-pin PASS with no pin mark and full for a full step"
problems=()

sat_out="$satisfied_work/report.md"
render "$satisfied_work" "$sat_out"

kind_cell_is "$sat_out" "$full" full
kind_cell_is "$sat_out" "$satisfied" already-satisfied

report_on "$name" "$sat_out"


fixture_work leafcount_work
many_pin="a pinned step that launched many leaves"
many_sat="a satisfied step that launched many leaves"
two_leaf="a full step with only two leaves in the log"
for t in 20000 20100; do
  step=$many_pin; [[ $t -eq 20100 ]] && step=$many_sat
  sv "$step" "$t"         conductor ""    step-start ""
  sv "$step" $((t + 10)) developer red   launch  1 '"name": "develop-red"'
  sv "$step" $((t + 20)) verifier  red   launch  1 '"name": "verify-red"'
  sv "$step" $((t + 30)) verifier  red   verdict 1 '"verdict": "REJECT", "reason": "passes already"'
  sv "$step" $((t + 40)) developer red   launch  2 '"name": "revise-red"'
  sv "$step" $((t + 50)) verifier  red   launch  2 '"name": "verify-red"'
  sv "$step" $((t + 60)) verifier  red   verdict 2 '"verdict": "REJECT", "reason": "passes already"'
  sv "$step" $((t + 70)) verifier  pin   launch  1 '"name": "verdict-pin"'
  sv "$step" $((t + 80)) verifier  pin   verdict 1 '"verdict": "PASS", "reason": "already satisfied"'
done
sv "$many_pin" 20090 conductor pin pin ""
sv "$two_leaf" 20200 conductor ""    step-start ""
sv "$two_leaf" 20210 developer green launch  1 '"name": "develop-green"'
sv "$two_leaf" 20220 verifier  green launch  1 '"name": "verify-green"'
sv "$two_leaf" 20230 verifier  green verdict 1 '"verdict": "PASS", "reason": "the step is pinned and no wider"'
sv "$two_leaf" 20240 conductor ""    step-done ""

name="#454 the By-step kind follows the step's pin mark or verify-pin verdict, not its leaf count"
problems=()

leafcount_out="$leafcount_work/report.md"
render "$leafcount_work" "$leafcount_out"

kind_cell_is "$leafcount_out" "$many_pin" pin
kind_cell_is "$leafcount_out" "$many_sat" already-satisfied
kind_cell_is "$leafcount_out" "$two_leaf" full

report_on "$name" "$leafcount_out"


fixture_work allfull_work
first_full="the first of two steps that ran red, green and refactor"
second_full="the second of two steps that ran red, green and refactor"
full_step "$first_full" 21000
full_step "$second_full" 21200

name="#454 a report over only full steps still renders the kind column, reading full on every row"
problems=()

allfull_out="$allfull_work/report.md"
render "$allfull_work" "$allfull_out"

kind_cell_is "$allfull_out" "$first_full" full
kind_cell_is "$allfull_out" "$second_full" full

report_on "$name" "$allfull_out"


by_step_note_names() {
  probe "$PROBE_PRELUDE"'
lines = open(sys.argv[1]).read().splitlines()
start = next((i for i, l in enumerate(lines) if l.strip() == "#### By step"), None)
if start is None:
    complain("want a #### By step heading, the report has none")
else:
    i = start + 1
    while i < len(lines) and not lines[i].strip().startswith("|"):
        i += 1
    while i < len(lines) and lines[i].strip().startswith("|"):
        i += 1
    note = next((l for l in lines[i:] if l.strip()), "")
    if note.startswith("#"):
        complain("want a line under the By-step table, the next line is the heading %r" % note)
    else:
        for word in ("turns", "dollars", "comparable", "VERI_MODEL",
                     "VERI_MODEL_DEVELOPER", "VERI_MODEL_VERIFIER"):
            if word not in note:
                complain("want the line under the By-step table to name %r, got %r"
                         % (word, note))
print("\n".join(problems))
' "$@"
}

name="#454 the By-step table is followed by a line naming turns as comparable across runs, dollars as not, and the three model knobs"
problems=()

by_step_note_names "$allfull_out"

report_on "$name" "$allfull_out"

report_reads_as_before() {
  probe "$PROBE_PRELUDE"'
path, before = sys.argv[1:3]
lines = open(path).read().splitlines()
start = next((i for i, l in enumerate(lines) if l.strip() == "#### By step"), None)
if start is None:
    complain("want a #### By step heading, the report has none")
else:
    i = start + 1
    while i < len(lines) and not lines[i].strip().startswith("|"):
        i += 1
    header = cells(lines[i]) if i < len(lines) else []
    drop = header.index("kind") if "kind" in header else None
    while i < len(lines) and lines[i].strip().startswith("|"):
        if drop is not None:
            row = lines[i].strip()[1:-1].split("|")
            lines[i] = "|" + "|".join(row[:drop] + row[drop + 1:]) + "|"
        i += 1
    j = i + 1
    if j < len(lines) and lines[j].strip() and not lines[j].startswith("#"):
        del lines[j:j + 2]
    want = open(before).read().splitlines()
    for n, (got, exp) in enumerate(zip(lines, want), 1):
        if got != exp:
            complain("line %d: want %r, got %r" % (n, exp, got))
    if len(lines) != len(want):
        complain("want %d lines, got %d" % (len(want), len(lines)))
print("\n".join(problems))
' "$@"
}

fixture_work before_work
old_full="a full step"
old_pin="a pinned step"
old_usage() {
  printf '"duration_ms": "0", "duration_api_ms": "%s", "num_turns": "%s", "total_cost_usd": "%s", "input_tokens": "100", "output_tokens": "200", "cache_read_input_tokens": "300", "cache_creation_input_tokens": "400"' "$1" "$2" "$3"
}
sv "$old_full" 1000 conductor ""    step-start ""
sv "$old_full" 1010 developer red   launch  1 '"name": "develop-red"'
sv "$old_full" 1100 developer red   exit    1 '"status": "0", "secs": "90"'
sv "$old_full" 1100 developer red   usage   1 "$(old_usage 70000 5 0.40)"
sv "$old_full" 1110 verifier  red   launch  1 '"name": "verify-red"'
sv "$old_full" 1130 verifier  red   exit    1 '"status": "0", "secs": "20"'
sv "$old_full" 1130 verifier  red   usage   1 "$(old_usage 15000 2 0.10)"
sv "$old_full" 1130 verifier  red   verdict 1 '"verdict": "REJECT", "reason": "wrong reason"'
sv "$old_full" 1140 developer red   launch  2 '"name": "revise-red"'
sv "$old_full" 1200 developer red   exit    2 '"status": "0", "secs": "60"'
sv "$old_full" 1200 developer red   usage   2 "$(old_usage 50000 4 0.30)"
sv "$old_full" 1210 verifier  red   launch  2 '"name": "verify-red"'
sv "$old_full" 1230 verifier  red   exit    2 '"status": "0", "secs": "20"'
sv "$old_full" 1230 verifier  red   usage   2 "$(old_usage 15000 2 0.10)"
sv "$old_full" 1230 verifier  red   verdict 2 '"verdict": "PASS", "reason": "fails as written"'
sv "$old_full" 1300 developer green launch  1 '"name": "develop-green"'
sv "$old_full" 1400 developer green exit    1 '"status": "0", "secs": "100"'
sv "$old_full" 1400 developer green usage   1 "$(old_usage 80000 9 0.70)"
sv "$old_full" 1410 verifier  green launch  1 '"name": "verify-green"'
sv "$old_full" 1430 verifier  green exit    1 '"status": "0", "secs": "20"'
sv "$old_full" 1430 verifier  green usage   1 "$(old_usage 10000 3 0.20)"
sv "$old_full" 1430 verifier  green verdict 1 '"verdict": "PASS", "reason": "pinned"'
sv "$old_full" 1500 conductor ""    step-done ""
sv "$old_pin"  2000 conductor ""    step-start ""
sv "$old_pin"  2010 developer red   launch  1 '"name": "develop-red"'
sv "$old_pin"  2100 developer red   exit    1 '"status": "0", "secs": "90"'
sv "$old_pin"  2100 developer red   usage   1 "$(old_usage 60000 6 0.50)"
sv "$old_pin"  2110 verifier  pin   launch  1 '"name": "verdict-pin"'
sv "$old_pin"  2130 verifier  pin   exit    1 '"status": "0", "secs": "20"'
sv "$old_pin"  2130 verifier  pin   usage   1 "$(old_usage 12000 2 0.15)"
sv "$old_pin"  2130 verifier  pin   verdict 1 '"verdict": "PASS", "reason": "already satisfied"'
sv "$old_pin"  2140 conductor pin   pin     ""

before_report="$before_work/before.md"
printf '%s\n' '### 📊 Metrics — issue 108

Wall time for the issue: unknown s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Every figure in this report is wall-clock: the log carries no awake-clock reading, so time the machine spent asleep is counted in them.
Steps done: 2 of unknown planned.
Outcome: unknown — the log carries no mark ending the run.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 5 | 1 | 1 | 0 | 280 | 210 | 19 | 500 | 1000 | 1500 | 2000 | 1.40 |
| green | 2 | 1 | 0 | 0 | 120 | 90 | 12 | 200 | 400 | 600 | 800 | 0.90 |
| pin | 1 | 1 | 0 | 0 | 20 | 12 | 2 | 100 | 200 | 300 | 400 | 0.15 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 110 | 0.50 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- |
| a full step | 6 | 2 | 1 | 0 | 0 | 0 | 240 | 25 | 600 | 1200 | 1800 | 2400 | 1.80 | 500 | unknown | unknown | unknown |  |  |
| a pinned step | 2 | 1 | 0 | 0 | 0 | 0 | 72 | 8 | 200 | 400 | 600 | 800 | 0.65 | unknown | unknown | unknown | unknown |  |  |

#### Test-command seconds, by tier

| tier |
| --- |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 33 | 800 | 1600 | 2400 | 3200 | 2.45 |' > "$before_report"

name="#454 every By-step column that existed before, and every other section, reads the same for an existing log"
problems=()

before_out="$before_work/report.md"
render "$before_work" "$before_out"

report_reads_as_before "$before_out" "$before_report"

report_on "$name" "$before_out"

PASSES_PRELUDE='
def pass_rows(path, step, wanted):
    tables = tables_in(path)
    section = next((t for t in tables
                    if sum(1 for r in t[1:] if is_row(r, step)) == len(wanted)), None)
    if section is None:
        labels = [", ".join(repr(r[0]) for r in t[1:] if r) for t in tables]
        complain("want a table with %d rows for step %r, one per refactor pass, the report has tables with rows: %s"
                 % (len(wanted), step, "; ".join(labels) or "nothing"))
        print("\n".join(problems))
        raise SystemExit(0)
    header, rows = section[0], [r for r in section[1:] if is_row(r, step)]
    return header, rows, column(header, "the pass", lambda c: c.strip() == "pass", step)

def pass_row(rows, at, index, step):
    row = next((r for r in rows if at < len(r) and r[at] == index), None)
    if row is None:
        complain("want a row for pass %s of step %r, its rows have passes: %s"
                 % (index, step, ", ".join(repr(r[at]) for r in rows if at < len(r))))
    return row

def expected_rows(rows, at, wanted, step):
    for arg in wanted:
        index, expected = arg.split("=", 1)
        row = pass_row(rows, at, index, step)
        if row is not None:
            yield index, expected, row
'

passes_say() {
  local out_file="$1" step="$2"; shift 2
  probe "$PROBE_PRELUDE$PASSES_PRELUDE"'
path, step = sys.argv[1], sys.argv[2]
wanted = sys.argv[3:]
header, rows, at = pass_rows(path, step, wanted)
spent = column(header, "the transforms against budget",
               lambda c: "refactor" in c or "transform" in c, step)
stop = column(header, "why the pass stopped", lambda c: "stop" in c, step)
if None not in (at, spent, stop):
    for index, expected, row in expected_rows(rows, at, wanted, step):
        pair, reason = expected.split(",", 1)
        for what, i, want in (("transforms/budget", spent, pair), ("stopped", stop, reason)):
            got = row[i] if i < len(row) else ""
            if got != want:
                complain("pass %s of step %r %s: want %r, got %r" % (index, step, what, want, got))

print("\n".join(problems))
' "$out_file" "$step" "$@"
}

fixture_work twice_work

twice="a step whose refactor phase ran twice"

sv "$twice" 50000 conductor ""       step-start ""
sv "$twice" 50002 developer refactor launch  1 '"name": "develop-refactor"'
sv "$twice" 50008 developer refactor exit    1 '"status": "0", "secs": "6"'
sv "$twice" 50010 conductor refactor refactor "" '"transforms": "2", "budget": "5", "stopped": "nothing-structural", "pass": "1"'
sv "$twice" 50012 verifier  refactor launch  1 '"name": "verify-refactor"'
sv "$twice" 50016 verifier  refactor exit    1 '"status": "0", "secs": "4"'
sv "$twice" 50016 verifier  refactor verdict 1 '"verdict": "PASS", "reason": "behaviour is preserved"'
sv "$twice" 50102 developer refactor launch  2 '"name": "develop-refactor"'
sv "$twice" 50108 developer refactor exit    2 '"status": "0", "secs": "6"'
sv "$twice" 50110 conductor refactor refactor "" '"transforms": "1", "budget": "5", "stopped": "structural-owed", "pass": "2"'
sv "$twice" 50112 verifier  refactor launch  2 '"name": "verify-refactor"'
sv "$twice" 50116 verifier  refactor exit    2 '"status": "0", "secs": "4"'
sv "$twice" 50116 verifier  refactor verdict 2 '"verdict": "PASS", "reason": "behaviour is preserved"'
sv "$twice" 50120 conductor ""       step-done ""


name="#502 a step with two refactor marks shows one per-pass row each, with its own transforms against budget and its own stop reason"
problems=()

twice_out="$twice_work/report.md"
render "$twice_work" "$twice_out"

passes_say "$twice_out" "$twice" "1=2/5,nothing-structural" "2=1/5,structural-owed"

report_on "$name" "$twice_out"

one_pass_says() {
  local out_file="$1"; shift
  probe "$PROBE_PRELUDE"'
path = sys.argv[1]
tables = tables_in(path)
by_step = next((t for t in tables if "revise" in t[0]), None)
per_pass = next((t for t in tables if "pass" in t[0]), None)
for arg in sys.argv[2:]:
    step, expected = arg.split("=", 1)
    pair, reason = expected.split(",", 1)
    if by_step is None:
        complain("want a By-step table headed with a revise column, the report has none")
    else:
        row = next((r for r in by_step[1:] if is_row(r, step)), None)
        if row is None:
            complain("want a By-step row for step %r, it has none" % step)
        else:
            for what, heading, want in (("refactor", lambda c: c == "refactor", pair),
                                        ("stopped", lambda c: "stop" in c, reason)):
                i = column(by_step[0], what, heading, step)
                got = row[i] if i is not None and i < len(row) else ""
                if i is not None and got != want:
                    complain("By-step %s of step %r: want %r, got %r" % (what, step, want, got))
    if per_pass is None:
        complain("want a per-pass table headed with a pass column, the report has none")
    else:
        n = sum(1 for r in per_pass[1:] if is_row(r, step))
        if n != 1:
            complain("want exactly one per-pass row for step %r, got %d" % (step, n))
print("\n".join(problems))
' "$out_file" "$@"
}

fixture_work once_work

unindexed="a step whose one refactor mark carries no pass index"
indexed="a step whose one refactor mark carries pass one"

sv "$unindexed" 60000 conductor ""       step-start ""
sv "$unindexed" 60002 developer refactor launch  1 '"name": "develop-refactor"'
sv "$unindexed" 60008 developer refactor exit    1 '"status": "0", "secs": "6"'
sv "$unindexed" 60010 conductor refactor refactor "" '"transforms": "3", "budget": "5", "stopped": "structural-owed"'
sv "$unindexed" 60020 conductor ""       step-done ""
sv "$indexed"   61000 conductor ""       step-start ""
sv "$indexed"   61002 developer refactor launch  1 '"name": "develop-refactor"'
sv "$indexed"   61008 developer refactor exit    1 '"status": "0", "secs": "6"'
sv "$indexed"   61010 conductor refactor refactor "" '"transforms": "1", "budget": "4", "stopped": "nothing-structural", "pass": "1"'
sv "$indexed"   61020 conductor ""       step-done ""


name="#502 a step with one refactor mark, with or without a pass index, keeps its By-step refactor and stopped cells and appears once in the per-pass section"
problems=()

once_out="$once_work/report.md"
render "$once_work" "$once_out"

one_pass_says "$once_out" "$unindexed=3/5,structural-owed" "$indexed=1/4,nothing-structural"

report_on "$name" "$once_out"

pass_costs_say() {
  local out_file="$1" step="$2"; shift 2
  probe "$PROBE_PRELUDE$PASSES_PRELUDE"'
path, step = sys.argv[1], sys.argv[2]
wanted = sys.argv[3:]
header, rows, at = pass_rows(path, step, wanted)
verdict = column(header, "the verdict", lambda c: "verdict" in c, step)
wall = column(header, "the wall seconds", lambda c: "wall" in c, step)
cost = column(header, "the cost", lambda c: "$" in c or "cost" in c, step)
if None not in (at, verdict, wall, cost):
    for index, expected, row in expected_rows(rows, at, wanted, step):
        want_verdict, want_wall, want_cost = expected.split(",")
        got = row[verdict] if verdict < len(row) else ""
        if got != want_verdict:
            complain("pass %s of step %r verdict: want %r, got %r" % (index, step, want_verdict, got))
        for what, i, want in (("wall s", wall, want_wall), ("$", cost, want_cost)):
            got = row[i] if i < len(row) else ""
            if number(got) is None or abs(number(got) - float(want)) > 0.005:
                complain("pass %s of step %r %s: want %s, got %r" % (index, step, what, want, got))

print("\n".join(problems))
' "$out_file" "$step" "$@"
}

two_pass_log() {
  local step="$1" order="$2"
  sv "$step" 70000 conductor ""       step-start ""
  sv "$step" 70001 developer green    launch  1 '"name": "develop-green"'
  sv "$step" 70001 developer green    exit    1 '"status": "0", "secs": "9"'
  sv "$step" 70001 developer green    usage   1 "$(old_usage 0 3 0.70)"
  sv "$step" 70002 developer refactor launch  1 '"name": "develop-refactor"'
  sv "$step" 70008 developer refactor exit    1 '"status": "0", "secs": "6"'
  sv "$step" 70008 developer refactor usage   1 "$(old_usage 0 3 0.30)"
  if [[ "$order" == mark-first ]]; then
    sv "$step" 70010 conductor refactor refactor "" '"transforms": "2", "budget": "5", "stopped": "nothing-structural", "pass": "1"'
  fi
  sv "$step" 70012 verifier  refactor launch  1 '"name": "verify-refactor"'
  sv "$step" 70016 verifier  refactor exit    1 '"status": "0", "secs": "4"'
  sv "$step" 70016 verifier  refactor usage   1 "$(old_usage 0 3 0.20)"
  sv "$step" 70016 verifier  refactor verdict 1 '"verdict": "PASS", "reason": "behaviour is preserved"'
  if [[ "$order" == verdict-first ]]; then
    sv "$step" 70017 conductor refactor refactor "" '"transforms": "2", "budget": "5", "stopped": "nothing-structural", "pass": "1"'
  fi
  sv "$step" 70050 developer green    launch  2 '"name": "develop-green"'
  sv "$step" 70058 developer green    exit    2 '"status": "0", "secs": "8"'
  sv "$step" 70058 developer green    usage   2 "$(old_usage 0 3 0.60)"
  sv "$step" 70102 developer refactor launch  2 '"name": "develop-refactor"'
  sv "$step" 70109 developer refactor exit    2 '"status": "0", "secs": "7"'
  sv "$step" 70109 developer refactor usage   2 "$(old_usage 0 3 0.25)"
  if [[ "$order" == mark-first ]]; then
    sv "$step" 70110 conductor refactor refactor "" '"transforms": "1", "budget": "5", "stopped": "structural-owed", "pass": "2"'
  fi
  sv "$step" 70112 verifier  refactor launch  2 '"name": "verify-refactor"'
  sv "$step" 70117 verifier  refactor exit    2 '"status": "0", "secs": "5"'
  sv "$step" 70117 verifier  refactor usage   2 "$(old_usage 0 3 0.15)"
  sv "$step" 70117 verifier  refactor verdict 2 '"verdict": "REJECT", "reason": "behaviour changed"'
  if [[ "$order" == verdict-first ]]; then
    sv "$step" 70118 conductor refactor refactor "" '"transforms": "1", "budget": "5", "stopped": "structural-owed", "pass": "2"'
  fi
  sv "$step" 70119 verifier  green    launch  2 '"name": "verify-green"'
  sv "$step" 70120 verifier  green    exit    2 '"status": "0", "secs": "3"'
  sv "$step" 70120 verifier  green    usage   2 "$(old_usage 0 3 0.05)"
  sv "$step" 70120 verifier  green    verdict 2 '"verdict": "PASS", "reason": "the test is green"'
  sv "$step" 70121 conductor ""       bail    "" '"cause": "revise-exhausted", "classification": "process"'
}

fixture_work costs_work

costed="a step whose two refactor passes each spent their own"
two_pass_log "$costed" mark-first

name="#502 each per-pass row carries that pass's verify-refactor verdict, wall seconds and cost"
problems=()

costs_out="$costs_work/report.md"
render "$costs_work" "$costs_out"

pass_costs_say "$costs_out" "$costed" "1=PASS,10,0.50" "2=REJECT,12,0.40"

report_on "$name" "$costs_out"

fixture_work ordered_work

ordered="a step whose refactor marks follow each pass's verdict"
two_pass_log "$ordered" verdict-first

name="#502 each per-pass row carries its own verdict, wall and cost when the mark follows the verdict"
problems=()

ordered_out="$ordered_work/report.md"
render "$ordered_work" "$ordered_out"

pass_costs_say "$ordered_out" "$ordered" "1=PASS,10,0.50" "2=REJECT,12,0.40"

report_on "$name" "$ordered_out"

pass_revises_say() {
  local out_file="$1" step="$2"; shift 2
  probe "$PROBE_PRELUDE$PASSES_PRELUDE"'
path, step = sys.argv[1], sys.argv[2]
wanted = sys.argv[3:]
header, rows, at = pass_rows(path, step, wanted)
revises = column(header, "the revises", lambda c: "revise" in c, step)
if None not in (at, revises):
    for index, want, row in expected_rows(rows, at, wanted, step):
        got = row[revises] if revises < len(row) else ""
        if got != want:
            complain("pass %s of step %r revises: want %r, got %r" % (index, step, want, got))

print("\n".join(problems))
' "$out_file" "$step" "$@"
}

fixture_work revised_work

revised="a step whose two refactor passes each spent their own revises"

sv "$revised" 80000 conductor ""       step-start ""
sv "$revised" 80010 verifier  refactor verdict 1 '"verdict": "REJECT", "reason": "behaviour changed"'
sv "$revised" 80011 conductor refactor revise  1 '"budget": "3"'
sv "$revised" 80020 verifier  refactor verdict 2 '"verdict": "PASS", "reason": "behaviour is preserved"'
sv "$revised" 80021 conductor refactor refactor "" '"transforms": "2", "budget": "5", "stopped": "nothing-structural", "pass": "1"'
sv "$revised" 80030 verifier  green    verdict 2 '"verdict": "REJECT", "reason": "a second criterion was pinned in passing"'
sv "$revised" 80031 conductor green    revise  1 '"budget": "3"'
sv "$revised" 80040 verifier  green    verdict 3 '"verdict": "PASS", "reason": "the test is green"'
sv "$revised" 80050 verifier  refactor verdict 3 '"verdict": "REJECT", "reason": "behaviour changed"'
sv "$revised" 80051 conductor refactor revise  1 '"budget": "3"'
sv "$revised" 80060 verifier  refactor verdict 4 '"verdict": "REJECT", "reason": "behaviour changed"'
sv "$revised" 80061 conductor refactor revise  2 '"budget": "3"'
sv "$revised" 80070 verifier  refactor verdict 5 '"verdict": "PASS", "reason": "behaviour is preserved"'
sv "$revised" 80071 conductor refactor refactor "" '"transforms": "1", "budget": "5", "stopped": "structural-owed", "pass": "2"'
sv "$revised" 80072 conductor ""       step-done ""

name="#502 each per-pass row carries the count of refactor-phase revises spent in that pass"
problems=()

revised_out="$revised_work/report.md"
render "$revised_work" "$revised_out"

pass_revises_say "$revised_out" "$revised" "1=1" "2=2"

report_on "$name" "$revised_out"

fixture_work looped_work

looped="a step whose first pass was revised after its refactor mark"

sv "$looped" 90000 conductor ""       step-start ""
sv "$looped" 90002 developer refactor launch  1 '"name": "develop-refactor"'
sv "$looped" 90008 developer refactor exit    1 '"status": "0", "secs": "6"'
sv "$looped" 90008 developer refactor usage   1 "$(old_usage 0 3 0.30)"
sv "$looped" 90010 verifier  refactor launch  1 '"name": "verify-refactor"'
sv "$looped" 90014 verifier  refactor exit    1 '"status": "0", "secs": "4"'
sv "$looped" 90014 verifier  refactor usage   1 "$(old_usage 0 3 0.20)"
sv "$looped" 90014 verifier  refactor verdict 1 '"verdict": "REJECT", "reason": "behaviour changed"'
sv "$looped" 90015 conductor refactor refactor "" '"transforms": "2", "budget": "5", "stopped": "nothing-structural", "pass": "1"'
sv "$looped" 90016 conductor refactor revise  1 '"budget": "3"'
sv "$looped" 90017 developer refactor launch  2 '"name": "revise-refactor"'
sv "$looped" 90022 developer refactor exit    2 '"status": "0", "secs": "5"'
sv "$looped" 90022 developer refactor usage   2 "$(old_usage 0 3 0.10)"
sv "$looped" 90023 verifier  refactor launch  2 '"name": "verify-refactor"'
sv "$looped" 90026 verifier  refactor exit    2 '"status": "0", "secs": "3"'
sv "$looped" 90026 verifier  refactor usage   2 "$(old_usage 0 3 0.05)"
sv "$looped" 90026 verifier  refactor verdict 2 '"verdict": "PASS", "reason": "behaviour is preserved"'
sv "$looped" 90050 developer green    launch  2 '"name": "develop-green"'
sv "$looped" 90058 developer green    exit    2 '"status": "0", "secs": "8"'
sv "$looped" 90058 developer green    usage   2 "$(old_usage 0 3 0.60)"
sv "$looped" 90060 developer refactor launch  3 '"name": "develop-refactor"'
sv "$looped" 90067 developer refactor exit    3 '"status": "0", "secs": "7"'
sv "$looped" 90067 developer refactor usage   3 "$(old_usage 0 3 0.25)"
sv "$looped" 90068 verifier  refactor launch  3 '"name": "verify-refactor"'
sv "$looped" 90070 verifier  refactor exit    3 '"status": "0", "secs": "2"'
sv "$looped" 90070 verifier  refactor usage   3 "$(old_usage 0 3 0.15)"
sv "$looped" 90070 verifier  refactor verdict 3 '"verdict": "PASS", "reason": "behaviour is preserved"'
sv "$looped" 90071 conductor refactor refactor "" '"transforms": "1", "budget": "5", "stopped": "nothing-left", "pass": "2"'
sv "$looped" 90072 conductor ""       step-done ""

name="#502 a pass's revise loop written after its refactor mark counts toward that pass, whose verdict is its last"
problems=()

looped_out="$looped_work/report.md"
render "$looped_work" "$looped_out"

pass_costs_say "$looped_out" "$looped" "1=PASS,18,0.65" "2=PASS,9,0.40"
pass_revises_say "$looped_out" "$looped" "1=1" "2=0"

report_on "$name" "$looped_out"

pass_rows_in_block_says() {
  local out_file="$1" step="$2" passes="$3"
  probe "$PROBE_PRELUDE"'
path, step, passes = sys.argv[1], sys.argv[2], int(sys.argv[3])
with open(path) as f:
    lines = f.read().splitlines()
start = next((i for i, l in enumerate(lines) if l.startswith("### ") and "Metrics" in l), None)
if start is None:
    complain("want a ### Metrics heading, the report has none")
else:
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("### ")), len(lines))
    block = path + ".block"
    with open(block, "w") as f:
        f.write("\n".join(lines[start:end]) + "\n")
    tables = tables_in(block)
    n = max([sum(1 for r in t[1:] if is_row(r, step)) for t in tables
             if any(c.lower() == "pass" for c in t[0])] or [0])
    if n != passes:
        complain("want %d per-pass rows for step %r inside the Metrics block, got %d" % (passes, step, n))
print("\n".join(problems))
' "$out_file" "$step" "$passes"
}

name="#502 the per-pass section is part of the Metrics block whether the run ended in done, bail or stop"
problems=()

for ending in done bail stop; do
  fixture_work ended_work
  ended="a step with two refactor passes, of a run that ended in $ending"
  two_pass_log "$ended" verdict-first
  if [[ "$ending" != bail ]]; then
    grep -v '"event": "bail"' "$fixture_log" > "$fixture_log.kept"
    mv "$fixture_log.kept" "$fixture_log"
  fi
  case "$ending" in
    done) sv "$ended" 70122 conductor "" done "" '"pr": "https://github.com/ztrange/veri/pull/999"' ;;
    stop) sv "$ended" 70122 conductor refactor stop "" '"mode": "at-ledger", "at": "refactor"' ;;
  esac
  ended_out="$ended_work/report.md"
  render "$ended_work" "$ended_out"
  pass_rows_in_block_says "$ended_out" "$ended" 2
  passes_say "$ended_out" "$ended" "1=2/5,nothing-structural" "2=1/5,structural-owed"
done

report_on "$name" "$ended_out"

headings_say() {
  local out_file="$1"
  probe "$PROBE_PRELUDE"'
path = sys.argv[1]
want = {
    "#### By phase": ["phase", "attempts", "PASS", "REJECT", "kills", "wall s", "API s", "turns",
                      "input", "output", "cache read", "cache creation", "$"],
    "#### Rework and waste, by phase": ["phase", "rework wall s", "rework $", "waste wall s", "waste $"],
    "#### By step": ["step", "attempts", "PASS", "REJECT", "kills", "retries", "no-verdict", "API s",
                     "turns", "input", "output", "cache read", "cache creation", "$", "wall s",
                     "revise", "refactor", "stopped", "crossed at", "split", "kind"],
    "#### Total": ["run", "turns", "input", "output", "cache read", "cache creation", "$"],
}
lines = open(path).read().splitlines()
def header_under(heading):
    at = next((i for i, l in enumerate(lines) if l.strip() == heading), None)
    if at is None:
        return None
    return next((cells(l) for l in lines[at + 1:] if l.strip().startswith("|")), None)
for heading, columns in want.items():
    got = header_under(heading)
    if got != columns:
        complain("want %r headed %s, got %s" % (heading, "|".join(columns), got and "|".join(got)))
tier = header_under("#### Test-command seconds, by tier")
if not tier or tier[0] != "tier":
    complain("want the tier table keyed by tier, got %s" % (tier and "|".join(tier)))
per_pass = [t for t in tables_in(path) if "pass" in t[0] and t[0][0] == "step"]
if not per_pass:
    complain("want a per-pass table keyed by step with a pass column, the report has none")
for t in per_pass:
    if any(c.lower() == "kind" for c in t[0]):
        complain("want no kind column in the per-pass table, it is headed %s" % "|".join(t[0]))
print("\n".join(problems))
' "$out_file"
}

name="#502 no existing table's key or column names change, and the per-pass table has no kind column"
problems=()

fixture_work headed_work
headed="a step with two refactor passes, read for its table headings"
two_pass_log "$headed" verdict-first
headed_out="$headed_work/report.md"
render "$headed_work" "$headed_out"
headings_say "$headed_out"

report_on "$name" "$headed_out"

structural_section_says() {
  local out_file="$1" step="$2" pair="$3" want="$4"
  probe "$PROBE_PRELUDE"'
path, step, pair, want = sys.argv[1:5]
lines = open(path).read().splitlines()
start = next((i for i, l in enumerate(lines) if l.startswith("### ") and "Metrics" in l), None)
end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("### ")), len(lines)) if start is not None else 0
block = lines[start:end] if start is not None else []
heads = [i for i, l in enumerate(block) if l.startswith("#### ") and "structural" in l.lower()]
if want == "absent":
    if heads:
        complain("want no structural-pass section for a log with no such mark, got %r" % block[heads[0]])
elif not heads:
    complain("want a #### section naming the structural pass inside the Metrics block, the report has none")
else:
    transforms, budget, stopped = want.split(":", 1)[1].split(",")
    at = heads[0]
    stop = next((i for i in range(at + 1, len(block)) if block[i].startswith("#")), len(block))
    body = "\n".join(block[at + 1:stop])
    figures = re.findall(r"\d+(?:\.\d+)?", body)
    for what, value in (("transforms", transforms), ("budget", budget)):
        if value not in figures:
            complain("want the structural-pass section to carry its %s %s, its body is %r" % (what, value, body))
    if stopped not in body:
        complain("want the structural-pass section to carry stopped=%s, its body is %r" % (stopped, body))
tables = tables_in(path)
cell = cell_in(tables, step, "refactor", lambda c: c == "refactor")
if cell is not None and cell != pair:
    complain("By-step refactor of step %r: want %r, got %r" % (step, pair, cell))
print("\n".join(problems))
' "$out_file" "$step" "$pair" "$want"
}

structural_log() {
  sv "$1" 80000 conductor ""       step-start ""
  sv "$1" 80002 developer refactor launch  1 '"name": "develop-refactor"'
  sv "$1" 80008 developer refactor exit    1 '"status": "0", "secs": "6"'
  sv "$1" 80010 conductor refactor refactor "" '"transforms": "1", "budget": "5", "stopped": "nothing-structural", "pass": "1"'
  sv "$1" 80020 conductor ""       step-done ""
}

structural_section() {
  awk '/^#### Structural pass/ {on=1; next} /^####/ {on=0} on' "$1" > "$2"
}

structural_mark_section() {
  local dir
  fixture_work "$1"
  dir="${!1}"
  structural_log "$2"
  sv "" 80030 conductor "" structural-pass "" "$3"
  sv "" 80040 conductor "" done "" '"pr": "https://github.com/ztrange/veri/pull/999"'
  render "$dir" "$dir/report.md"
  structural_section "$dir/report.md" "$dir/section.txt"
}

name="#503 the structural-pass mark renders as its own Metrics section, apart from the per-step refactor cells, and a log without one renders none"
problems=()

fixture_work structural_work
structured="a step followed by a structural pass"
structural_log "$structured"
sv "" 80030 conductor "" structural-pass "" '"transforms": "3", "budget": "10", "stopped": "budget-spent"'
sv "" 80040 conductor "" done "" '"pr": "https://github.com/ztrange/veri/pull/999"'
structural_out="$structural_work/report.md"
render "$structural_work" "$structural_out"
structural_section_says "$structural_out" "$structured" "1/5" "present:3,10,budget-spent"

fixture_work unstructured_work
unstructured="a step with no structural pass after it, the run never reaching its PR"
structural_log "$unstructured"
unstructured_out="$unstructured_work/report.md"
render "$unstructured_work" "$unstructured_out"
structural_section_says "$unstructured_out" "$unstructured" "1/5" "absent"

report_on "$name" "$structural_out"

name="#585 a structural-pass mark carrying only stopped=nothing-structural renders the whole report, its row naming the stop without a spent/budget figure"
problems=()

fixture_work bare_structural_work
bare_structural="a step followed by a structural pass that found nothing to do"
structural_log "$bare_structural"
sv "" 80030 conductor "" structural-pass "" '"stopped": "nothing-structural"'
sv "" 80040 conductor "" done "" '"pr": "https://github.com/ztrange/veri/pull/999"'
bare_structural_out="$bare_structural_work/report.md"
render "$bare_structural_work" "$bare_structural_out"
grep -F '#### Total' "$bare_structural_out" > /dev/null ||
  problems+=("want the report to reach its #### Total section after the structural row, it stops short")
grep -F -A3 '#### Structural pass' "$bare_structural_out" > "$bare_structural_work/section.txt"
grep -F 'nothing-structural' "$bare_structural_work/section.txt" > /dev/null ||
  problems+=("want the structural section to carry stopped=nothing-structural, the report has none")

report_on "$name" "$bare_structural_out"

name="#585 a structural-pass mark carrying only stopped=nothing-structural shows that stop reason with no spent/budget figure"
problems=()

fixture_work bare_figure_work
bare_figure="a step followed by a structural pass that found nothing to do"
structural_log "$bare_figure"
sv "" 80030 conductor "" structural-pass "" '"stopped": "nothing-structural"'
sv "" 80040 conductor "" done "" '"pr": "https://github.com/ztrange/veri/pull/999"'
bare_figure_out="$bare_figure_work/report.md"
render "$bare_figure_work" "$bare_figure_out"
structural_section "$bare_figure_out" "$bare_figure_work/section.txt"
grep -F 'nothing-structural' "$bare_figure_work/section.txt" > /dev/null ||
  problems+=("want the structural section to name nothing-structural, got: $(cat "$bare_figure_work/section.txt")")
if grep -E '[0-9]+/[0-9]+' "$bare_figure_work/section.txt" > /dev/null; then
  problems+=("want the structural section without a spent/budget figure, got: $(cat "$bare_figure_work/section.txt")")
fi

report_on "$name" "$bare_figure_out"

name="#596 a structural-pass mark with stopped=budget-spent below its budget names the mark inconsistent, with its transforms and budget"
problems=()

unspent="a step followed by a structural pass that claims a budget it never spent"
structural_mark_section unspent_work "$unspent" '"transforms": "0", "budget": "10", "stopped": "budget-spent"'
grep -i 'inconsistent' "$unspent_work/section.txt" > "$unspent_work/inconsistent.txt"
if ! grep -w '0' "$unspent_work/inconsistent.txt" > /dev/null ||
   ! grep -w '10' "$unspent_work/inconsistent.txt" > /dev/null; then
  problems+=("want the structural section to carry an inconsistent-mark line naming transforms 0 and budget 10, got: $(cat "$unspent_work/section.txt")")
fi

spent="a step followed by a structural pass that spent its whole budget"
structural_mark_section spent_work "$spent" '"transforms": "10", "budget": "10", "stopped": "budget-spent"'
if grep -i 'inconsistent' "$spent_work/section.txt" > /dev/null; then
  problems+=("want no inconsistent-mark line for stopped=budget-spent with transforms equal to budget 10, got: $(cat "$spent_work/section.txt")")
fi

report_on "$name" "$unspent_work/report.md"

name="#596 a structural-pass mark whose stopped is none of the three reasons names the mark inconsistent, with the reason it found"
problems=()

unknown_stop="a step followed by a structural pass that stopped for a reason the pass does not have"
structural_mark_section unknown_stop_work "$unknown_stop" '"transforms": "1", "budget": "3", "stopped": "test-files-only"'
grep -i 'inconsistent' "$unknown_stop_work/section.txt" > "$unknown_stop_work/inconsistent.txt"
grep -F 'test-files-only' "$unknown_stop_work/inconsistent.txt" > /dev/null ||
  problems+=("want the structural section to carry an inconsistent-mark line naming stopped=test-files-only, got: $(cat "$unknown_stop_work/section.txt")")

report_on "$name" "$unknown_stop_work/report.md"

name="#596 a structural-pass mark missing stopped, or carrying transforms without budget, names the mark inconsistent and the report still renders"
problems=()

malformed_mark_inconsistent() {
  structural_mark_section "$1" "a step followed by a structural pass whose mark $2" "$3"
  grep -i 'inconsistent' "${!1}/section.txt" > /dev/null ||
    problems+=("want the structural section to carry an inconsistent-mark line for a mark that $2, got: $(cat "${!1}/section.txt")")
}

malformed_mark_inconsistent no_stop_work "has no stopped" '"transforms": "1", "budget": "3"'
malformed_mark_inconsistent no_budget_work "has transforms but no budget" '"transforms": "1", "stopped": "candidates-done"'
malformed_mark_inconsistent bare_work "has neither stopped nor transforms" '"budget": "3"'

report_on "$name" "$no_stop_work/report.md"

name="#596 a consistent structural-pass mark names nothing inconsistent and renders the same Structural pass section as before"
problems=()

consistent_mark_renders() {
  structural_mark_section "$1" "a step followed by a structural pass that $2" "$3"
  grep -v '^$' "${!1}/section.txt" > "${!1}/rendered.txt"
  printf '%s\n' "${@:4}" > "${!1}/want.txt"
  if grep -i 'inconsistent' "${!1}/section.txt" > /dev/null; then
    problems+=("want no inconsistent-mark line for a pass that $2, got: $(cat "${!1}/section.txt")")
  fi
  diff "${!1}/want.txt" "${!1}/rendered.txt" > /dev/null ||
    problems+=("want the Structural pass section for a pass that $2 unchanged, diff: $(diff "${!1}/want.txt" "${!1}/rendered.txt")")
}

consistent_mark_renders done_work "ran out of candidates" '"transforms": "2", "budget": "3", "stopped": "candidates-done"' \
  '| pass | refactor | stopped |' '| --- | ---: | --- |' '| issue | 2/3 | candidates-done |'
consistent_mark_renders spent_three_work "spent its whole budget" '"transforms": "3", "budget": "3", "stopped": "budget-spent"' \
  '| pass | refactor | stopped |' '| --- | ---: | --- |' '| issue | 3/3 | budget-spent |'
consistent_mark_renders nothing_work "found nothing structural" '"stopped": "nothing-structural"' \
  'Stopped: nothing-structural'

report_on "$name" "$done_work/report.md"

name="#726 a log that reaches its draft PR with no structural-pass mark renders the Structural pass section, its row saying the pass was not marked"
problems=()

fixture_work unmarked_work
unmarked="a step whose run readied its PR without marking the structural pass"
structural_log "$unmarked"
sv "" 80040 conductor "" done "" '"pr": "https://github.com/ztrange/veri/pull/999"'
unmarked_out="$unmarked_work/report.md"
render "$unmarked_work" "$unmarked_out"
if grep -F '#### Structural pass' "$unmarked_out" > /dev/null; then
  structural_section "$unmarked_out" "$unmarked_work/section.txt"
  grep -i 'not marked' "$unmarked_work/section.txt" > /dev/null ||
    problems+=("want the Structural pass section to say the pass was not marked, got: $(cat "$unmarked_work/section.txt")")
else
  problems+=("want a #### Structural pass section for a run that reached its draft PR without the mark, the report has none")
fi

report_on "$name" "$unmarked_out"

name="#495 the planned-step count is the number of ledger-steps.sh's records, counting no box of its own"
problems=()

fixture_work ledger_steps_work
counted_step="a step the stub module numbers first of three"
sv "$counted_step" 90000 conductor "" step-start ""
sv "$counted_step" 90100 conductor "" step-done  ""
plan_of "$counted_step"

stub="$ledger_steps_work/stub"
mkdir -p "$stub"
cp "$METRICS" "$stub/"
cp -R "$HERE/../lib" "$stub/lib"
cp -R "$HERE/../veri" "$stub/veri"
cat > "$stub/ledger-steps.sh" <<'EOF'
#!/bin/sh
cat >/dev/null
printf '1\tdone\tstep\t0\t0\t\ta step the stub module numbers first of three\n'
printf '2\topen\tstep\t0\t0\t\ta second step\n'
printf '3\topen\tstep\t0\t0\t\ta third step\n'
EOF
chmod +x "$stub/ledger-steps.sh"

ledger_steps_out="$ledger_steps_work/report.md"
METRICS="$stub/metrics.sh" render "$ledger_steps_work" "$ledger_steps_out"

progress_says "$ledger_steps_out" 1 3

report_on "$name" "$ledger_steps_out"

by_model_says() {
  local out_file="$1"; shift
  probe "$PROBE_PRELUDE"'
path = sys.argv[1]
COLUMNS = ["attempts", "PASS", "REJECT", "kills", "wall s", "API s", "turns",
           "input", "output", "cache read", "cache creation", "$"]
lines = open(path).read().splitlines()
at = next((i for i, l in enumerate(lines) if l.strip() == "#### By model"), None)
if at is None:
    complain("want a \"#### By model\" section, the report has headings: %s"
             % ", ".join(repr(l) for l in lines if l.startswith("#")))
else:
    body = []
    for l in lines[at + 1:]:
        if l.startswith("#"):
            break
        if l.strip().startswith("|"):
            row = cells(l)
            if not all(SEPARATOR.match(c) for c in row if c):
                body.append(row)
    if not body:
        complain("want a table under \"#### By model\", there is none")
    else:
        header, rows = body[0], body[1:]
        keys = len(header) - len(COLUMNS)
        if keys < 1 or header[keys:] != COLUMNS:
            complain("want \"#### By model\" headed by its key and then %s, got %s"
                     % ("|".join(COLUMNS), "|".join(header)))
        else:
            for arg in sys.argv[2:]:
                if arg.startswith("!"):
                    absent = [r for r in rows if arg[1:] in r[:keys]]
                    if absent:
                        complain("want no By model row for role %r, the rows are: %s"
                                 % (arg[1:], "; ".join("|".join(r) for r in rows)))
                    continue
                key, expected = arg.split("=", 1)
                role, model = key.split("@")
                hit = [r for r in rows
                       if role in r[:keys] and model in r[:keys]]
                if len(hit) != 1:
                    complain("want one By model row for role %r and model %r, the rows are: %s"
                             % (role, model, "; ".join("|".join(r) for r in rows) or "none"))
                    continue
                for name, want, got in zip(COLUMNS, expected.split(","), hit[0][keys:]):
                    said = number(got)
                    if said is None or abs(said - float(want)) > 0.005:
                        complain("By model %s on %s %s: want %s, got %r" % (role, model, name, want, got))
print("\n".join(problems))
' "$out_file" "$@"
}

name="#604 metrics.sh prints a By model table, one row per (role, model), carrying the By phase columns"
problems=()

fixture_work modeled_work
modeled="a step whose developer ran on one model and whose verifier ran on another"
developer_model='"model": "claude-opus-5-5"'
verifier_model='"model": "claude-haiku-4-5-20251001"'
sv "$modeled" 9000 conductor ""    step-start ""
sv "$modeled" 9010 developer red   launch  1 '"name": "develop-red"'
sv "$modeled" 9100 developer red   exit    1 '"status": "0", "secs": "90"'
sv "$modeled" 9100 developer red   usage   1 "$(usage_json 70000), $developer_model"
sv "$modeled" 9110 verifier  red   launch  1 '"name": "verify-red"'
sv "$modeled" 9130 verifier  red   exit    1 '"status": "0", "secs": "20"'
sv "$modeled" 9130 verifier  red   usage   1 "$(usage_json 15000), $verifier_model"
sv "$modeled" 9130 verifier  red   verdict 1 '"verdict": "PASS", "reason": "the case fails as written"'
sv "$modeled" 9200 developer green launch  1 '"name": "develop-green"'
sv "$modeled" 9300 developer green exit    1 '"status": "0", "secs": "100"'
sv "$modeled" 9300 developer green usage   1 "$(usage_json 80000), $developer_model"
sv "$modeled" 9310 verifier  green launch  1 '"name": "verify-green"'
sv "$modeled" 9330 verifier  green exit    1 '"status": "0", "secs": "20"'
sv "$modeled" 9330 verifier  green usage   1 "$(usage_json 10000), $verifier_model"
sv "$modeled" 9330 verifier  green verdict 1 '"verdict": "REJECT", "reason": "the production change is wider than the case asks for"'
sv "$modeled" 9400 conductor ""    usage   "" "$(usage_json 5000), $developer_model"
sv "$modeled" 9400 conductor ""    step-done ""
modeled_out="$modeled_work/report.md"
render "$modeled_work" "$modeled_out"
by_model_says "$modeled_out" \
  "developer@claude-opus-5-5=2,0,0,0,190,150,18,2000,4000,6000,8000,1.00" \
  "verifier@claude-haiku-4-5-20251001=2,1,1,0,40,25,18,2000,4000,6000,8000,1.00" \
  "!conductor"

report_on "$name" "$modeled_out"

header_says() {
  local out_file="$1"; shift
  probe '
import re, sys

path, wants = sys.argv[1], sys.argv[2:]
header = []
for l in open(path).read().splitlines():
    if l.startswith("####"):
        break
    if l.strip() and not l.strip().startswith("|"):
        header.append(l.strip())
text = "\n".join(header)
for want in wants:
    if "=" in want:
        knob, value = want.split("=", 1)
        said = re.search(r"\b%s\b`?[\s:=]*`?%s(?![\w.-])" % (re.escape(knob), re.escape(value)), text)
        if said is None:
            print("want the header to state %s as %s, the header says: %s"
                  % (knob, value, " / ".join(repr(l) for l in header)))
    elif re.search(r"(?<![\w.-])%s(?![\w.-])" % re.escape(want), text) is None:
        print("want the header to name the model %s that answered, the header says: %s"
              % (want, " / ".join(repr(l) for l in header)))
' "$out_file" "$@"
}

name="#604 the metrics header states the requested VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER, or unset, next to the models that answered"
problems=()

fixture_work knobs_work
knobbed="a step whose verifier was asked for one model and answered on another"
sv "$knobbed" 9000 conductor ""  step-start ""
sv "$knobbed" 9010 developer red launch  1 '"name": "develop-red", "model": "claude-opus-5-5"'
sv "$knobbed" 9100 developer red exit    1 '"status": "0", "secs": "90"'
sv "$knobbed" 9100 developer red usage   1 "$(usage_json 70000), \"model\": \"claude-opus-5-5\""
sv "$knobbed" 9110 verifier  red launch  1 '"name": "verify-red", "model": "claude-sonnet-5-5"'
sv "$knobbed" 9130 verifier  red exit    1 '"status": "0", "secs": "20"'
sv "$knobbed" 9130 verifier  red usage   1 "$(usage_json 15000), \"model\": \"claude-haiku-4-5-20251001\""
sv "$knobbed" 9130 verifier  red verdict 1 '"verdict": "PASS", "reason": "the case fails as written"'
sv "$knobbed" 9400 conductor ""  step-done ""
knobs_out="$knobs_work/report.md"
VERI_MODEL= VERI_MODEL_DEVELOPER=claude-opus-5-5 VERI_MODEL_VERIFIER=claude-sonnet-5-5 \
  render "$knobs_work" "$knobs_out"
header_says "$knobs_out" \
  VERI_MODEL=unset \
  VERI_MODEL_DEVELOPER=claude-opus-5-5 \
  VERI_MODEL_VERIFIER=claude-sonnet-5-5 \
  claude-haiku-4-5-20251001

report_on "$name" "$knobs_out"

name="#604 a log whose usage events carry no model still yields a report, its By model table saying the model was not recorded"
problems=()

fixture_work unmodeled_work
unmodeled="a step logged before usage events carried a model"
sv "$unmodeled" 9000 conductor ""    step-start ""
sv "$unmodeled" 9010 developer red   launch  1 '"name": "develop-red", "model": ""'
sv "$unmodeled" 9100 developer red   exit    1 '"status": "0", "secs": "90"'
sv "$unmodeled" 9100 developer red   usage   1 "$(usage_json 70000)"
sv "$unmodeled" 9110 verifier  red   launch  1 '"name": "verify-red", "model": ""'
sv "$unmodeled" 9130 verifier  red   exit    1 '"status": "0", "secs": "20"'
sv "$unmodeled" 9130 verifier  red   usage   1 "$(usage_json 15000)"
sv "$unmodeled" 9130 verifier  red   verdict 1 '"verdict": "PASS", "reason": "the case fails as written"'
sv "$unmodeled" 9400 conductor ""    step-done ""
unmodeled_out="$unmodeled_work/report.md"
render "$unmodeled_work" "$unmodeled_out"
by_model_says "$unmodeled_out" "developer@not recorded=1" "verifier@not recorded=1"

report_on "$name" "$unmodeled_out"

name="metrics.sh run through a symlink to the skill directory, from another working directory, answers with the same stdout and exit code as run in place, reading that directory's .tdd/ and never the skill's"
problems=()

linked="$(scratch_dir)"
ln -s "$HERE/../.." "$linked/skill"

in_place_out="$landed_work/in-place.md"
linked_out="$landed_work/linked.md"
( cd "$landed_work" && "$METRICS" 108 ) > "$in_place_out" 2>/dev/null
in_place_status=$?
( cd "$landed_work" && "$linked/skill/scripts/metrics.sh" 108 ) > "$linked_out" 2>/dev/null
linked_status=$?

[[ "$linked_status" -eq "$in_place_status" ]] ||
  problems+=("want the symlinked run to exit $in_place_status as the in-place run does, it exited $linked_status")
[[ "$linked_status" -eq 0 ]] ||
  problems+=("want the symlinked run to exit 0, it exited $linked_status")
cmp -s "$in_place_out" "$linked_out" ||
  problems+=("want the symlinked run's stdout to be the in-place run's, the diff is: $(diff "$in_place_out" "$linked_out")")
progress_says "$linked_out" 2 2
outcome_says "$linked_out" pr

report_on "$name" "$linked_out"

name="metrics.sh run in a working directory with no .tdd/events.jsonl exits 1 and prints nothing on stdout"
problems=()

logless_work="$(scratch_dir)"
mkdir -p "$logless_work/.tdd"
logless_out="$(scratch_dir)/report.md"
( cd "$logless_work" && "$METRICS" 108 ) > "$logless_out" 2>/dev/null
logless_status=$?

[[ "$logless_status" -eq 1 ]] ||
  problems+=("want metrics.sh to exit 1 with no .tdd/events.jsonl, it exited $logless_status")
[[ ! -s "$logless_out" ]] ||
  problems+=("want nothing on stdout with no .tdd/events.jsonl, it printed $(printf '%q' "$(cat "$logless_out")")")

report_on "$name" "$logless_out"

finish
