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

finish
