#!/usr/bin/env bash
# Unit test for the ADR set under docs/adr/ — like docs-gap-adr.test.sh this suite has no
# script as its subject: it reads the records as text and asserts that one of them carries
# a price. Zero-dependency plain-shell asserts, same idiom as that suite.
#
# Why this exists (issue #202): two documents are re-sent and re-billed on every request of
# the session that loads them — skills/tdd/SKILL.md in every conductor request, CLAUDE.md in
# every request made in this repo, leaves included. The overnight run of 2026-09-14 22:00 →
# 2026-09-15 06:08 measured what that costs: 1,285 deduplicated requests over 94 sessions,
# $313 in total, of which those two preambles were ~6% before either file had helped anyone.
#
# The number that matters to the next author is not the total, though — it is the rate: what
# ONE token of preamble costs per night at that volume. #202 cuts 1,676 tokens out of
# SKILL.md and moves case histories out of CLAUDE.md, and both of those cuts are only ever
# repaid a token at a time. A reader who knows the rate can price a page of prose before
# adding it; a reader who knows only that some cut once saved ~6% cannot. That rate rests on
# a volume and a date — 1,285 requests, 2026-09-15 — because a price per night means nothing
# without the night it was counted on, and a later run at a different volume has to be able
# to tell that this figure was superseded rather than simply wrong.
#
# Contract under test:
#   Some file in docs/adr/, named like the rest of the set (NNNN-slug.md), is about the
#   preamble and says all three of: what one preamble token costs per night, in money; the
#   request volume that price is computed at; and the date of the measurement it rests on.
#   Which file, and how it is worded, are the author's — each probe below accepts any
#   phrasing that carries its fact.
#
# Where this suite lives (issue #143, ADR 0016): here, with the rest of the docs lane's
# suites, and not under the `make test` glob, because its subject is a record under docs/adr/
# and `make test` is what preflight reads its baseline off, what every Green leaf runs and
# what both blind verifiers run. A case there would let rewording this ADR redden a
# development run that never touched it — and no-docs-reads.test.sh fails the run for a suite
# there that so much as names a path in this tree. `make docs-test` globs this directory, so
# this suite runs by existing and owes no Makefile edit (#137).
#
# It reads seventeen small files and spawns no subprocess per probe, so it costs
# `make docs-test` well under a second.
#
# Run: docs/tests/preamble-cost-adr.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
ADR_DIR="$ROOT/docs/adr"
pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output says which part of the price is missing rather than just that the case broke.
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

# probe <message> <regex>... — one fact the record has to carry, written as the regexes that
# would show it is there: all of them have to match, and `message` names the fact once if any
# does not. Reads `$lc`, the lowercased text of the ADR under examination, and appends to
# `$problems` the way report() reads it. Same helper as docs-gap-adr.test.sh's, for the same
# reason: the case pins what the record says and not how it is phrased.
probe() {
  local msg="$1"; shift
  local re
  for re in "$@"; do
    [[ "$lc" =~ $re ]] || { problems+=("$msg"); return; }
  done
}

# probe_preamble_price — the whole contract, as the three facts the record has to carry.
# Reads `$lc`, the lowercased text of one ADR, and leaves in `$problems` one line per fact
# that file is short of. Separated from the sweep below so that what the record must say is
# in one place and which file says it is in another: a change to the contract edits only
# this function.
probe_preamble_price() {
  probe "does not price one preamble token per night, in money" \
    '\$[0-9]' '(per|each|one|a)( [a-z]+)? token' 'night'
  probe "does not give the request volume that price is computed at" \
    '1,?285' 'request'
  probe "does not carry the date of the measurement it rests on" \
    '2026-09-15'
}

# find_price_record — which file says it, the other half of the split above. One ADR has to
# carry the whole price, not three ADRs a fact each: the point of the record is that a reader
# who finds it can stop looking. So the sweep is per file — every probe against one file's
# text — and it stops at the first file that misses none. Only files about the preamble are
# candidates; the rest of the set is about the conductor and would otherwise turn up as a
# near miss on a shared word like "request". A file that misses some is kept as the closest
# miss, because "no ADR records this" and "the ADR forgot the volume" are different repairs
# and the failure below has to tell them apart.
#
# Sets four globals the case reads: `found` (the file carrying the whole price, empty if
# none), `adr_seen` and `candidates` (how far the sweep got), and `best_file` /
# `best_missing` (the closest miss and the facts it is short). `problems` is deliberately
# local: inside here it is one file's scratch list, outside it is the case's own failure
# list, and the two must not be the same array.
find_price_record() {
  local adr
  local -a problems

  adr_seen=0 candidates=0 found=""
  best_file="" best_missing=()
  for adr in "$ADR_DIR"/[0-9][0-9][0-9][0-9]-*.md; do
    [[ -f "$adr" ]] || continue
    adr_seen=$((adr_seen + 1))
    lc="$(tr '[:upper:]' '[:lower:]' < "$adr")"
    [[ "$lc" =~ preamble ]] || continue
    candidates=$((candidates + 1))

    problems=()
    probe_preamble_price

    if [[ "${#problems[@]}" -eq 0 ]]; then found="$adr"; return; fi
    if [[ -z "$best_file" || "${#problems[@]}" -lt "${#best_missing[@]}" ]]; then
      best_file="$adr"; best_missing=("${problems[@]}")
    fi
  done
}

# --- the price of a preamble token is on the record --------------------------------
name="an ADR records what one preamble token costs per night, at the request volume measured on 2026-09-15"

find_price_record

problems=()
if [[ "$adr_seen" -eq 0 ]]; then
  problems+=("no ADRs found under docs/adr/ — the sweep read nothing")
elif [[ -z "$found" && "$candidates" -eq 0 ]]; then
  problems+=("no ADR of the $adr_seen under docs/adr/ is about the preamble at all — what a preamble token costs per night is unrecorded")
elif [[ -z "$found" ]]; then
  problems+=("no ADR of the $adr_seen under docs/adr/ records the price; the closest, ${best_file##*/}:")
  problems+=("${best_missing[@]}")
fi

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
