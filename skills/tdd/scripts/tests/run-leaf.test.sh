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
grep -q -- '-p' "$work/argv" && grep -q 'Verify the test for issue 3.' "$work/argv" \
  && grep -q -- 'stream-json' "$work/argv" && ok || no "passes prompt via -p in stream-json"

run "$work/prompt.txt" ok 0 --allowed-tools 'Read,Bash' >/dev/null
grep -q -- '--allowed-tools' "$work/argv" && grep -q 'Read,Bash' "$work/argv" \
  && ok || no "passes extra args through"

out="$(printf 'piped prompt body' | run - 'VERDICT: PASS' 0)"
grep -q 'piped prompt body' "$work/argv" && ok || no "reads prompt from stdin on -"

envstub="$(scratch_dir)"
claude_stub "$envstub" 'env > "$ENV_OUT"'
problems=()
noarg="$(scratch_dir)"
printf 'usage: run-leaf.sh <prompt-file|-> [claude args...]\n' > "$noarg/want-err"
( cd "$work" && env PATH="$stubdir:$PATH" ARGV_OUT="$noarg/argv" "$LEAF" \
    > "$noarg/out" 2> "$noarg/err" ); code=$?
[[ "$code" == 2 ]] || problems+=("exited $code, wanted 2")
[[ -s "$noarg/out" ]] && problems+=("stdout was not empty: $(cat "$noarg/out")")
cmp -s "$noarg/want-err" "$noarg/err" || problems+=("stderr was not exactly the usage line: $(cat "$noarg/err")")
report "with no argument, prints exactly the usage line and one newline on stderr, nothing on stdout, and exits 2"

problems=()
linked="$(scratch_dir)"
ln -s "$(cd "$HERE/../.." && pwd)" "$linked/skill"
elsewhere="$(scratch_dir)"
printf 'the prompt in the other working directory' > "$elsewhere/prompt.txt"
for how in linked inplace; do
  if [[ "$how" == linked ]]; then leaf="$linked/skill/scripts/run-leaf.sh"; else leaf="$LEAF"; fi
  ( cd "$elsewhere" && env PATH="$stubdir:$PATH" ARGV_OUT="$elsewhere/$how.argv" \
      FAKE_RESULT='VERDICT: PASS' FAKE_CODE=3 "$leaf" prompt.txt > "$elsewhere/$how.out" 2>/dev/null )
  printf '%s\n' "$?" > "$elsewhere/$how.code"
done
grep -Fx 'the prompt in the other working directory' "$elsewhere/linked.argv" > /dev/null 2>&1 \
  || problems+=("through the symlink, claude was not given the other working directory's prompt")
cmp -s "$elsewhere/inplace.out" "$elsewhere/linked.out" \
  || problems+=("stdout through the symlink differed from in place: $(cat "$elsewhere/linked.out")")
[[ "$(cat "$elsewhere/linked.code")" == 3 && "$(cat "$elsewhere/inplace.code")" == 3 ]] \
  || problems+=("exit codes: through the symlink $(cat "$elsewhere/linked.code"), in place $(cat "$elsewhere/inplace.code"), wanted 3 and 3")
report "run through a symlink to the skill directory from another working directory, reads that directory's relative prompt and prints and exits as in place"

problems=()
source "$HERE/../lib/background.sh"
streamed="$(scratch_dir)"
streamstub="$(scratch_dir)"
claude_stub "$streamstub" "$(cat <<'STUB'
printf '%s\n' '{"type":"system","subtype":"init","session_id":"x"}'
looks=0
while [ ! -e "$RELEASE" ] && [ "$looks" -lt 1500 ]; do sleep 0.02; looks=$((looks + 1)); done
printf '%s\n' '{"type":"result","subtype":"success","is_error":false,"result":"VERDICT: PASS"}'
STUB
)"
appears_in() {  # appears_in <file> <line>
  local looks=0
  while [[ "$looks" -lt 500 ]]; do
    grep -Fx "$2" "$1" > /dev/null 2>&1 && return 0
    looks=$((looks + 1))
    sleep 0.02
  done
  return 1
}
on_exit bg_kill "$streamed/record"
bg_start "$streamed/record" env CLAUDE_BIN="$streamstub/claude" RELEASE="$streamed/release" \
  "$LEAF" "$work/prompt.txt" > "$streamed/out" 2>/dev/null
