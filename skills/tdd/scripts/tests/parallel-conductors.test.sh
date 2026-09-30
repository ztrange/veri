#!/usr/bin/env bash
# Unit tests for scripts/parallel-conductors.sh — rung 3's selection layer. Run from a target
# repo's primary checkout, it launches up to VERI_PARALLEL supervised conductors at once over
# the issues solvable-issues.sh prints, and reports one line per issue it launched (#102).
#
# Contract under test (issue #102):
#   parallel-conductors.sh [--repo owner/name] [--continue-on-bail]
#   VERI_PARALLEL=<n>    conductors running at once, default 1. A whole number ≥ 1; anything
#                        else, set-but-empty included, is exit 2 before anything is launched,
#                        because N conductors are N concurrent `claude -p` sessions, billed as
#                        such — a value the script cannot read is never guessed into a spend.
#   VERI_GH_JSON=<dir>   passed through to solvable-issues.sh, so the solvable set is a
#                        fixture and no case reaches GitHub.
#   CLAUDE_BIN=<path>    passed through to every conductor: here a stub that records that it
#                        ran, which is what "a conductor was launched" means to these cases.
#
# Run: scripts/tests/parallel-conductors.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
PARALLEL="$HERE/../parallel-conductors.sh"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
source "$HERE/lib/harness.sh"

fresh_repo() {
  local dir="$1"
  shift
  git init -q -b main "$@" "$dir" >/dev/null 2>&1
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
  env -u VERI_PARALLEL -u VERI_LABEL -u VERI_PRIORITY_LABEL -u VERI_MAX_ISSUES \
    VERI_GH_JSON="$gh" CLAUDE_BIN="$stub" VERI_POLL=0.05 "${vars[@]+"${vars[@]}"}" \
    "$skill/scripts/parallel-conductors.sh" "$@" > "$out" 2>&1 && code=0 || code=$?
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
printf '{"body": "Closes #%s", "state": "OPEN", "isDraft": $2, "url": "https://example.test/pull/%s"}\n' "\$n" "\$n" >> "$1/prs.lines"
printf '[%s]\n' "\$(paste -sd, "$1/prs.lines")" > "$1/prs.json"
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
  (cd "$repo" && run_launcher "$work/gh-$name" "$work/claude-$name" "$work/$name.out"; echo "$code" > "$work/$name.code")
  code="$(cat "$work/$name.code")"
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
# hazard: git init makes info/ from templates, which make test's symlinked git misses on macOS (#581).
mkdir -p "$own_exclude/.git/info"
printf '*.scratch' > "$own_exclude/.git/info/exclude"
for run in 1 2; do
  solvable_fixture "$work/gh16-$run" 7
  record_stub "$work/claude-own-exclude-$run" "$work/own-exclude-record" "$work/gh16-$run"
  (cd "$own_exclude" && run_launcher "$work/gh16-$run" "$work/claude-own-exclude-$run" "$work/own-exclude-$run.out"; echo "$code" > "$work/own-exclude.code")
done
code="$(cat "$work/own-exclude.code")"
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
  (cd "$repo" && run_launcher "$gh18" "$stub18" "$work/exit-$shape.out" "${vars[@]+"${vars[@]}"}"; echo "$code" > "$work/exit-$shape.code")
  code="$(cat "$work/exit-$shape.code")"
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
  (cd "$repo" && run_launcher "$gh19" "$stub19" "$work/stop-$shape.out" "${vars[@]+"${vars[@]}"}"; echo "$code" > "$work/stop-$shape.code")
  code="$(cat "$work/stop-$shape.code")"
  got_report="$(grep -E '^(#[0-9]+ — |stopped: )' "$work/stop-$shape.out")"
  if [[ "$got_report" != "$want_report" ]]; then
    bad+=" [$shape: exit=$code, report '$(printf '%s' "$got_report" | tr '\n' '|')' want '$(printf '%s' "$want_report" | tr '\n' '|')'; output: $(tr '\n' '|' < "$work/stop-$shape.out")]"
  fi
done

[[ -z "$bad" ]] \
  && ok || no "the report prints one line per issue in launch order, then one line naming what stopped the loop ($bad )"

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

finish
