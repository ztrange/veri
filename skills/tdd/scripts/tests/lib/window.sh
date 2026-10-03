#!/usr/bin/env bash
# Sourced by suites: windows prints one context window per occurrence of an ERE, one per line;
# window prints the first.
# Usage: source "$HERE/lib/window.sh"; windows <text> <pattern> [radius, default 250]
# Each window is up to <radius> characters either side of its match, within the match's line,
# so an occurrence inside another's window still gets a window of its own. Returns 0.

windows() {
  local pattern="$2" radius="${3:-250}" line rest match before at from
  while IFS= read -r line; do
    rest="$line"
    at=0
    while [[ "$rest" =~ $pattern ]]; do
      match="${BASH_REMATCH[0]}"
      before="${rest%%"$match"*}"
      at=$((at + ${#before}))
      from=$((at > radius ? at - radius : 0))
      printf '%s\n' "${line:from:at - from + ${#match} + radius}"
      at=$((at + ${#match}))
      [[ -z "$match" ]] && at=$((at + 1))
      ((at > ${#line})) && break
      rest="${line:at}"
    done
  done <<<"$1"
  return 0
}

window() {
  local first
  first="$(windows "$@")"
  printf '%s\n' "${first%%$'\n'*}"
}
