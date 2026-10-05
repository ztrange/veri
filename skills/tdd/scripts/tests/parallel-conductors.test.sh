#!/usr/bin/env bash
# Unit tests for scripts/parallel-conductors.sh — rung 3's selection layer. Run from a target
# repo's primary checkout, it launches up to VERI_PARALLEL supervised conductors at once over
# the issues solvable-issues.sh prints, and reports one line per issue it launched.
#
# Contract under test:
#   parallel-conductors.sh [--repo owner/name] [--continue-on-bail]
#   VERI_PARALLEL=<n>    conductors running at once, default 1. A whole number ≥ 1; anything
#                        else, set-but-empty included, is exit 2 before anything is launched.
#   VERI_GH_JSON=<dir>   passed through to solvable-issues.sh, so the solvable set is a
#                        fixture and no case reaches GitHub.
#   CLAUDE_BIN=<path>    passed through to every conductor: here a stub that records that it
#                        ran, which is what "a conductor was launched" means to these cases.
#
# Run: scripts/tests/parallel-conductors.test.sh
set -uo pipefail
unset VERI_GH_DRIVER

HERE="$(cd "$(dirname "$0")" && pwd)"
PARALLEL="$HERE/../parallel-conductors.sh"
source "$HERE/lib/harness.sh"
work="$(scratch_dir)"

fresh_repo() {
  local dir="$1"
  shift
  new_repo -b main "$@" "$dir" >/dev/null 2>&1
  git -C "$dir" -c user.name=t -c user.email=t@t commit -q --allow-empty -m init >/dev/null 2>&1
}

target="$work/target"
fresh_repo "$target"
cd "$target" || exit 2

gh_json="$work/gh"
mkdir -p "$gh_json"
printf '[]\n' > "$gh_json/prs.json"
cat > "$gh_json/issues.json" <<'JSON'
[
  {
    "number": 7,
    "title": "a solvable issue",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## What to build\n\nSomething.\n\n## Blocked by\n\nNone.\n"
  }
]
JSON

launched="$work/launched"
stub="$work/claude"
printf '#!/bin/sh\necho "$*" >> "%s"\n' "$launched" > "$stub"
chmod +x "$stub"

bad=""
for value in 0 two ''; do
  rm -f "$launched"
  env -u VERI_LABEL -u VERI_PRIORITY_LABEL -u VERI_MAX_ISSUES \
    VERI_PARALLEL="$value" VERI_GH_JSON="$gh_json" CLAUDE_BIN="$stub" \
    "$PARALLEL" >/dev/null 2>&1 && code=0 || code=$?
  conductor_files="$(ls -d .tdd/conductor-* 2>/dev/null)"
  if [[ "$code" != 2 || -e "$launched" || -n "$conductor_files" ]]; then
    bad+=" [VERI_PARALLEL='$value': exit=$code want 2, stub ran: $([[ -e "$launched" ]] && echo yes || echo no), conductor files: '${conductor_files}']"
  fi
done

[[ -z "$bad" ]] \
  && ok || no "VERI_PARALLEL not a whole number >= 1 (0, a word, set-but-empty) is exit 2 with no conductor launched ($bad )"

skill="$work/skill"
mkdir -p "$skill"
cp "$HERE/../../SKILL.md" "$skill/SKILL.md"
cp -R "$HERE/.." "$skill/scripts"
rm -rf "$skill/scripts/tests"

gh_fixture() {
  mkdir -p "$1"
  : > "$1/prs.lines"
  printf '[]\n' > "$1/prs.json"
  cat > "$1/issues.json"
}

solvable_fixture() {
  local dir="$1" n sep="" issues="["
  shift
  for n in "$@"; do
    issues+="$sep"'{"number": '"$n"', "title": "issue '"$n"'", "labels": [{"name": "ready-for-agent"}], "state": "OPEN", "body": "## Blocked by\n\nNone.\n"}'
    sep=","
  done
  printf '%s]\n' "$issues" | gh_fixture "$dir"
}

