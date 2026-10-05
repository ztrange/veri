#!/usr/bin/env bash
# Tests for scripts/run-leaf.sh — the leaf invocation, driven against a stub `claude` on
# PATH that records its argv to $ARGV_OUT, emits a minimal stream-json stream whose result
# event carries $FAKE_RESULT, and exits $FAKE_CODE.
#
# Contract under test:
#   run-leaf.sh runs claude with `--output-format stream-json`, then appends the clean
#   final result via extract-result.sh; it owns no progress log.
#
# Run: scripts/tests/run-leaf.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
LEAF="$HERE/../run-leaf.sh"
source "$HERE/lib/harness.sh"

stubdir="$(scratch_dir)"
work="$(scratch_dir)"
claude_stub "$stubdir" "$(cat <<'STUB'
printf '%s\n' "$@" > "$ARGV_OUT"
printf '%s\n' '{"type":"system","subtype":"init","session_id":"x"}'
printf '{"type":"assistant","message":{"content":[{"type":"text","text":"%s"}]}}\n' "${FAKE_RESULT:-ok}"
printf '{"type":"result","subtype":"success","is_error":false,"result":"%s"}\n' "${FAKE_RESULT:-ok}"
exit "${FAKE_CODE:-0}"
STUB
)"

run() {  # run <prompt-file> <fake-result> <fake-code> [extra args...]
  local pf="$1" res="$2" fcode="$3"; shift 3
  ( cd "$work" && env PATH="$stubdir:$PATH" ARGV_OUT="$work/argv" \
      FAKE_RESULT="$res" FAKE_CODE="$fcode" \
      "$LEAF" "$pf" "$@" )
}

printf 'Verify the test for issue 3.' > "$work/prompt.txt"

out="$(run "$work/prompt.txt" 'VERDICT: PASS' 0)"
[[ "$out" == *'VERDICT: PASS'* ]] && ok || no "returns extracted result text"

[[ "$out" == *'"type":"result"'* ]] && ok || no "streams raw events for heartbeat"

grep -q -- '-p' "$work/argv" && grep -q 'Verify the test for issue 3.' "$work/argv" \
  && grep -q -- 'stream-json' "$work/argv" && ok || no "passes prompt via -p in stream-json"

run "$work/prompt.txt" 'VERDICT: REJECT' 1 >/dev/null; code=$?
[[ "$code" == 1 ]] && ok || no "propagates leaf exit status (got $code)"

run "$work/prompt.txt" ok 7 >/dev/null; code=$?
[[ "$code" == 2 ]] && ok || no "maps a foreign leaf exit status to 2 (got $code)"

run "$work/prompt.txt" ok 0 --allowed-tools 'Read,Bash' >/dev/null
grep -q -- '--allowed-tools' "$work/argv" && grep -q 'Read,Bash' "$work/argv" \
  && ok || no "passes extra args through"

out="$(printf 'piped prompt body' | run - 'VERDICT: PASS' 0)"
grep -q 'piped prompt body' "$work/argv" && ok || no "reads prompt from stdin on -"

run "$work/prompt.txt" ok 0 >/dev/null
[[ ! -e "$work/.tdd" ]] && ok || no "does not own a .tdd log"

failing_cp="$(scratch_dir)"
printf '#!/bin/sh\nexit 5\n' > "$failing_cp/cp"
chmod +x "$failing_cp/cp"
home="$(scratch_dir)"
: > "$home/.gitconfig"
PATH="$failing_cp:$PATH" HOME="$home" run "$work/prompt.txt" ok 0 >/dev/null 2>&1; code=$?
[[ "$code" == 2 ]] \
  && ok || no "ends with exit 2 when it fails inside its own EXIT trap's lifetime (code=$code)"

session_vars=(CLAUDECODE CLAUDE_CODE_SESSION_ID CLAUDE_CODE_HOST_SESSION_ID
  CLAUDE_CODE_MESSAGING_SOCKET CLAUDE_CODE_MESSAGING_TOKEN CLAUDE_PID
  CLAUDE_CODE_CHILD_SESSION CLAUDE_CODE_ENTRYPOINT)
envstub="$(scratch_dir)"
claude_stub "$envstub" 'env > "$ENV_OUT"'
leaf_env_lacks() {  # leaf_env_lacks <var>... -- <NAME=value>...
  local names=()
  while [[ "$1" != -- ]]; do names+=("$1"); shift; done
  shift
  rm -f "$work/env"
  ( cd "$work" && env "$@" CLAUDE_BIN="$envstub/claude" \
      ENV_OUT="$work/env" "$LEAF" "$work/prompt.txt" ) >/dev/null 2>&1
  problems=()
  if [[ ! -f "$work/env" ]]; then
    problems+=("the leaf's claude was never started")
    return
  fi
  for v in "${names[@]}"; do
    grep -E "^$v=" "$work/env" > /dev/null && problems+=("$v reached the leaf's claude")
  done
  return 0
}
session_env=()
for v in "${session_vars[@]}"; do session_env+=("$v=from-the-conductor"); done
leaf_env_lacks "${session_vars[@]}" -- "${session_env[@]}"
report "starts claude without the conductor session's variables (#621)"

leaf_env_lacks CLAUDE_AUTO_BACKGROUND_TASKS -- CLAUDE_AUTO_BACKGROUND_TASKS=true
report "starts claude without CLAUDE_AUTO_BACKGROUND_TASKS (#621)"

leaf_env_lacks -- 'VERI_TEST_CMD=make unit'
grep -Fx 'VERI_TEST_CMD=make unit' "$work/env" > /dev/null 2>&1 \
  || problems+=("VERI_TEST_CMD did not reach the leaf's claude with the caller's value")
