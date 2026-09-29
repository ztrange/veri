#!/usr/bin/env bash
# comment-class.sh — print every `#` line of the given shell files as `<file>:<line>:<class>`.
#
# Usage: comment-class.sh [--sweepable] <file>…
#
# Class 1 is a comment in code, 2 a `#` line inside a heredoc redirected to a file or piped to tee, dd or sponge,
# 3 a `#` line inside any other heredoc, including one written to a `.md` file. --sweepable prints classes 1 and 2 only, less the comment block
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
  BEGIN { writer = "\\|[[:space:]]*(tee|dd|sponge)[[:space:]]"; name = "[A-Za-z_][A-Za-z0-9_]*" }
  function pop() { q = substr(q, 1, length(q) - 1) }
  function scan(s,   i, c, t) {
    for (i = 1; i <= length(s); i++) {
      c = substr(s, i, 1); t = substr(q, length(q))
      if (t == "\047") { if (c == "\047") pop(); continue }
      if (c == "\\") { i++; continue }
      if (t == "\"") {
        if (c == "\"") pop()
        else if (c == "$" && substr(s, i + 1, 1) == "(") { q = q "("; i++ }
        continue
      }
      if (t == "(" && c == ")") { pop(); continue }
      if (t == "(" && c == "(") { q = q "("; continue }
      if (c == "#" && substr(s, i - 1, 1) ~ /[[:space:]]/) return
      if (c == "\047" || c == "\"") q = q c
    }
  }
  FNR == 1 { delim = ""; q = ""; header = /^#!/ }
  { comment = /^[[:space:]]*#/ }
  !comment { header = 0 }
  delim != "" {
    end = $0
    if (dash) sub(/^\t+/, "", end)
    if (end == delim) delim = ""
    else if (comment && !(sweepable && (cls == 3 || (body && end ~ /^#!/)))) print FILENAME ":" FNR ":" cls
    body = 0
    next
  }
  q != "" { scan($0); next }
  comment {
    if (!(sweepable && (header || /^[[:space:]]*# hazard:/))) print FILENAME ":" FNR ":1"
    next
  }
  { scan($0); line = $0; gsub(/<<</, "", line) }
  match(line, name "=[^[:space:];]*\\.md[\"\047]?([[:space:];]|$)") {
    v = substr(line, RSTART, RLENGTH); sub(/=.*/, "", v); mdvar[v] = 1
  }
  match(line, "<<-?[[:space:]]*[\"\047]?" name) {
    out = line; gsub(/[02-9]>+[[:space:]]*[^[:space:]]*/, "", out)
    cls = out ~ />[[:space:]]*[^&[:space:]]/ || out ~ writer ? 2 : 3
    if (out ~ "(>|" writer "[^|]*)[[:space:]]*[^&|[:space:]]*\\.md[\"\047]?([[:space:]]|$)") cls = 3
    delim = substr(line, RSTART + 2, RLENGTH - 2)
    dash = delim ~ /^-/
    body = 1
    sub(/^-?[[:space:]]*["'\'']?/, "", delim)
    if (match(out, ">[[:space:]]*\"?\\$" name)) {
      v = substr(out, RSTART, RLENGTH); sub(/^>[[:space:]]*"?\$/, "", v)
      if (v in mdvar) cls = 3
    }
  }
' "$@"