run_launcher() {
  local gh="$1" stub="$2" out="$3" vars=()
  shift 3
  while (( $# )) && [[ "$1" != -- ]]; do vars+=("$1"); shift; done
  (( $# )) && shift
  env -u VERI_PARALLEL -u VERI_LABEL -u VERI_PRIORITY_LABEL -u VERI_MAX_ISSUES -u VERI_CONDUCTOR_CTX_BUDGET \
    VERI_GH_JSON="$gh" CLAUDE_BIN="$stub" VERI_POLL=0.05 "${vars[@]+"${vars[@]}"}" \
    "$skill/scripts/parallel-conductors.sh" "$@" > "$out" 2>&1 && code=0 || code=$?
}

run_launcher_in() {
  local repo="$1"
  shift
  (cd "$repo" && run_launcher "$@"; exit "$code") && code=0 || code=$?
}

expect_lines() {
  [[ "$3" == "$2" ]] \
    && ok || no "$1 (exit=$code)
$(diff <(printf '%s\n' "$2") <(printf '%s\n' "$3"))
launcher output:
$(cat "$4")"
}

gh2="$work/gh2"
solvable_fixture "$gh2" 7 8

open_pr() {
  cat <<SH
command -v register_pr > /dev/null 2>&1 || register_pr() { bash -c '. "\$1"; shift; register_pr "\$@"' _ "$HERE/lib/gh-fixture.sh" "\$@"; }
register_pr "$1" "\$n" $2
SH
}

ready_pr() { open_pr "$1" false; }

bail_event='{"ts": 1, "issue": "7", "actor": "conductor", "phase": "develop-red", "step": "1", "event": "bail", "attempt": "1", "skill_commit": "", "cause": "revise-budget"}'
bailed_pr() {
  cat <<SH
mkdir -p ".tdd/wt/\$n/.tdd"
printf '%s\n' '$bail_event' >> ".tdd/wt/\$n/.tdd/events.jsonl"
SH
  open_pr "$1" true
}

conductor_stub() {
  {
    cat <<'HEAD'
#!/bin/sh
n="$(sed -n 's/^Solve issue #\([0-9]*\) .*/\1/p')"
HEAD
    cat
    cat <<'TAIL'
printf '%s\n' '{"type":"result","subtype":"success","is_error":false,"result":"ok"}'
exit 0
TAIL
  } > "$1"
  chmod +x "$1"
}

record_stub() {
  conductor_stub "$1" <<STUB
echo "start \$n" >> "$2"
$(ready_pr "$3")
STUB
}

timeline_stub() {
  local path="$1" timeline="$2" gh="$3" lock="${4:-}" lock_take="" lock_drop=""
  if [[ -n "$lock" ]]; then
    lock_take="if mkdir \"$lock\" 2>/dev/null; then held=1; else held=0; echo \"overlap \$n\" >> \"$timeline\"; fi"
    lock_drop="[ \"\$held\" = 1 ] && rmdir \"$lock\""
  fi
  conductor_stub "$path" <<STUB
$lock_take
echo "start \$n" >> "$timeline"
i=0
while [ "\$i" -lt \$(( ${PATIENCE:-1} * 50 )) ] && [ "\$(grep -c '^start' "$timeline")" -lt 2 ]; do
  sleep 0.02; i=\$((i + 1))
done
echo "end \$n" >> "$timeline"
$(ready_pr "$gh")
$lock_drop
STUB
}

timeline="$work/timeline"
seq_stub="$work/claude-seq"
timeline_stub "$seq_stub" "$timeline" "$gh2" "$work/running"

run_launcher "$gh2" "$seq_stub" "$work/seq.out"
want_timeline="$(printf 'start 7\nend 7\nstart 8\nend 8')"
got_timeline="$(cat "$timeline" 2>/dev/null)"
expect_lines "VERI_PARALLEL unset runs two solvable issues' conductors one after another" "$want_timeline" "$got_timeline" "$work/seq.out"

gh3="$work/gh3"
solvable_fixture "$gh3" 7 8

timeline3="$work/timeline3"
par_stub="$work/claude-par"
timeline_stub "$par_stub" "$timeline3" "$gh3"

run_launcher "$gh3" "$par_stub" "$work/par.out" VERI_PARALLEL=2
got_timeline="$(cat "$timeline3" 2>/dev/null)"
first_two="$(head -n 2 "$timeline3" 2>/dev/null | sort)"
all_four="$(sort "$timeline3" 2>/dev/null)"
[[ "$first_two" == "$(printf 'start 7\nstart 8')" \
   && "$all_four" == "$(printf 'end 7\nend 8\nstart 7\nstart 8')" ]] \
  && ok || no "VERI_PARALLEL=2 runs two solvable issues' conductors at once — both start before either ends (exit=$code)
timeline:
$got_timeline
launcher output:
$(cat "$work/par.out")"

gh_ctx="$work/gh-ctx"
solvable_fixture "$gh_ctx" 7 8

ctx_stub="$work/claude-ctx"
conductor_stub "$ctx_stub" <<STUB
case "\$n" in
  7) read=50000 create=3438 ;;
  *) read=60000 create=2000 ;;
esac
printf '{"type":"assistant","message":{"role":"assistant","usage":{"input_tokens":7,"cache_creation_input_tokens":%s,"cache_read_input_tokens":%s,"output_tokens":120}}}\n' "\$create" "\$read"
printf '{"type":"user","message":{"role":"user","usage":{"input_tokens":7,"cache_creation_input_tokens":9,"cache_read_input_tokens":900,"output_tokens":120}}}\n'
$(ready_pr "$gh_ctx")
STUB

run_launcher "$gh_ctx" "$ctx_stub" "$work/ctx.out" VERI_PARALLEL=2
got_ctx="$(grep '^context ' "$work/ctx.out" | sort)"
expect_lines "VERI_PARALLEL=2 prints each conductor's assistant events as 'context <issue> <cache_read + cache_creation>' attributed to its own issue" "$(printf 'context 7 53438\ncontext 8 62000')" "$got_ctx" "$work/ctx.out"
expect_lines "a non-assistant event carrying cache usage prints no 'context' line" "" "$(grep '^context [0-9]* 909$' "$work/ctx.out" || true)" "$work/ctx.out"

stub_waits() {
  cat <<SH
await_context() {
  until grep -Fx "\$1" "$1" > /dev/null; do :; done
}
heartbeats() {
  i=0
  while [ \$i -lt \$1 ]; do echo '{"type":"system","subtype":"heartbeat"}'; i=\$((i + 1)); done
}
await_stop() {
  mkfifo "$1.stop.\$\$"
  read stop_line < "$1.stop.\$\$"
}
over_budget_step_done() {
  echo '{"type":"assistant","message":{"role":"assistant","content":[{"type":"tool_use","id":"t1","name":"Bash","input":{"command":"VERI_ISSUE=7 VERI_ACTOR=conductor \$S/event.sh step-done"}}],"usage":{"input_tokens":5,"cache_creation_input_tokens":100,"cache_read_input_tokens":150000,"output_tokens":30}}}'
  await_context 'context 7 150100'
}
await_gone() {
  until [ -r "\$1" ] && ! kill -0 "\$(cat "\$1")" 2>/dev/null; do :; done
}
SH
}

await_gone() {
  while [[ -r "$1" ]] && kill -0 "$(cat "$1")" 2>/dev/null; do :; done
}

await_out="$work/await.out"
: > "$await_out"
sh -c "$(stub_waits "$await_out")
sleep() { :; }
looks=0
grep() {
  looks=\$((looks + 1))
  case \" \$* \" in *\" $await_out \"*) ;; *) looks=101 ;; esac
  [ \$looks -le 100 ] || echo 'context 7 1' >> '$await_out'
  command grep \"\$@\"
}
await_context 'context 7 1'
command grep -Fx 'context 7 1' '$await_out' > /dev/null && echo returned-after-line || echo returned-before-line" \
  > "$work/await.result" 2>&1
expect_lines "stub_waits' await_context returns only once its context line has arrived, however many looks that takes" "returned-after-line" "$(cat "$work/await.result")" "$await_out"

heartbeat_line='{"type":"system","subtype":"heartbeat"}'
sh -c "$(stub_waits "$await_out")
sleep() { echo slept; }
heartbeats 3" > "$work/heartbeats.result" 2>&1 < /dev/null
expect_lines "stub_waits' heartbeats prints its heartbeat lines without calling sleep" "$(printf '%s\n' "$heartbeat_line" "$heartbeat_line" "$heartbeat_line")" "$(cat "$work/heartbeats.result")" "$await_out"

echo 1 > "$work/gone.pid"
gone_result="$(
  sleep() { echo slept; }
  looks=0
  kill() { looks=$((looks + 1)); (( looks <= 300 )); }
  await_gone "$work/gone.pid" 2>&1
  (( looks > 300 )) && echo returned-once-gone || echo returned-while-alive
)"
expect_lines "await_gone returns only once the stopped stub's pid is gone, however many looks that takes, without calling sleep" "returned-once-gone" "$gone_result" "$work/gone.pid"

sh -c "$(stub_waits "$await_out")
sleep() { echo slept; }
looks=0
kill() { looks=\$((looks + 1)); [ \$looks -le 300 ]; }
await_gone '$work/gone.pid'
[ \$looks -gt 300 ] && echo returned-once-gone || echo returned-while-alive" > "$work/stub-gone.result" 2>&1 < /dev/null
expect_lines "stub_waits' await_gone returns only once the other stub's pid is gone, however many looks that takes, without calling sleep" "returned-once-gone" "$(cat "$work/stub-gone.result")" "$work/gone.pid"

gh_stop="$work/gh-stop"
solvable_fixture "$gh_stop" 7
stop_marks="$work/stop.marks"
stop_launches="$work/stop.launches"
: > "$stop_marks"
stop_stub="$work/claude-stop"
conductor_stub "$stop_stub" <<STUB
echo "\$n" >> "$stop_launches"
if [ "\$(wc -l < "$stop_launches")" -eq 1 ]; then
  echo \$\$ > "$stop_marks.pid"
$(stub_waits "$work/stop.out")
  echo '{"type":"assistant","message":{"role":"assistant","usage":{"input_tokens":5,"cache_creation_input_tokens":0,"cache_read_input_tokens":150000,"output_tokens":40}}}'
  await_context 'context 7 150000'
  echo mid-step >> "$stop_marks"
  over_budget_step_done
  heartbeats 50
  echo before-result >> "$stop_marks"
  echo '{"type":"user","message":{"role":"user","content":[{"type":"tool_result","tool_use_id":"t1","content":""}]}}'
  await_stop
  echo after-step-done >> "$stop_marks"
fi
$(ready_pr "$gh_stop")
STUB

run_launcher "$gh_stop" "$stop_stub" "$work/stop.out" VERI_CONDUCTOR_CTX_BUDGET=100000
await_gone "$stop_marks.pid"
expect_lines "a conductor over VERI_CONDUCTOR_CTX_BUDGET is not stopped mid-step nor at the step-done call, and is stopped once that call's result appears" "$(printf 'mid-step\nbefore-result')" "$(cat "$stop_marks")" "$work/stop.out"

gh_under="$work/gh-under"
solvable_fixture "$gh_under" 7
under_marks="$work/under.marks"
: > "$under_marks"
under_stub="$work/claude-under"
conductor_stub "$under_stub" <<STUB
$(stub_waits "$work/under.out")
echo '{"type":"assistant","message":{"role":"assistant","content":[{"type":"tool_use","id":"t1","name":"Bash","input":{"command":"VERI_ISSUE=7 VERI_ACTOR=conductor \$S/event.sh step-done"}}],"usage":{"input_tokens":5,"cache_creation_input_tokens":0,"cache_read_input_tokens":110000,"output_tokens":30}}}'
await_context 'context 7 110000'
echo '{"type":"user","message":{"role":"user","content":[{"type":"tool_result","tool_use_id":"t1","content":""}]}}'
heartbeats 50
echo under-budget-step-done >> "$under_marks"
echo '{"type":"assistant","message":{"role":"assistant","content":[{"type":"tool_use","id":"t2","name":"Bash","input":{"command":"make test"}}],"usage":{"input_tokens":5,"cache_creation_input_tokens":0,"cache_read_input_tokens":150000,"output_tokens":30}}}'
await_context 'context 7 150000'
echo '{"type":"user","message":{"role":"user","content":[{"type":"tool_result","tool_use_id":"t2","content":""}]}}'
heartbeats 50
echo over-budget-mid-step >> "$under_marks"
$(ready_pr "$gh_under")
STUB

run_launcher "$gh_under" "$under_stub" "$work/under.out"
expect_lines "a conductor under the default VERI_CONDUCTOR_CTX_BUDGET of 120000 is not stopped at a step-done result, nor at a later tool result once over budget with no new step-done" "$(printf 'under-budget-step-done\nover-budget-mid-step')" "$(cat "$under_marks")" "$work/under.out"

gh_beside="$work/gh-beside"
solvable_fixture "$gh_beside" 7 8
beside_marks="$work/beside.marks"
: > "$beside_marks"
beside_launches="$work/beside.launches"
: > "$beside_launches"
beside_stub="$work/claude-beside"
conductor_stub "$beside_stub" <<STUB
$(stub_waits "$work/beside.out")
echo "\$n" >> "$beside_launches"
if [ "\$n" = 7 ] && [ "\$(grep -c '^7$' "$beside_launches")" -eq 1 ]; then
  echo \$\$ > "$beside_marks.7.pid"
  over_budget_step_done
  echo before-result-7 >> "$beside_marks"
  echo '{"type":"user","message":{"role":"user","content":[{"type":"tool_result","tool_use_id":"t1","content":""}]}}'
  await_stop
  echo after-step-done-7 >> "$beside_marks"
elif [ "\$n" = 8 ]; then
  await_gone "$beside_marks.7.pid"
  echo 8-outlived-7 >> "$beside_marks"
  heartbeats 20
  echo end-8 >> "$beside_marks"
fi
$(ready_pr "$gh_beside")
STUB

run_launcher "$gh_beside" "$beside_stub" "$work/beside.out" VERI_PARALLEL=2 VERI_CONDUCTOR_CTX_BUDGET=100000
expect_lines "while one conductor is stopped over VERI_CONDUCTOR_CTX_BUDGET at step-done, the conductor running beside it is not stopped and runs to its own end" "$(printf 'before-result-7\n8-outlived-7\nend-8')" "$(cat "$beside_marks")" "$work/beside.out"

gh_again="$work/gh-again"
solvable_fixture "$gh_again" 7 8
again_launches="$work/again.launches"
: > "$again_launches"
again_stub="$work/claude-again"
conductor_stub "$again_stub" <<STUB
echo "\$n" >> "$again_launches"
if [ "\$n" = 7 ] && [ "\$(grep -c '^7$' "$again_launches")" -eq 1 ]; then
$(stub_waits "$work/again.out")
  over_budget_step_done
  echo '{"type":"user","message":{"role":"user","content":[{"type":"tool_result","tool_use_id":"t1","content":""}]}}'
  await_stop
  exit 0
fi
$(ready_pr "$gh_again")
STUB

again_bin="$work/again-bin"
mkdir -p "$again_bin"
cat > "$again_bin/sleep" <<SH
#!/bin/sh
case "\$(ps -o command= -p \$PPID)" in
  *claude-again*) echo "sleep \$*" >> "$work/again.slept" ;;
