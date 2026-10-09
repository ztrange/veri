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

fixture_work landed_work

opener="the table reports steps done of planned, of a run that landed"
closer="the issue outcome of a run that landed is its draft PR"

sv "$opener" 13000 conductor "" step-start ""
sv "$opener" 13100 conductor "" step-done  ""
sv "$closer" 13200 conductor "" step-start ""
sv "$closer" 13300 conductor "" step-done  ""
sv "$closer" 13400 conductor "" done       "" '"pr": "https://github.com/ztrange/veri/pull/999"'

plan_of "$opener" "$closer"

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

name="metrics.sh run in a working directory with no .tdd/events.jsonl exits 2 and prints nothing on stdout"
problems=()

logless_work="$(scratch_dir)"
mkdir -p "$logless_work/.tdd"
logless_out="$(scratch_dir)/report.md"
( cd "$logless_work" && "$METRICS" 108 ) > "$logless_out" 2>/dev/null
logless_status=$?

[[ "$logless_status" -eq 2 ]] ||
  problems+=("want metrics.sh to exit 2 with no .tdd/events.jsonl, it exited $logless_status")
[[ ! -s "$logless_out" ]] ||
  problems+=("want nothing on stdout with no .tdd/events.jsonl, it printed $(printf '%q' "$(cat "$logless_out")")")

report_on "$name" "$logless_out"

finish
