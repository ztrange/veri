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
    /^## / { inunit = (substr($0, 4) == unit); intable = 0; next }
    !inunit { next }
    /^\|[ \t]*ID[ \t]*\|/ { intable = 1; skip = 1; next }
    intable && skip { skip = 0; next }
    intable && /^\|/ {
      split($0, c, "|")
      id = trim(c[2])
      if (trim(c[3]) == "") { printf "%s:%d: empty Requirement for %s\n", file, NR, id > "/dev/stderr"; failed = 1; exit 2 }
      if (id in seen) { printf "%s:%d: duplicate ID %s\n", file, NR, id > "/dev/stderr"; failed = 1; exit 2 }
      seen[id] = 1
      rows = rows id "\t" trim(c[3]) "\n"
    }
    END { if (!failed) printf "%s", rows }
  ' "$1"
}

main() {
  case "${1:-}" in
    units) [[ $# -eq 2 ]] && { units "$2"; return; } ;;
    claims) [[ $# -eq 3 ]] && { claims "$2" "$3"; return; } ;;
  esac
  echo "usage: requirements.sh units <file> | claims <file> <unit>" >&2
  return 2
}

[[ "${BASH_SOURCE[0]}" == "$0" ]] && main "$@"