esac
exec $(command -v sleep) "\$@"
SH
chmod +x "$again_bin/sleep"
run_launcher "$gh_again" "$again_stub" "$work/again.out" VERI_CONDUCTOR_CTX_BUDGET=100000 PATH="$again_bin:$PATH"
expect_lines "the again case's stub holds after its step-done result without calling sleep" "" "$(cat "$work/again.slept" 2>/dev/null)" "$work/again.out"
expect_lines "a conductor stopped over VERI_CONDUCTOR_CTX_BUDGET is launched again for the same issue before a not-yet-launched solvable issue takes its slot" "$(printf '7\n7\n8')" "$(cat "$again_launches")" "$work/again.out"

expect_lines "a conductor relaunched after an over-budget stop prints 'restarted <n>' naming its issue" "restarted 7" "$(grep '^restarted ' "$work/again.out" || true)" "$work/again.out"

park_run() {
  local name="$1" gh="$work/gh-$1"
  shift
  fresh_repo "$work/$name"
  solvable_fixture "$gh" 7 8
  : > "$work/$name.launches"
  conductor_stub "$work/claude-$name" <<STUB
echo "\$n" >> "$work/$name.launches"
if [ "\$n" = 7 ]; then
  mkdir -p .tdd/parked
  echo 'Which test command should this run use?' > .tdd/parked/7.md
$(bailed_pr "$gh")
  exit 0
fi
$(ready_pr "$gh")
STUB
  run_launcher_in "$work/$name" "$gh" "$work/claude-$name" "$work/$name.out" "$@"
}

park_run park
expect_lines "a conductor that halts writing .tdd/parked/<n>.md prints 'parked <n>', its slot takes the next solvable issue even without --continue-on-bail and with its draft PR's log ending in a bail, and <n> is not launched again while still solvable" \
  "$(printf 'parked 7\n7\n8')" "$(grep '^parked ' "$work/park.out"; cat "$work/park.launches")" "$work/park.out"

bad=""
for mode in stop continue; do
  flag=()
  [[ "$mode" == continue ]] && flag=(-- --continue-on-bail)
  park_run "park-$mode" "${flag[@]+"${flag[@]}"}"
  got_launches="$(tr '\n' ',' < "$work/park-$mode.launches")"
  as_bail="$(grep -E '^#7 — bailed|^stopped: #7' "$work/park-$mode.out" | tr '\n' '|')"
  if [[ "$got_launches" != "7,8," || -n "$as_bail" ]]; then
    bad+=" [$mode: exit=$code, launches '$got_launches' want '7,8,', #7 reported as a bail: '$as_bail' want none; output: $(tr '\n' '|' < "$work/park-$mode.out")]"
  fi
done

[[ -z "$bad" ]] \
  && ok || no "a parked conductor does not stop new launches, with or without --continue-on-bail, and is never reported as a bail even when its draft PR's log ends in one ($bad )"

gh_one="$work/gh-one"
solvable_fixture "$gh_one" 7 8
one_marks="$work/one.marks"
: > "$one_marks"
one_launches="$work/one.launches"
: > "$one_launches"
one_stub="$work/claude-one"
conductor_stub "$one_stub" <<STUB
$(stub_waits "$work/one.out")
echo "\$n" >> "$one_launches"
if [ "\$n" = 7 ] && [ "\$(grep -c '^7$' "$one_launches")" -eq 1 ]; then
  echo \$\$ > "$one_marks.pid"
  echo '{"type":"assistant","message":{"role":"assistant","usage":{"input_tokens":5,"cache_creation_input_tokens":0,"cache_read_input_tokens":150000,"output_tokens":40}}}'
  await_context 'context 7 150000'
  echo mid-step-7 >> "$one_marks"
  over_budget_step_done
  heartbeats 50
  echo before-result-7 >> "$one_marks"
  echo '{"type":"user","message":{"role":"user","content":[{"type":"tool_result","tool_use_id":"t1","content":""}]}}'
  await_stop
  echo after-step-done-7 >> "$one_marks"
  exit 0
elif [ "\$n" = 8 ]; then
  echo '{"type":"assistant","message":{"role":"assistant","content":[{"type":"tool_use","id":"t1","name":"Bash","input":{"command":"VERI_ISSUE=8 VERI_ACTOR=conductor \$S/event.sh step-done"}}],"usage":{"input_tokens":5,"cache_creation_input_tokens":0,"cache_read_input_tokens":50000,"output_tokens":30}}}'
  await_context 'context 8 50000'
  echo '{"type":"user","message":{"role":"user","content":[{"type":"tool_result","tool_use_id":"t1","content":""}]}}'
  heartbeats 50
  echo end-8 >> "$one_marks"
fi
$(ready_pr "$gh_one")
STUB

run_launcher "$gh_one" "$one_stub" "$work/one.out" VERI_PARALLEL=1 VERI_CONDUCTOR_CTX_BUDGET=100000
await_gone "$one_marks.pid"
expect_lines "with VERI_PARALLEL=1 a conductor over VERI_CONDUCTOR_CTX_BUDGET mid-step is stopped only after its step-done result and relaunched for the same issue, and one that never crosses the budget is never stopped or relaunched" \
  "$(printf 'mid-step-7\nbefore-result-7\nend-8\n--\n7\n7\n8\n--\nrestarted 7')" \
  "$(cat "$one_marks"; echo --; cat "$one_launches"; echo --; grep '^restarted ' "$work/one.out" || true)" "$work/one.out"

