#!/usr/bin/env bash
# Sourced by suites: fenced_lines prints "<line>\t<text>" for every line inside a ``` fence of
# <file> that matches the awk regex <pattern>; with <heading>, only fences under the ## or ###
# heading that begins with it.
# Usage: source "$HERE/lib/fenced-lines.sh"; fenced_lines <file> <pattern> [<heading>]

fenced_lines() {
  PAT="$2" HEAD="${3-}" awk '
    ENVIRON["HEAD"] != "" && /^## |^### / { inside = (index($0, ENVIRON["HEAD"]) == 1); fence = 0; next }
    ENVIRON["HEAD"] != "" && !inside { next }
    /^[[:space:]]*```/ { fence = !fence; next }
    fence && $0 ~ ENVIRON["PAT"] { printf "%d\t%s\n", NR, $0 }
  ' "$1"
}
