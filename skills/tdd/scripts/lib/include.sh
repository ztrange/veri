#!/usr/bin/env bash
# lib/include.sh — sourced, not run: defines `resolve_includes`.
#
# resolve_includes <var> <prompts-dir> — replace every {{INCLUDE:<file>}} token in the value of
# <var>, and in each partial it pulls in, with the contents of <prompts-dir>/<file>.
# Returns 2, naming the path on stderr, when a named partial cannot be read.
resolve_includes() {
  local include_re='\{\{INCLUDE:([^}]*)\}\}' rest="${!1}" out="" token part
  while [[ "$rest" =~ $include_re ]]; do
    token="${BASH_REMATCH[0]}"
    part="$2/${BASH_REMATCH[1]}"
    out+="${rest%%"$token"*}"
    [[ -r "$part" ]] || { echo "missing partial: $part" >&2; return 2; }
    rest="$(cat "$part")${rest#*"$token"}"
  done
  printf -v "$1" '%s' "$out$rest"
}
