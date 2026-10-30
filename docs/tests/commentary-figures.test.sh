#!/usr/bin/env bash
# Unit test for the tunable defaults docs/wt/commentary.py states — a number the page's
# prose writes down that a script under skills/tdd/scripts/ encodes as code. Like
# suite-lanes.test.sh this suite has no script as its subject: it reads both files as text
# and asserts they say the same figure. Zero-dependency plain-shell asserts, same idiom as
# the other suites under docs/tests/.
#
# Why this exists (issue #146): the walkthrough is generated from the scripts, so `make
# docs` happily rebuilds a page whose hand-written commentary contradicts the source it
# sits beside — editing `heartbeat="${VERI_HEARTBEAT:-180}"` alone leaves the commentary
# confidently stating the old figure, and no build guard notices, because the commentary is
# an input to the build and not something it derives. Both figures were guarded from the
# development lane instead (supervise.test.sh case 10, refactor-budget.test.sh case 8),
# which put a docs fact inside `make test` — the command every veri leaf runs and the
# conductor reads its baseline off, so docs prose could stop a TDD cycle on a red the code
# did not cause (ADR 0016). A docs fact belongs in the docs lane, and `make docs-test`
# globs this directory, so this suite runs by existing (#137).
#
# Contract under test:
#   Every figure docs/wt/commentary.py states for VERI_HEARTBEAT or VERI_REFACTOR_BUDGET is
#   the one the script encodes as that tunable's default. A drift fails naming the file, the
#   statement inside it, and both figures — what to fix, and to what.
#
# Each statement is located by a regex that ends at the figure it states, and a site whose
# pattern can no longer be found reports `<none>`: a rewording that moves a statement out
# of this check's sight is drift too, and must fail rather than pass silently. One
# statement is knowingly out of reach — commentary.py also spells the heartbeat out in
# words once ("a hang trips in two seconds instead of a hundred and eighty"), which no
# regex here can compare against a number.
#
# The same figures are stated in each script's own `Tunables` header and in SKILL.md.
# Those statements are development's, and development's suites hold them; this suite's
# subject is only what the page says.
#
# It reads three files and spawns a few greps per site, builds no page and asks git
# nothing, so it costs `make docs-test` well under a second.
#
# Run: docs/tests/commentary-figures.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"

# The file under examination, named once: every failure message quotes it, and every site
# below reads it, so a rename is one edit rather than five.
COMMENTARY='docs/wt/commentary.py'
pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output says which statement drifted rather than just that the case did.
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

# stated <file> <extended-regex> — the figure the first match of <regex> states, or
# '<none>' / '<no-file>' when there is nothing to read. Newlines are squashed to spaces
# first, because the commentary wraps at ~90 columns and a statement split across two lines
# is still one statement; the figure is the LAST run of digits in the match, which is why
# every regex below stops at it. The same helper reads the code site, since
# `heartbeat="${VERI_HEARTBEAT:-180}"` states the figure as much as a sentence does — and
# it is the statement the others must match.
stated() {
  local hit
  [[ -f "$1" ]] || { echo '<no-file>'; return; }
  hit="$(tr '\n' ' ' < "$1" | grep -oE "$2" | head -1)"
  [[ -n "$hit" ]] || { echo '<none>'; return; }
  printf '%s' "$hit" | grep -oE '[0-9]+' | tail -1
}

# --- the commentary's tunable figures are the ones the scripts encode ----------------
# The scripts are shims over veri/*.py (#807 family), so the encoded default is read from the
# module. The streaming-note and refactor-budget-assignment sites are gone: the chunks that
# carried them were dropped when their scripts shrank to shims (#2710).
name="every VERI_HEARTBEAT and VERI_REFACTOR_BUDGET default docs/wt/commentary.py states is the figure the script encodes"

problems=()
while IFS='|' read -r site script script_re prose_re; do
  [[ -n "$site" ]] || continue
  encoded="$(stated "$ROOT/$script" "$script_re")"
  got="$(stated "$ROOT/$COMMENTARY" "$prose_re")"
  if [[ ! "$encoded" =~ ^[0-9]+$ ]]; then
    problems+=("$script: no default found to check $COMMENTARY's $site against, read: $encoded")
  elif [[ "$got" != "$encoded" ]]; then
    problems+=("$COMMENTARY $site: says $got, $script encodes $encoded")
  fi
done <<'SITES'
contract-table|skills/tdd/scripts/veri/supervise.py|numeric_env\("VERI_HEARTBEAT", "[0-9]+"|VERI_HEARTBEAT</code> [0-9]+s
budgets-diagram|skills/tdd/scripts/veri/refactor_budget.py|DEFAULT_BUDGET = [0-9]+|VERI_REFACTOR_BUDGET +\([0-9]+
SITES
report "$name"

# --- no chunk claims a line past the end of its script (#533) -------------------------
name="#533 no chunk in docs/wt/commentary.py claims a line past the end of its script"

problems=()
while read -r script first last; do
  path="$ROOT/skills/tdd/scripts/$script"
  if [[ ! -f "$path" ]]; then
    problems+=("$COMMENTARY: chunk L$first-L$last names $script, which is not under skills/tdd/scripts/")
    continue
  fi
  total="$(awk 'END { print NR }' "$path")"
  if [[ "$last" -gt "$total" ]]; then
    problems+=("$script: chunk L$first-L$last in $COMMENTARY runs past the script's $total lines")
  fi
done < <(awk '
  /^    file="/ { match($0, /"[^"]+"/); file = substr($0, RSTART + 1, RLENGTH - 2) }
  match($0, /lines=\([0-9]+, *[0-9]+\)/) {
    range = substr($0, RSTART, RLENGTH); gsub(/[^0-9,]/, "", range)
    split(range, ab, ","); print file, ab[1], ab[2]
  }' "$ROOT/$COMMENTARY")
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
