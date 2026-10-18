#!/usr/bin/env bash
# requirements.sh — read a REQUIREMENTS.md.
#
# usage: requirements.sh units <file>    # each prose unit the file declares, one per line, in file order
#        requirements.sh claims <file> <unit>    # the unit's rows as ID<TAB>Requirement, Why omitted
# Exit:  0  printed
#        2  bad arguments, or a table that does not parse (stderr names the line)
set -uo pipefail

units() {
  awk '
    /^## / { heading = substr($0, 4); next }
    /^\|[ \t]*ID[ \t]*\|[ \t]*Requirement[ \t]*\|[ \t]*Why[ \t]*\|/ { if (heading != "") print heading; heading = "" }
  ' "$1"
}

claims() {
  awk -v unit="$2" -v file="$1" '
    function trim(s) { gsub(/^[ \t]+|[ \t]+$/, "", s); return s }
    function fail(msg) { printf "%s:%d: %s\n", file, NR, msg > "/dev/stderr"; failed = 1; exit 2 }
    /^## / { inunit = (substr($0, 4) == unit); intable = 0; next }
    !inunit { next }
    /^\|[ \t]*ID[ \t]*\|/ {
      split($0, h, "|")
      if (trim(h[3]) != "Requirement" || trim(h[4]) != "Why") fail("header lacks a column")
      intable = 1; skip = 1; next
    }
    intable && skip { skip = 0; next }
    intable && /^\|/ {
      split($0, c, "|")
      id = trim(c[2])
      if (id == "") fail("empty ID")
      if (trim(c[3]) == "") fail("empty Requirement for " id)
      if (id in seen) fail("duplicate ID " id)
      seen[id] = 1
      rows = rows id "\t" trim(c[3]) "\n"
    }
    END { if (!failed) printf "%s", rows }
  ' "$1"
}

main() {
  case "${1:-}" in
    units) [[ $# -eq 2 ]] && { units "$2"; return; } ;;
    claims)
      if [[ $# -eq 3 ]]; then
        [[ -f "$2" ]] || { echo "requirements.sh: file is missing: $2" >&2; return 2; }
        local text; text=$'\n'"$(< "$2")"$'\n'
        [[ "$text" == *$'\n## '"$3"$'\n'* ]] || { echo "requirements.sh: unit is not declared: $3" >&2; return 2; }
        claims "$2" "$3"; return
      fi ;;
  esac
  echo "usage: requirements.sh units <file> | claims <file> <unit>" >&2
  return 2
}

[[ "${BASH_SOURCE[0]}" == "$0" ]] && main "$@"
