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
# Contract under test (this step only — the refusal, not the passing path and not what the
# conductor does with it):
#   leaf-launchable.sh, with the leaf binary failing
#                             → exit 2, nothing on stdout, and a diagnostic on stderr that
#                               names the cause (what the binary said) and the supported
#                               invocation (a plain shell, `claude -p "/tdd <n>"`).
#
# `CLAUDE_BIN` is the seam the stub below is injected through, the same swap every other
# suite makes to keep a real model off the wire.
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

# 1. The refusal itself, with `env -u CLAUDECODE` for the reason the header gives.
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
