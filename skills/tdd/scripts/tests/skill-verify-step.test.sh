#!/usr/bin/env bash
# Unit test for the step a verifier launch in skills/tdd/SKILL.md carries. Like
# skill-leaf-launch.test.sh and skill-suite-runs.test.sh this suite belongs to no single
# script: its subject is the procedure, read as text, the way the session that follows it
# reads it. Zero-dependency plain-shell asserts, same idiom, picked up by `make test`'s
# glob by existing.
#
# Why this exists (issue #223): `verify.sh` and `build-verify-prompt.sh` now take an
# optional `--step "<STEP>"` flag, and every `verify-*.md` prompt shows that step and scopes
# the verdict to it. The flag is worth exactly as much as the call sites that pass it — and
# it is a FLAG and only a flag, never read from an ambient `VERI_STEP` (verify.sh:34-40), so
# the `VERI_STEP='<STEP>'` prefix those launch lines already carry for the event log does
# not scope one verdict. A document that describes the flag and does not type it leaves
# every verifier judging the whole spec, which is the defect: on #113 step 2 of 9 a blind
# verify-refactor rejected for a criterion belonging to step 5, and the run spent its whole
# REVISE_BUDGET discovering that no revise could satisfy both.
#
# Contract under test:
#   Every `verify.sh` call SKILL.md tells the conductor to run — the red, pin, green,
#   refactor, revise re-verify and resume launches — passes `--step "<STEP>"` before
#   verify.sh's positionals; and every one that can judge green — the green launch and the
#   revise re-verify, whose phase is `<phase>` — passes `--fast-cmd '<fast-cmd>'` after it.
#
# A call is a line naming `verify.sh` with the **spec file** among its arguments: that is
# what tells a line a conductor copies as it stands from prose about one. The script
# inventory's synopsis (SKILL.md:129) names the spec too and is deliberately not among them
# — it spells the phase as the alternation `<red|green|refactor|pin|plan>`, so it documents the
# script's own usage rather than making a call. `verify.sh exited 2` in *Bailing* and the
# `$S/verify.sh pin …` back-reference in *Already satisfied* name no spec, so neither is
# matched either.
#
# Run: skills/tdd/scripts/tests/skill-verify-step.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root.
ROOT="$(cd "$HERE/../../../.." && pwd)"

# The document twice: the path as every failure message spells it, and the same path
# resolved for the probe to read, so a message can never name a file the probe did not open.
skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"

# What a call has to carry, written down once so the probe and the message it fails with
# cannot drift apart: verify.sh's own flag, spelled with the placeholder the document uses
# for the ledger's step text everywhere else, in the DOUBLE quotes SKILL.md's step-title rule
# now sets (#431): a title is the planning leaf's own English, and an apostrophe in it closes
# a single-quoted `'<STEP>'` early, killing the line in the shell the conductor typed it into.
flag='--step "<STEP>"'

# The one pattern the probe below matches a launch line with, built from that same `flag` so
# the two cannot drift: nothing in the flag's spelling is an ERE metacharacter, so it goes in
# as it stands. The phase alternation after it is what pins the POSITION — `--step` has to
# sit between `verify.sh` and the phase the call judges, which is a word in a concrete launch
# and the `<phase>` placeholder in the revise loop's. Green's call also passes the fast tier's
# command (#341), after the step and still ahead of the phase.
call_re="verify\.sh $flag( --fast-cmd '<fast-cmd>')? (red|green|refactor|pin|<phase>)"

pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output names the launch lines that are wrong rather than just saying the case is.
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

# verify_calls — the verify.sh calls of SKILL.md, each prefixed with its line number.
#
# The spec file is the mark of a call, in either spelling the document uses for it: the
# launch lines name `.tdd/issue-<n>-spec.md` and the resume paragraph names `<spec-file>`.
# The synopsis is dropped by the alternation only it spells, rather than by its line number,
# which moves with every edit above it.
verify_calls() {
  grep -nE 'verify\.sh.*(<spec-file>|\.tdd/issue-<n>-spec\.md)' "$skill_path" |
    grep -vF '<red|green|refactor|pin|plan>'
}

# 1. One criterion — every verify.sh call the conductor makes says which step it is about —
#    and so one case. The flag is asked for in the one position verify.sh accepts it, ahead
#    of the phase and the positionals that follow it, because a `--step` after the phase is
#    read as the target test id and the verdict is scoped by nothing.
name="$skill_md passes $flag on every verify.sh call it tells the conductor to run"
problems=()

calls="$(verify_calls)"
if [[ -z "$calls" ]]; then
  problems+=("$skill_md has no verify.sh call naming a spec file — the calls this case is about could not be read")
else
  while IFS= read -r numbered; do
    [[ -n "$numbered" ]] || continue
    lineno="${numbered%%:*}"
    line="${numbered#*:}"
    [[ "$line" =~ $call_re ]] ||
      problems+=("$skill_md:$lineno does not pass $flag before verify.sh's positionals: $line")
  done <<< "$calls"
fi

report "$name"

# 2. A call that can judge green passes the fast tier's command too (#341): green is the one
#    phase build-verify-prompt.sh refuses without `--fast-cmd`, exit 2, and the conductor
#    reads exit 2 as a system failure. The revise loop's re-verify spells its phase
#    `<phase>`, which is green whenever a green was rejected, so it owes the flag as much as
#    the green launch does — a revised green would otherwise bail instead of being judged.
fast_flag="--fast-cmd '<fast-cmd>'"
green_re="verify\.sh $flag( $fast_flag)? (green|<phase>) "
name="$skill_md passes $fast_flag on every verify.sh call that can judge green"
problems=()

if [[ -n "$calls" ]]; then
  while IFS= read -r numbered; do
    [[ -n "$numbered" ]] || continue
    lineno="${numbered%%:*}"
    line="${numbered#*:}"
    [[ "$line" =~ $green_re ]] || continue
    [[ "$line" == *"verify.sh $flag $fast_flag "* ]] ||
      problems+=("$skill_md:$lineno can judge green but does not pass $fast_flag: $line")
  done <<< "$calls"
fi

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
