#!/usr/bin/env bash
# Unit tests for scripts/render-leaf-log.sh — turn a leaf's `claude -p --output-format
# stream-json` log (`.tdd/<leaf>.out`) into the readable lines the dashboard's Chatter pane
# shows (issue #255). One line per thing said or done:
#
#   <assistant text>                  what the leaf said
#   > <tool>: <first input line>      a tool call, with the first line of its input
#   < <tool result>                   the result, cut to its first line and 80 characters,
#                                     with `…` marking that something was cut
#
# Events that are neither — the system init, thinking blocks, the terminal result record —
# print nothing.
#
# Run: scripts/tests/render-leaf-log.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
RENDER="$HERE/../render-leaf-log.sh"
FIXTURES="$HERE/fixtures/render-leaf-log"
pass=0 fail=0
check() {  # check <name> <fixture> <expected-stdout>
  local name="$1" fixture="$2" exp="$3" out
  out="$("$RENDER" < "$fixture" 2>&1)"
  if [[ "$out" == "$exp" ]]; then pass=$((pass + 1)); else
    fail=$((fail + 1)); echo "FAIL - $name"
    diff <(printf '%s\n' "$exp") <(printf '%s\n' "$out") | sed 's/^/    /'
  fi
}

# 1. a captured leaf log renders as assistant text, each tool call's name and first input
#    line, and a truncated tool result — one per line
check "renders text, tool calls and truncated results one per line" \
"$FIXTURES/leaf.out" \
'Reading the suite before adding the case.
> Bash: cat skills/tdd/scripts/tests/extract-result.test.sh
< #!/usr/bin/env bash…
> Read: /repo/README.md
< # veri — a Claude Code skill suite that solves one GitHub issue under strict TDD…
> Bash: make test
< 3 passed, 0 failed
The case is added and fails as predicted.'

# 2. a line that is not JSON is no answer the renderer can give — exit 2, not a traceback's 1
name="exits 2 on a line that is not JSON"
printf '%s\n' '{"type":"assistant","message":{"content":[{"type":"text","text":"hi"}]}}' \
  'not json at all' | "$RENDER" >/dev/null 2>&1
rc=$?
if [[ "$rc" -eq 2 ]]; then pass=$((pass + 1)); else
  fail=$((fail + 1)); echo "FAIL - $name"
  echo "    expected exit 2, got $rc"
fi

# 3. the header's account of a line that is not JSON says what the script does with the
#    records BEFORE it: they are discarded too, because the accumulated output is written
#    only after the loop that exit leaves. "no rendering can be given" alone leaves a reader
#    to guess whether the pane gets what the script managed — it gets nothing (#384).
name="the header says a non-JSON line discards the records already rendered"
header="$(sed -n '2,/^set -euo pipefail$/p' "$RENDER" | sed -n 's/^#[[:space:]]\{0,1\}//p')"
rendered_before="$(printf '%s\n' \
  '{"type":"assistant","message":{"content":[{"type":"text","text":"hi"}]}}' \
  'not json at all' | "$RENDER" 2>/dev/null)"
if [[ -n "$rendered_before" ]]; then
  fail=$((fail + 1)); echo "FAIL - $name"
  echo "    expected the script to print nothing, got: $rendered_before"
elif grep -qE 'discard|throw[sn]? away|already rendered|records before it' <<< "$header"; then
  pass=$((pass + 1))
else
  fail=$((fail + 1)); echo "FAIL - $name"
  echo "    the header never says the records already rendered are discarded:"
  grep -n 'not JSON' <<< "$header" | sed 's/^/    /'
fi

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
