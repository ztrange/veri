#!/usr/bin/env bash
# Unit test for the ADR set under docs/adr/ — like workflow-timeouts.test.sh this suite
# has no script as its subject: it reads the records as text and asserts that one of them
# carries a decision. Zero-dependency plain-shell asserts, same idiom as that suite.
#
# Why this exists (issue #125): "the build fails rather than emit a wrong page" was a
# recorded choice, and #125 reverses half of it — a script line no commentary chunk covers
# is now debt the page carries and reports, not a refusal to build. A reversal that lives
# only in a diff is a decision the next reader has to re-derive from the code that won, so
# the ADR set is where it has to land: what the old guard bought, what replaced it, and
# what the page promises now that it no longer promises complete prose.
#
# Contract under test:
#   Some file in docs/adr/, named like the rest of the set (NNNN-slug.md), says all four
#   of: the build once failed on a line no commentary covered; it now builds and marks
#   that line owed instead; the source it shows is still verbatim, always; and the prose
#   beside it may lag. Which file, and how it is worded, are the author's — each probe
#   below accepts any phrasing that carries its fact.
#
# Where this suite lives (issue #137): here, with the rest of the docs pipeline's suites,
# because that is what its subject is — `make test` is what every veri leaf runs after every
# edit and what the conductor reads its baseline off, so a docs assertion inside it lets the
# docs pipeline stop development on a red the code did not cause (ADR 0016). It sat under
# the `make test` glob while `make docs-test` still named its suites one recipe line each,
# which made a suite added here run only once the Makefile was edited too; that target globs
# docs/tests/*.test.sh now, so this suite runs by existing. It reads sixteen small files and
# spawns no subprocess per probe, so it costs `make docs-test` well under a second.
#
# Run: docs/tests/docs-gap-adr.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
ADR_DIR="$ROOT/docs/adr"
pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output says which half of the contract broke rather than just that the case did.
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

# probe <message> <regex>... — one fact the record has to carry, written as the regexes
# that would show it is there: all of them have to match, and `message` names the fact once
# if any does not. Reads `$lc`, the lowercased text of the ADR under examination, and
# appends to `$problems` the way report() reads it. Each regex accepts any wording that
# carries the fact, so the case pins what the record says and not how it is phrased.
probe() {
  local msg="$1"; shift
  local re
  for re in "$@"; do
    [[ "$lc" =~ $re ]] || { problems+=("$msg"); return; }
  done
}

# probe_reversal_record — the whole contract, as the four facts the record has to carry.
# Reads `$lc`, the lowercased text of one ADR, and leaves in `$problems` one line per fact
# that file is short of — the protocol probe() and report() already share. Separated from
# the sweep below so that what the record must say is in one place, and choosing which file
# says it is in another: a change to the contract edits only this function.
probe_reversal_record() {
  probe "does not say the build once failed on a line no commentary covered" \
    '(fail|refus)' '(uncovered|not covered|no commentary|without commentary|gap)'
  probe "does not say the build now carries that line as debt, marked owed" \
    'owed' '(mark|render|list|note|report)'
  probe "does not say the source the page shows is still verbatim" \
    'verbatim'
  probe "does not say the prose beside it may lag" \
    '(prose|commentary)' '(lag|behind|catch(es|ing)? up)'
}

# find_reversal_record — which file says it, the other half of the split above. One ADR has
# to carry the whole decision, not four ADRs a fact each: the point of the record is that a
# reader who finds it can stop looking. So the sweep is per file — every probe against one
# file's text — and it stops at the first file that misses none. Only files that mention
# commentary at all are candidates; the rest of the set is about the conductor and would
# otherwise turn up as a near miss on a shared word like "fail". A file that misses some is
# kept as the closest miss, because "no ADR records this" and "the ADR forgot the promise"
# are different repairs and the failure below has to tell them apart.
#
# Sets four globals the case reads: `found` (the file carrying the whole record, empty if
# none), `adr_seen` and `candidates` (how far the sweep got), and `best_file` /
# `best_missing` (the closest miss and the facts it is short). `problems` is deliberately
# local: inside here it is one file's scratch list, outside it is the case's own failure
# list, and the two must not be the same array.
find_reversal_record() {
  local adr
  local -a problems

  adr_seen=0 candidates=0 found=""
  best_file="" best_missing=()
  for adr in "$ADR_DIR"/[0-9][0-9][0-9][0-9]-*.md; do
    [[ -f "$adr" ]] || continue
    adr_seen=$((adr_seen + 1))
    lc="$(tr '[:upper:]' '[:lower:]' < "$adr")"
    [[ "$lc" =~ commentar ]] || continue
    candidates=$((candidates + 1))

    problems=()
    probe_reversal_record

    if [[ "${#problems[@]}" -eq 0 ]]; then found="$adr"; return; fi
    if [[ -z "$best_file" || "${#problems[@]}" -lt "${#best_missing[@]}" ]]; then
      best_file="$adr"; best_missing=("${problems[@]}")
    fi
  done
}

# --- the reversal is on the record -------------------------------------------------
name="an ADR records that the walkthrough build tolerates uncovered lines, and what the page promises instead"

find_reversal_record

problems=()
if [[ "$adr_seen" -eq 0 ]]; then
  problems+=("no ADRs found under docs/adr/ — the sweep read nothing")
elif [[ -z "$found" && "$candidates" -eq 0 ]]; then
  problems+=("no ADR of the $adr_seen under docs/adr/ mentions commentary at all — the reversal is unrecorded")
elif [[ -z "$found" ]]; then
  problems+=("no ADR of the $adr_seen under docs/adr/ records the reversal; the closest, ${best_file##*/}:")
  problems+=("${best_missing[@]}")
fi

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
