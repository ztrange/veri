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

finish
