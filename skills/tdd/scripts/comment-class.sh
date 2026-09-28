#!/usr/bin/env bash
# comment-class.sh — print every `#` line of the given shell files as `<file>:<line>:<class>`.
#
# Usage: comment-class.sh <file>…
#
# Class 1 is a comment in code.
#
# Exit: 0 printed, 2 bad arguments.
set -uo pipefail

if (( $# == 0 )); then
  echo "usage: comment-class.sh <file>…" >&2
  exit 2
fi

awk '/^[[:space:]]*#/ { print FILENAME ":" FNR ":1" }' "$@"