read -r streamed_pid _ < "$streamed/record"
appears_in "$streamed/out" '{"type":"system","subtype":"init","session_id":"x"}' \
  || problems+=("the first stream-json line was not in stdout while claude waited: '$(cat "$streamed/out")'")
grep -F '"type":"result"' "$streamed/out" > /dev/null \
  && problems+=("the result record was in stdout before the release: '$(cat "$streamed/out")'")
: > "$streamed/release"
wait "$streamed_pid"; code=$?
bg_kill "$streamed/record"
expected='{"type":"system","subtype":"init","session_id":"x"}
{"type":"result","subtype":"success","is_error":false,"result":"VERDICT: PASS"}

VERDICT: PASS'
[[ "$code" == 0 ]] || problems+=("exited $code, wanted 0")
[[ "$(cat "$streamed/out")" == "$expected" ]] || problems+=("stdout after the release differed: '$(cat "$streamed/out")'")
report "streams claude's stdout as it arrives: the first line is out while claude waits, the result record only after, then the full stdout and exit 0"

problems=()
dispositions="$(scratch_dir)"
printf '%s\n' '#!/usr/bin/env bash' 'trap -p PIPE XFSZ > "$DISP_OUT"' \
  "printf '%s\n' '{\"type\":\"result\",\"subtype\":\"success\",\"is_error\":false,\"result\":\"ok\"}'" \
  > "$dispositions/claude"
chmod +x "$dispositions/claude"
for handed in SIG_DFL SIG_IGN; do
  ( cd "$work" && env CLAUDE_BIN="$dispositions/claude" DISP_OUT="$dispositions/$handed" python3 -c '
import os, signal, sys
for name in ("SIGPIPE", "SIGXFSZ"):
    signal.signal(getattr(signal, name), getattr(signal, sys.argv[1]))
os.execv(sys.argv[2], sys.argv[2:])
' "$handed" "$LEAF" "$work/prompt.txt" > /dev/null 2>&1 )
done
[[ -f "$dispositions/SIG_DFL" && ! -s "$dispositions/SIG_DFL" ]] \
  || problems+=("with the caller's SIGPIPE and SIGXFSZ at their default, claude had: '$(cat "$dispositions/SIG_DFL" 2>&1)'")
printf "trap -- '' SIGPIPE\ntrap -- '' SIGXFSZ\n" > "$dispositions/want-ignored"
cmp -s "$dispositions/want-ignored" "$dispositions/SIG_IGN" \
  || problems+=("with the caller's SIGPIPE and SIGXFSZ ignored, claude had: '$(cat "$dispositions/SIG_IGN" 2>&1)'")
report "hands claude SIGPIPE and SIGXFSZ as its caller had them: at their default when the caller left them default, ignored when the caller ignored them"

problems=()
pyc="$(scratch_dir)"
printf 'ANSWER = 1\n' > "$pyc/mod.py"
touch -t 202301010000.00 "$pyc/mod.py"
claude_stub "$pyc" "$(cat <<'STUB'
cd "$MOD_DIR" || exit 2
same_second='import os, sys; open("mod.py", "w").write(sys.argv[1]); os.utime("mod.py", (1700000100, 1700000100))'
python3 -c 'import mod; print(mod.ANSWER)' > before
python3 -c "$same_second" 'ANSWER = 2
'
python3 -c 'import mod; print(mod.ANSWER)' > mutated
python3 -c "$same_second" 'ANSWER = 1
'
python3 -c 'import mod; print(mod.ANSWER)' > after
printf '%s\n' '{"type":"result","subtype":"success","is_error":false,"result":"ok"}'
STUB
)"
( cd "$work" && env -u PYTHONDONTWRITEBYTECODE -u PYTHONPYCACHEPREFIX CLAUDE_BIN="$pyc/claude" \
    MOD_DIR="$pyc" "$LEAF" "$work/prompt.txt" > /dev/null 2>&1 )
