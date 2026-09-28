#!/usr/bin/env bash
# lib/leaf-model.sh — sourced, not run: defines `leaf_model`, and sources lib/leaf-role.sh.
#
# leaf_model <leaf-name> — print the model the leaf runs on and return 0: VERI_MODEL_DEVELOPER
# or VERI_MODEL_VERIFIER for its role, else VERI_MODEL, else nothing. Return 2 with a
# diagnostic on stderr for an empty name, a name leaf_role refuses, or a value with whitespace.
#
# hazard: `${BASH_SOURCE[0]}`, not `$0`, names this file when sourced.
# hazard: `tr`, not `${var^^}`, which bash 3.2 lacks.
_veri_lib_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$_veri_lib_dir/leaf-role.sh"
unset _veri_lib_dir

leaf_model() {
  local name="$1"

  if [[ -z "$name" ]]; then
    echo "leaf-model: usage: leaf-model.sh <leaf-name>" >&2
    return 2
  fi

  local role_line
  role_line="$(leaf_role "$name")" || return 2

  local actor="${role_line#VERI_ACTOR=}"
  actor="${actor%% *}"
  local role_var="VERI_MODEL_$(printf '%s' "$actor" | tr '[:lower:]' '[:upper:]')"

  local model="${!role_var:-${VERI_MODEL:-}}"

  if [[ "$model" =~ [[:space:]] ]]; then
    echo "leaf-model: model '$model' contains whitespace (a model id or alias is one word)" >&2
    return 2
  fi

  if [[ -n "$model" ]]; then
    echo "$model"
  fi
}