bad=""
for shape in done parked; do
  gh_end="$work/gh-end-$shape"
  solvable_fixture "$gh_end" 7 8
  fresh_repo "$work/end-$shape"
  : > "$work/end-$shape.launches"
  if [[ "$shape" == done ]]; then
    finish_step="$(ready_pr "$gh_end")"
  else
    finish_step="mkdir -p .tdd/parked
echo 'Which test command should this run use?' > .tdd/parked/\$n.md"
  fi
  conductor_stub "$work/claude-end-$shape" <<STUB
echo "\$n" >> "$work/end-$shape.launches"
$finish_step
STUB
  run_launcher_in "$work/end-$shape" "$gh_end" "$work/claude-end-$shape" "$work/end-$shape.out" VERI_PARALLEL=1
  got_launches="$(tr '\n' ',' < "$work/end-$shape.launches")"
  if [[ "$code" != 0 || "$got_launches" != "7,8," ]]; then
    bad+=" [$shape: exit=$code want 0, launches '$got_launches' want '7,8,'; output: $(tr '\n' '|' < "$work/end-$shape.out")]"
  fi
done

[[ -z "$bad" ]] \
  && ok || no "with VERI_PARALLEL=1 the launcher exits 0 once nothing is left to take after launching conductors, and exits 0 when every issue still solvable is parked ($bad )"

gh4="$work/gh4"
gh_fixture "$gh4" <<'JSON'
[
  {"number": 5, "title": "not opted in", "labels": [], "state": "OPEN",
   "body": "## Blocked by\n\nNone.\n"},
  {"number": 6, "title": "blocked", "labels": [{"name": "ready-for-agent"}], "state": "OPEN",
   "body": "## Blocked by\n\n- #9\n"},
  {"number": 7, "title": "plain", "labels": [{"name": "ready-for-agent"}], "state": "OPEN",
   "body": "## Blocked by\n\nNone.\n"},
  {"number": 8, "title": "urgent", "labels": [{"name": "ready-for-agent"}, {"name": "priority"}],
   "state": "OPEN", "body": "## Blocked by\n\nNone.\n"},
  {"number": 9, "title": "the open blocker", "labels": [], "state": "OPEN",
   "body": "## Blocked by\n\nNone.\n"}
]
JSON

order="$work/order"
order_stub="$work/claude-order"
record_stub "$order_stub" "$order" "$gh4"

run_launcher "$gh4" "$order_stub" "$work/order.out"
want_order="$(printf 'start 8\nstart 7')"
got_order="$(cat "$order" 2>/dev/null)"
expect_lines "launches follow solvable-issues.sh's printed order and never an issue it did not print" "$want_order" "$got_order" "$work/order.out"

gh5="$work/gh5"
gh_fixture "$gh5" <<'JSON'
[
  {"number": 7, "title": "stays solvable", "labels": [{"name": "ready-for-agent"}], "state": "OPEN",
   "body": "## Blocked by\n\nNone.\n"}
]
JSON

again="$work/again"
again_stub="$work/claude-again"
conductor_stub "$again_stub" <<STUB
if grep -x "start \$n" "$again" > /dev/null 2>&1; then
  $(ready_pr "$gh5")
fi
echo "start \$n" >> "$again"
STUB

run_launcher "$gh5" "$again_stub" "$work/again.out"
want_again="start 7"
got_again="$(cat "$again" 2>/dev/null)"
expect_lines "an issue still solvable after its conductor finished is not launched a second time" "$want_again" "$got_again" "$work/again.out"

gh6="$work/gh6"
gh_fixture "$gh6" <<'JSON'
[
  {"number": 7, "title": "runs first", "labels": [{"name": "ready-for-agent"}], "state": "OPEN",
   "body": "## Blocked by\n\nNone.\n"},
  {"number": 8, "title": "unblocked mid-run", "labels": [{"name": "ready-for-agent"}], "state": "OPEN",
   "body": "## Blocked by\n\n- #9\n"},
  {"number": 9, "title": "the blocker", "labels": [], "state": "OPEN",
   "body": "## Blocked by\n\nNone.\n"}
]
JSON

unblock="$work/unblock"
unblock_stub="$work/claude-unblock"
conductor_stub "$unblock_stub" <<STUB
echo "start \$n" >> "$unblock"
if [ "\$n" = 7 ]; then
  sed 's/"title": "the blocker", "labels": \[\], "state": "OPEN"/"title": "the blocker", "labels": [], "state": "CLOSED"/' \
    "$gh6/issues.json" > "$gh6/issues.json.new" && mv "$gh6/issues.json.new" "$gh6/issues.json"
fi
$(ready_pr "$gh6")
STUB

run_launcher "$gh6" "$unblock_stub" "$work/unblock.out"
want_unblock="$(printf 'start 7\nstart 8')"
got_unblock="$(cat "$unblock" 2>/dev/null)"
expect_lines "an issue that became solvable while another conductor ran is launched next" "$want_unblock" "$got_unblock" "$work/unblock.out"

bad=""
for cap in 2; do
  gh7="$work/gh7-$cap"
  solvable_fixture "$gh7" 7 8 9
  capped="$work/capped-$cap"
  cap_stub="$work/claude-cap-$cap"
  record_stub "$cap_stub" "$capped" "$gh7"
  run_launcher "$gh7" "$cap_stub" "$work/cap-$cap.out" VERI_MAX_ISSUES="$cap"
  case "$cap" in
    2) want_cap="$(printf 'start 7\nstart 8')" ;;
  esac
  got_cap="$(cat "$capped" 2>/dev/null)"
  if [[ "$got_cap" != "$want_cap" ]]; then
    bad+=" [VERI_MAX_ISSUES=$cap: exit=$code, launched '$(printf '%s' "$got_cap" | tr '\n' ',')' want '$(printf '%s' "$want_cap" | tr '\n' ',')']"
  fi
done

[[ -z "$bad" ]] \
  && ok || no "VERI_MAX_ISSUES caps the launches of one invocation ($bad )"

gh8="$work/gh8"
solvable_fixture "$gh8" 7 8 9

outcome_stub="$work/claude-outcome"
conductor_stub "$outcome_stub" <<STUB
if [ "\$n" = 8 ] || [ "\$n" = 9 ]; then
  mkdir -p ".tdd/wt/\$n/.tdd"
  printf '%s\n' '{"ts": 1, "issue": "'"\$n"'", "actor": "conductor", "phase": "develop-red", "step": "1", "event": "launch", "attempt": "1", "skill_commit": ""}' \
    '{"ts": 2, "issue": "'"\$n"'", "actor": "conductor", "phase": "develop-red", "step": "1", "event": "bail", "attempt": "1", "skill_commit": "", "cause": "revise-budget"}' \
    >> ".tdd/wt/\$n/.tdd/events.jsonl"
  [ "\$n" = 9 ] && printf '%s\n' '{"ts": 3, "issue": "9", "actor": "conductor", "phase": "develop-red", "step": "1", "event": "launch", "attempt": "2", "skill_commit": ""}' \
    >> ".tdd/wt/\$n/.tdd/events.jsonl"
  $(open_pr "$gh8" true)
else
  $(ready_pr "$gh8")
fi
STUB

run_launcher "$gh8" "$outcome_stub" "$work/outcome.out"
want_outcome="$(printf '#7 — done https://example.test/pull/7\n#8 — bailed https://example.test/pull/8')"
got_outcome="$(grep -E '^#[0-9]+ — ' "$work/outcome.out")"
expect_lines "a ready PR is reported '#<n> — done <pr-url>', a draft PR whose event log ends in a bail '#<n> — bailed <pr-url>', and a draft PR whose log does not end in one never bailed" "$want_outcome" "$got_outcome" "$work/outcome.out"

gh9="$work/gh9"
solvable_fixture "$gh9" 7

clock_stub() {
  printf '#!/bin/sh\nc="$(cat "%s" 2>/dev/null || echo 0)"\n[ -e "%s" ] && c=$((c + %s))\necho "$c" > "%s"\necho "$c"\n' \
    "$2" "${4:-/}" "$3" "$2" > "$1"
  chmod +x "$1"
}

