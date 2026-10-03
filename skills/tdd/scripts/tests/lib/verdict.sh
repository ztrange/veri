#!/usr/bin/env bash
# Sourced by guard suites: reports the case named $1 green when it has no problems, otherwise red
# followed by them — each further argument as one indented line, or with none, the suite's own
# $problems text as it stands.
# Usage: source "$HERE/lib/verdict.sh"; verdict <name> [problem...]

verdict() {
  local name="$1"
  shift
  if (( $# > 0 )); then
    no "$name"
    printf '    %s\n' "$@"
  elif [[ -z "${problems-}" ]]; then
    ok
  else
    no "$name"
    printf '%s' "$problems"
  fi
}
