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

source "$(cd "$(dirname "$0")" && pwd)/lib/exit-contract.sh"

# hazard: `|| [[ -n $line ]]` keeps a last line that has no trailing newline.
lines=()
while IFS= read -r line || [[ -n "$line" ]]; do
  lines+=( "$line" )
done

ltrim() { printf '%s' "${1#"${1%%[![:space:]]*}"}"; }
rtrim() { printf '%s' "${1%"${1##*[![:space:]]}"}"; }

verdict_re='^[[:space:]]*[Vv][Ee][Rr][Dd][Ii][Cc][Tt]:[[:space:]]*(.*)$'
vidx=-1
for i in "${!lines[@]}"; do
  if [[ "${lines[$i]}" =~ $verdict_re ]]; then
    vidx=$i
  fi
done

if [[ "$vidx" -lt 0 ]]; then
  echo "parse-verdict: no VERDICT: line found" >&2
  exit 2
fi

[[ "${lines[$vidx]}" =~ $verdict_re ]]
tail="${BASH_REMATCH[1]}"

word="${tail%%[[:space:]]*}"
word="$(printf '%s' "$word" | tr '[:lower:]' '[:upper:]')"
case "$word" in
  PASS)   code=0 ;;
  REJECT) code=1 ;;
  *) echo "parse-verdict: unrecognised verdict word '$word'" >&2; exit 2 ;;
esac

inline="${tail#"${tail%%[[:space:]]*}"}"   # drop the first (verdict) token
inline="$(ltrim "$inline")"
for sep in '—' '–' '-' ':'; do inline="${inline#"$sep"}"; done
inline="$(ltrim "$inline")"

following=""
if (( vidx + 1 < ${#lines[@]} )); then
  rest=( "${lines[@]:vidx+1}" )
  if [[ "${rest[0]}" =~ ^[[:space:]]*[Rr][Ee][Aa][Ss][Oo][Nn]:[[:space:]]*(.*)$ ]]; then
    rest[0]="${BASH_REMATCH[1]}"
  fi
  printf -v following '%s\n' "${rest[@]}"
fi

reason="$following"
reason="$(rtrim "$reason")"
[[ -z "$reason" ]] && reason="$inline"
reason="$(ltrim "$reason")"
reason="$(rtrim "$reason")"

fence_re='^[[:space:]]*(```|~~~)[[:space:]]*$'
last="${reason##*$'\n'}"
if [[ "$last" =~ $fence_re ]]; then
  if [[ "$reason" == *$'\n'* ]]; then reason="${reason%$'\n'*}"; else reason=""; fi
  reason="$(rtrim "$reason")"
fi

printf '%s\n' "$reason"
exit "$(to_contract "$code")"