jump_clock="$work/awake-clock"
clock_stub "$jump_clock" "$work/awake-count" 1000

hang() {
  cat <<SH
i=0
while [ "\$i" -lt \$(( ${PATIENCE:-5} * 50 )) ]; do sleep 0.02; i=\$((i + 1)); done
SH
}

hang_stub="$work/claude-hang"
hang | conductor_stub "$hang_stub"

run_launcher "$gh9" "$hang_stub" "$work/killed.out" VERI_RUN_TIMEOUT=60 VERI_AWAKE_CLOCK="$jump_clock" VERI_KILL_POLL=0.01
want_killed="#7 — killed after 60s"
got_killed="$(grep -E '^#[0-9]+ — ' "$work/killed.out")"
expect_lines "a conductor its supervisor killed (supervise exit 2) is reported '#<n> — killed after <VERI_RUN_TIMEOUT>s'" "$want_killed" "$got_killed" "$work/killed.out"

gh_race="$work/gh-race"
mkdir -p "$gh_race"
: > "$gh_race/prs.lines"
printf '[]\n' > "$gh_race/prs.json"
race_snippet="$(ready_pr "$gh_race")"
(
  source "$HERE/lib/gh-fixture.sh"
  register_pr_between_read_and_write() {
    [[ -e "$gh_race/interleaved" ]] && return 0
    : > "$gh_race/interleaved"
    ( n=13; eval "$race_snippet" )
  }
  n=12
  eval "$race_snippet"
) > /dev/null 2>&1
race_json="$(cat "$gh_race/prs.json")"
race_bad=""
[[ -e "$gh_race/interleaved" ]] || race_bad+="interleaving never happened: the ready-PR registration never went through register_pr; "
[[ "$race_json" == *'pull/12"'* ]] || race_bad+="PR 12 missing from prs.json: $race_json; "
[[ "$race_json" == *'pull/13"'* ]] || race_bad+="PR 13 missing from prs.json: $race_json; "
[[ -z "$race_bad" ]] \
  && ok || no "#588 a ready PR registered by the suite's stubs is not lost when another registers between its read of the PR lines and its write of prs.json ( $race_bad)"

bad=""
for mode in stop continue; do
  gh10="$work/gh10-$mode"
  solvable_fixture "$gh10" 11 12 13
  rm -rf .tdd/wt/11
  bail_record="$work/bail-$mode"
  bail_stub="$work/claude-bail-$mode"
  conductor_stub "$bail_stub" <<STUB
echo "start \$n" >> "$bail_record"
case "\$n" in
  11)
    mkdir -p ".tdd/wt/11/.tdd"
    printf '%s\n' '{"ts": 1, "issue": "11", "actor": "conductor", "phase": "develop-red", "step": "1", "event": "bail", "attempt": "1", "skill_commit": "", "cause": "revise-budget"}' \
      >> ".tdd/wt/11/.tdd/events.jsonl"
    $(open_pr "$gh10" true)
    ;;
  12)
    i=0
    while [ "\$i" -lt \$(( ${PATIENCE:-1} * 50 )) ] && ! grep -x 'start 13' "$bail_record" > /dev/null 2>&1; do
      sleep 0.02; i=\$((i + 1))
    done
    echo "end 12" >> "$bail_record"
    $(ready_pr "$gh10")
    ;;
  *)
    $(ready_pr "$gh10")
    ;;
esac
STUB
  flag=()
  [[ "$mode" == continue ]] && flag=(-- --continue-on-bail)
  run_launcher "$gh10" "$bail_stub" "$work/bail-$mode.out" VERI_PARALLEL=2 "${flag[@]+"${flag[@]}"}"
  got_bail="$(sort "$bail_record" 2>/dev/null | tr '\n' ',')"
  case "$mode" in
    stop)     want_bail="end 12,start 11,start 12," ;;
    continue) want_bail="end 12,start 11,start 12,start 13," ;;
  esac
  twelve_done="$(grep -xF '#12 — done https://example.test/pull/12' "$work/bail-$mode.out")"
  if [[ "$got_bail" != "$want_bail" || -z "$twelve_done" ]]; then
    bad+=" [$mode: exit=$code, record '$got_bail' want '$want_bail', #12 reported done: $([[ -n "$twelve_done" ]] && echo yes || echo no); output: $(tr '\n' '|' < "$work/bail-$mode.out")]"
  fi
done

[[ -z "$bad" ]] \
  && ok || no "the first bail stops new launches while running conductors finish, and --continue-on-bail keeps launching and skips the bailed number ($bad )"

gh11="$work/gh11"
solvable_fixture "$gh11" 7 8
rm -f "$work/awake-count"

run_launcher "$gh11" "$hang_stub" "$work/kill-stop.out" VERI_RUN_TIMEOUT=60 VERI_AWAKE_CLOCK="$jump_clock" VERI_KILL_POLL=0.01
want_kill_stop="#7 — killed after 60s"
got_kill_stop="$(grep -E '^#[0-9]+ — ' "$work/kill-stop.out")"
expect_lines "the first kill stops new launches: #8 is never launched after #7 is killed" "$want_kill_stop" "$got_kill_stop" "$work/kill-stop.out"

bad=""
for shape in a b; do
  gh12="$work/gh12-$shape"
  solvable_fixture "$gh12" 7
  seen="$work/seen-$shape"
  env_stub="$work/claude-env-$shape"
  conductor_stub "$env_stub" <<STUB
env | grep -E '^VERI_(HEARTBEAT|TIMEOUT|STUCK_RETRIES|POLL)=' | sort > "$seen" || true
$(ready_pr "$gh12")
STUB
  case "$shape" in
    a) caller=(VERI_HEARTBEAT=111 VERI_POLL=0.05 VERI_STUCK_RETRIES=3) ;;
    b) caller=(VERI_TIMEOUT=222) ;;
  esac
  env -u VERI_PARALLEL -u VERI_LABEL -u VERI_PRIORITY_LABEL -u VERI_MAX_ISSUES \
    -u VERI_HEARTBEAT -u VERI_TIMEOUT -u VERI_STUCK_RETRIES -u VERI_POLL \
    VERI_GH_JSON="$gh12" CLAUDE_BIN="$env_stub" "${caller[@]}" \
    "$skill/scripts/parallel-conductors.sh" > "$work/env-$shape.out" 2>&1 && code=0 || code=$?
  want_seen="$(printf '%s\n' "${caller[@]}" | sort)"
  got_seen="$(cat "$seen" 2>/dev/null || echo '<conductor never ran>')"
  if [[ "$got_seen" != "$want_seen" ]]; then
    bad+=" [caller '$(printf '%s' "$want_seen" | tr '\n' ' ')': exit=$code, conductor saw '$(printf '%s' "$got_seen" | tr '\n' ' ')'; output: $(tr '\n' '|' < "$work/env-$shape.out")]"
  fi
done

[[ -z "$bad" ]] \
  && ok || no "the caller's VERI_HEARTBEAT, VERI_TIMEOUT, VERI_STUCK_RETRIES and VERI_POLL reach each conductor exactly as they were, set or unset ($bad )"

gh13="$work/gh13"
solvable_fixture "$gh13" 7
rm -f "$work/step-count"

outer_starts="$work/outer-starts"
step_clock="$work/step-clock"
clock_stub "$step_clock" "$work/step-count" 30 "$outer_starts"

outer_stub="$work/claude-outer"
conductor_stub "$outer_stub" <<STUB
echo "start \$n" >> "$outer_starts"
$(hang)
STUB

run_launcher "$gh13" "$outer_stub" "$work/outer.out" VERI_RUN_TIMEOUT=60 VERI_AWAKE_CLOCK="$step_clock" \
  VERI_KILL_POLL=0.01 VERI_HEARTBEAT=1 VERI_TIMEOUT=1 VERI_STUCK_RETRIES=3
want_outer="$(printf 'start 7\nsupervise[conductor-7]: killed-stuck — hard timeout 60s exceeded')"
got_outer="$(cat "$outer_starts" 2>/dev/null; grep -E '^supervise\[conductor-7\]: (retry|killed-stuck|failure|success)' "$work/outer.out")"
expect_lines "the outer supervisor runs with heartbeat and timeout both VERI_RUN_TIMEOUT and no stuck retries" "$want_outer" "$got_outer" "$work/outer.out"

