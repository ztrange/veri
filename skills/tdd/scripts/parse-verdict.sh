#!/usr/bin/env bash
# parse-verdict.sh — extract a blind verifier leaf's structured verdict from its output.
#
# A verifier leaf ends its output with a verdict block:
#
#     VERDICT: PASS | REJECT
#     REASON: <one or more lines of justification>
#
# This pure transform reads the leaf's full raw output on stdin and resolves it to a
# verdict + reason. The verdict word may appear earlier in the leaf's free-form
# reasoning, so the LAST `VERDICT:` line is the authoritative one. The reason may be
# given on a following `REASON:` line (possibly multi-line) or inline after the verdict
# word (`VERDICT: REJECT — <reason>`).
#
# Usage:   parse-verdict.sh < leaf-output.txt
#
# stdout:  the reason text (the human-facing justification), trimmed.
# exit:    0 PASS · 1 REJECT · 2 malformed/no recognisable verdict (stdout empty,
#          a diagnostic on stderr). Exit-code-as-verdict mirrors a test's own exit
#          status: the verifier's judgement is ground truth the conductor branches on.
set -euo pipefail

# Read stdin into an array of lines (bash 3.2 has no mapfile). The `|| [[ -n ... ]]`
# keeps a final line that lacks a trailing newline.
lines=()
while IFS= read -r line || [[ -n "$line" ]]; do
  lines+=( "$line" )
done

# ltrim/rtrim helpers operating on a single string value.
ltrim() { printf '%s' "${1#"${1%%[![:space:]]*}"}"; }
rtrim() { printf '%s' "${1%"${1##*[![:space:]]}"}"; }

# Find the last VERDICT: line; everything after the colon is its tail.
vidx=-1
for i in "${!lines[@]}"; do
  if [[ "${lines[$i]}" =~ ^[[:space:]]*[Vv][Ee][Rr][Dd][Ii][Cc][Tt]:[[:space:]]*(.*)$ ]]; then
    vidx=$i
  fi
done

if [[ "$vidx" -lt 0 ]]; then
  echo "parse-verdict: no VERDICT: line found" >&2
  exit 2
fi

[[ "${lines[$vidx]}" =~ ^[[:space:]]*[Vv][Ee][Rr][Dd][Ii][Cc][Tt]:[[:space:]]*(.*)$ ]]
tail="${BASH_REMATCH[1]}"

# Verdict word = first whitespace-delimited token of the tail, normalised to upper.
word="${tail%%[[:space:]]*}"
word="$(printf '%s' "$word" | tr '[:lower:]' '[:upper:]')"
case "$word" in
  PASS)   code=0 ;;
  REJECT) code=1 ;;
  *) echo "parse-verdict: unrecognised verdict word '$word'" >&2; exit 2 ;;
esac

# Inline reason = the verdict line after the word, with a leading separator stripped.
inline="${tail#"${tail%%[[:space:]]*}"}"   # drop the first (verdict) token
inline="$(ltrim "$inline")"
for sep in '—' '–' '-' ':'; do inline="${inline#"$sep"}"; done
inline="$(ltrim "$inline")"

# Following reason = the lines after the verdict line, with a leading REASON: label
# stripped from the first of them. This is the common, multi-line-capable form.
following=""
if (( vidx + 1 < ${#lines[@]} )); then
  rest=( "${lines[@]:vidx+1}" )
  if [[ "${rest[0]}" =~ ^[[:space:]]*[Rr][Ee][Aa][Ss][Oo][Nn]:[[:space:]]*(.*)$ ]]; then
    rest[0]="${BASH_REMATCH[1]}"
  fi
  printf -v following '%s\n' "${rest[@]}"
fi

# Prefer a non-empty following block; otherwise the inline reason. Trim the edges
# (including blank leader/trailer lines) but preserve internal line breaks.
reason="$following"
reason="$(rtrim "$reason")"
[[ -z "$reason" ]] && reason="$inline"
reason="$(ltrim "$reason")"
reason="$(rtrim "$reason")"

# A leaf often wraps its verdict block in a ``` (or ~~~) code fence; the opening fence
# sits above the VERDICT line and is ignored, but the closing fence trails the reason.
# Drop a trailing fence-only line so it doesn't leak into the mirrored reason.
fence_re='^[[:space:]]*(```|~~~)[[:space:]]*$'
last="${reason##*$'\n'}"
if [[ "$last" =~ $fence_re ]]; then
  if [[ "$reason" == *$'\n'* ]]; then reason="${reason%$'\n'*}"; else reason=""; fi
  reason="$(rtrim "$reason")"
fi

printf '%s\n' "$reason"
exit "$code"