[[ "$(cat "$pyc/before" 2>&1)" == 1 ]] || problems+=("before the mutation the module answered '$(cat "$pyc/before" 2>&1)', wanted 1")
[[ "$(cat "$pyc/mutated" 2>&1)" == 2 ]] || problems+=("the mutated module answered '$(cat "$pyc/mutated" 2>&1)', wanted 2")
[[ "$(cat "$pyc/after" 2>&1)" == 1 ]] \
  || problems+=("the module reverted in the mutation's second at its size answered '$(cat "$pyc/after" 2>&1)' on its next import, wanted 1 as before the mutation")
report "under a leaf, a Python module mutated and reverted at the same whole-second mtime and size is re-read from source on its next import (#873)"

problems=()
for caller in unset 0 empty; do
  case "$caller" in
    unset) caller_env=(-u PYTHONDONTWRITEBYTECODE) ;;
    0) caller_env=(PYTHONDONTWRITEBYTECODE=0) ;;
    empty) caller_env=(PYTHONDONTWRITEBYTECODE=) ;;
  esac
  rm -f "$work/env"
  ( cd "$work" && env "${caller_env[@]}" CLAUDE_BIN="$envstub/claude" \
      ENV_OUT="$work/env" "$LEAF" "$work/prompt.txt" ) >/dev/null 2>&1
  grep -Fx 'PYTHONDONTWRITEBYTECODE=1' "$work/env" > /dev/null 2>&1 \
    || problems+=("with the caller's PYTHONDONTWRITEBYTECODE $caller, the leaf's claude had: '$(grep '^PYTHONDONTWRITEBYTECODE=' "$work/env" 2>&1)'")
done
report "hands the leaf PYTHONDONTWRITEBYTECODE=1 whether the caller left it unset, set it to 0 or set it empty (#873)"

problems=()
nopyc="$(scratch_dir)"
mkdir -p "$nopyc/tree/pkg"
printf 'ANSWER = 1\n' > "$nopyc/tree/mod.py"
: > "$nopyc/tree/pkg/__init__.py"
printf 'ANSWER = 2\n' > "$nopyc/tree/pkg/sub.py"
claude_stub "$nopyc" "$(cat <<'STUB'
cd "$MOD_DIR" || exit 2
python3 -c 'import mod, pkg.sub; print(mod.ANSWER + pkg.sub.ANSWER)' > ../answer
printf '%s\n' '{"type":"result","subtype":"success","is_error":false,"result":"ok"}'
STUB
)"
( cd "$work" && env -u PYTHONDONTWRITEBYTECODE -u PYTHONPYCACHEPREFIX CLAUDE_BIN="$nopyc/claude" \
    MOD_DIR="$nopyc/tree" "$LEAF" "$work/prompt.txt" > /dev/null 2>&1 )
[[ "$(cat "$nopyc/answer" 2>&1)" == 3 ]] || problems+=("the leaf's python3 answered '$(cat "$nopyc/answer" 2>&1)', wanted 3")
written="$(cd "$nopyc/tree" && find . -name '*.pyc' | sort)"
[[ -z "$written" ]] || problems+=("a Python process under the leaf wrote bytecode into the tree it imported from: $written")
report "a Python process under a leaf writes no .pyc into the tree it imports from (#873)"

problems=()
sig="$(scratch_dir)"
mkdir -p "$sig/tools"
for tool in pkill killall; do
  printf '#!/bin/sh\nprintf "%%s\\n" "$*" > "%s/%s-ran"\n' "$sig" "$tool" > "$sig/tools/$tool"
  chmod +x "$sig/tools/$tool"
done
claude_stub "$sig" "$(cat <<'STUB'
pkill -n -f 'exp-sleep 60' > "$SIG_DIR/pkill-out" 2>&1
killall exp-sleep > "$SIG_DIR/killall-out" 2>&1
printf '%s\n' '{"type":"result","subtype":"success","is_error":false,"result":"ok"}'
STUB
)"
( cd "$work" && env PATH="$sig/tools:$PATH" CLAUDE_BIN="$sig/claude" SIG_DIR="$sig" \
    "$LEAF" "$work/prompt.txt" > /dev/null 2>&1 )
