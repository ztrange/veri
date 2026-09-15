#!/usr/bin/env bash
# Tests for scripts/run-conductor.sh — the CONDUCTOR invocation, driven against a stub
# `claude` on PATH (no real subprocess, no model call), the way run-leaf.test.sh drives the
# leaf one. Same stub, same seam: `CLAUDE_BIN` swaps the binary and the stub records its
# argv to $ARGV_OUT.
#
# Why a conductor is launched this way at all — the ~25,000 tokens of interactive harness
# surface it never touches, and why the stream flags are part of the criterion rather than a
# detail of how it is spelled — is run-conductor.sh's own header, which this suite does not
# restate.
#
# Contract under test (this step only):
#   `run-conductor.sh <issue>` launches the conductor binary in print mode — `-p` — with
#   `--output-format stream-json --verbose`, and the issue it was asked for reaches the
#   prompt that launch carries; the child it launches inherits none of the parent session's
#   eight handles while still inheriting every `VERI_*` tunable; and whatever status that
#   child exits with is the status the script exits with.
#
# The two halves of that second sentence are one criterion and not two: the severing is done
# by editing the environment the child is given, so a script that drops the handles by
# handing the child a scrubbed environment and one that drops them by handing it an empty one
# are indistinguishable until something asks what survived. `VERI_MODEL_VERIFIER` is what
# asks.
#
# Not asked here: what SKILL.md says about the two launch modes. That is a later step.
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
# stream-json stream, and exits with $STUB_EXIT — 0 unless a case asks for another status,
# which is the seam the exit-forwarding case below drives. Same shape as run-leaf.test.sh's.
cat > "$stubdir/claude" <<'STUB'
#!/usr/bin/env bash
printf '%s\n' "$@" > "$ARGV_OUT"
[[ -n "${ENV_OUT:-}" ]] && env > "$ENV_OUT"
printf '%s\n' '{"type":"system","subtype":"init","session_id":"x"}'
printf '%s\n' '{"type":"result","subtype":"success","is_error":false,"result":"ok"}'
exit "${STUB_EXIT:-0}"
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

# The eight handles a nested `claude` would otherwise inherit from the session that launched
# it — the messaging socket and token most of all, which wire a second session into the
# first one's IPC channel. Each carries the value it is set to, because the list that sets
# them and the list that then looks for them gone must be the same list: a name set here but
# probed under a second spelling is a probe that passes having watched nothing.
handles=(
  CLAUDECODE=1
  CLAUDE_CODE_SESSION_ID=parent-session
  CLAUDE_CODE_HOST_SESSION_ID=parent-host-session
  CLAUDE_CODE_MESSAGING_SOCKET=/tmp/parent.sock
  CLAUDE_CODE_MESSAGING_TOKEN=parent-token
  CLAUDE_PID=4141
  CLAUDE_CODE_CHILD_SESSION=1
  CLAUDE_CODE_ENTRYPOINT=cli
)

envfile="$work/env"

# 2. The environment the child is handed: the session handles severed, the tunables intact.
name="the launch severs the eight session handles and passes VERI_* through"
problems=()

( cd "$work" && env PATH="$stubdir:$PATH" ARGV_OUT="$argv" ENV_OUT="$envfile" \
    "${handles[@]}" \
    VERI_MODEL_VERIFIER=probe-verifier-model \
    "$CONDUCTOR" "$issue" ) >/dev/null 2>&1

if [[ ! -f "$envfile" ]]; then
  problems+=("the conductor binary was never launched — $CONDUCTOR recorded no environment")
else
  for handle in "${handles[@]}"; do
    grep -q "^${handle%%=*}=" "$envfile" &&
      problems+=("${handle%%=*} is still in the child's environment")
  done
  grep -qx -- 'VERI_MODEL_VERIFIER=probe-verifier-model' "$envfile" ||
    problems+=("VERI_MODEL_VERIFIER did not reach the child's environment")
fi

report "$name"

# 3. The status: a conductor that died is a conductor the caller must be able to see died,
# so the child's status is the script's and not a status the script invents. 17 because it is
# neither 0 nor one of the four codes this repository's scripts speak, so a script that
# forwards it cannot be a script that happens to produce the same number some other way.
name="a non-zero child exit is the script's exit"
problems=()

( cd "$work" && env PATH="$stubdir:$PATH" ARGV_OUT="$argv" STUB_EXIT=17 \
    "$CONDUCTOR" "$issue" ) >/dev/null 2>&1
status=$?

[[ "$status" -eq 17 ]] ||
  problems+=("the script exited $status, not the child's 17")

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
