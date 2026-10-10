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

run_launcher "$gh_again" "$again_stub" "$work/again.out" VERI_CONDUCTOR_CTX_BUDGET=100000

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
role_repo="$work/role"
fresh_repo "$role_repo"
status_after_launch "$role_repo" role
got_refusals="$(grep -F 'leaf-role:' "$work/role.out" | sort -u)"
[[ -s "$work/role-record" ]] || got_refusals+="<conductor never ran>"
expect_lines "supervising a conductor-<n> prints no leaf-role.sh refusal" "" "$got_refusals" "$work/role.out"

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

finish
