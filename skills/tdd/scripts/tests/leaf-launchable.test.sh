#!/usr/bin/env bash
# Unit tests for scripts/leaf-launchable.sh — the preflight check that a leaf can actually
# be LAUNCHED (issue #187).
# Zero-dependency plain-shell asserts, same idiom as leaf-role.test.sh.
#
# Why the check exists, why it probes the capability instead of testing one variable's name,
# and why its refusal is exit 2 with an empty stdout are all said in its header
# (leaf-launchable.sh:4-22), once.
#
# What follows from that here: every probe below runs with `env -u CLAUDECODE`. The cause
# under test is the probe launch failing, so the variable that once caused it is cleared —
# a check written as a test of that name answers "launchable" under these cases and fails
# them.
#
# Contract under test (the script's own answer, not what the conductor does with it):
#   leaf-launchable.sh, with the leaf binary failing
#                             → exit 2, nothing on stdout, and a diagnostic on stderr that
#                               names the cause (what the binary said) and the supported
#                               invocation (a plain shell, `claude -p "/tdd <n>"`).
#                             → and nothing else happens: no worktree created, no spec
#                               written, no test command run, no issue comment posted.
#   leaf-launchable.sh, with the leaf binary launching
#                             → exit 0 and both streams empty: the healthy run, which is
#                               every run, observes nothing of the check at all.
#
# `CLAUDE_BIN` is the seam the stub below is injected through, the same swap every other
# suite makes to keep a real model off the wire.
#
# Run: scripts/tests/leaf-launchable.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
LAUNCHABLE="$HERE/../leaf-launchable.sh"

source "$HERE/lib/harness.sh"

binary_said='Error: Claude Code cannot be launched inside another Claude Code session.'

supported='claude -p "/tdd'

failing_stub() {
  local bin="$1"
  cat > "$bin" <<STUB
#!/bin/sh
printf '%s\n' '$binary_said' >&2
printf '%s\n' 'Nested sessions share runtime resources and will crash all active sessions.' >&2
exit 1
STUB
  chmod +x "$bin"
}

name='leaf-launchable.sh refuses when the leaf binary cannot launch — exit 2, nothing on stdout, a diagnostic on stderr naming the cause and the supported invocation'
problems=()
tmp="$(mktemp -d)"
failing_stub "$tmp/claude"
out="$tmp/out" err="$tmp/err"
env -u CLAUDECODE CLAUDE_BIN="$tmp/claude" "$LAUNCHABLE" >"$out" 2>"$err" && code=0 || code=$?
err_text="$(cat "$err")" out_text="$(cat "$out")"
[[ "$code" == 2 ]] ||
  problems+=("want exit 2, got $code")
[[ -z "$out_text" ]] ||
  problems+=("want nothing on stdout, got: $(printf '%q' "$out_text")")
[[ "$err_text" == *"$binary_said"* ]] ||
  problems+=("want the cause on stderr — $(printf '%q' "$binary_said") — got: $(printf '%q' "$err_text")")
[[ "$err_text" == *"$supported"* ]] ||
  problems+=("want the supported invocation on stderr — $(printf '%q' "$supported") — got: $(printf '%q' "$err_text")")
rm -rf "$tmp"
report "$name"

name='leaf-launchable.sh refuses without a side effect — no worktree, no spec, no test command, no issue comment'
problems=()
tmp="$(mktemp -d)"
failing_stub "$tmp/claude"

stubdir="$tmp/bin"
mkdir -p "$stubdir"
for shim in git gh make; do
  cat > "$stubdir/$shim" <<STUB
#!/bin/sh
printf '%s\n' "$shim \$*" >> "\$ARGV_OUT"
STUB
  chmod +x "$stubdir/$shim"
done

work="$tmp/work"
mkdir -p "$work"
argv="$tmp/argv"
: > "$argv"

( cd "$work" && env -u CLAUDECODE PATH="$stubdir:$PATH" ARGV_OUT="$argv" \
    CLAUDE_BIN="$tmp/claude" "$LAUNCHABLE" >/dev/null 2>/dev/null ) && code=0 || code=$?
called="$(cat "$argv")"
left_behind="$(cd "$work" && ls -A)"

[[ "$code" == 2 ]] ||
  problems+=("want the refusal (exit 2) to be what this case observed, got exit $code")
[[ -z "$called" ]] ||
  problems+=("want no worktree, no issue comment and no test command — want nothing called, got: $(printf '%q' "$called")")
[[ -z "$left_behind" ]] ||
  problems+=("want no spec written — want the run directory still empty, got: $(printf '%q' "$left_behind")")
rm -rf "$tmp"
report "$name"

name='leaf-launchable.sh passes when the leaf binary launches — exit 0, nothing on stdout, nothing on stderr'
problems=()
tmp="$(mktemp -d)"
cat > "$tmp/claude" <<'STUB'
#!/bin/sh
printf '%s\n' '1.2.3 (Claude Code)'
printf '%s\n' 'some chatter the probe did not ask for' >&2
exit 0
STUB
chmod +x "$tmp/claude"
out="$tmp/out" err="$tmp/err"
env -u CLAUDECODE CLAUDE_BIN="$tmp/claude" "$LAUNCHABLE" >"$out" 2>"$err" && code=0 || code=$?
err_text="$(cat "$err")" out_text="$(cat "$out")"
[[ "$code" == 0 ]] ||
  problems+=("want exit 0, got $code")
[[ -z "$out_text" ]] ||
  problems+=("want nothing on stdout, got: $(printf '%q' "$out_text")")
[[ -z "$err_text" ]] ||
  problems+=("want nothing on stderr, got: $(printf '%q' "$err_text")")
rm -rf "$tmp"
report "$name"

finish
