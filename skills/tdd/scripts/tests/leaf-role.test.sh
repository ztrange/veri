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
#   a recognised leading word → the same refusal, for both shapes that carry no phase:
#   with no phase after it      `develop`, which has no `-` at all, and `develop-`, whose
#                               `-` has nothing after it.
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
# `verify-<phase>` name on every attempt (SKILL.md:654-659), so a verifier's attempt number
# is the conductor's to pass, not this mapping's to read. A leaf name that does carry one
# — `revise-green-2`'s trailing `2` — is exactly what the second probe pins.
#
# Run: scripts/tests/leaf-role.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
LEAF_ROLE="$HERE/../leaf-role.sh"
pass=0 fail=0

source "$HERE/lib/harness.sh"

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

capture() {
  local out err
  out="$(mktemp)" err="$(mktemp)"
  "$LEAF_ROLE" "$1" >"$out" 2>"$err" && code=0 || code=$?
  out_text="$(cat "$out")" err_text="$(cat "$err")"
  rm -f "$out" "$err"
}

role_probe() {
  local leaf="$1"; shift
  local code out_text err_text wanted_assignment key expected got
  capture "$leaf"
  [[ "$code" == 0 ]] ||
    problems+=("$leaf: want exit 0, got $code")
  [[ -z "$err_text" ]] ||
    problems+=("$leaf: want nothing on stderr, got: $(printf '%q' "$err_text")")
  for wanted_assignment in "$@"; do
    key="${wanted_assignment%%=*}" expected="${wanted_assignment#*=}"
    got="$(assignment "$out_text" "$key")"
    [[ "$got" == "$expected" ]] ||
      problems+=("$leaf: want $key=$(printf '%q' "$expected"), got $(printf '%q' "$got") (printed: $(printf '%q' "$out_text"))")
  done
}

refusal_probe() {
  local leaf="$1"
  local code out_text err_text
  capture "$leaf"
  [[ "$code" == 2 ]] ||
    problems+=("$leaf: want exit 2, got $code")
  [[ -z "$out_text" ]] ||
    problems+=("$leaf: want nothing on stdout, got: $(printf '%q' "$out_text")")
  [[ "$err_text" == *leaf-role* ]] ||
    problems+=("$leaf: want the script named on stderr, got: $(printf '%q' "$err_text")")
  [[ "$err_text" == *"$leaf"* ]] ||
    problems+=("$leaf: want the name on stderr, got: $(printf '%q' "$err_text")")
}

name="leaf-role.sh maps a leaf name to its role: develop-red is developer/red/attempt 1, revise-green-2 is developer/green/attempt 2, verify-refactor is verifier/refactor"
problems=()
role_probe develop-red     VERI_ACTOR=developer VERI_PHASE=red      VERI_ATTEMPT=1
role_probe revise-green-2  VERI_ACTOR=developer VERI_PHASE=green    VERI_ATTEMPT=2
role_probe verify-refactor VERI_ACTOR=verifier  VERI_PHASE=refactor
report "$name"

name="leaf-role.sh fails closed on a leaf name whose leading word it does not recognise: a diagnostic naming the script and the name on stderr, nothing on stdout, exit 2"
problems=()
refusal_probe plan-red
report "$name"

name="leaf-role.sh fails closed on a leaf name with a recognised leading word but no phase after it — develop, with no dash at all, and develop-, whose dash has nothing after it: a diagnostic naming the script and the name on stderr, nothing on stdout, exit 2"
problems=()
refusal_probe develop
refusal_probe develop-
report "$name"

name="leaf-role.sh's two refusals name all four accepted shapes, conductor-* alongside develop-*, revise-* and verify-* (#506)"
problems=()
for leaf in plan-red develop; do
  capture "$leaf"
  for shape in 'develop-*' 'revise-*' 'verify-*' 'conductor-*'; do
    [[ "$err_text" == *"$shape"* ]] ||
      problems+=("$leaf: want $shape named on stderr, got: $(printf '%q' "$err_text")")
  done
done
report "$name"

name="leaf-role.sh still refuses plan-red, develop and develop- with exit 2 and still maps develop-red, revise-green-2, verify-refactor and conductor-506 to the same actor and phase (#506)"
problems=()
refusal_probe plan-red
refusal_probe develop
refusal_probe develop-
role_probe develop-red     VERI_ACTOR=developer VERI_PHASE=red      VERI_ATTEMPT=1
role_probe revise-green-2  VERI_ACTOR=developer VERI_PHASE=green    VERI_ATTEMPT=2
role_probe verify-refactor VERI_ACTOR=verifier  VERI_PHASE=refactor
role_probe conductor-506   VERI_ACTOR=conductor VERI_PHASE=506      VERI_ATTEMPT=1
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
