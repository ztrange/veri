#!/usr/bin/env bash
# Tests for scripts/comment-class.sh — prints every `#` line of the shell files it is given
# as `<file>:<line>:<class>`, class 1 a comment in code, 2 a `#` line in a heredoc written
# to a file, 3 one in any other heredoc.
#
# Admitted to the fast tier by its own usage count: git 0, python3 0, server 0, sleep 0.
#
# Run: scripts/tests/unit/comment-class.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
CLASSIFY="$HERE/../../comment-class.sh"
pass=0 fail=0

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

verdict() {
  if [[ -z "$problems" ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1)); echo "FAIL - $1"
    printf '%s' "$problems"
  fi
}

# 1. a comment in code, outside any heredoc, is reported with its file and line as class 1.
problems=""
f="$work/plain.sh"
printf '%s\n' 'echo one' '# a comment in code' 'echo two' > "$f"
out="$("$CLASSIFY" "$f" 2>"$work/stderr")" && code=0 || code=$?
if [[ "$code" != 0 ]]; then
  problems+="    want exit 0, got $code; stderr: $(cat "$work/stderr")"$'\n'
fi
if ! grep -E "^$f:2:1(:|$)" <<< "$out" > /dev/null; then
  problems+="    want a line '$f:2:1', got:"$'\n'"$out"$'\n'
fi
verdict "a comment in code outside any heredoc is reported as class 1 with its file and line"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
