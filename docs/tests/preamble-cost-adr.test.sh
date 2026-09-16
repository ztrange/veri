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
#   And a second record, of the cuts #202 refused to make: some file in that set names the
#   once-per-run procedure and the contingent paths (pin, revise, bail, resume), says they
#   were declined rather than deferred, gives the hazard that declines them — a conductor
#   which must read a file before it can bail might not bail, on the path that runs when
#   things are already broken — and says that half of SKILL.md is closed, with what would
#   have to change to reopen it.
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

# find_record <probe-fn> — which file says it, the other half of the split above. One ADR has
# to carry a whole contract, not three ADRs a fact each: the point of a record is that a reader
# who finds it can stop looking. So the sweep is per file — every probe against one file's
# text — and it stops at the first file that misses none. Only files about the preamble are
# candidates; the rest of the set is about the conductor and would otherwise turn up as a
# near miss on a shared word like "request". A file that misses some is kept as the closest
# miss, because "no ADR records this" and "the ADR forgot the volume" are different repairs
# and the failures below have to tell them apart.
#
# The contract to ask for is the argument, so that both cases below share one sweep: what a
# record must say lives in a probe_* function, which file says it lives here, once.
#
# Sets five globals the cases read: `found` (the file carrying the whole contract, empty if
# none), `adr_seen` and `candidates` (how far the sweep got), and `best_file` /
# `best_missing` (the closest miss and the facts it is short). Everything else is local,
# including the two names the probes read out of this scope: `problems`, which inside here is
# one file's scratch list and outside is a case's own failure list — the two must not be the
# same array — and `lc`, the text of whichever file the sweep is on, which no caller has any
# use for once the sweep has ended.
find_record() {
  local probe_fn="$1"
  local adr lc
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
    "$probe_fn"

    if [[ "${#problems[@]}" -eq 0 ]]; then found="$adr"; return; fi
    if [[ -z "$best_file" || "${#problems[@]}" -lt "${#best_missing[@]}" ]]; then
      best_file="$adr"; best_missing=("${problems[@]}")
    fi
  done
}

# --- the price of a preamble token is on the record --------------------------------
name="an ADR records what one preamble token costs per night, at the request volume measured on 2026-09-15"

find_record probe_preamble_price

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

# probe_decline_record — the second contract, as the four facts the record of the *refusal*
# has to carry. Step 1 of #202 tabled three candidate cuts in SKILL.md and the operator took
# one; the other two — the once-per-run procedure (3,684 tokens) and the contingent paths the
# conductor takes when something has already gone wrong: pin, revise, bail, resume (3,142
# tokens) — are a real ~7,800-token saving that was refused. A saving that large, refused and
# recorded nowhere, is one the next reader re-proposes from the same table and the same
# arithmetic, because the arithmetic is the half that is written down. What is not is the
# hazard: those paths are read on the turn something is already broken, and a conductor that
# must `Read` a file before it can bail is a conductor that might not bail.
#
# So the record owes what it declined, that it declined it rather than deferred it, why, and
# that the question is closed — with the one thing that would reopen it, since "closed" with
# no way back is an invitation to reopen it by simply not knowing it was shut.
#
# Same shape as probe_preamble_price above, and handed to the same find_record sweep: what
# this record must say is here, which file says it is that sweep's business, not this one's.
probe_decline_record() {
  probe "does not name the two cuts it declines — the once-per-run procedure, and the contingent paths the conductor takes when something has already gone wrong" \
    'once[ -]per[ -]run' '(contingent|bail)'
  probe "does not say they were declined rather than taken or deferred" \
    '(declin|reject|refus|not cut)'
  probe "does not give the hazard that declines them — that a conductor which must read a file before it can bail might not bail, on the path that runs when things are already broken" \
    '(read|load)' 'bail' '((might|may|could) (not|fail)|fails? to)' 'already (broken|wrong|gone wrong|failing)'
  probe "does not close that half of the file, nor name what would have to change to reopen it" \
    '(closed|closes|shut|reopen)' 'skill\.md'
}

# --- the two cuts that were refused are on the record, and that half is closed ------
name="an ADR records the two cuts #202 declined and the hazard that declines them, so that half of skills/tdd/SKILL.md is closed"

find_record probe_decline_record

problems=()
if [[ "$adr_seen" -eq 0 ]]; then
  problems+=("no ADRs found under docs/adr/ — the sweep read nothing")
elif [[ -z "$found" && "$candidates" -eq 0 ]]; then
  problems+=("no ADR of the $adr_seen under docs/adr/ is about the preamble at all — the ~7,800 tokens #202 refused to cut, and why, are unrecorded")
elif [[ -z "$found" ]]; then
  problems+=("no ADR of the $adr_seen under docs/adr/ records the decline; the closest, ${best_file##*/}:")
  problems+=("${best_missing[@]}")
fi

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
