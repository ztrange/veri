#!/usr/bin/env bash
# lib/leaf-role.sh — sourced, not run: defines `leaf_role`.
#
# leaf_role <leaf-name> — print `VERI_ACTOR=… VERI_PHASE=… VERI_ATTEMPT=…` for a name shaped
# develop-*, revise-*, verify-* or conductor-* and return 0; develop and revise are both the
# developer, and a trailing -<digits> is the attempt, 1 without one. Return 2 with a diagnostic
# on stderr, nothing on stdout, for an empty name, an unknown leading word or no phase.
#
# hazard: `${name#*-}` returns the whole name when it has no `-`, so the phase is cut by length.
leaf_role() {
  local name="$1"

  if [[ -z "$name" ]]; then
    echo "leaf-role: usage: leaf-role.sh <leaf-name>" >&2
    return 2
  fi

  local actor_word="${name%%-*}"
  local actor
  local want='develop-*|revise-*|verify-*|conductor-*'

  case "$actor_word" in
    develop|revise) actor=developer ;;
    verify)         actor=verifier  ;;
    conductor)      actor=conductor ;;
    *)
      echo "leaf-role: leaf name '$name' has an unknown leading word (want $want)" >&2
      return 2
      ;;
  esac

  local phase_attempt="${name:${#actor_word}+1}"

  if [[ -z "$phase_attempt" ]]; then
    echo "leaf-role: leaf name '$name' says no phase (want $want)" >&2
    return 2
  fi

  local phase attempt

  if [[ "$phase_attempt" =~ ^(.*)-([0-9]+)$ ]]; then
    phase="${BASH_REMATCH[1]}"
    attempt="${BASH_REMATCH[2]}"
  else
    phase="$phase_attempt"
    attempt=1
  fi

  echo "VERI_ACTOR=$actor VERI_PHASE=$phase VERI_ATTEMPT=$attempt"
}
