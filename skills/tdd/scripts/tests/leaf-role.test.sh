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

# capture <leaf-name> — run the mapping once and leave its three results in the caller's
# locals `code`, `out_text` and `err_text`. Both probes below judge all three, and collecting
# them is temp-file bookkeeping that would otherwise be spelled identically in each: a probe
# that forgot the `2>` would let a diagnostic escape to the suite's own stderr and still pass.
# The assignments are deliberately unqualified — bash scoping is dynamic, so they land in the
# `local` the calling probe declared, and nothing here leaks into the next case.
capture() {
  local out err
  out="$(mktemp)" err="$(mktemp)"
  "$LEAF_ROLE" "$1" >"$out" 2>"$err" && code=0 || code=$?
  out_text="$(cat "$out")" err_text="$(cat "$err")"
  rm -f "$out" "$err"
}

# role_probe <leaf-name> <KEY=value> … — one leaf name the mapping must answer, and the
# assignments its answer must contain. Every probe also asserts exit 0 and silence on stderr:
# a name the mapping knows is not a diagnosable event, and a script that printed its answer
# to stderr would otherwise pass while `env $(…)` at the call site received nothing.
#
# Each argument is a whole assignment, and the loop names it so: `wanted_assignment` is the
# `KEY=value` pair, `key` and `expected` the two halves cut out of it. The pair was called
# `want` before, which is the name the rest of this suite's siblings give the expected VALUE
# (leaf-timeout.test.sh's `good_probe <baseline> <want>`) — so one word meant the pair here
# and its right half there, three lines apart.
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

# refusal_probe <leaf-name> — a name the mapping must refuse, and the three things a refusal
# owes whatever made the name unreadable. Which names those are, and what each would have been
# answered with had it not been refused, belongs to the two cases below that call this: the
# shapes differ, the obligations do not. Exit 2 rather than 1: a leaf name the mapping
# cannot read is "no answer could be obtained", the plumbing speaking, not a clean negative
# any caller could act on. Nothing on stdout, because the answer is consumed as
# `env $(leaf-role.sh "$name") …` — a refusal that printed a half-role there would be
# word-split into the caller's environment and logged as if it were a role. And the
# diagnostic must carry both the script and the offending name: the writers call this from
# inside supervise.sh and the harvester, so a bare "unbound variable" on some run's stderr
# names neither what refused nor what it choked on.
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

# 1. The whole of this step's criterion, as one case: the three leaf names the criterion
#    itself names, each with the role it says that name means.
#
#    They are the three shapes a leaf name comes in, and each probe does work the others
#    cannot. `develop-red` is the plain developer leaf, and its attempt 1 pins that a name
#    with no number still yields an attempt — a mapping that emitted none would leave
#    event.sh writing `attempt: ""` on the first launch of every step, which is the
#    "absent is not the spelling of unknown" rule event.sh:20-22 already refuses.
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

# 2. The mapping fails closed on a leading word it does not know.
#
#    `plan-red` is the shape this guards against: a well-formed leaf name — leading word, a
#    phase after the dash — launched under a role nobody taught this script. Guessing is the
#    failure mode worth refusing; which two guesses those are, and why neither is visible
#    until someone reads the log and believes it, is said beside the arm that refuses them
#    (leaf-role.sh:46-49).
name="leaf-role.sh fails closed on a leaf name whose leading word it does not recognise: a diagnostic naming the script and the name on stderr, nothing on stdout, exit 2"
problems=()
refusal_probe plan-red
report "$name"

# 3. The mapping fails closed on a name whose leading word it does know but which says no
#    phase — both shapes that can carry none, as one case, because they are owed one refusal
#    and not two.
#
#    It is a case of its own rather than more of case 2 because the invention it refuses has a
#    different source — not an arm nobody wrote, but the cut the phase is read by. What that
#    cut leaves each of these names, and the answer `leaf-role.sh develop` would otherwise have
#    printed, is said beside the cut (leaf-role.sh:58-62); why the empty phase may not be
#    logged in place of a refusal is said beside the guard (leaf-role.sh:69-71).
#
#    Each probe does work the other cannot. `develop` is the plain shape: the actor is
#    readable, and there is nothing after it to read a phase out of. `develop-` reaches the
#    same missing answer by the shape that hides it — the name does carry a `-`, so anything
#    asking whether the STRING has one is satisfied while the phase read out of it is still the
#    empty string, which is what makes it the name that pins the guard on the phase rather than
#    on the shape. It is not a name a run launches today; it is what a caller's own string
#    handling produces when the phase it meant to append was empty, and the refusal is what
#    turns that into a diagnostic on the spot instead of a blank field found later.
name="leaf-role.sh fails closed on a leaf name with a recognised leading word but no phase after it — develop, with no dash at all, and develop-, whose dash has nothing after it: a diagnostic naming the script and the name on stderr, nothing on stdout, exit 2"
problems=()
refusal_probe develop
refusal_probe develop-
report "$name"

# 4. Both refusals list every accepted shape, conductor-* included (#506).
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

# 5. The message change moved no exit code and no accepted name (#506).
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
