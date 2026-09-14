#!/usr/bin/env bash
# Unit tests for scripts/refactor-triage.sh — reads a finished refactor leaf's report on
# stdin and says whether another refactor leaf is worth launching. Zero-dependency
# plain-shell asserts, same idiom as refactor-budget.test.sh, the suite for the script on
# the refactor loop's other axis — refactor-triage.sh's own header is where the two axes
# are told apart.
#
# Why this exists (issue #149): the loop's two stop conditions are a leaf reporting
# `nothing left to tidy` and `refactor-budget.sh` exiting 3, and in practice only the
# second fires — a leaf asked for one transform always finds one, so the loop spends its
# whole budget on transforms that reword and re-cite. Since #149 every `CANDIDATES:` line
# the leaf reports carries the class of the transform it names — `structural` for one that
# removes duplication, extracts, inlines, deletes dead code, renames or moves logic, and
# `cosmetic` for one that only rewords, re-cites, reflows or re-comments. This script is
# what turns those classed lines into the loop's third stop condition.
#
# Contract under test, in the four-code convention (CLAUDE.md, *Exit codes are the API*):
#   report on stdin → exit 0, printing the structural candidates, when at least one is
#                     listed: there is work left that is worth a leaf.
#                   → exit 3 when only cosmetic candidates or `none` remain.
#                   → exit 2, diagnostic on stderr and nothing on stdout, when a candidate
#                     line carries no class or an unknown one, or the report lists no
#                     `CANDIDATES:` line at all.
#
# Run: scripts/tests/refactor-triage.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
TRIAGE="$HERE/../refactor-triage.sh"
pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output says which probe broke rather than just that the case did. Same helper
# refactor-budget.test.sh uses.
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

# 1. the loop continues while structural work is left. A report whose CANDIDATES: lines
#    list two structural transforms and one cosmetic one is the "keep going" answer: exit
#    0, and the structural candidates on stdout so the conductor can mirror them into its
#    `### 🛠️ Refactor` comment.
#
#    What the case pins is that each structural candidate is named on a line of its own
#    and that the cosmetic one is not there — not the exact prefix each line carries,
#    which is the script's business, not the loop's. The line count is what says the
#    surrounding RESULT:/FLAGS: lines were read and not echoed.
#
#    The fixture is a whole report rather than three bare candidate lines because that is
#    what the conductor pipes in: the leaf's last lines, verbatim (develop-refactor.md,
#    *Report*). Quoted heredoc, so `$tmp` inside the third candidate stays the two
#    characters a leaf would have written and is not expanded here.
name="a report listing structural candidates exits 0 and prints them"
problems=()

leaf_report="$(mktemp)"
# The heredoc writes to a file rather than into `report="$(cat <<'REPORT' … )"`: bash 3.2
# — the level this repository holds itself to — scans a command substitution for its
# closing paren without knowing a heredoc is inside it, so the apostrophe in `verify.sh's`
# below reads as an unterminated quote and the whole suite fails to parse.
cat > "$leaf_report" <<'REPORT'
RESULT: applied "fold verify.sh's two prompt paths into one", suite green
FLAGS: none
CANDIDATES: structural | fold verify.sh's two mktemp calls into one helper
CANDIDATES: cosmetic | reflow the header comment to ninety columns
CANDIDATES: structural | rename $tmp to $prompt_file, which is what it holds
REPORT

# Separate the two streams into their own files: stdout is what the case reads back, and
# a diagnostic must not be able to arrive mixed into it and count as a candidate.
out="$(mktemp)" err="$(mktemp)"
"$TRIAGE" <"$leaf_report" >"$out" 2>"$err" && code=0 || code=$?

[[ "$code" == 0 ]] ||
  problems+=("want exit 0 while structural candidates remain, got $code")

lines="$(grep -c '' "$out")"
[[ "$lines" == 2 ]] ||
  problems+=("want the 2 structural candidates on stdout, one per line, got $lines line(s): $(printf '%q' "$(cat "$out")")")

# -F so the transform text is matched as the literal a leaf wrote, not as a pattern: `$`
# and `'` are ordinary characters in a candidate.
while IFS= read -r transform; do
  hits="$(grep -cF "$transform" "$out")"
  [[ "$hits" == 1 ]] ||
    problems+=("want the structural candidate '$transform' named on exactly 1 line of stdout, found on $hits")
done <<'STRUCTURAL'
fold verify.sh's two mktemp calls into one helper
rename $tmp to $prompt_file, which is what it holds
STRUCTURAL

cosmetic='reflow the header comment to ninety columns'
grep -qF "$cosmetic" "$out" &&
  problems+=("the cosmetic candidate '$cosmetic' is on stdout; only structural ones belong there")

rm -f "$leaf_report" "$out" "$err"
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