fresh="$work/fresh"
fresh_repo "$fresh"
status_after_launch() {
  local repo="$1" name="$2"
  solvable_fixture "$work/gh-$name" 7
  record_stub "$work/claude-$name" "$work/$name-record" "$work/gh-$name"
  run_launcher_in "$repo" "$work/gh-$name" "$work/claude-$name" "$work/$name.out"
  got_status="$(git -C "$repo" status --porcelain 2>&1)"
  [[ -s "$work/$name-record" ]] || got_status+="<conductor never ran>"
}
status_after_launch "$fresh" clean
expect_lines "in a target repo that has never seen veri, the caller's git status --porcelain stays empty after a launch" "" "$got_status" "$work/clean.out"

bare_info="$work/no-info"
fresh_repo "$bare_info" --template=
rm -rf "$bare_info/.git/info"
status_after_launch "$bare_info" no-info
expect_lines "a repo with no info/ directory still has an empty git status --porcelain after a launch" "" "$got_status" "$work/no-info.out"

own_exclude="$work/own-exclude"
fresh_repo "$own_exclude"
# hazard: git-init makes info/ from templates, which make test's symlinked git misses on macOS (#581).
mkdir -p "$own_exclude/.git/info"
printf '*.scratch' > "$own_exclude/.git/info/exclude"
for run in 1 2; do
  solvable_fixture "$work/gh16-$run" 7
  record_stub "$work/claude-own-exclude-$run" "$work/own-exclude-record" "$work/gh16-$run"
  run_launcher_in "$own_exclude" "$work/gh16-$run" "$work/claude-own-exclude-$run" "$work/own-exclude-$run.out"
done
got_exclude="$(cat "$own_exclude/.git/info/exclude")"
expect_lines "the caller's exclude keeps its last line intact and gains .tdd/* exactly once over two launches" \
  "$(printf '*.scratch\n.tdd/*')" "$got_exclude" "$work/own-exclude-2.out"

role_repo="$work/role"
fresh_repo "$role_repo"
status_after_launch "$role_repo" role
got_refusals="$(grep -F 'leaf-role:' "$work/role.out" | sort -u)"
[[ -s "$work/role-record" ]] || got_refusals+="<conductor never ran>"
expect_lines "supervising a conductor-<n> prints no leaf-role.sh refusal" "" "$got_refusals" "$work/role.out"

bad=""
for shape in done bailed killed plumbing nothing bad-parallel; do
  repo="$work/exit-$shape"
  fresh_repo "$repo"
  gh18="$work/gh18-$shape"
  vars=()
  issues=(7)
  stub18="$work/claude-exit-$shape"
  case "$shape" in
    done)         want_exit=0 ;;
    bailed)       want_exit=1
                  conductor_stub "$stub18" <<STUB
$(bailed_pr "$gh18")
STUB
                  ;;
    killed)       want_exit=1; rm -f "$work/awake-count"; cp "$hang_stub" "$stub18"
                  vars=(VERI_RUN_TIMEOUT=60 VERI_AWAKE_CLOCK="$jump_clock" VERI_KILL_POLL=0.01) ;;
    plumbing)     want_exit=2; vars=(VERI_PRIORITY_LABEL=) ;;
    nothing)      want_exit=3; issues=() ;;
    bad-parallel) want_exit=2; vars=(VERI_PARALLEL=0) ;;
  esac
  solvable_fixture "$gh18" "${issues[@]+"${issues[@]}"}"
  [[ -e "$stub18" ]] || record_stub "$stub18" "$work/exit-$shape-record" "$gh18"
  run_launcher_in "$repo" "$gh18" "$stub18" "$work/exit-$shape.out" "${vars[@]+"${vars[@]}"}"
  got_file="$(cat "$repo/.tdd/parallel.exit" 2>/dev/null || echo '<missing>')"
  if [[ "$code" != "$want_exit" || "$got_file" != "$want_exit" ]]; then
    bad+=" [$shape: exit=$code want $want_exit, .tdd/parallel.exit '$got_file' want '$want_exit'; output: $(tr '\n' '|' < "$work/exit-$shape.out")]"
  fi
done

[[ -z "$bad" ]] \
  && ok || no "exit 0 all done, 1 a bail or a kill, 2 plumbing, 3 nothing solvable, and .tdd/parallel.exit carries the final code on every exit path ($bad )"

bad=""
for shape in drain bail cap plumbing first-bail; do
  repo="$work/stop-$shape"
  fresh_repo "$repo"
  gh19="$work/gh19-$shape"
  solvable_fixture "$gh19" 7 8
  stub19="$work/claude-stop-$shape"
  vars=()
  case "$shape" in
    drain)      record_stub "$stub19" "$work/stop-$shape-record" "$gh19"
                want_report="$(printf '#7 — done https://example.test/pull/7\n#8 — done https://example.test/pull/8\nstopped: nothing solvable')" ;;
    bail)       conductor_stub "$stub19" <<STUB
$(bailed_pr "$gh19")
STUB
                want_report="$(printf '#7 — bailed https://example.test/pull/7\nstopped: #7 bailed')" ;;
    cap)        record_stub "$stub19" "$work/stop-$shape-record" "$gh19"
                vars=(VERI_MAX_ISSUES=1)
                want_report="$(printf '#7 — done https://example.test/pull/7\nstopped: VERI_MAX_ISSUES reached')" ;;
    plumbing)   record_stub "$stub19" "$work/stop-$shape-record" "$gh19"
                vars=(VERI_PRIORITY_LABEL=)
                want_report="stopped: solvable-issues.sh could not answer" ;;
    first-bail) conductor_stub "$stub19" <<STUB
if [ "\$n" = 8 ]; then
  i=0
  while [ "\$i" -lt \$(( ${PATIENCE:-5} * 50 )) ] && [ ! -e .tdd/conductor-7.exit ]; do
    sleep 0.02; i=\$((i + 1))
  done
  sleep 1
fi
$(bailed_pr "$gh19")
STUB
                vars=(VERI_PARALLEL=2)
                want_report="$(printf '#7 — bailed https://example.test/pull/7\n#8 — bailed https://example.test/pull/8\nstopped: #7 bailed')" ;;
  esac
  run_launcher_in "$repo" "$gh19" "$stub19" "$work/stop-$shape.out" "${vars[@]+"${vars[@]}"}"
  got_report="$(grep -E '^(#[0-9]+ — |stopped: )' "$work/stop-$shape.out")"
  if [[ "$got_report" != "$want_report" ]]; then
    bad+=" [$shape: exit=$code, report '$(printf '%s' "$got_report" | tr '\n' '|')' want '$(printf '%s' "$want_report" | tr '\n' '|')'; output: $(tr '\n' '|' < "$work/stop-$shape.out")]"
  fi
done

[[ -z "$bad" ]] \
  && ok || no "the report prints one line per issue in launch order, then one line naming what stopped the loop ($bad )"

bad=""
declare -A where_code where_report where_file where_ran
ln -s "$skill" "$work/skill-link"
for shape in in-place symlink; do
  repo="$work/where-$shape"
  fresh_repo "$repo"
  gh_where="$work/gh-where-$shape"
  solvable_fixture "$gh_where" 7
  record_stub "$work/claude-where-$shape" "$work/where-$shape-record" "$gh_where"
  where_skill="$skill"
  [[ "$shape" == symlink ]] && where_skill="$work/skill-link"
  skill="$where_skill" run_launcher_in "$repo" "$gh_where" "$work/claude-where-$shape" "$work/where-$shape.out"
  where_code[$shape]="$code"
  where_report[$shape]="$(grep -E '^(#[0-9]+ — |stopped: )' "$work/where-$shape.out")"
  where_file[$shape]="$(cat "$repo/.tdd/parallel.exit" 2>/dev/null || echo '<missing>')"
  where_ran[$shape]="$(cat "$work/where-$shape-record" 2>/dev/null)"
