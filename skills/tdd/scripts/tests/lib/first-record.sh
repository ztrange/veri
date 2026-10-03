#!/usr/bin/env bash
# Sourced by suites: first_record prints the first line of <text> every <flag> <pattern> pair
# matches, or nothing; record_number prints that line's number instead.
# Usage: source "$HERE/lib/first-record.sh"
#        first_record <text> [<grep-flag> <pattern>]...
#        record_number <text> <grep-flag> <pattern>

# hazard: a `grep … | head` pipeline under pipefail can answer with grep's SIGPIPE.
first_record() {
  local text="$1"
  shift
  while [[ "$#" -gt 0 ]]; do
    text="$(grep "$1" -- "$2" <<< "$text")"
    shift 2
  done
  head -1 <<< "$text"
}

record_number() {
  local hits
  hits="$(grep -n "$2" -- "$3" <<< "$1")"
  [[ -n "$hits" ]] || return 0
  head -1 <<< "$hits" | cut -d: -f1
}
