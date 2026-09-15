#!/usr/bin/env bash
# Tests for scripts/run-conductor.sh — the CONDUCTOR invocation, driven against a stub
# `claude` on PATH (no real subprocess, no model call), the way run-leaf.test.sh drives the
# leaf one. Same stub, same seam: `CLAUDE_BIN` swaps the binary and the stub records its
# argv to $ARGV_OUT.
#
# Why this exists (issue #207): a conductor typed as `/tdd <n>` into an interactive session
# is an interactive chat session, and pays ~25,000 tokens a request — measured across 1,481
# conductor requests, median first-request context 53,438 against a bare `claude -p` floor
# of 28,321 in this repo — for a harness surface it never touches: the skills roster, the
# full tool schemas, the interactive system prompt. Everything a conductor does is Bash,
# Read, Write, Edit and `gh`; it invokes no skill, because it *is* the skill. run-conductor.sh
# is the conductor-level counterpart of run-leaf.sh: one conductor, one `claude -p`
# subprocess.
#
# Contract under test (this step only):
#   `run-conductor.sh <issue>` launches the conductor binary in print mode — `-p` — with
#   `--output-format stream-json --verbose`, and the issue it was asked for reaches the
#   prompt that launch carries.
#
# Why the stream flags are part of the criterion and not a detail of how it is spelled:
# print mode's default output format stays SILENT until the conductor finishes, so a run
# that takes an hour is indistinguishable from one that died in its first minute — the same
# reason run-leaf.sh:11-18 gives for a leaf. A conductor launched without them is a
# conductor nobody can watch, which is why the step says "with a streamed event output"
# rather than just "as `claude -p`".
#
# Not asked here: that the eight inherited session handles are absent from the child's
# environment and `VERI_*` is not, that the child's exit status is the script's, and what
# SKILL.md says about the two launch modes. Those are this issue's later steps.
#
# Run: scripts/tests/run-conductor.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
CONDUCTOR="$HERE/../run-conductor.sh"
pass=0 fail=0

# The issue asked for. A number nothing else in an argv would carry, so a probe that finds
# it has found the one this script was given and not a version, a budget or a port.
issue=4242

stubdir="$(mktemp -d)"
work="$(mktemp -d)"
trap 'rm -rf "$stubdir" "$work"' EXIT

# The stub `claude`: records its argv one argument per line to $ARGV_OUT, emits a minimal
# stream-json stream, and exits 0. Same shape as run-leaf.test.sh's.
cat > "$stubdir/claude" <<'STUB'
#!/usr/bin/env bash
printf '%s\n' "$@" > "$ARGV_OUT"
printf '%s\n' '{"type":"system","subtype":"init","session_id":"x"}'
printf '%s\n' '{"type":"result","subtype":"success","is_error":false,"result":"ok"}'
exit 0
STUB
chmod +x "$stubdir/claude"

argv="$work/argv"

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output names the flag that is missing rather than just saying the launch was wrong.
# Same helper, same shape, as hermetic-suites.test.sh's.
report() {
  local name="$1"
  if [[ "${#problems[@]}" -eq 0 ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1))
    echo "FAIL - $name"
    printf '    %s\n' "${problems[@]}"
  fi
}

# flag <name> — the launch carried <name> as an argument of its own. Whole lines, because
# the stub writes one argument per line: a substring match would accept `--verbose` found
# inside a prompt that merely mentions it.
flag() {
  grep -qx -- "$1" "$argv" ||
    problems+=("the launch does not carry $1")
}

# valued <flag> <value> — <flag> was passed with <value> as the argument right after it,
# which is what `claude` reads and what a bare `grep` for the two words separately cannot
# tell from them landing at opposite ends of the command line.
valued() {
  grep -A1 -x -- "$1" "$argv" | grep -qx -- "$2" ||
    problems+=("the launch does not carry $1 $2")
}

# 1. The criterion: one conductor, launched as `claude -p` for the issue, streaming events.
name="run-conductor.sh <issue> launches claude -p for that issue in stream-json"
problems=()

( cd "$work" && env PATH="$stubdir:$PATH" ARGV_OUT="$argv" \
    "$CONDUCTOR" "$issue" ) >/dev/null 2>&1

# Fail closed: no argv file means the stub was never reached, so every probe below would be
# reading a file that does not exist and reporting four problems for one. One says it.
if [[ ! -f "$argv" ]]; then
  problems+=("the conductor binary was never launched — $CONDUCTOR recorded no argv")
else
  flag -p
  valued --output-format stream-json
  flag --verbose
  grep -q -- "$issue" "$argv" ||
    problems+=("issue $issue does not reach the prompt the launch carries")
fi

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