done
want_where="$(printf '#7 — done https://example.test/pull/7\nstopped: nothing solvable')"
for shape in in-place symlink; do
  if [[ "${where_ran[$shape]}" != "start 7" || "${where_report[$shape]}" != "$want_where" \
        || "${where_code[$shape]}" != "${where_code[in-place]}" || "${where_file[$shape]}" != "${where_code[in-place]}" ]]; then
    bad+=" [$shape: exit=${where_code[$shape]} want ${where_code[in-place]}, .tdd/parallel.exit '${where_file[$shape]}', conductor ran '${where_ran[$shape]}' want 'start 7', report '$(printf '%s' "${where_report[$shape]}" | tr '\n' '|')'; output: $(tr '\n' '|' < "$work/where-$shape.out")]"
  fi
done

[[ -z "$bad" ]] \
  && ok || no "run through a symlink to the skill directory and from another working directory, parallel-conductors.sh finds solvable-issues.sh, supervise.sh and run-conductor.sh and answers as it does run in place ($bad )"

scope_loop_md="$HERE/../../SCOPE-LOOP.md"
sentences="$(tr '\n' ' ' < "$scope_loop_md" | tr -s ' ' | sed 's/\. /.\n/g')"
said() {
  local lines="$sentences" pattern
  for pattern in "$@"; do
    lines="$(grep -iE -e "$pattern" <<<"$lines")"
  done
  [[ -n "$lines" ]]
}
bad=""
grep -F '${VERI_PARALLEL:-1}' "$scope_loop_md" > /dev/null \
  || bad+=" [no \${VERI_PARALLEL:-1} read]"
said 'VERI_PARALLEL|(at|is) 1([^0-9]|$)' 'rung 2' '(unchanged|nothing[^.]*chang)' \
  || bad+=" [no sentence says at 1 rung 2 is unchanged]"
said '(above|over|more than|greater than) 1([^0-9]|$)' 'parallel-conductors\.sh' \
  || bad+=" [no sentence says above 1 it runs parallel-conductors.sh]"
said 'parallel-conductors\.sh' 'detach(-| )then(-| )wait' \
  || bad+=" [no sentence says parallel-conductors.sh runs detach-then-wait]"
said 'relay' 'report' \
  || bad+=" [no sentence says the report is relayed]"

[[ -z "$bad" ]] \
  && ok || no "SCOPE-LOOP.md documents VERI_PARALLEL: at 1 rung 2 is unchanged, above 1 it runs parallel-conductors.sh detach-then-wait and relays the report ($bad )"

context_md="$HERE/../../../../CONTEXT.md"
record() {
  awk -v open="$1" '
    hit && (/^$/ || /^[0-9]+\. / || /^## /) { exit }
    $0 ~ open { hit = 1 }
    hit { printf "%s ", $0 }
  ' "$context_md"
}
rung3="$(record '^3[.] [*][*]Parallel[*][*]')"
in_flight="$(record '^[*][*]In flight[*][*]:')"
bad=""
if [[ -z "$rung3" ]]; then
  bad+=" [no rung 3 (**Parallel**) entry in the scope ladder]"
else
  grep -F 'parallel-conductors.sh' <<<"$rung3" > /dev/null \
    || bad+=" [rung 3's entry does not name parallel-conductors.sh]"
fi
if [[ -z "$in_flight" ]]; then
  bad+=" [no **In flight**: glossary entry]"
else
  grep -iE 'local' <<<"$in_flight" | grep -iE 'one invocation' > /dev/null \
    || bad+=" [the In flight entry does not say it is local to one invocation]"
fi
newest_adr=0
for n in $(grep -oE 'ADR-?0*[0-9]+' <<<"$rung3 $in_flight" | grep -oE '[1-9][0-9]*$'); do
  (( n > newest_adr )) && newest_adr=$n
done
(( newest_adr > 24 )) \
  || bad+=" [neither entry names an ADR numbered above 0024]"

[[ -z "$bad" ]] \
  && ok || no "CONTEXT.md records rung 3: its entry names parallel-conductors.sh, In flight is defined as local to one invocation, and a new ADR is cited ($bad )"

bad=""
for value in abc 0 -1 1.5; do
  tag="${value//[^a-z0-9]/_}"
  gh22="$work/gh22-$tag"
  solvable_fixture "$gh22" 7
  capped22="$work/capped22-$tag"
  cap22_stub="$work/claude-cap22-$tag"
  record_stub "$cap22_stub" "$capped22" "$gh22"
  run_launcher "$gh22" "$cap22_stub" "$work/cap22-$tag.out" VERI_MAX_ISSUES="$value"
  named=no
  grep -F 'VERI_MAX_ISSUES' "$work/cap22-$tag.out" | grep -F -- "$value" > /dev/null && named=yes
  if [[ "$code" != 2 || -e "$capped22" || "$named" != yes ]]; then
    bad+=" [VERI_MAX_ISSUES='$value': exit=$code want 2, launched: $([[ -e "$capped22" ]] && echo yes || echo no), named: $named]"
  fi
done

[[ -z "$bad" ]] \
  && ok || no "#505 VERI_MAX_ISSUES not a whole number >= 1 (a word, 0, a negative, a fraction) is exit 2 naming it and the value, with no conductor launched ($bad )"

gh23="$work/gh23"
solvable_fixture "$gh23" 7
capped23="$work/capped23"
cap23_stub="$work/claude-cap23"
record_stub "$cap23_stub" "$capped23" "$gh23"
run_launcher "$gh23" "$cap23_stub" "$work/cap23.out" VERI_MAX_ISSUES=
named=no
grep -F "VERI_MAX_ISSUES must be a whole number >= 1: ''" "$work/cap23.out" > /dev/null && named=yes
[[ "$code" == 2 && ! -e "$capped23" && "$named" == yes ]] \
  && ok || no "#505 VERI_MAX_ISSUES set but empty is exit 2 naming it and the empty value '', with no conductor launched ( [exit=$code want 2, launched: $([[ -e "$capped23" ]] && echo yes || echo no), named: $named] $(cat "$work/cap23.out") )"

bad=""
for value in abc 1.5 -1; do
  tag="${value//[^a-z0-9]/_}"
  gh_budget="$work/gh-budget-$tag"
  solvable_fixture "$gh_budget" 7
  budget_launched="$work/budget-launched-$tag"
  budget_stub="$work/claude-budget-$tag"
  record_stub "$budget_stub" "$budget_launched" "$gh_budget"
  run_launcher "$gh_budget" "$budget_stub" "$work/budget-$tag.out" VERI_CONDUCTOR_CTX_BUDGET="$value"
  named=no
  grep -F 'VERI_CONDUCTOR_CTX_BUDGET' "$work/budget-$tag.out" > /dev/null && named=yes
  if [[ "$code" != 2 || -e "$budget_launched" || "$named" != yes ]]; then
    bad+=" [VERI_CONDUCTOR_CTX_BUDGET='$value': exit=$code want 2, launched: $([[ -e "$budget_launched" ]] && echo yes || echo no), named: $named]"
  fi
done

[[ -z "$bad" ]] \
  && ok || no "VERI_CONDUCTOR_CTX_BUDGET not a whole number (a word, a fraction, a negative) is exit 2 naming it, with no conductor launched ($bad )"

gh24="$work/gh24"
solvable_fixture "$gh24" 7 8 9
capped24="$work/capped24"
cap24_stub="$work/claude-cap24"
record_stub "$cap24_stub" "$capped24" "$gh24"
run_launcher "$gh24" "$cap24_stub" "$work/cap24.out"
want24="$(printf 'start 7\nstart 8\nstart 9')"
got24="$(cat "$capped24" 2>/dev/null)"
[[ "$code" == 0 && "$got24" == "$want24" ]] \
  && ok || no "#505 VERI_MAX_ISSUES unset applies no cap and launches every solvable issue ( [exit=$code want 0, launched '$(printf '%s' "$got24" | tr '\n' ',')' want '$(printf '%s' "$want24" | tr '\n' ',')'] $(cat "$work/cap24.out") )"

refusing_gh="$work/graphql-refusing-bin"
mkdir -p "$refusing_gh"
cat > "$refusing_gh/gh" <<'STUB'
#!/bin/sh
refusal='GitHub GraphQL is not available from Claude Code sessions; use the REST API (gh api repos/{owner}/{repo}/...)'
if [ "$GH_GRAPHQL" = refused ]; then
  case "$1" in
    issue|pr|repo) echo "HTTP 403: $refusal" >&2; exit 1 ;;
  esac
  case "$*" in
    "api graphql"*) echo "HTTP 403: $refusal" >&2; exit 1 ;;
  esac
