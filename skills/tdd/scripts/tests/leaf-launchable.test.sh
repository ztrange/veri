#!/usr/bin/env bash
# Unit tests for scripts/leaf-launchable.sh — the preflight check that a leaf can actually
# be LAUNCHED, beside the `claude auth status` check SKILL.md preflight 0.2 already makes
# and for the same reason: a fault that makes every leaf die at launch is neither a verdict
# nor a hang, so it has no bail classification and has to be caught before a cycle starts
# (issue #187).
# Zero-dependency plain-shell asserts, same idiom as leaf-role.test.sh.
#
# Why this exists: a `/tdd <n>` run driven from inside an interactive Claude Code session
# passed preflight in full — clean tree, both CLIs authenticated, a 93 s green baseline, a
# worktree entered, the spec written, a resume comment posted to the issue thread — and then
# lost its first leaf to the binary's own refusal. The cost of missing it is that whole
# prologue, paid for a run that cannot take a single step.
#
# The question is asked of the CAPABILITY, not of one variable's name: the check launches
# the leaf binary and reads what happened. `CLAUDECODE` was the known cause on 2026-09-14
# and, as of 2026-09-15, the binary no longer refuses on it — so a check spelled as "is
# CLAUDECODE set" would today refuse a configuration that works, and would still miss the
# next guard of the same kind. Every probe here therefore runs with `env -u CLAUDECODE`:
# the refusal it pins is owed to the probe launch failing, and to nothing about the
# environment the suite was called from.
#
# Contract under test (this step only — the refusal, not the passing path and not what the
# conductor does with it):
#   leaf-launchable.sh, with the leaf binary failing
#                             → exit 2, nothing on stdout, and a diagnostic on stderr that
#                               names the cause (what the binary said) and the supported
#                               invocation (a plain shell, `claude -p "/tdd <n>"`).
#
# Exit 2 rather than 1: "no answer could be obtained" — the plumbing broke and no leaf can
# run — not a clean negative any caller could act on. Nothing on stdout because a preflight
# check that printed its refusal there would be captured by a conductor reading it in a
# command substitution.
#
# `CLAUDE_BIN` is the injection seam run-leaf.sh already reads (run-leaf.sh:56), so the
# stub below is the same swap every other suite makes to keep a real model off the wire.
#
# Run: scripts/tests/leaf-launchable.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
LAUNCHABLE="$HERE/../leaf-launchable.sh"
pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output says which obligation the refusal missed rather than just that the case did.
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

# The line the real binary printed on 2026-09-14, written down once: the stub prints it and
# the probe below looks for it in the diagnostic. Quoting what the binary said is what makes
# the check one about the capability — a fixed message of its own would name a cause the
# script had guessed rather than the one it observed.
binary_said='Error: Claude Code cannot be launched inside another Claude Code session.'

# The supported invocation, in the words the diagnostic owes an operator who is reading it
# from inside their own session. A prefix, not the whole line: what follows `/tdd` is the
# issue number's placeholder and how that is spelled is the diagnostic's to choose.
supported='claude -p "/tdd'

# failing_stub — a `claude` that cannot launch, whatever it is asked. Printed on stderr
# because that is where the real binary puts it, and the arguments are ignored on purpose:
# which probe launch the script makes is its own to decide, and pinning it here would make
# that choice a test failure.
failing_stub() {
  local bin="$1"
  cat > "$bin" <<STUB
#!/usr/bin/env bash
printf '%s\n' '$binary_said' >&2
printf '%s\n' 'Nested sessions share runtime resources and will crash all active sessions.' >&2
exit 1
STUB
  chmod +x "$bin"
}

# 1. The refusal itself. `env -u CLAUDECODE` for the reason in the header: the cause under
#    test is the failing launch, so the variable that once caused it is cleared, and a check
#    written as a test of that name answers "launchable" here and fails this case.
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

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
