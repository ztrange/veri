#!/usr/bin/env bash
# Unit tests for scripts/leaf-model.sh — says which model one leaf runs on.
#
# Contract under test:
#   VERI_MODEL=<x> leaf-model.sh <leaf-name>  → prints <x> and exits 0, for a leaf of
#                                 EITHER role.
#   leaf-model.sh <leaf-name>  with no model variable set
#                              → prints NOTHING and exits 0.
#   VERI_MODEL=<x> VERI_MODEL_VERIFIER=<y> leaf-model.sh <leaf-name>
#                              → the role variable wins for that role's leaves and for no
#                                others: <y> for `verify-*`, <x> still for `develop-*` and
#                                `revise-*`, and the mirror image for VERI_MODEL_DEVELOPER.

set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
LEAF_MODEL="$HERE/../leaf-model.sh"
LEAF_ROLE="$HERE/../leaf-role.sh"
ROOT="$(cd "$HERE/../../../.." && pwd)"
skill_md="skills/tdd/SKILL.md"

source "$HERE/lib/harness.sh"

model_call() {
  local -a envargs
  label="VERI_MODEL=$1 VERI_MODEL_DEVELOPER=$2 VERI_MODEL_VERIFIER=$3 $4"
  envargs=(-u VERI_MODEL -u VERI_MODEL_DEVELOPER -u VERI_MODEL_VERIFIER)
  [[ "$1" == unset ]] || envargs+=(VERI_MODEL="$1")
  [[ "$2" == unset ]] || envargs+=(VERI_MODEL_DEVELOPER="$2")
  [[ "$3" == unset ]] || envargs+=(VERI_MODEL_VERIFIER="$3")
  out="$(mktemp)" err="$(mktemp)"
  env "${envargs[@]}" "$LEAF_MODEL" "$4" >"$out" 2>"$err" && code=0 || code=$?
}

model_probe() {
  local want="$5" out err code label
  model_call "$1" "$2" "$3" "$4"
  [[ "$code" == 0 ]] ||
    problems+=("$label: want exit 0, got $code")
  [[ "$(cat "$out")" == "$want" ]] ||
    problems+=("$label: want $(printf '%q' "$want") on stdout, got: $(printf '%q' "$(cat "$out")")")
  [[ ! -s "$err" ]] ||
    problems+=("$label: want nothing on stderr, got: $(printf '%q' "$(cat "$err")")")
  rm -f "$out" "$err"
}

model_refuses() {
  local out err code label
  model_call "$1" "$2" "$3" "$4"
  [[ "$code" == 2 ]] ||
    problems+=("$label: want exit 2, got $code")
  [[ ! -s "$out" ]] ||
    problems+=("$label: want nothing on stdout, got: $(printf '%q' "$(cat "$out")")")
  [[ -s "$err" ]] ||
    problems+=("$label: want a diagnostic on stderr, got nothing")
  rm -f "$out" "$err"
}

name="VERI_MODEL is printed for a leaf of either role; with no model variable set, nothing is printed and the exit is still 0"
problems=()
model_probe sonnet unset unset develop-red  sonnet
model_probe sonnet unset unset verify-green sonnet
model_probe unset unset unset develop-red  ""
model_probe unset unset unset verify-green ""
report "$name"

name="a role variable beats VERI_MODEL for that role's leaves only"
problems=()
model_probe sonnet unset opus develop-red    sonnet
model_probe sonnet unset opus revise-green-2 sonnet
model_probe sonnet unset opus verify-green   opus
model_probe sonnet opus unset develop-red    opus
model_probe sonnet opus unset revise-green-2 opus
model_probe sonnet opus unset verify-green   sonnet
report "$name"

name="a value containing whitespace and a leaf name leaf-role.sh refuses each exit 2 with a diagnostic, while opus[1m] is accepted"
problems=()
model_refuses 'sonnet 5' unset unset develop-red
model_refuses unset unset $'opus\t1m' verify-green
model_refuses sonnet unset unset frobnicate-red
model_refuses unset unset unset frobnicate-red
model_probe 'opus[1m]' unset unset develop-red  'opus[1m]'
model_probe unset unset 'opus[1m]' verify-green 'opus[1m]'
report "$name"

name="$skill_md's preflight runs leaf-model.sh for a developer name and for a verifier name, and says its exit 2 stops the run"
problems=()
preflight="$(awk '/^### [0-9]+\..*[Pp]reflight/ { inside = 1; print; next }
                  inside && /^### / { exit }
                  inside' "$ROOT/$skill_md")"
if [[ -z "$preflight" ]]; then
  problems+=("$skill_md: no numbered '### … Preflight' section — what preflight runs could not be read")
else
  roles=""
  while IFS= read -r leaf; do
    [[ -n "$leaf" ]] || continue
    role_line="$("$LEAF_ROLE" "$leaf" 2>/dev/null)" ||
      { problems+=("$skill_md preflight: leaf-model.sh is called with '$leaf', a name leaf-role.sh refuses"); continue; }
    roles="$roles $(printf '%s\n' "$role_line" | sed -n 's/.*VERI_ACTOR=\([a-z]*\).*/\1/p')"
  done <<< "$(printf '%s\n' "$preflight" \
    | grep -o 'leaf-model\.sh[[:space:]][^[:space:]]*' \
    | awk '{ print $2 }' \
    | tr -d '`"'"'"'' \
    | sed 's/[),;:.]*$//' \
    | grep -v '^$')"
  for want in developer verifier; do
    [[ "$roles" == *" $want"* ]] ||
      problems+=("$skill_md preflight: no leaf-model.sh call with a $want leaf name (names found:${roles:-" none"})")
  done
  lowered="$(printf '%s\n' "$preflight" | tr '[:upper:]' '[:lower:]')"
  [[ "$lowered" == *leaf-model.sh* && "$lowered" == *"exit 2"* \
     && "$lowered" =~ (verbatim|diagnostic) ]] ||
    problems+=("$skill_md preflight: does not say leaf-model.sh's exit 2 stops the run, reporting its stderr diagnostic")
fi
report "$name"

finish