fi
case "$*" in
  "issue list"*) exec cat "$GH_FX/issues.json" ;;
  "pr list"*) exec cat "$GH_FX/prs.json" ;;
  *-q*|*--jq*|*--template*) ;;
  "api "*[?\&]page=[!1]*|"api "*[?\&]page=1?*) echo '[]'; exit 0 ;;
  "api "*"repos/{owner}/{repo}/issues"*) exec cat "$GH_FX/rest-issues.json" ;;
  "api "*"repos/{owner}/{repo}/pulls"*) exec cat "$GH_FX/rest-pulls.json" ;;
esac
echo "gh stub: unexpected call: gh $*" >&2
exit 1
STUB
chmod +x "$refusing_gh/gh"

graphql_run() {  # graphql_run <working|refused>; sets $out and $code
  local fx="$work/gh25-$1" stub="$work/claude-gh25-$1"
  mkdir -p "$fx"
  printf '[]\n' > "$fx/prs.json"
  printf '[]\n' > "$fx/rest-pulls.json"
  printf '%s\n' '[{"number": 7, "title": "issue 7", "labels": [{"name": "ready-for-agent"}], "state": "OPEN", "body": "## Blocked by\n\nNone.\n"}]' > "$fx/issues.json"
  printf '%s\n' '[{"number": 7, "title": "issue 7", "labels": [{"id": 1, "name": "ready-for-agent", "color": "ededed"}], "state": "open", "body": "## Blocked by\n\nNone.\n"}]' > "$fx/rest-issues.json"
  conductor_stub "$stub" <<STUB
mkdir -p ".tdd/wt/\$n/.tdd"
printf '%s\n' '$bail_event' >> ".tdd/wt/\$n/.tdd/events.jsonl"
printf '[{"body": "Closes #%s", "state": "OPEN", "isDraft": true, "url": "https://example.test/pull/%s"}]\n' "\$n" "\$n" > "$fx/prs.json"
printf '[{"number": 906, "body": "Closes #906", "state": "open", "draft": true, "html_url": "https://example.test/pull/906", "url": "https://api.github.test/repos/o/r/pulls/906"}]\n[{"number": 907, "body": "Closes #%s", "state": "open", "draft": true, "html_url": "https://example.test/pull/%s", "url": "https://api.github.test/repos/o/r/pulls/907"}]\n' "\$n" "\$n" > "$fx/rest-pulls.json"
STUB
  run_launcher "" "$stub" "$work/gh25-$1.out" PATH="$refusing_gh:$PATH" GH_GRAPHQL="$1" GH_FX="$fx"
  out="$(grep -E '^(#[0-9]+ — |stopped: )' "$work/gh25-$1.out")"
}

graphql_run working; working="$out" working_code="$code"
graphql_run refused
[[ "$working_code" == 1 && "$working" == "$(printf '#7 — bailed https://example.test/pull/7\nstopped: #7 bailed')" \
   && "$code" == "$working_code" && "$out" == "$working" ]] \
  && ok || no "#568 against a gh that refuses GraphQL with the 403 and answers REST in two pages, the draft PR on the second, parallel-conductors.sh prints the same report and exit code as against a working gh ( [working gh: exit=$working_code want 1, report '$(printf '%s' "$working" | tr '\n' '|')' want '#7 — bailed https://example.test/pull/7|stopped: #7 bailed'; GraphQL refused: exit=$code want $working_code, report '$(printf '%s' "$out" | tr '\n' '|')' want the same] $(tr '\n' '|' < "$work/gh25-refused.out") )"

pr_pages=(
  '{"number": 901, "body": "Closes #901", "state": "open", "draft": true, "html_url": "https://example.test/pull/901"}, {"number": 902, "body": "", "state": "open", "draft": false, "html_url": "https://example.test/pull/902"}'
  '{"number": 903, "body": "Closes #903", "state": "open", "draft": false, "html_url": "https://example.test/pull/903"}, {"number": 904, "body": "", "state": "open", "draft": true, "html_url": "https://example.test/pull/904"}'
  '{"number": 905, "body": "Closes #%s", "state": "open", "draft": true, "html_url": "https://example.test/pull/%s"}'
)
proxy_gh="$work/proxy-refusing-bin"
mkdir -p "$proxy_gh"
cat > "$proxy_gh/gh" <<'STUB'
#!/bin/sh
proxy='gh: Numeric-ID repository paths (repositories/{id}/...) are not supported through this proxy. Use repos/{owner}/{repo}/... endpoints instead. (HTTP 403)'
case "$1" in
  issue|pr|repo) echo "HTTP 403: GitHub GraphQL is not available from Claude Code sessions" >&2; exit 1 ;;
  api) shift ;;
  *) echo "gh stub: unexpected call: gh $*" >&2; exit 1 ;;
esac
paginate="" path=""
for arg in "$@"; do
  case "$arg" in
    --paginate) paginate=1 ;;
    -*) echo "gh stub: unsupported flag $arg" >&2; exit 1 ;;
    *) path="$arg" ;;
  esac
done
case "$path" in
  *repositories/*) echo "$proxy" >&2; exit 1 ;;
  "repos/{owner}/{repo}/issues"*) list=issues ;;
  "repos/{owner}/{repo}/pulls"*) list=pulls ;;
  *) echo "gh stub: unexpected path $path" >&2; exit 1 ;;
esac
page="$(printf '%s\n' "$path" | sed -n 's/.*[?&]page=\([0-9][0-9]*\).*/\1/p')"
[ -n "$page" ] || page=1
if [ -f "$GH_FX/$list-$page.json" ]; then cat "$GH_FX/$list-$page.json"; else echo '[]'; fi
if [ -n "$paginate" ] && [ -f "$GH_FX/$list-$((page + 1)).json" ]; then echo "$proxy" >&2; exit 1; fi
exit 0
STUB
chmod +x "$proxy_gh/gh"

paged_run() {  # paged_run <one|three>; sets $out and $code
  local fx="$work/gh26-$1" stub="$work/claude-gh26-$1" i
  mkdir -p "$fx"
  printf '%s\n' '[{"number": 7, "title": "issue 7", "labels": [{"id": 1, "name": "ready-for-agent", "color": "ededed"}], "state": "open", "body": "## Blocked by\n\nNone.\n"}]' > "$fx/issues-1.json"
  {
    printf '%s\n' "mkdir -p \".tdd/wt/\$n/.tdd\""
    printf '%s\n' "printf '%s\\n' '$bail_event' >> \".tdd/wt/\$n/.tdd/events.jsonl\""
    if [[ "$1" == one ]]; then
      printf "printf '[%s]\\\\n' \"\$n\" \"\$n\" > \"%s/pulls-1.json\"\n" "$(IFS=,; printf '%s' "${pr_pages[*]}")" "$fx"
    else
      for i in 0 1 2; do
        printf "printf '[%s]\\\\n' \"\$n\" \"\$n\" > \"%s/pulls-%s.json\"\n" "${pr_pages[i]}" "$fx" "$((i + 1))"
      done
    fi
  } | conductor_stub "$stub"
  run_launcher "" "$stub" "$work/gh26-$1.out" PATH="$proxy_gh:$PATH" GH_FX="$fx"
  out="$(grep -E '^(#[0-9]+ — |stopped: )' "$work/gh26-$1.out")"
}

paged_run one; one_out="$out" one_code="$code"
paged_run three
[[ "$one_code" == 1 && "$one_out" == "$(printf '#7 — bailed https://example.test/pull/7\nstopped: #7 bailed')" \
   && "$code" == "$one_code" && "$out" == "$one_out" ]] \
  && ok || no "#592 against a gh that serves open PRs over three pages on repos/{owner}/{repo}, the draft PR on the third, and refuses repositories/{id} with the proxy's 403, parallel-conductors.sh prints the same report and exit code as against a single-page fixture holding the same PRs ( [single page: exit=$one_code want 1, report '$(printf '%s' "$one_out" | tr '\n' '|')' want '#7 — bailed https://example.test/pull/7|stopped: #7 bailed'; three pages: exit=$code want $one_code, report '$(printf '%s' "$out" | tr '\n' '|')' want the same] $(tr '\n' '|' < "$work/gh26-three.out") )"

finish
