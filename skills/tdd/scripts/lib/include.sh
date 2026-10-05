#!/usr/bin/env bash
# lib/include.sh — sourced, not run: defines `resolve_includes`.
#
# resolve_includes <var> <prompts-dir> — replace every {{INCLUDE:<file>}} token in the value of
# <var>, and in each partial it pulls in, with the contents of <prompts-dir>/<file>.
# Returns 2, naming the path on stderr, when a named partial cannot be read or includes itself.
resolve_includes() {
  local _include_out
  _include_expand "${!1}" "$2" "" || return 2
  printf -v "$1" '%s' "$_include_out"
}

_include_expand() {
  local include_re='\{\{INCLUDE:([^}]*)\}\}' rest="$1" out="" token part
  while [[ "$rest" =~ $include_re ]]; do
    token="${BASH_REMATCH[0]}"
    part="$2/${BASH_REMATCH[1]}"
    out+="${rest%%"$token"*}"
    rest="${rest#*"$token"}"
    [[ -r "$part" ]] || { echo "missing partial: $part" >&2; return 2; }
    case $'\n'"$3"$'\n' in
      *$'\n'"$part"$'\n'*) echo "partial includes itself: $part" >&2; return 2 ;;
    esac
    _include_expand "$(cat "$part")" "$2" "$3"$'\n'"$part" || return 2
    out+="$_include_out"
  done
  _include_out="$out$rest"
}
