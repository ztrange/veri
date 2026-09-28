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

classify() {
  out="$("$CLASSIFY" "$@" 2>"$work/stderr")" && code=0 || code=$?
  if [[ "$code" != 0 ]]; then
    problems+="    want exit 0, got $code; stderr: $(cat "$work/stderr")"$'\n'
  fi
}

want_line() {
  if ! grep -E "^$1(:|$)" <<< "$out" > /dev/null; then
    problems+="    $2, got:"$'\n'"$out"$'\n'
  fi
}

# 1. a comment in code, outside any heredoc, is reported with its file and line as class 1.
problems=""
f="$work/plain.sh"
printf '%s\n' 'echo one' '# a comment in code' 'echo two' > "$f"
classify "$f"
want_line "$f:2:1" "want a line '$f:2:1'"
verdict "a comment in code outside any heredoc is reported as class 1 with its file and line"

# 2. a `#` line inside a heredoc is reported apart from a comment in the same file, never as class 1.
problems=""
f="$work/mixed.sh"
printf '%s\n' 'echo one' '# a comment in code' 'cat << EOF' '# a line in a heredoc' 'EOF' '# a comment after the heredoc' > "$f"
classify "$f"
want_line "$f:2:1" "want a line '$f:2:1'"
want_line "$f:4:[23]" "want line 4 reported as class 2 or 3"
want_line "$f:6:1" "want a line '$f:6:1' once the heredoc closes"
verdict "a # line inside a heredoc is counted apart from a comment in the same file, never as class 1"

# 3. a heredoc left open at the end of one file does not carry into the next.
problems=""
f="$work/open.sh"
g="$work/after.sh"
printf '%s\n' 'cat <<EOF' '# a line in a heredoc' > "$f"
printf '%s\n' '# a comment in code' > "$g"
classify "$f" "$g"
want_line "$g:1:1" "want a line '$g:1:1'"
verdict "a heredoc left open at the end of one file does not carry into the next"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
