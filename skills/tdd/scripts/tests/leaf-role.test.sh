#!/usr/bin/env bash
# Unit tests for scripts/leaf-role.sh — the one place a leaf's NAME is turned into the role
# its events are logged under (issue #107, ADR-0014: observability is a per-run event log
# written by the scripts, not a service).
# Zero-dependency plain-shell asserts, same idiom as leaf-timeout.test.sh.
#
# Why the mapping is a script of its own is said in its header (leaf-role.sh:5-9), once.
#
# Contract under test (this step only — the mapping, not any writer that uses it):
#   leaf-role.sh <leaf-name>  → prints the leaf's role as env assignments,
#                               `VERI_ACTOR=<actor> VERI_PHASE=<phase> VERI_ATTEMPT=<n>`,
#                               and exits 0 with nothing on stderr.
#   the mapping itself        → `develop-red` is actor `developer`, phase `red`, attempt 1;
#                               `revise-green-2` is `developer`, `green`, attempt 2;
#                               `verify-refactor` is `verifier`, phase `refactor`.
#   a leading word it does    → a diagnostic naming this script and the name on stderr,
#   not recognise               nothing on stdout, exit 2.
#
# Assignments rather than three bare values, in `VERI_*` spelling, because of where the
# answer goes: the context event.sh reads is the environment (event.sh:17-19), so a caller
# writes `env $(leaf-role.sh "$name") event.sh launch …` and the variable names stay spelled
# in this one script instead of at every writer's call site. The probe below looks each
# assignment up BY KEY, so neither the order of the three nor whether they share a line is
# pinned — both are the implementation's to choose, and pinning them would make a later
# writer's convenience a test failure.
#
# `verify-refactor`'s attempt is not probed, because the criterion does not state one and the
# name cannot carry it: the revise loop re-runs `verify.sh <phase>` under the same
# `verify-<phase>` name on every attempt (SKILL.md:641-644), so a verifier's attempt number
# is the conductor's to pass, not this mapping's to read. A leaf name that does carry one
# — `revise-green-2`'s trailing `2` — is exactly what the second probe pins.
#
# Run: scripts/tests/leaf-role.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
LEAF_ROLE="$HERE/../leaf-role.sh"
pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output says which probe broke rather than just that the case did.
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

# assignment <printed> <key> — the value the printed role gives <key>, or the literal
# `<<missing>>` when no assignment names it. `$printed` is deliberately unquoted: the word
# splitting is the point — it is the same splitting `env $(leaf-role.sh …)` does at the call
# site, so the probe reads the assignments exactly as the caller will, and it treats a
# newline between them the same way a space is treated.
assignment() {
  local printed="$1" key="$2" word
  for word in $printed; do
    if [[ "$word" == "$key="* ]]; then
      printf '%s\n' "${word#*=}"
      return 0
    fi
  done
  printf '%s\n' '<<missing>>'
}

# role_probe <leaf-name> <KEY=want> … — one leaf name the mapping must answer, and the
# assignments its answer must contain. Every probe also asserts exit 0 and silence on stderr:
# a name the mapping knows is not a diagnosable event, and a script that printed its answer
# to stderr would otherwise pass while `env $(…)` at the call site received nothing.
role_probe() {
  local leaf="$1"; shift
  local out err code printed want key expected got
  out="$(mktemp)" err="$(mktemp)"
  "$LEAF_ROLE" "$leaf" >"$out" 2>"$err" && code=0 || code=$?
  [[ "$code" == 0 ]] ||
    problems+=("$leaf: want exit 0, got $code")
  [[ ! -s "$err" ]] ||
    problems+=("$leaf: want nothing on stderr, got: $(printf '%q' "$(cat "$err")")")
  printed="$(cat "$out")"
  for want in "$@"; do
    key="${want%%=*}" expected="${want#*=}"
    got="$(assignment "$printed" "$key")"
    [[ "$got" == "$expected" ]] ||
      problems+=("$leaf: want $key=$(printf '%q' "$expected"), got $(printf '%q' "$got") (printed: $(printf '%q' "$printed"))")
  done
  rm -f "$out" "$err"
}

