#!/usr/bin/env bash
# comment-class.sh — print every `#` line of the given shell files as `<file>:<line>:<class>`.
#
# Usage: comment-class.sh [--sweepable] <file>…
#
# Class 1 is a comment in code, 2 a `#` line inside a heredoc redirected to a file or piped to tee, dd or sponge,
# 3 a `#` line inside any other heredoc. --sweepable prints classes 1 and 2 only, less the comment block
# after a leading `#!` line, a `#!` line opening a heredoc's body and any comment starting `# hazard:`.
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
  function scan(s,   i, c) {
    for (i = 1; i <= length(s); i++) {
      c = substr(s, i, 1)
      if (q == "\047") { if (c == "\047") q = ""; continue }
      if (c == "\\") { i++; continue }
      if (q == "\"") { if (c == "\"") q = ""; continue }
      if (c == "#" && substr(s, i - 1, 1) ~ /[[:space:]]/) return
      if (c == "\047" || c == "\"") q = c
    }
  }
  FNR == 1 { delim = ""; q = ""; header = /^#!/ }
  { comment = /^[[:space:]]*#/ }
  !comment { header = 0 }
  delim != "" {
    end = $0
    if (dash) sub(/^\t+/, "", end)
    if (end == delim) delim = ""
    else if (comment && !(sweepable && (cls == 3 || (body && /^#!/)))) print FILENAME ":" FNR ":" cls
    body = 0
    next
  }
  q != "" { scan($0); next }
  comment {
    if (!(sweepable && (header || /^[[:space:]]*# hazard:/))) print FILENAME ":" FNR ":1"
    next
  }
  { scan($0); line = $0; gsub(/<<</, "", line) }
  match(line, /<<-?[[:space:]]*["'\'']?[A-Za-z_][A-Za-z0-9_]*/) {
    out = line; gsub(/[02-9]>+[[:space:]]*[^[:space:]]*/, "", out)
    cls = out ~ />[[:space:]]*[^&[:space:]]/ || out ~ /\|[[:space:]]*(tee|dd|sponge)[[:space:]]/ ? 2 : 3
    delim = substr(line, RSTART + 2, RLENGTH - 2)
    dash = delim ~ /^-/
    body = 1
    sub(/^-?[[:space:]]*["'\'']?/, "", delim)
  }
' "$@"
