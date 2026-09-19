#!/usr/bin/env bash
# Unit tests for how the conductor's Red section handles a criterion no lightweight,
# behavior-level test can pin — like skill-red-prediction.test.sh and skill-suite-runs.test.sh
# this suite belongs to no single script: its subject is skills/tdd/SKILL.md, read as text,
# the way the session that follows it reads it.
# Zero-dependency plain-shell asserts, same idiom as skill-red-prediction.test.sh.
#
# Why this exists (issue #331): #331's acceptance criterion "the suite starts at most N
# python3" was satisfied by a leaf adding suites that re-run whole suites under a counting
# shim (+41s of `make test`); #333's "launches overlap" made a suite twice as slow. Both are
# criteria a Red developer leaf CAN satisfy — just not with a test that is lightweight and
# behavior-oriented — and until now the pipeline gave it no way to say so: the only report
# line was `AGAINST_UNMODIFIED: FAILS | PASSES`, so a leaf facing an unpinnable criterion had
# to either force a costly or implementation-pinning test through, or fabricate a FAILS/PASSES
# it did not observe. develop-red.md now offers a third outcome, `UNTESTABLE`, and this suite
# pins what the conductor does when it sees one: skip the blind verifier (there is nothing on
# disk for it to judge) and bail immediately, classified as a process failure since the
# criterion as phrased — not the plumbing — is what could not be satisfied.
#
# Contract under test:
#   1. SKILL.md's Red section states what a valid test is: behaviour over mechanism (no
#      process/fork count or timing assertion), with the in-process-spy carve-out for a call
#      count the criterion itself names.
#   2. SKILL.md's Red section's verify sub-step branches on `AGAINST_UNMODIFIED: UNTESTABLE`
#      by skipping verify-red and verify-pin and bailing immediately, with cause
#      `untestable-criterion`.
#   3. SKILL.md's Bailing section lists `untestable-criterion` as a **process** failure
#      cause, alongside `revise-exhausted`.
#
# Run: scripts/tests/skill-red-untestable.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root.
ROOT="$(cd "$HERE/../../../.." && pwd)"

# The document twice: the path as every failure message spells it, and the same path
# resolved for the probes to read, so a message can never name a file the probes did not
# open. Same pairing skill-red-prediction.test.sh uses.
skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"

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

# plain — stdin with emphasis marks and backticks dropped and the case folded, because
# `**UNTESTABLE**` and "untestable" are the same word. The probes' regexes are then written
# one way and match however the author chose to mark the words up.
plain() {
  tr -d '*`' | tr '[:upper:]' '[:lower:]'
}

# doc_text <heading-prefix> [<from-regex>] — the text of the first SKILL.md section whose
# heading STARTS WITH the literal <heading-prefix>, optionally from the first line matching
# <from-regex>, up to the line before the next heading of any level. Same shape as
# skill-red-prediction.test.sh's helper of the same name; omitting <from-regex> reads the
# whole section from its heading. The text is normalised through `plain` and joined onto one
# line, so a sentence split over a line break still reads as one.
doc_text() {
  awk -v h="$1" -v from="${2:-}" '
    !in_s && index($0, h) == 1 { in_s = 1; if (from == "") want = 1; next }
    in_s && /^#/ { exit }
    in_s {
      if (!want && from != "" && $0 ~ from) want = 1
      if (want) print
    }' "$skill_path" | plain | tr '\n' ' '
}

# says <regex> <fact> — one thing the text has to carry, written as the regex of any
# wording that would carry it; `fact` names it once if nothing matches.
says() {
  [[ "$text" =~ $1 ]] || problems+=("$2")
}

# 1. SKILL.md's Red section states what a valid test is: behaviour over mechanism, with the
#    in-process-spy carve-out for a call count the criterion itself names. Read from the
#    "Develop." sub-step, where develop-red's template is described, since that is where
#    the rule belongs — a reader who skips straight to the verify sub-step has already been
#    told what the leaf was asked for.
name="$skill_md's Red section states what a valid test is (behaviour over mechanism, with the in-process-spy carve-out)"
problems=()
text="$(doc_text '#### Red' 'Develop\.')"
if [[ -z "${text// /}" ]]; then
  problems+=("$skill_md's Red section has no \"Develop.\" sub-step — what a valid test is could not be read")
else
  says 'process[^.]{0,20}(count|fork)|fork[^.]{0,20}count' \
    "$skill_md never forbids pinning a process or fork count"
  says 'make profile' \
    "$skill_md never points process/fork counts or timings at make profile instead of an assertion"
  says 'in-process spy' \
    "$skill_md never carves out an in-process spy for a call count the criterion itself names"
fi
report "$name"

# 2. SKILL.md's Red section's verify sub-step skips verify-red/verify-pin and bails
#    immediately on UNTESTABLE, with cause untestable-criterion. Read from the "Verify
#    (blind)." sub-step, the one that already branches on FAILS and PASSES, so an UNTESTABLE
#    that this suite cannot find there is a branch not yet wired into the sub-step readers
#    read, not merely mentioned somewhere in the phase.
name="$skill_md's Red section skips the blind verifier and bails immediately on AGAINST_UNMODIFIED: UNTESTABLE"
problems=()
text="$(doc_text '#### Red' 'Branch on the leaf')"
if [[ -z "${text// /}" ]]; then
  problems+=("$skill_md's Red section has no \"Verify (blind).\" sub-step — the UNTESTABLE branch could not be read")
else
  says 'untestable' \
    "$skill_md's verify sub-step never branches on UNTESTABLE"
  says 'skip[^.]{0,60}verify-(red|pin)|verify-(red|pin)[^.]{0,60}skip' \
    "$skill_md never says to skip verify-red/verify-pin on UNTESTABLE"
  says 'bail' \
    "$skill_md never says to bail on UNTESTABLE"
  says 'untestable-criterion' \
    "$skill_md never names the untestable-criterion cause token for this bail"
fi
report "$name"

# 3. SKILL.md's Bailing section classifies untestable-criterion as a process failure,
#    alongside revise-exhausted — the same category, for the same reason: the methodology
#    (here, the criterion as phrased) could not be satisfied, not that the plumbing broke.
#    Read from the causes list itself rather than the whole Bailing section, so a mention of
#    "process" anywhere else in the procedure (e.g. "process failure" in the Red section
#    above) cannot stand in for the causes list actually carrying the token.
name="$skill_md's Bailing causes list classifies untestable-criterion as a process failure"
problems=()
text="$(doc_text '## Bailing' 'killed-stuck')"
if [[ -z "${text// /}" ]]; then
  problems+=("$skill_md's Bailing section has no causes list starting at killed-stuck — the classification could not be read")
else
  says 'untestable-criterion[^.]{0,220}process' \
    "$skill_md's Bailing causes list never classifies untestable-criterion as a process failure"
fi
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
