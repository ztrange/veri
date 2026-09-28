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
    problems+="    want a line matching '$1', got:"$'\n'"$out"$'\n'
  fi
}

# 1. a comment in code, outside any heredoc, is reported with its file and line as class 1.
problems=""
f="$work/plain.sh"
printf '%s\n' 'echo one' '# a comment in code' 'echo two' > "$f"
classify "$f"
want_line "$f:2:1"
verdict "a comment in code outside any heredoc is reported as class 1 with its file and line"

# 2. a `#` line inside a heredoc is reported apart from a comment in the same file, never as class 1.
problems=""
f="$work/mixed.sh"
printf '%s\n' 'echo one' '# a comment in code' 'cat << EOF' '# a line in a heredoc' 'EOF' '# a comment after the heredoc' > "$f"
classify "$f"
want_line "$f:2:1"
want_line "$f:4:[23]"
want_line "$f:6:1"
verdict "a # line inside a heredoc is counted apart from a comment in the same file, never as class 1"

# 3. a heredoc left open at the end of one file does not carry into the next.
problems=""
f="$work/open.sh"
g="$work/after.sh"
printf '%s\n' 'cat <<EOF' '# a line in a heredoc' > "$f"
printf '%s\n' '# a comment in code' > "$g"
classify "$f" "$g"
want_line "$g:1:1"
verdict "a heredoc left open at the end of one file does not carry into the next"

# 4. a quoted or <<- heredoc delimiter opens a heredoc; a here-string <<< opens none.
problems=""
f="$work/delims.sh"
printf '%s\n' "cat <<'EOF'" '# in a single-quoted heredoc' 'EOF' 'cat <<"EOF"' '# in a double-quoted heredoc' 'EOF' \
  'cat <<-EOF' '# in a dash heredoc' $'\tEOF' 'cat <<< word' '# a comment after a here-string' > "$f"
classify "$f"
want_line "$f:2:[23]"
want_line "$f:5:[23]"
want_line "$f:8:[23]"
want_line "$f:11:1"
verdict "a # line in a quoted or <<- heredoc is never class 1, and a here-string opens no heredoc"

# 5. a `#` line in a heredoc redirected to a file is class 2; one sent to a model, a variable, stdout or stderr is class 3.
problems=""
f="$work/targets.sh"
printf '%s\n' 'cat > "$dir/fixture.txt" <<EOF' '# written to a file' 'EOF' 'claude -p <<EOF' '# sent to a model' 'EOF' \
  'prompt="$(cat <<EOF' '# held in a variable' 'EOF' ')"' 'cat <<EOF' '# printed to stdout' 'EOF' \
  'cat >&2 <<EOF' '# printed to stderr' 'EOF' > "$f"
classify "$f"
want_line "$f:2:2"
want_line "$f:5:3"
want_line "$f:8:3"
want_line "$f:12:3"
want_line "$f:15:3"
verdict "a # line in a heredoc redirected to a file is class 2, and one sent to a model, a variable, stdout or stderr is class 3"

# 6. a heredoc whose opener redirects only a file descriptor such as stderr to a file is class 3, not class 2.
problems=""
f="$work/fd-redirect.sh"
printf '%s\n' 'claude -p 2>/dev/null <<EOF' '# sent to a model with stderr discarded' 'EOF' > "$f"
classify "$f"
want_line "$f:2:3"
verdict "a heredoc sent to a command whose opener redirects only stderr to a file is class 3, not class 2"

# 7. a `#` line in a heredoc piped to a file writer such as tee is class 2.
problems=""
f="$work/piped-tee.sh"
printf '%s\n' 'cat <<EOF | tee "$dir/fixture.txt"' '# written to a file through tee' 'EOF' > "$f"
classify "$f"
want_line "$f:2:2"
verdict "a # line in a heredoc piped to tee writing a file is class 2"

# 8. a `#` line in a heredoc piped to a file writer other than tee, such as dd or sponge, is class 2.
problems=""
f="$work/piped-writers.sh"
printf '%s\n' 'cat <<EOF | dd of="$dir/fixture.txt"' '# written to a file through dd' 'EOF' \
  'cat <<EOF | sponge "$dir/fixture.txt"' '# written to a file through sponge' 'EOF' > "$f"
classify "$f"
want_line "$f:2:2"
want_line "$f:5:2"
verdict "a # line in a heredoc piped to dd or sponge writing a file is class 2"

# 9. the sweepable report lists class 1 and class 2 lines, and never a class 3 line.
problems=""
f="$work/sweepable.sh"
printf '%s\n' '# a comment in code' 'cat > "$dir/fixture.txt" <<EOF' '# written to a file' 'EOF' \
  'claude -p <<EOF' '# sent to a model' 'EOF' > "$f"
classify --sweepable "$f"
want_line "$f:1:1"
want_line "$f:3:2"
if grep -E "^$f:6(:|$)" <<< "$out" > /dev/null; then
  problems+="    want no line for $f:6, a class 3 line, got:"$'\n'"$out"$'\n'
fi
verdict "the sweepable report lists class 1 and class 2 lines and never a class 3 line"

# 10. the sweepable report omits the leading contract header and a comment marked `# hazard:`,
#     and still lists a code comment after the header.
problems=""
f="$work/header-hazard.sh"
printf '%s\n' '#!/usr/bin/env bash' '# tool.sh — print its one argument.' '#' '# Usage: tool.sh <arg>' \
  '# Exit: 0 printed, 2 bad arguments.' 'set -uo pipefail' '' \
  '# hazard: under set -u an unset name exits with the status of the previous command' 'echo "${1:-}"' > "$f"
classify --sweepable "$f"
if [[ -n "$out" ]]; then
  problems+="    want an empty sweepable report, got:"$'\n'"$out"$'\n'
fi
printf '%s\n' '# print the argument, or nothing' 'echo "${1:-}"' >> "$f"
classify --sweepable "$f"
if [[ "$out" != "$f:10:1" ]]; then
  problems+="    want only $f:10:1 once a code comment follows the header, got:"$'\n'"$out"$'\n'
fi
verdict "the sweepable report omits a leading contract header and a comment marked as a shell-hazard warning"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
