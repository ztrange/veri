#!/usr/bin/env bash
# Unit tests for scripts/leaf-role.sh — the one place a leaf's NAME is turned into the role
# its events are logged under.
#
# Contract under test:
#   leaf-role.sh <leaf-name>  → prints the leaf's role as env assignments,
#                               `VERI_ACTOR=<actor> VERI_PHASE=<phase> VERI_ATTEMPT=<n>`,
#                               and exits 0 with nothing on stderr.
#   the mapping itself        → `develop-red` is actor `developer`, phase `red`, attempt 1;
#                               `revise-green-2` is `developer`, `green`, attempt 2;
#                               `verify-refactor` is `verifier`, phase `refactor`.
#   a leading word it does    → a diagnostic naming this script and the name on stderr,
#   not recognise               nothing on stdout, exit 2.
#   a recognised leading word → the same refusal, for both shapes that carry no phase:
#   with no phase after it      `develop` and `develop-`.
#
# Run: scripts/tests/leaf-role.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
LEAF_ROLE="$HERE/../leaf-role.sh"

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

name="leaf-role.sh refuses no argument and one empty argument with exit 2, nothing on stdout and stderr exactly the line usage: leaf-role.sh <leaf-name>"
problems=()
for args in none empty; do
  out="$(mktemp)" err="$(mktemp)"
  if [[ "$args" == none ]]; then
    "$LEAF_ROLE" >"$out" 2>"$err" && code=0 || code=$?
  else
    "$LEAF_ROLE" "" >"$out" 2>"$err" && code=0 || code=$?
  fi
  out_text="$(cat "$out")" err_text="$(cat "$err")"
  rm -f "$out" "$err"
  [[ "$code" == 2 ]] ||
    problems+=("$args: want exit 2, got $code")
  [[ -z "$out_text" ]] ||
    problems+=("$args: want nothing on stdout, got: $(printf '%q' "$out_text")")
  [[ "$err_text" == 'usage: leaf-role.sh <leaf-name>' ]] ||
    problems+=("$args: want stderr exactly 'usage: leaf-role.sh <leaf-name>', got: $(printf '%q' "$err_text")")
done
report "$name"

name="leaf-role.sh, run through a symlink to the skill directory and from another working directory, prints the same stdout and stderr and exits with the same code as when run in place, for develop-red (exit 0) and plan-red (exit 2)"
problems=()
scratch="$(scratch_dir)"
ln -s "$(cd "$HERE/../.." && pwd)" "$scratch/skill"
mkdir "$scratch/elsewhere"
for leaf in develop-red plan-red; do
  "$LEAF_ROLE" "$leaf" >"$scratch/in.out" 2>"$scratch/in.err" && in_code=0 || in_code=$?
  (cd "$scratch/elsewhere" && "$scratch/skill/scripts/leaf-role.sh" "$leaf") \
    >"$scratch/link.out" 2>"$scratch/link.err" && link_code=0 || link_code=$?
  case "$leaf" in develop-red) want=0 ;; plan-red) want=2 ;; esac
  [[ "$in_code" == "$want" ]] ||
    problems+=("$leaf: want exit $want in place, got $in_code")
  [[ "$link_code" == "$in_code" ]] ||
    problems+=("$leaf: want exit $in_code through the symlink, got $link_code")
  for stream in out err; do
    cmp -s "$scratch/in.$stream" "$scratch/link.$stream" ||
      problems+=("$leaf: std$stream differs through the symlink: in place $(printf '%q' "$(cat "$scratch/in.$stream")"), through the symlink $(printf '%q' "$(cat "$scratch/link.$stream")")")
  done
done
rm -rf "$scratch"
report "$name"

finish
