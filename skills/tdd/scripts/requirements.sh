#!/usr/bin/env bash
# requirements.sh — read a REQUIREMENTS.md.
#
# usage: requirements.sh units <file>    # each prose unit the file declares, one per line, in file order
# Exit:  0  printed
#        2  bad arguments
set -uo pipefail

units() {
  awk '
    /^## / { heading = substr($0, 4); next }
    /^\|[ \t]*ID[ \t]*\|[ \t]*Requirement[ \t]*\|[ \t]*Why[ \t]*\|/ { if (heading != "") print heading; heading = "" }
  ' "$1"
}

main() {
  if [[ $# -lt 2 || "$1" != units ]]; then
    echo "usage: requirements.sh units <file>" >&2
    return 2
  fi
  units "$2"
}

[[ "${BASH_SOURCE[0]}" == "$0" ]] && main "$@"