grep -E '^GIT_CONFIG_GLOBAL=.' "$work/env" > /dev/null 2>&1 \
  || problems+=("GIT_CONFIG_GLOBAL was not set in the leaf's claude")
report "still passes VERI_TEST_CMD and GIT_CONFIG_GLOBAL through to claude (#621)"

unset_session=()
for v in "${session_vars[@]}" CLAUDE_AUTO_BACKGROUND_TASKS; do unset_session+=(-u "$v"); done
problems=()
for pair in 0:0 1:1 2:2 3:3 7:2; do
  fcode="${pair%%:*}" want="${pair##*:}"
  out="$( cd "$work" && env "${unset_session[@]}" PATH="$stubdir:$PATH" ARGV_OUT="$work/argv" \
      FAKE_RESULT="VERDICT: PASS" FAKE_CODE="$fcode" "$LEAF" "$work/prompt.txt" 2>/dev/null )"
  code=$?
  expected='{"type":"system","subtype":"init","session_id":"x"}
{"type":"assistant","message":{"content":[{"type":"text","text":"VERDICT: PASS"}]}}
{"type":"result","subtype":"success","is_error":false,"result":"VERDICT: PASS"}

VERDICT: PASS'
  [[ "$code" == "$want" ]] || problems+=("stub exit $fcode: run-leaf.sh exited $code, wanted $want")
  [[ "$out" == "$expected" ]] || problems+=("stub exit $fcode: stdout differed: $out")
done
report "with no session variable set, exits with the stub's code (0-3, else 2) and prints the same stdout (#621)"

planted="$(scratch_dir)"
cp -R "$HERE/../.." "$planted/tdd"
printf '%s\n' 'SESSION_VARS+=(VERI_PLANTED_621)' >> "$planted/tdd/scripts/lib/session-env.sh"
claude_stub "$envstub" 'cat > /dev/null; env > "$ENV_OUT"'
rm -f "$work/leaf.env" "$work/conductor.env"
( cd "$work" && env VERI_PLANTED_621=from-the-conductor CLAUDE_BIN="$envstub/claude" \
    ENV_OUT="$work/leaf.env" "$planted/tdd/scripts/run-leaf.sh" "$work/prompt.txt" ) >/dev/null 2>&1
( cd "$work" && env VERI_PLANTED_621=from-the-conductor CLAUDE_BIN="$envstub/claude" \
    ENV_OUT="$work/conductor.env" GIT_CEILING_DIRECTORIES="$planted" \
    "$planted/tdd/scripts/run-conductor.sh" 4242 ) >/dev/null 2>&1
problems=()
for who in leaf conductor; do
  if [[ ! -f "$work/$who.env" ]]; then
    problems+=("the $who's claude was never started")
  elif grep -E '^VERI_PLANTED_621=' "$work/$who.env" > /dev/null; then
    problems+=("VERI_PLANTED_621, added to lib/session-env.sh's SESSION_VARS, reached the $who's claude")
  fi
done
report "a variable added to the shared session list reaches neither the leaf's nor the conductor's claude (#621)"

lost=()
for how in unset empty; do
  if [[ "$how" == unset ]]; then id_args=(-u CLAUDE_CODE_SESSION_ID); else id_args=(CLAUDE_CODE_SESSION_ID=); fi
  leaf_env_lacks -- "${id_args[@]}" 'VERI_TEST_CMD=make unit' VERI_FAKE_CARRIER=x-unrelated-y
  grep -Fx 'VERI_TEST_CMD=make unit' "$work/env" > /dev/null 2>&1 \
    || problems+=("session id $how: VERI_TEST_CMD did not reach the leaf's claude with the caller's value")
  grep -Fx 'VERI_FAKE_CARRIER=x-unrelated-y' "$work/env" > /dev/null 2>&1 \
    || problems+=("session id $how: VERI_FAKE_CARRIER did not reach the leaf's claude with the caller's value")
  lost+=("${problems[@]}")
done
problems=("${lost[@]}")
report "with the session id unset or empty, strips nothing beyond SESSION_VARS (#933)"

leaf_env_lacks -- CLAUDE_CODE_SESSION_ID=sess-933-fake 'VERI_TEST_CMD=make unit' \
  GIT_CONFIG_GLOBAL=/from/the/caller
grep -Fx 'VERI_TEST_CMD=make unit' "$work/env" > /dev/null 2>&1 \
  || problems+=("VERI_TEST_CMD did not reach the leaf's claude with the caller's value")
gcg="$(grep -E '^GIT_CONFIG_GLOBAL=' "$work/env" 2>/dev/null)"
[[ -n "${gcg#GIT_CONFIG_GLOBAL=}" && "$gcg" != 'GIT_CONFIG_GLOBAL=/from/the/caller' ]] \
  || problems+=("GIT_CONFIG_GLOBAL in the leaf's claude was not the one run-leaf.sh set: '${gcg}'")
report "with the session id set, still passes VERI_TEST_CMD and run-leaf.sh's GIT_CONFIG_GLOBAL through (#933)"

leaf_env_lacks CLAUDE_CODE_SESSION_ID VERI_FAKE_CARRIER -- CLAUDE_CODE_SESSION_ID=sess-933-fake \
  VERI_FAKE_CARRIER=x-sess-933-fake-y
report "strips a variable whose value contains the session id, and the id itself (#933)"

leaf_env_lacks CLAUDE_CODE_REMOTE_SESSION_ID -- CLAUDE_CODE_SESSION_ID=sess-966-fake \
  CLAUDE_CODE_REMOTE_SESSION_ID=remote-unrelated-value
report "starts claude without CLAUDE_CODE_REMOTE_SESSION_ID, whose value need not contain the session id (#966)"

finish
