#!/usr/bin/env bash
# comment-class.sh — print every `#` line of the given shell files as `<file>:<line>:<class>`.
#
# Usage: comment-class.sh [--sweepable] <file>…
#
# Class 1 is a comment in code, 2 a `#` line inside a heredoc redirected to a file or piped to tee, dd or sponge,
# 3 a `#` line inside any other heredoc. --sweepable prints classes 1 and 2 only.
#
# Exit: 0 printed, 2 bad arguments.
set -uo pipefail

sweepable=0
if [[ "${1:-}" == --sweepable ]]; then
  sweepable=1
  shift
fi

if (( $# == 0 )); then
  echo "usage: comment-class.sh [--sweepable] <file>…" >&2
  exit 2
fi

awk -v sweepable="$sweepable" '
  FNR == 1 { delim = "" }
  delim != "" {
    end = $0
    if (dash) sub(/^\t+/, "", end)
    if (end == delim) delim = ""
    else if ($0 ~ /^[[:space:]]*#/ && !(sweepable && cls == 3)) print FILENAME ":" FNR ":" cls
    next
  }
  /^[[:space:]]*#/ { print FILENAME ":" FNR ":1"; next }
  { line = $0; gsub(/<<</, "", line) }
  match(line, /<<-?[[:space:]]*["'\'']?[A-Za-z_][A-Za-z0-9_]*/) {
    out = line; gsub(/[02-9]>+[[:space:]]*[^[:space:]]*/, "", out)
    cls = out ~ />[[:space:]]*[^&[:space:]]/ || out ~ /\|[[:space:]]*(tee|dd|sponge)[[:space:]]/ ? 2 : 3
    delim = substr(line, RSTART + 2, RLENGTH - 2)
    dash = delim ~ /^-/
    sub(/^-?[[:space:]]*["'\'']?/, "", delim)
  }
' "$@"
