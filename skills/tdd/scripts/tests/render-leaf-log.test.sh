#!/usr/bin/env bash
# Unit tests for scripts/render-leaf-log.sh — turn a leaf's `claude -p --output-format
# stream-json` log (`.tdd/<leaf>.out`) into the readable lines the dashboard's Chatter pane
# shows.
#
# Contract under test:
#   <assistant text>                  what the leaf said
#   > <tool>: <first input line>      a tool call, with the first line of its input
#   < <tool result>                   the result, cut to its first line and 80 characters,
#                                     with `…` marking that something was cut
#   anything else                     the system init, thinking blocks, the terminal result
#                                     record — prints nothing
#
# Run: scripts/tests/render-leaf-log.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
RENDER="$HERE/../render-leaf-log.sh"
FIXTURES="$HERE/fixtures/render-leaf-log"
source "$HERE/lib/harness.sh"
check() {  # check <name> <fixture> <expected-stdout>
  local name="$1" fixture="$2" exp="$3" out
  out="$("$RENDER" < "$fixture" 2>&1)"
  if [[ "$out" == "$exp" ]]; then ok; else
    no "$name"
    diff <(printf '%s\n' "$exp") <(printf '%s\n' "$out") | sed 's/^/    /'
  fi
}

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

render_after_bad_line() {  # render_after_bad_line — the renderer's own stdout, stderr and status
  printf '%s\n' '{"type":"assistant","message":{"content":[{"type":"text","text":"hi"}]}}' \
    'not json at all' | "$RENDER"
}

name="exits 2 on a line that is not JSON"
render_after_bad_line >/dev/null 2>&1
rc=$?
if [[ "$rc" -eq 2 ]]; then ok; else
  no "$name"
  echo "    expected exit 2, got $rc"
fi

name="a JSON line that is not an object exits 2, and an extra argument is ignored with the stdin still rendered and exit 0"
printf '%s\n' '[1, 2]' | "$RENDER" >/dev/null 2>&1
array_code=$?
extra="$("$RENDER" extra-arg < "$FIXTURES/leaf.out" 2>&1)"; extra_code=$?
plain="$("$RENDER" < "$FIXTURES/leaf.out" 2>&1)"
if [[ "$array_code" -eq 2 && "$extra_code" -eq 0 && "$extra" == "$plain" && "$extra" == *"> Bash: make test"* ]]; then ok; else
  no "$name"
  echo "    non-object exit: expected 2, got $array_code; extra-argument exit: expected 0, got $extra_code"
  diff <(printf '%s\n' "$plain") <(printf '%s\n' "$extra") | sed 's/^/    /'
fi

work="$(scratch_dir)"
ln -s "$(cd "$HERE/../.." && pwd)" "$work/linked-skill"
mkdir -p "$work/elsewhere"
in_place="$("$RENDER" < "$FIXTURES/leaf.out" 2>&1)"; in_place_code=$?
linked="$(cd "$work/elsewhere" && "$work/linked-skill/scripts/render-leaf-log.sh" < "$FIXTURES/leaf.out" 2>&1)"; linked_code=$?
if [[ "$linked" == "$in_place" && "$linked_code" -eq "$in_place_code" && "$in_place" == *"> Bash: make test"* ]]; then ok; else
  no "render-leaf-log.sh run through a symlink to the skill directory and from another working directory renders as it does when run in place"
  diff <(printf '%s\nexit %s\n' "$in_place" "$in_place_code") <(printf '%s\nexit %s\n' "$linked" "$linked_code")
fi

finish
