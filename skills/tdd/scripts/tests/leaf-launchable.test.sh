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
#!/bin/sh
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

# 2. The refusal's cost. A preflight-class stop is one a run pays nothing for, so the
# obligation is stated as what did NOT happen rather than as what did: the four things the
# prologue of a run does — enter a worktree, write the spec, run the baseline suite, post a
# `### ▶️ Resuming` comment to the issue thread — are exactly what #187 observed a run doing
# before it died at its first leaf.
#
# Three of them are observable as a process this script never starts, and the fourth as a
# file it never leaves behind, so the case watches for both: `git`, `gh` and `make` are
# shimmed onto PATH ahead of the real ones and record every call, and the script runs in an
# empty directory of its own that is read back afterwards. A recorder that records nothing
# and a directory that is still empty is the whole assertion.
#
# The shims are named rather than derived: these are the three binaries every side effect in
# the list above goes through — `git worktree add`, `gh issue comment`, and the run's test
# command, which in this repository is `make test`.
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

# The cwd the script is run from, empty at the start: a spec written relative to the run's
# directory — which is how write-spec.sh puts one there — lands here and is read back below.
work="$tmp/work"
mkdir -p "$work"
argv="$tmp/argv"
: > "$argv"

( cd "$work" && env -u CLAUDECODE PATH="$stubdir:$PATH" ARGV_OUT="$argv" \
    CLAUDE_BIN="$tmp/claude" "$LAUNCHABLE" >/dev/null 2>/dev/null ) && code=0 || code=$?
called="$(cat "$argv")"
left_behind="$(cd "$work" && ls -A)"

# The refusal is this case's premise, not its claim: a probe that came back some other way
# would make the two checks below true of a path nobody took.
[[ "$code" == 2 ]] ||
  problems+=("want the refusal (exit 2) to be what this case observed, got exit $code")
[[ -z "$called" ]] ||
  problems+=("want no worktree, no issue comment and no test command — want nothing called, got: $(printf '%q' "$called")")
[[ -z "$left_behind" ]] ||
  problems+=("want no spec written — want the run directory still empty, got: $(printf '%q' "$left_behind")")
rm -rf "$tmp"
report "$name"

# 3. The passing path: a leaf binary that launches. This is the case for the run that has
# nothing wrong with it, which is every run, so what it pins is that the check costs such a
# run nothing it can observe — exit 0, and both streams empty. Silence on stdout is the
# script's stated contract (a conductor reading it in a command substitution captures
# nothing); silence on stderr is the same obligation one step further, since a diagnostic
# printed on the healthy path is a preflight that cries wolf every run.
#
# The stub prints on both streams before succeeding, the way the real binary prints a version
# string: a check that let its probe's own output through would fail here rather than at the
# first operator who wondered what the extra line meant.
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

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