for tool in pkill killall; do
  [[ ! -e "$sig/$tool-ran" ]] \
    || problems+=("the leaf's $tool reached the signalling tool, with arguments '$(cat "$sig/$tool-ran")'")
  for phrase in 'signal only processes you started' 'by the pid you recorded'; do
    grep -iF "$phrase" "$sig/$tool-out" > /dev/null 2>&1 \
      || problems+=("the leaf's $tool printed no '$phrase': '$(cat "$sig/$tool-out" 2>&1)'")
  done
done
report "refuses a leaf's pkill and killall before they signal anything, naming the rule: signal only processes you started, by the pid you recorded (#1427)"

problems=()
pg="$(scratch_dir)"
mkdir -p "$pg/tools"
printf '#!/bin/sh\nprintf "%%s\\n" "$*" >> "%s/pgrep-ran"\n' "$pg" > "$pg/tools/pgrep"
printf '#!/bin/sh\npgrep -g 0\nprintf "%%s\\n" "$?" > "%s/suite-exit"\n' "$pg" > "$pg/suite.sh"
chmod +x "$pg/tools/pgrep" "$pg/suite.sh"
claude_stub "$pg" "$(cat <<'STUB'
{ kill $(pgrep -f 'exp-sleep 60'); } > "$PG_DIR/kill-out" 2>&1
"$PG_DIR/suite.sh"
printf '%s\n' '{"type":"result","subtype":"success","is_error":false,"result":"ok"}'
STUB
)"
( cd "$work" && env PATH="$pg/tools:$PATH" CLAUDE_BIN="$pg/claude" PG_DIR="$pg" \
    "$LEAF" "$work/prompt.txt" > /dev/null 2>&1 )
leaf_lookup="$(grep -F -- '-f exp-sleep 60' "$pg/pgrep-ran" 2>/dev/null)"
[[ -z "$leaf_lookup" ]] \
  || problems+=("the leaf's kill \$(pgrep …) reached the process lookup, with arguments '$leaf_lookup'")
for phrase in 'signal only processes you started' 'by the pid you recorded'; do
  grep -iF "$phrase" "$pg/kill-out" > /dev/null 2>&1 \
    || problems+=("the leaf's kill \$(pgrep …) printed no '$phrase': '$(cat "$pg/kill-out" 2>&1)'")
done
grep -Fx -- '-g 0' "$pg/pgrep-ran" > /dev/null 2>&1 \
  || problems+=("a script the leaf ran had its pgrep -g refused: calls seen '$(cat "$pg/pgrep-ran" 2>&1)'")
[[ "$(cat "$pg/suite-exit" 2>&1)" == 0 ]] \
  || problems+=("a script the leaf ran saw its pgrep -g exit '$(cat "$pg/suite-exit" 2>&1)', not 0")
report "refuses a leaf's kill \$(pgrep …) naming the rule, while a script the leaf runs still reaches pgrep -g (#1427)"

problems=()
own="$(scratch_dir)"
claude_stub "$own" "$(cat <<'STUB'
bash -c 'sleep 30 & pid=$!
env kill "$pid" 2> "$OWN_DIR/kill-err"; status=$?
printf "%s\n" "$status" > "$OWN_DIR/kill-exit"
[ "$status" = 0 ] || /bin/kill "$pid"
wait "$pid"; printf "%s\n" "$?" > "$OWN_DIR/wait-exit"'
printf '%s\n' '{"type":"result","subtype":"success","is_error":false,"result":"ok"}'
STUB
)"
( cd "$work" && env CLAUDE_BIN="$own/claude" OWN_DIR="$own" \
    "$LEAF" "$work/prompt.txt" > /dev/null 2>&1 )
[[ "$(cat "$own/kill-exit" 2>&1)" == 0 ]] \
  || problems+=("the leaf's kill of a pid it recorded exited '$(cat "$own/kill-exit" 2>&1)', not 0: '$(cat "$own/kill-err" 2>&1)'")
[[ "$(cat "$own/wait-exit" 2>&1)" == 143 ]] \
  || problems+=("the process the leaf started ended with '$(cat "$own/wait-exit" 2>&1)', not 143 (SIGTERM)")
report "a leaf can still kill <pid> a process it started and recorded the pid of (#1427)"

finish