# 1. The whole of this step's criterion, as one case: the three leaf names the criterion
#    itself names, each with the role it says that name means.
#
#    They are the three shapes a leaf name comes in, and each probe does work the others
#    cannot. `develop-red` is the plain developer leaf, and its attempt 1 pins that a name
#    with no number still yields an attempt — a mapping that emitted none would leave
#    event.sh writing `attempt: ""` on the first launch of every step, which is the
#    "absent is not the spelling of unknown" rule event.sh:22-25 already refuses.
#    `revise-green-2` is the name that carries its own attempt: its role is `developer` and
#    `green` even though the name says neither word, so a mapping that read the leading word
#    as the actor or the trailing word as the phase is caught, and its attempt 2 is the only
#    place the trailing count is read. `verify-refactor` is the other actor — `verifier`, the
#    blind half of the pipeline, whose events must never be logged as the developer's, since
#    telling a REJECT's verdict from the work it judged is the whole point of the two roles.
name="leaf-role.sh maps a leaf name to its role: develop-red is developer/red/attempt 1, revise-green-2 is developer/green/attempt 2, verify-refactor is verifier/refactor"
problems=()
role_probe develop-red     VERI_ACTOR=developer VERI_PHASE=red      VERI_ATTEMPT=1
role_probe revise-green-2  VERI_ACTOR=developer VERI_PHASE=green    VERI_ATTEMPT=2
role_probe verify-refactor VERI_ACTOR=verifier  VERI_PHASE=refactor
report "$name"

# refusal_probe <leaf-name> — a name whose leading word is none of the three the mapping
# knows, and the three things a refusal owes. Exit 2 rather than 1: a leaf name the mapping
# cannot read is "no answer could be obtained", the plumbing speaking, not a clean negative
# any caller could act on. Nothing on stdout, because the answer is consumed as
# `env $(leaf-role.sh "$name") …` — a refusal that printed a half-role there would be
# word-split into the caller's environment and logged as if it were a role. And the
# diagnostic must carry both the script and the offending name: the writers call this from
# inside supervise.sh and the harvester, so a bare "unbound variable" on some run's stderr
# names neither what refused nor what it choked on.
refusal_probe() {
  local leaf="$1"
  local out err code stderr_text
  out="$(mktemp)" err="$(mktemp)"
  "$LEAF_ROLE" "$leaf" >"$out" 2>"$err" && code=0 || code=$?
  stderr_text="$(cat "$err")"
  [[ "$code" == 2 ]] ||
    problems+=("$leaf: want exit 2, got $code")
  [[ ! -s "$out" ]] ||
    problems+=("$leaf: want nothing on stdout, got: $(printf '%q' "$(cat "$out")")")
  [[ "$stderr_text" == *leaf-role* ]] ||
    problems+=("$leaf: want the script named on stderr, got: $(printf '%q' "$stderr_text")")
  [[ "$stderr_text" == *"$leaf"* ]] ||
    problems+=("$leaf: want the name on stderr, got: $(printf '%q' "$stderr_text")")
  rm -f "$out" "$err"
}

# 2. The mapping fails closed on a leading word it does not know.
#
#    `plan-red` is the shape this guards against: a well-formed leaf name — leading word, a
#    phase after the dash — launched under a role nobody taught this script. Guessing is the
#    failure mode worth refusing, because both wrong answers are silent: an actor defaulted
#    to `developer` files a leaf's events under a role it never had, and an empty actor writes
#    `"actor": ""` into a log whose whole purpose is telling the two halves of the pipeline
#    apart. Neither is visible until someone reads the log and believes it.
name="leaf-role.sh fails closed on a leaf name whose leading word it does not recognise: a diagnostic naming the script and the name on stderr, nothing on stdout, exit 2"
problems=()
refusal_probe plan-red
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
