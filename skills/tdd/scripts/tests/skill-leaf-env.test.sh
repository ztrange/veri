#!/usr/bin/env bash
# Unit tests for the environment a leaf inherits from the launch lines skills/tdd/SKILL.md
# prescribes: it runs the launch lines it finds there against a stub `claude`, and asks the
# leaf at the far end what it can see.
#
# Contract under test:
#   Every launch line in SKILL.md that sends a leaf through supervise.sh into run-leaf.sh,
#   run with the document's own variables supplied, gives the `claude` process at the far
#   end VERI_TEST_CMD carrying the run's test command — and leaves an event log whose every
#   line carries the run's issue and step.
#
# Run: skills/tdd/scripts/tests/skill-leaf-env.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"
SCRIPTS="$(cd "$HERE/.." && pwd)"

skill_md="skills/tdd/SKILL.md"
md="$ROOT/$skill_md"


source "$HERE/lib/harness.sh"

problem() {
  problems+=("$skill_md:$lineno $1:$line")
}

WORK="$(scratch_dir)"
stub="$WORK/stub"       # the fake `claude` every launch below ends in
run="$WORK/run"         # one tree per launch line, named for its leaf
mkdir -p "$stub" "$run"

scripts_fingerprint() {
  ( cd "$SCRIPTS" && find ./*.sh lib prompts -type f -exec cksum {} + | LC_ALL=C sort -k3 )
}
SCRIPTS_BEFORE="$(scripts_fingerprint)"

SENTINEL='make sentinel-test-cmd'

SENTINEL_ISSUE=143
LITERAL_STEP='A title naming `kill %1`, the "blind" verifier, $HOME and the shell s own job spec'
SENTINEL_STEP="${LITERAL_STEP/shell s own/shell\'s own}"

cleared_run_context=(env -u VERI_TEST_CMD -u VERI_ISSUE -u VERI_STEP)

claude_stub "$stub" "$(cat <<'STUB'
printf '%s\n' "${VERI_TEST_CMD-<unset>}" > "$SEEN"
printf '%s\n' "${VERI_STEP-<unset>}" > "$SEEN.step"
printf '%s\n' '{"type":"result","subtype":"success","is_error":false,"result":"ok"}'
STUB
)"


launch_over() {
  local pidfile pid found=0
  for pidfile in "$1"/.tdd/*.pid; do
    [[ -f "$pidfile" ]] || continue
    found=1
    pid="$(cat "$pidfile" 2>/dev/null)" || continue
    kill -0 "$pid" 2>/dev/null && return 1
  done
  (( found ))
}

completion_landed() {
  local exitfile
  for exitfile in "$1"/.tdd/*.exit; do
    [[ -f "$exitfile" ]] && return 0
  done
  return 1
}

plant_ledger() {
  printf '# Plan for #%s\n\n- [ ] %s\n' "$SENTINEL_ISSUE" "$2" > "$1/.tdd/issue-$SENTINEL_ISSUE.md"
}

plant_ticked_ledger() {
  printf '# Plan for #%s\n\n- [x] %s ⟂ refactor pending\n- [ ] a later step the run has not reached\n' \
    "$SENTINEL_ISSUE" "$2" > "$1/.tdd/issue-$SENTINEL_ISSUE.md"
}

LAUNCH_RECORD="$WORK/launch-record"

note_launch() {
  local shape=plain ledger="$1/.tdd/issue-$SENTINEL_ISSUE.md"
  [[ "$line" == *detach-leaf.sh* ]] || return 0
  if grep -F 'refactor pending' "$ledger" > /dev/null 2>&1; then
    shape=ticked
  elif grep -F '[x]' "$ledger" > /dev/null 2>&1; then
    shape=done
  fi
  printf '%s\t%s\t%s\n' "$lineno" "$shape" "$line" >> "$LAUNCH_RECORD"
}

launched_beside() {
  local shape=plain
  [[ "$2" != plant_ticked_ledger ]] || shape=ticked
  grep -Fx -- "$1"$'\t'"$shape"$'\t'"$3" "$LAUNCH_RECORD" > /dev/null 2>&1
}

launched_test_cmd() {
  local leaf="$1" launch="$2"
  shift 2
  local dir="$run/$lineno-$leaf"
  local seen="$dir/seen"
  mkdir -p "$dir/.tdd"
  printf '%s\t%s\n' "$lineno" "$line" > "$dir/origin"
  if [[ "$leaf" == develop-refactor ]]; then
    plant_ticked_ledger "$dir" "$SENTINEL_STEP"
  else
    plant_ledger "$dir" "$SENTINEL_STEP"
  fi
  note_launch "$dir"
  local file
  for file in "$@"; do
    printf 'the %s this launch names, which the stub never reads\n' "$file" > "$dir/$file"
  done
  ( cd "$dir" && "${cleared_run_context[@]}" \
      S="$SCRIPTS" CLAUDE_BIN="$stub/claude" SEEN="$seen" \
      VERI_STUCK_RETRIES=0 VERI_NO_VERDICT_RETRIES=0 VERI_HEARTBEAT=30 VERI_TIMEOUT=60 VERI_POLL=0.2 \
      bash -c "$launch" ) >/dev/null 2>&1
  local deadline=$(( SECONDS + 60 ))
  until [[ -f "$dir/.tdd/$leaf.exit" ]]; do
    launch_over "$dir" && completion_landed "$dir" && break
    (( SECONDS >= deadline )) && break
    sleep 0.2
  done
  local answer
  answer="$(cat "$seen" 2>/dev/null)" || { echo '<no leaf ran>'; return; }
  [[ -f "$dir/.tdd/$leaf.exit" ]] || { echo "<no completion file under leaf $leaf>"; return; }
  printf '%s\n' "$answer"
}

expect_sentinel() {
  local leaf="$1" got
  got="$(launched_test_cmd "$@")"
  [[ "$got" == "$SENTINEL" ]] ||
    problem "launches $leaf, whose leaf saw VERI_TEST_CMD=$got, want $SENTINEL"
}

runnable() {
  local launch="$1" step="${2:-$LITERAL_STEP}"
  launch="${launch//<test-cmd>/$SENTINEL}"
  launch="${launch//<phase>/red}"
  launch="${launch//<k>/1}"
  launch="${launch//<n>/$SENTINEL_ISSUE}"
  launch="${launch//<STEP>/$step}"
  launch="${launch//<test-path>/probe.test.sh}"
  launch="${launch//<target-test-id>/probe-target}"
  launch="${launch//<green-sha>/0123abc}"  # refactor's 4th slot must be a sha (#151)
  launch="${launch//<fast-cmd>/make probe-fast}"  # green's --fast-cmd (#341)
  launch="${launch//<onto-sha>/0123abc}"  # rebase's two slots must be shas too (#238)
  launch="${launch//<pre-rebase-sha>/4567def}"
  launch="${launch//<base-sha>/89abcde}"
  launch="${launch//<conflicting-files>/probe.txt}"
  launch="${launch//\[target\]/probe-target}"
  [[ "$launch" != *'<'*'>'* ]] || return 1
  printf '%s\n' "$launch"
}

no_launch() {
  problems+=("$skill_md has no line launching $1 — the launch this case is about could not be found")
}

take_line() {
  lineno="${1%%:*}"
  line="${1#*:}"
  launch="$(runnable "$line" "${2-}")" || {
    problem "names a placeholder this probe cannot supply, so its launch could not be run"
    return 1
  }
}

scan_launches() {
  local pattern="$1" shape="$2" check="$3"
  local lines numbered lineno line launch
  lines="$(grep -nE "$pattern" "$md")"
  if [[ -z "$lines" ]]; then
    no_launch "$shape"
    return
  fi
  while IFS= read -r numbered; do
    [[ -n "$numbered" ]] || continue
    take_line "$numbered" || continue
    "$check" "$launch"
  done <<< "$lines"
}

run_case() {
  local name="$1"
  shift
  local problems=()
  "$@"
  report "$name"
}

only_complaint_about() {
  local needle="$1" asked="$2"
  local got=( "${problems[@]}" )
  problems=()
  if [[ "${#got[@]}" -ne 1 || "${got[0]}" != *"$needle"* ]]; then
    problems+=("$asked reported: ${got[*]:-<nothing>}")
  fi
}

arg_after() {
  local script="${1//./\\.}"
  sed -E "s/.*$script +([^ ]+).*/\1/" <<< "$2"
}

check_developer_launch() {
  local launch="$1" leaf prompt
  leaf="$(arg_after supervise.sh "$launch")"
  prompt="$(head -1 < <(grep -oE '\.tdd/[A-Za-z0-9_.-]+\.prompt' <<< "$launch"))"
  if [[ -z "$prompt" ]]; then
    problem "launches $leaf with no .tdd/<name>.prompt file to run, so its leaf could not be started"
    return
  fi
  expect_sentinel "$leaf" "$launch" "$prompt"
}

run_case "every leaf $skill_md launches through supervise.sh sees the run's test command as VERI_TEST_CMD" \
  scan_launches \
  '\$S/supervise\.sh .*run-leaf\.sh' \
  "a leaf through supervise.sh into run-leaf.sh" \
  check_developer_launch

check_verifier_launch() {
  local launch="$1" clean phase spec subject
  clean="$(sed -E "s/ --(step|fast-cmd) ('[^']*'|\"[^\"]*\")//g" <<< "$launch")"
  read -r phase spec subject _ <<< "${clean#*run-verdict.sh }"
  expect_sentinel "verify-$phase" "$launch" "$spec" "$subject"
}

run_case "every verifier $skill_md launches through verify.sh sees the run's test command as VERI_TEST_CMD" \
  scan_launches \
  '\$S/detach-leaf\.sh .*\$S/run-verdict\.sh .*\.tdd/issue-<n>-spec\.md' \
  "a verifier through run-verdict.sh against a spec file" \
  check_verifier_launch

bad_context() {
  python3 -c '
import sys, json
log, issue, step = sys.argv[1], sys.argv[2], sys.argv[3]
bad = []
lines = [l for l in open(log).read().splitlines() if l.strip()]
for line in lines:
    try:
        obj = json.loads(line)
    except Exception:
        bad.append("unparseable event line")
        continue
    if obj.get("issue") != issue or obj.get("step") != step:
        bad.append("%s issue=%r step=%r" % (obj.get("event"), obj.get("issue"), obj.get("step")))
if not lines:
    print("<<no event line written>>")
elif bad:
    print("; ".join(bad))
' "$1" "$SENTINEL_ISSUE" "$2" 2>/dev/null || echo '<<no event log>>'
}

scan_launch_trees() {
  local trees tree lineno line complaint want_step
  trees=( "$run"/* )
  if [[ ! -d "${trees[0]}" ]]; then
    problems+=("no launch line was run, so no leaf's events could be read")
  else
    for tree in "${trees[@]}"; do
      if [[ ! -f "$tree/origin" ]]; then
        problems+=("${tree#$run/} was launched with no record of which line of $skill_md ran it")
        continue
      fi
      IFS=$'\t' read -r lineno line < "$tree/origin"
      want_step=""
      [[ "$line" != *VERI_STEP* ]] || want_step="$SENTINEL_STEP"
      [[ "$line" != *"VERI_STEP='<STEP>'"* ]] || want_step="$LITERAL_STEP"
      complaint="$(bad_context "$tree/.tdd/events.jsonl" "$want_step")"
      [[ -z "$complaint" ]] ||
        problem "leaves events that do not carry issue=$SENTINEL_ISSUE step='$want_step' ($complaint)"
    done
  fi
}

run_case "every leaf $skill_md launches leaves events carrying the run's issue and step" \
  scan_launch_trees

scan_launch_step_env() {
  local trees tree lineno line want_step got
  trees=( "$run"/* )
  if [[ ! -d "${trees[0]}" ]]; then
    problems+=("no launch line was run, so no leaf's VERI_STEP could be read")
    return
  fi
  for tree in "${trees[@]}"; do
    [[ -f "$tree/origin" ]] || continue
    IFS=$'\t' read -r lineno line < "$tree/origin"
    [[ "$line" != *' verdict-plan '* ]] || continue
    want_step="$SENTINEL_STEP"
    [[ "$line" != *"VERI_STEP='<STEP>'"* ]] || want_step="$LITERAL_STEP"
    got="$(cat "$tree/seen.step" 2>/dev/null)" || got='<no leaf ran>'
    [[ "$got" == "$want_step" ]] ||
      problem "launches ${tree#$run/}, whose leaf saw VERI_STEP=<$got>, want <$want_step>"
  done
}

run_case "every leaf $skill_md launches with VERI_STEP set sees the run's step as VERI_STEP" \
  scan_launch_step_env

scan_fixture_naming() {
  local fixture i=0 lineno line launch
  read -r -d '' fixture <<'FIXTURE' || true
VERI_TEST_CMD='<test-cmd>' VERI_ISSUE=<n> VERI_STEP='<STEP>' $S/detach-leaf.sh $S/supervise.sh fixture-good-1 $S/run-leaf.sh .tdd/fixture-good-1.prompt
VERI_ISSUE=<n> VERI_STEP='<STEP>' $S/detach-leaf.sh $S/supervise.sh fixture-bad $S/run-leaf.sh .tdd/fixture-bad.prompt
VERI_TEST_CMD='<test-cmd>' VERI_ISSUE=<n> VERI_STEP='<STEP>' $S/detach-leaf.sh $S/supervise.sh fixture-good-2 $S/run-leaf.sh .tdd/fixture-good-2.prompt
FIXTURE
  while IFS= read -r line; do
    [[ -n "$line" ]] || continue
    i=$((i + 1))
    lineno="fixture-naming-$i"
    launch="$(runnable "$line")" || {
      problem "fixture-naming line $i names a placeholder this probe cannot supply"
      continue
    }
    check_developer_launch "$launch"
  done <<< "$fixture"
  only_complaint_about "fixture-bad" "the fixture's three launches (only the middle one broken)"
}

run_case "a single broken launch line is reported by name, alone, while unrelated lines report nothing" \
  scan_fixture_naming

_fixture_report_case() {
  local lineno="999" line="sample line text"
  local problems=()
  problem "sample problem"
  report "sample case"
}

scan_message_format() {
  local out want
  out="$(
    pass=0; fail=0
    _fixture_report_case
    echo "----"
    echo "${pass:-0} passed, $fail failed"
  )"
  want=$'FAIL - sample case\n    skills/tdd/SKILL.md:999 sample problem:sample line text\n----\n0 passed, 1 failed'
  [[ "$out" == "$want" ]] ||
    problems+=("report()'s and problem()'s output shape has drifted: got $(tr '\n' '|' <<< "$out")")
}

run_case "report()'s FAIL line, its indented problem line, and the count line keep their shape" \
  scan_message_format

developer_launch_fixture() {
  local tag="$1"
  lineno="$tag-1"
  leaf="fixture-$tag"
  prompt=".tdd/$leaf.prompt"
  read -r line <<FIXTURE
VERI_TEST_CMD='<test-cmd>' VERI_ISSUE=<n> VERI_STEP='<STEP>' \$S/detach-leaf.sh \$S/supervise.sh $leaf \$S/run-leaf.sh $prompt
FIXTURE
  launch="$(runnable "$line")" || {
    problems+=("the $tag fixture names a placeholder this probe cannot supply")
    return 1
  }
}

scan_wrong_leaf_name() {
  local lineno line launch leaf prompt
  developer_launch_fixture wrong-leaf-name || return
  expect_sentinel "$leaf-no-such-leaf" "$launch" "$prompt"
  only_complaint_about "$line" "a launch whose leaf name no completion file is written under"
}

run_case "a launch writing no completion file under the derived leaf name is reported, naming that line" \
  scan_wrong_leaf_name

ANSWER_CEILING=15

scan_answer_latency() {
  local lineno line launch leaf prompt started elapsed
  developer_launch_fixture answer-latency || return
  started=$SECONDS
  launched_test_cmd "$leaf-no-such-leaf" "$launch" "$prompt" >/dev/null
  elapsed=$(( SECONDS - started ))
  (( elapsed < ANSWER_CEILING )) ||
    problems+=("a launch whose derived leaf name no completion file is written under was answered after ${elapsed}s, want under ${ANSWER_CEILING}s: the wait ran on past the supervisor that had already exited")
}

run_case "a derived leaf name no launch writes is answered once its supervisor is gone, not at the end of the wait budget" \
  scan_answer_latency

stage_recorder() {
  stage="$WORK/$1-scripts"
  seen="$WORK/$1-seen"
  tree="$WORK/$1-tree"
  mkdir -p "$stage" "$tree/.tdd"
  local script
  for script in "$SCRIPTS"/*.sh "$SCRIPTS/lib" "$SCRIPTS/prompts" "$SCRIPTS/veri"; do
    [[ "${script##*/}" == detach-leaf.sh ]] || ln -s "$script" "$stage/"
  done
  ln -s "$RECORDERS/detach-leaf.sh" "$stage/detach-leaf.sh"
}

write_recorders() {
  RECORDERS="$WORK/recorders"
  mkdir -p "$RECORDERS"
  cat > "$RECORDERS/detach-leaf.sh" <<'STUB'
#!/bin/sh
printf '%s\n' "${VERI_STEP-<unset>}" > "$SEEN"
step='<no --step argument>'
while [ "$#" -gt 0 ]; do
  if [ "$1" = --step ]; then step="${2-<--step with no value>}"; break; fi
  shift
done
printf '%s\n' "$step" > "$SEEN.argv"
STUB
  cat > "$RECORDERS/title.sh" <<'STUB'
#!/bin/sh
out="$SEEN.$(basename "$0" .sh)"
printf '%s\n' "${VERI_STEP-<unset>}" > "$out"
for a in "$@"; do printf '%s\n' "$a" >> "$out"; done
STUB
  chmod +x "$RECORDERS/detach-leaf.sh" "$RECORDERS/title.sh"
}

write_recorders

scan_stage_links() {
  local stage seen tree script name
  stage_recorder stage-links
  for script in "$SCRIPTS"/*.sh "$SCRIPTS"/lib/*; do
    name="${script#"$SCRIPTS"/}"
    [[ "$name" == detach-leaf.sh ]] && continue
    [[ "$stage/$name" -ef "$script" ]] ||
      problems+=("the stage reaches $name by a copy, want a link to $script")
  done
}

run_case "a stage reaches every script it does not replace by a link to the script under test, never a copy" \
  scan_stage_links

run_staged() {
  err="$( cd "$tree" && "${cleared_run_context[@]}" \
            S="$stage" SEEN="$seen" bash -c "$launch" 2>&1 >/dev/null )"
  got="$(cat "$seen" 2>/dev/null)" || got="$1"
  argv="$(cat "$seen.argv" 2>/dev/null)" || argv='<no verifier was launched>'
}
run_recorded() { note_launch "$tree"; run_staged "$1"; }

APOSTROPHE_STEP="A background process is killed by the pid recorded when it started, never by that shell's own job spec"

scan_step_title() {
  local title="${1:-$APOSTROPHE_STEP}" tag="${2:-step-title}"
  local leaf="${3:-develop-red}" planter="${4:-plant_ledger}"
  local lineno line numbered launch stage seen tree err got argv
  numbered="$(head -1 < <(grep -nE "\\\$S/detach-leaf\\.sh .*\\\$S/supervise\\.sh $leaf \\\$S/run-leaf\\.sh" "$md"))"
  if [[ -z "$numbered" ]]; then
    no_launch "$leaf through supervise.sh into run-leaf.sh"
    return
  fi
  take_line "$numbered" "$title" || return
  launched_beside "$lineno" "$planter" "$line" && return
  stage_recorder "$tag"
  printf 'the prompt this launch names, which the recorder never reads\n' \
    > "$tree/.tdd/$leaf.prompt"
  "$planter" "$tree" "$title"
  run_recorded '<no leaf was launched>'
  [[ "$got" == "$title" ]] ||
    problem "launched with the step title <$title>, whose leaf saw VERI_STEP=<$got> (the launching shell said: ${err//$'\n'//})"
}

run_case "a step title carrying an apostrophe reaches the leaf $skill_md launches with it intact" \
  scan_step_title

EXPANDING_STEP='A title naming `kill %1`, the "blind" verifier and $HOME reaches the leaf as written'

run_case "a step title carrying a dollar sign, a backtick and a double quote reaches the leaf $skill_md launches with it byte-identical (#437)" \
  scan_step_title "$EXPANDING_STEP" expanding-step-title


run_case "a step title carrying a dollar sign, a backtick and a double quote reaches the develop-refactor leaf $skill_md launches after the step is ticked, byte-identical (#437)" \
  scan_step_title "$EXPANDING_STEP" expanding-step-title-refactor develop-refactor plant_ticked_ledger

scan_verdict_step_title() {
  local title="$EXPANDING_STEP" tag=expanding-step-title-verdict
  local lineno line numbered launch stage seen tree err got argv
  numbered="$(head -1 < <(grep -nE '\$S/detach-leaf\.sh .*\$S/supervise\.sh verdict-red \$S/run-verdict\.sh' "$md"))"
  if [[ -z "$numbered" ]]; then
    no_launch "verdict-red through supervise.sh into run-verdict.sh"
    return
  fi
  take_line "$numbered" "$title" || return
  launched_beside "$lineno" plant_ledger "$line" && return
  stage_recorder "$tag"
  plant_ledger "$tree" "$title"
  run_recorded '<no verifier was launched>'
  [[ "$got" == "$title" ]] ||
    problem "launched with the step title <$title>, whose verifier saw VERI_STEP=<$got> (the launching shell said: ${err//$'\n'//})"
  [[ "$argv" == "$title" ]] ||
    problem "launched with the step title <$title>, whose verifier was handed --step <$argv> (the launching shell said: ${err//$'\n'//})"
}

run_case "a step title carrying a dollar sign, a backtick and a double quote reaches the verifier $skill_md launches, byte-identical in VERI_STEP and in --step (#437)" \
  scan_verdict_step_title

ledgers_for() {
  case "$1" in
    *'<'*'>'*|develop-exhausted|develop-reconcile) echo plant_ledger plant_ticked_ledger ;;
    *-refactor) echo plant_ticked_ledger ;;
    *) echo plant_ledger ;;
  esac
}

scan_every_step_title() {
  local title="$EXPANDING_STEP"
  local lines numbered filled lineno line launch leaf planter stage seen tree err got argv
  lines="$(grep -nE '\$S/detach-leaf\.sh .*\$S/supervise\.sh ' "$md" | grep -F 'VERI_STEP=')"
  if [[ -z "$lines" ]]; then
    no_launch "a leaf with VERI_STEP set through detach-leaf.sh and supervise.sh"
    return
  fi
  while IFS= read -r numbered; do
    [[ -n "$numbered" ]] || continue
    filled="${numbered//<name>/probe-leaf}"
    filled="${filled//<cmd> \[args...\]/\$S/run-leaf.sh .tdd/probe-leaf.prompt}"
    take_line "$filled" "$title" || continue
    line="${numbered#*:}"   # what every message quotes stays the document's own spelling
    leaf="$(arg_after supervise.sh "$launch")"
    for planter in $(ledgers_for "$(arg_after supervise.sh "$line")"); do
      launched_beside "$lineno" "$planter" "$line" && continue
      stage_recorder "every-step-title-$lineno-$planter"
      "$planter" "$tree" "$title"
      run_recorded '<no leaf was launched>'
      [[ "$got" == "$title" ]] ||
        problem "launched $leaf beside a ledger from $planter with the step title <$title>, whose leaf saw VERI_STEP=<$got> (the launching shell said: ${err//$'\n'//})"
      [[ "$line" == *--step* ]] || continue
      [[ "$argv" == "$title" ]] ||
        problem "launched $leaf beside a ledger from $planter with the step title <$title>, whose verifier was handed --step <$argv> (the launching shell said: ${err//$'\n'//})"
    done
  done <<< "$lines"
}

run_case "a step title carrying a dollar sign, a backtick and a double quote reaches every other developer and verifier leaf $skill_md launches with it, byte-identical (#437)" \
  scan_every_step_title

DECOY_STEP='a decoy step the ledger holds, which ledger-steps.sh current never names'

scan_current_step_title() {
  local title="$EXPANDING_STEP"
  local lines numbered filled lineno line launch leaf stage seen tree err got argv
  lines="$(grep -nE '\$S/detach-leaf\.sh .*\$S/supervise\.sh ' "$md" | grep -F 'VERI_STEP=' |
           grep -vF -e 'VERI_STEP="$(cat .tdd/issue-<n>.md | $S/next-unchecked.sh)"' \
                    -e 'VERI_STEP="$(cat .tdd/issue-<n>.md | $S/next-pending-refactor.sh)"')"
  if [[ -z "$lines" ]]; then
    no_launch "a leaf whose VERI_STEP reads the current step"
    return
  fi
  cat > "$RECORDERS/ledger-steps.sh" <<'STUB'
#!/bin/sh
case "$1" in current|current-or-last-done) ;; *) exit 2 ;; esac
cat "$SEEN.current"
STUB
  chmod +x "$RECORDERS/ledger-steps.sh"
  while IFS= read -r numbered; do
    [[ -n "$numbered" ]] || continue
    filled="${numbered//<name>/probe-leaf}"
    filled="${filled//<cmd> \[args...\]/\$S/run-leaf.sh .tdd/probe-leaf.prompt}"
    take_line "$filled" "$title" || continue
    line="${numbered#*:}"
    leaf="$(arg_after supervise.sh "$launch")"
    stage_recorder "current-step-title-$lineno"
    rm -f "$stage/ledger-steps.sh"
    ln -s "$RECORDERS/ledger-steps.sh" "$stage/ledger-steps.sh"
    plant_ledger "$tree" "$DECOY_STEP"
    printf '%s\n' "$title" > "$seen.current"
    run_staged '<no leaf was launched>'
    [[ "$got" == "$title" ]] ||
      problem "launched $leaf with ledger-steps.sh current answering <$title>, whose leaf saw VERI_STEP=<$got> (the launching shell said: ${err//$'\n'//})"
    [[ "$line" == *--step* ]] || continue
    [[ "$argv" == "$title" ]] ||
      problem "launched $leaf with ledger-steps.sh current answering <$title>, whose verifier was handed --step <$argv> (the launching shell said: ${err//$'\n'//})"
  done <<< "$lines"
}

run_case "every leaf and verifier launch line in $skill_md reads the step through ledger-steps.sh current, and a title carrying a dollar sign, a backtick and a double quote reaches VERI_STEP and --step byte-identical (#682)" \
  scan_current_step_title

plant_done_ledger() {
  printf '# Plan for #%s\n\n- [x] an earlier step the run finished\n- [x] %s\n' \
    "$SENTINEL_ISSUE" "$1" > "$tree/.tdd/issue-$SENTINEL_ISSUE.md"
}

scan_rebase_verifier_last_done() {
  local title="$EXPANDING_STEP"
  local lineno line numbered launch stage seen tree err got argv
  numbered="$(head -1 < <(grep -nE '\$S/detach-leaf\.sh .*\$S/supervise\.sh verdict-rebase \$S/run-verdict\.sh' "$md"))"
  if [[ -z "$numbered" ]]; then
    no_launch "verdict-rebase through supervise.sh into run-verdict.sh"
    return
  fi
  take_line "$numbered" "$title" || return
  stage_recorder rebase-verifier-last-done
  plant_done_ledger "$title"
  run_staged '<no verifier was launched>'
  [[ "$argv" == "$title" ]] ||
    problem "launched verdict-rebase beside a ledger with every step ticked, whose verifier was handed --step <$argv>, want the last done step <$title> (the launching shell said: ${err//$'\n'//})"
}

run_case "#753 the verify-rebase launch line in $skill_md, run with every ledger step ticked, hands its verifier the last done step's text as --step, byte-identical" \
  scan_rebase_verifier_last_done

scan_rebase_verifier_env_last_done() {
  local title="$EXPANDING_STEP"
  local lineno line numbered launch stage seen tree err got argv
  numbered="$(head -1 < <(grep -nE '\$S/detach-leaf\.sh .*\$S/supervise\.sh verdict-rebase \$S/run-verdict\.sh' "$md"))"
  if [[ -z "$numbered" ]]; then
    no_launch "verdict-rebase through supervise.sh into run-verdict.sh"
    return
  fi
  take_line "$numbered" "$title" || return
  stage_recorder rebase-verifier-env-last-done
  plant_done_ledger "$title"
  run_staged '<no verifier was launched>'
  [[ "$got" == "$title" ]] ||
    problem "launched verdict-rebase beside a ledger with every step ticked, whose verifier saw VERI_STEP=<$got>, want the last done step <$title> (the launching shell said: ${err//$'\n'//})"
}

run_case "#907 the Draft PR step's verdict-rebase launch line in $skill_md, run with every ledger step ticked, gives its verifier the last done step's text as VERI_STEP, byte-identical" \
  scan_rebase_verifier_env_last_done

prompt_step_arg() {
  local rec k
  mapfile -t rec < "$seen.build-develop-prompt" 2>/dev/null || rec=()
  for (( k = 1; k + 1 < ${#rec[@]}; k++ )); do
    [[ "${rec[k]}" != *-spec.md ]] || { printf '%s' "${rec[k+1]}"; return; }
  done
  printf '<no step argument>'
}

scan_develop_last_done() {
  local phase="$1" title="$EXPANDING_STEP"
  local lineno line numbered launch stage seen tree err got argv want
  stage_recorder "develop-$phase-last-done"
  rm -f "$stage/build-develop-prompt.sh"
  ln -s "$RECORDERS/title.sh" "$stage/build-develop-prompt.sh"
  plant_done_ledger "$title"
  numbered="$(head -1 < <(grep -nE "\\\$S/build-develop-prompt\\.sh $phase .*> \\.tdd/develop-$phase\\.prompt" "$md"))"
  numbered="${numbered//<branch>/tdd/probe-branch}"
  numbered="${numbered//<remote-sha>/0123abc}"
  if [[ -z "$numbered" ]]; then
    no_launch "build-develop-prompt.sh $phase into .tdd/develop-$phase.prompt"
  elif take_line "$numbered" "$title"; then
    run_staged '<no prompt was built>'
    want="$(prompt_step_arg)"
    [[ "$want" == "$title" ]] ||
      problem "built the develop-$phase prompt beside a ledger with every step ticked, passing build-develop-prompt.sh the step <$want>, want the last done step <$title> (the launching shell said: ${err//$'\n'//})"
  fi
  numbered="$(head -1 < <(grep -nE "\\\$S/detach-leaf\\.sh .*\\\$S/supervise\\.sh develop-$phase \\\$S/run-leaf\\.sh" "$md"))"
  if [[ -z "$numbered" ]]; then
    no_launch "develop-$phase through supervise.sh into run-leaf.sh"
    return
  fi
  take_line "$numbered" "$title" || return
  run_staged '<no leaf was launched>'
  [[ "$got" == "$title" ]] ||
    problem "launched develop-$phase beside a ledger with every step ticked, whose leaf saw VERI_STEP=<$got>, want the last done step <$title> (the launching shell said: ${err//$'\n'//})"
}

run_case "#892 the Draft PR step's develop-rebase block in $skill_md, run with every ledger step ticked, passes build-develop-prompt.sh rebase and the leaf's VERI_STEP the last done step's text, byte-identical" \
  scan_develop_last_done rebase

run_case "#892 the develop-reconcile block of Reconciling a rejected push in $skill_md, run with every ledger step ticked, passes build-develop-prompt.sh reconcile and the leaf's VERI_STEP the last done step's text, byte-identical" \
  scan_develop_last_done reconcile

scan_revise_last_done() {
  local title="$EXPANDING_STEP"
  local lineno line numbered launch stage seen tree err got argv want which pattern
  stage_recorder revise-last-done
  rm -f "$stage/build-develop-prompt.sh" "$stage/event.sh"
  ln -s "$RECORDERS/title.sh" "$stage/build-develop-prompt.sh"
  ln -s "$RECORDERS/title.sh" "$stage/event.sh"
  plant_done_ledger "$title"
  for which in mark prompt leaf re-verify; do
    case "$which" in
      mark)      pattern='\$S/event\.sh revise budget=' ;;
      prompt)    pattern='\$S/build-develop-prompt\.sh revise <phase> .*> \.tdd/revise-<phase>-<k>\.prompt' ;;
      leaf)      pattern='\$S/detach-leaf\.sh .*\$S/supervise\.sh revise-<phase>-<k> \$S/run-leaf\.sh' ;;
      re-verify) pattern='\$S/detach-leaf\.sh .*\$S/supervise\.sh verdict-<phase> \$S/run-verdict\.sh --step .* --fast-cmd ' ;;
    esac
    numbered="$(head -1 < <(grep -nE "$pattern" "$md"))"
    numbered="${numbered//<REVISE_BUDGET>/3}"
    if [[ -z "$numbered" ]]; then
      no_launch "the revise loop's $which line"
      continue
    fi
    take_line "$numbered" "$title" || continue
    rm -f "$seen" "$seen".*
    run_staged '<no leaf was launched>'
    case "$which" in
      mark)
        got="$(head -1 "$seen.event" 2>/dev/null)" || got='<no mark was made>'
        [[ "$got" == "$title" ]] ||
          problem "marked the revise event beside a ledger with every step ticked with VERI_STEP=<$got>, want the last done step <$title> (the launching shell said: ${err//$'\n'//})" ;;
      prompt)
        want="$(prompt_step_arg)"
        [[ "$want" == "$title" ]] ||
          problem "built the revise prompt beside a ledger with every step ticked, passing build-develop-prompt.sh the step <$want>, want the last done step <$title> (the launching shell said: ${err//$'\n'//})" ;;
      *)
        [[ "$got" == "$title" ]] ||
          problem "launched the revise loop's $which line beside a ledger with every step ticked, whose leaf saw VERI_STEP=<$got>, want the last done step <$title> (the launching shell said: ${err//$'\n'//})" ;;
    esac
  done
}

run_case "#892 the revise loop of Revising on a REJECT in $skill_md, run with every ledger step ticked, passes the revise mark's VERI_STEP, build-develop-prompt.sh revise, the revise leaf's VERI_STEP and the re-verify launch's VERI_STEP the last done step's text, byte-identical" \
  scan_revise_last_done

scan_revise_diff_last_done() {
  local title="$EXPANDING_STEP"
  local lineno line numbered launch stage seen tree err got argv want
  numbered="$(head -1 < <(grep -nE '\$S/build-develop-prompt\.sh revise diff .*> \.tdd/revise-diff-<k>\.prompt' "$md"))"
  if [[ -z "$numbered" ]]; then
    no_launch "build-develop-prompt.sh revise diff into .tdd/revise-diff-<k>.prompt"
    return
  fi
  take_line "$numbered" "$title" || return
  stage_recorder revise-diff-last-done
  rm -f "$stage/build-develop-prompt.sh"
  ln -s "$RECORDERS/title.sh" "$stage/build-develop-prompt.sh"
  plant_done_ledger "$title"
  run_staged '<no prompt was built>'
  want="$(prompt_step_arg)"
  [[ "$want" == "$title" ]] ||
    problem "built the revise diff prompt beside a ledger with every step ticked, passing build-develop-prompt.sh the step <$want>, want the last done step <$title> (the launching shell said: ${err//$'\n'//})"
}

run_case "#907 the revise diff prompt line of Revising on a REJECT in $skill_md, run with every ledger step ticked, passes build-develop-prompt.sh revise diff the last done step's text, byte-identical" \
  scan_revise_diff_last_done

scan_exhausted_last_done() {
  local title="$EXPANDING_STEP"
  local lineno line numbered launch stage seen tree err got argv want which pattern
  stage_recorder exhausted-last-done
  rm -f "$stage/build-develop-prompt.sh" "$stage/event.sh"
  ln -s "$RECORDERS/title.sh" "$stage/build-develop-prompt.sh"
  ln -s "$RECORDERS/title.sh" "$stage/event.sh"
  plant_done_ledger "$title"
  for which in prompt leaf mark; do
    case "$which" in
      prompt) pattern='\$S/build-develop-prompt\.sh exhausted .*> \.tdd/develop-exhausted\.prompt' ;;
      leaf)   pattern='\$S/detach-leaf\.sh .*\$S/supervise\.sh develop-exhausted \$S/run-leaf\.sh' ;;
      mark)   pattern='\$S/event\.sh step-escalated anchor=' ;;
    esac
    numbered="$(head -1 < <(grep -nE "$pattern" "$md"))"
    if [[ -z "$numbered" ]]; then
      no_launch "the revise-exhausted path's $which line"
      continue
    fi
    take_line "$numbered" "$title" || continue
    rm -f "$seen" "$seen".*
    run_staged '<no leaf was launched>'
    case "$which" in
      prompt)
        want="$(prompt_step_arg)"
        [[ "$want" == "$title" ]] ||
          problem "built the exhausted prompt beside a ledger with every step ticked, passing build-develop-prompt.sh the step <$want>, want the last done step <$title> (the launching shell said: ${err//$'\n'//})" ;;
      leaf)
        [[ "$got" == "$title" ]] ||
          problem "launched develop-exhausted beside a ledger with every step ticked, whose leaf saw VERI_STEP=<$got>, want the last done step <$title> (the launching shell said: ${err//$'\n'//})" ;;
      mark)
        got="$(head -1 "$seen.event" 2>/dev/null)" || got='<no mark was made>'
        [[ "$got" == "$title" ]] ||
          problem "marked step-escalated beside a ledger with every step ticked with VERI_STEP=<$got>, want the last done step <$title> (the launching shell said: ${err//$'\n'//})" ;;
    esac
  done
}

run_case "#907 the revise-exhausted path of Revising on a REJECT in $skill_md, run with every ledger step ticked, passes build-develop-prompt.sh exhausted, the develop-exhausted leaf's VERI_STEP and the step-escalated mark's VERI_STEP the last done step's text, byte-identical" \
  scan_exhausted_last_done

scan_bail_last_done() {
  local title="$EXPANDING_STEP"
  local lineno line numbered launch stage seen tree err got argv which pattern rec
  stage_recorder bail-last-done
  rm -f "$stage/preserve-attempt.sh" "$stage/event.sh"
  ln -s "$RECORDERS/title.sh" "$stage/preserve-attempt.sh"
  ln -s "$RECORDERS/title.sh" "$stage/event.sh"
  plant_done_ledger "$title"
  for which in preserve mark; do
    case "$which" in
      preserve) pattern='\$S/preserve-attempt\.sh <n> .* <phase> <attempt> bail$' ;;
      mark)     pattern='\$S/event\.sh bail cause=<cause>' ;;
    esac
    numbered="$(head -1 < <(grep -nE "$pattern" "$md"))"
    numbered="${numbered//<attempt>/1}"
    numbered="${numbered//<cause>/suite-red}"
    if [[ -z "$numbered" ]]; then
      no_launch "Bailing's $which line"
      continue
    fi
    take_line "$numbered" "$title" || continue
    rm -f "$seen" "$seen".*
    run_staged '<not run>'
    case "$which" in
      preserve)
        mapfile -t rec < "$seen.preserve-attempt" 2>/dev/null || rec=()
        got="${rec[2]-<no step argument>}"
        [[ "$got" == "$title" ]] ||
          problem "preserved a bailed attempt beside a ledger with every step ticked, passing preserve-attempt.sh the step <$got>, want the last done step <$title> (the typing shell said: ${err//$'\n'//})" ;;
      mark)
        got="$(head -1 "$seen.event" 2>/dev/null)" || got='<no mark was made>'
        [[ "$got" == "$title" ]] ||
          problem "marked bail beside a ledger with every step ticked with VERI_STEP=<$got>, want the last done step <$title> (the typing shell said: ${err//$'\n'//})" ;;
    esac
  done
}

run_case "#907 Bailing in $skill_md, run with every ledger step ticked, passes preserve-attempt.sh and the bail mark's VERI_STEP the last done step's text, byte-identical" \
  scan_bail_last_done

scan_stop_last_done() {
  local title="$EXPANDING_STEP"
  local lineno line numbered launch stage seen tree err got argv
  stage_recorder stop-last-done
  rm -f "$stage/event.sh"
  ln -s "$RECORDERS/title.sh" "$stage/event.sh"
  plant_done_ledger "$title"
  numbered="$(head -1 < <(grep -nE '\$S/event\.sh stop mode=<mode> at=<at>' "$md"))"
  numbered="${numbered//<mode>/at-ledger}"
  numbered="${numbered//<at>/step-done}"
  if [[ -z "$numbered" ]]; then
    no_launch "Stopping's stop mark"
    return
  fi
  take_line "$numbered" "$title" || return
  rm -f "$seen" "$seen".*
  run_staged '<not run>'
  got="$(head -1 "$seen.event" 2>/dev/null)" || got='<no mark was made>'
  [[ "$got" == "$title" ]] ||
    problem "marked stop beside a ledger with every step ticked with VERI_STEP=<$got>, want the last done step <$title> (the typing shell said: ${err//$'\n'//})"
}

run_case "#907 Stopping in $skill_md, run with every ledger step ticked, gives the stop mark's VERI_STEP the last done step's text, byte-identical" \
  scan_stop_last_done

scan_resume_last_done() {
  local title="$EXPANDING_STEP"
  local lineno line numbered launch stage seen tree err got argv
  stage_recorder resume-last-done
  rm -f "$stage/event.sh"
  ln -s "$RECORDERS/title.sh" "$stage/event.sh"
  plant_done_ledger "$title"
  numbered="$(head -1 < <(grep -noE '`VERI_ISSUE=[^`]*\$S/event\.sh resume`' "$md"))"
  numbered="${numbered//\`/}"
  if [[ -z "$numbered" ]]; then
    no_launch "Resume's resume mark"
    return
  fi
  take_line "$numbered" "$title" || return
  rm -f "$seen" "$seen".*
  run_staged '<not run>'
  got="$(head -1 "$seen.event" 2>/dev/null)" || got='<no mark was made>'
  [[ "$got" == "$title" ]] ||
    problem "marked resume beside a ledger with every step ticked with VERI_STEP=<$got>, want the last done step <$title> (the typing shell said: ${err//$'\n'//})"
}

run_case "#907 Resume in $skill_md, run with every ledger step ticked, gives the resume mark's VERI_STEP the last done step's text, byte-identical" \
  scan_resume_last_done

scan_transform_verifier_last_done() {
  local title="$EXPANDING_STEP"
  local lineno line numbered launch stage seen tree err got argv
  numbered="$(awk '
    /one structural pass/ { inside = 1 }
    /^2\. \*\*Mark the PR ready/ { inside = 0 }
    inside && /\$S\/detach-leaf\.sh .*\$S\/supervise\.sh verdict-transform \$S\/run-verdict\.sh/ { print NR ":" $0; exit }
  ' "$md")"
  if [[ -z "$numbered" ]]; then
    no_launch "verdict-transform through supervise.sh into run-verdict.sh in the structural pass"
    return
  fi
  take_line "${numbered//<base-sha>/89abcde}" "$title" || return
  stage_recorder transform-verifier-last-done
  plant_done_ledger "$title"
  run_staged '<no verifier was launched>'
  [[ "$argv" == "$title" ]] ||
    problem "launched verdict-transform beside a ledger with every step ticked, whose verifier was handed --step <$argv>, want the last done step <$title> (the launching shell said: ${err//$'\n'//})"
}

run_case "#753 the structural pass in $skill_md spells the transform verifier's launch line, and run with every ledger step ticked it hands its verifier the last done step's text as --step, byte-identical" \
  scan_transform_verifier_last_done

scan_phase_verifiers_last_done() {
  local title="$EXPANDING_STEP"
  local lineno line numbered launch stage seen tree err got argv which pattern
  for which in general revise; do
    case "$which" in
      general) pattern='\$S/supervise\.sh verdict-<phase> \$S/run-verdict\.sh --step .* <phase> … >' ;;
      revise)  pattern='\$S/supervise\.sh verdict-<phase> \$S/run-verdict\.sh --step .* --fast-cmd .<fast-cmd>. <phase> ' ;;
    esac
    numbered="$(head -1 < <(grep -nE "\\\$S/detach-leaf\\.sh .*$pattern" "$md"))"
    if [[ -z "$numbered" ]]; then
      no_launch "the $which verdict-<phase> shape through supervise.sh into run-verdict.sh"
      continue
    fi
    take_line "$numbered" "$title" || continue
    stage_recorder "phase-verifier-last-done-$which"
    plant_done_ledger "$title"
    run_staged '<no verifier was launched>'
    [[ "$argv" == "$title" ]] ||
      problem "launched the $which verdict-<phase> line beside a ledger with every step ticked, whose verifier was handed --step <$argv>, want the last done step <$title> (the launching shell said: ${err//$'\n'//})"
  done
}

run_case "#753 the general verifier launch shape and the revise loop's re-verify line in $skill_md, run with every ledger step ticked, hand their verifier the last done step's text as --step, byte-identical" \
  scan_phase_verifiers_last_done

scan_inline_ledger_reads() {
  local numbered lineno line
  while IFS= read -r numbered; do
    lineno="${numbered%%:*}" line="${numbered#*:}"
    problem "spells a ledger read inline, want ledger-steps.sh current, last-done or criterion <k>"
  done < <(grep -nF -e '|| $S/next-unchecked.sh' -e '|| cat .tdd/issue-<n>.md' \
                    -e 'tail -1 | cut -f7-' -e "sed -n '<k>p'" "$md")
}

run_case "$skill_md spells none of the inline current-step, last-done and criterion <k> pipelines, reading each through ledger-steps.sh current, last-done and criterion <k> (#682)" \
  scan_inline_ledger_reads

CRITERION_TEXT='The issue'"'"'s own words: `echo $SHELL` in "quotes" and $HOME, as the issue wrote them'
plant_done_ledger() {
  printf '# Plan for #%s\n\n- [x] %s\n- [ ] a later step the run has not reached\n' \
    "$SENTINEL_ISSUE" "$2" > "$1/.tdd/issue-$SENTINEL_ISSUE.md"
}

conductor_command() {
  local n="$1" script="$2" text before after
  text="${md_lines[n-1]}"
  if [[ "$text" != *'`'* ]]; then
    text="${text#"${text%%[![:space:]]*}"}"
    printf '%s\n' "${text%%  # *}"
    return
  fi
  before="${text%%"\$S/$script.sh"*}"
  after="${text#"$before"}"
  while [[ "$after" != *'`'* ]] && (( n < ${#md_lines[@]} )); do
    text="${md_lines[n]}"
    after+=" ${text#"${text%%[![:space:]]*}"}"
    n=$((n + 1))
  done
  printf '%s%s\n' "${before##*\`}" "${after%%\`*}"
}

stage_title_recorders() {
  local script
  for script in "$@"; do
    rm -f "$stage/$script.sh"
    ln -s "$RECORDERS/title.sh" "$stage/$script.sh"
  done
}

scan_shared_recorders() {
  local stage seen tree first='' tag name
  local titled=(event build-develop-prompt)
  local recorders=(detach-leaf "${titled[@]}")
  for tag in a b; do
    stage_recorder "shared-recorders-$tag"
    stage_title_recorders "${titled[@]}"
    first="${first:-$stage}"
  done
  for name in "${recorders[@]}"; do
    [[ -L "$first/$name.sh" && -L "$stage/$name.sh" ]] ||
      problems+=("$name.sh: a stage holds its own recorder, want a link to the one written once per suite run")
    [[ "$first/$name.sh" -ef "$stage/$name.sh" ]] ||
      problems+=("$name.sh: two stages reach different recorders, want both linked to one")
    [[ "$stage/$name.sh" -ef "$SCRIPTS/$name.sh" ]] &&
      problems+=("$name.sh: the stage reaches the script under test, want the recorder")
  done
}

run_case "each distinct recorder is written once per suite run and every stage reaches it by a link, its per-stage difference only \$SEEN" \
  scan_shared_recorders

fill_title() {
  launch="${cmd//<n>/$SENTINEL_ISSUE}"
  launch="${launch//<STEP>/$title}"
  launch="${launch//<distinctive substring of STEP>/$title}"
  launch="${launch//<substring>/$title}"
  launch="${launch//<anchor>/$title}"
  launch="${launch//<phase>/red}"
  launch="${launch//<k>/2}"
  launch="$(sed -E 's/<[^<>]*>/probe/g' <<< "$launch")"
}

beside_every_ledger() {
  local planter
  first=""
  for planter in plant_ledger plant_ticked_ledger plant_done_ledger; do
    i=$((i + 1))
    tree="$WORK/$1-$i-tree" seen="$WORK/$1-$i-seen"
    mkdir -p "$tree/.tdd"
    "$planter" "$tree" "$title"
    run_recorded '<not run>'
    failed=""
    if [[ ! -f "$seen.$script" ]]; then
      failed="$script.sh was never run "
    else
      "$2"
    fi
    [[ -n "$failed" ]] || break
    [[ -n "$first" ]] || first="$failed(the typing shell said: ${err//$'\n'//})"
  done
}

scan_conductor_titles() {
  local title="$EXPANDING_STEP"
  local md_lines hits numbered lineno line launch script cmd stage seen tree err got argv
  local i=0 rec want expected failed first
  local callees=(event preserve-attempt tick-ledger clear-refactor-pending tick-issue-criterion)
  local callee_re
  callee_re="$(IFS='|'; printf '%s' "${callees[*]}")"
  mapfile -t md_lines < "$md"
  hits="$(grep -nE "\\\$S/($callee_re)\\.sh" "$md" |
          grep -vE '^[0-9]+:- `')"
  if [[ -z "$hits" ]]; then
    no_launch "the conductor's own marks, preserve-attempt.sh or tick calls"
    return
  fi
  stage_recorder conductor-title
  local bin="$WORK/conductor-title-bin"
  mkdir -p "$bin"
  {
    printf '#!/bin/sh\ncat <<'"'"'BODY'"'"'\n'
    printf '## Problem\n\n- [ ] a checkbox in the prose, not a criterion\n\n'
    printf '## Acceptance criteria\n\n- [ ] the first criterion\n- [ ] %s\n      wrapped onto a second line\n\nTest command: `make test`\n' "$CRITERION_TEXT"
    printf 'BODY\n'
  } > "$bin/gh"
  chmod +x "$bin/gh"
  stage_title_recorders "${callees[@]}"
  while IFS= read -r numbered; do
    [[ -n "$numbered" ]] || continue
    lineno="${numbered%%:*}"
    [[ "$numbered" =~ \$S/($callee_re)\.sh ]] && script="${BASH_REMATCH[1]}"
    cmd="$(conductor_command "$lineno" "$script")"
    line="$cmd"
    [[ "$script" != event || "$cmd" == *VERI_STEP* || "$cmd" == *anchor=* ]] || continue
    fill_title
    expected="$title"
    [[ "$script" != tick-issue-criterion ]] || expected="$CRITERION_TEXT"
    PATH="$bin:$PATH" beside_every_ledger conductor-title check_conductor_title
    [[ -z "$failed" ]] ||
      problem "passes $script.sh <$expected>, which arrived as $first beside every ledger state"
  done <<< "$hits"
}

check_conductor_title() {
  mapfile -t rec < "$seen.$script"
  [[ "$cmd" != *VERI_STEP* || "${rec[0]}" == "$title" ]] ||
    failed+="VERI_STEP=<${rec[0]}> "
  [[ "$cmd" != *anchor=* ]] || printf '%s\n' "${rec[@]:1}" | grep -xF "anchor=$title" > /dev/null ||
    failed+="no argument anchor=<$title> "
  case "$script" in
    preserve-attempt|tick-issue-criterion) want="${rec[2]-<none>}" ;;
    tick-ledger|clear-refactor-pending) want="${rec[${#rec[@]}-1]}" ;;
    *) want="$title" ;;
  esac
  [[ "$want" == "$expected" ]] || failed+="title argument <$want> "
}

run_case "a step title carrying a dollar sign, a backtick and a double quote reaches every event.sh mark, preserve-attempt.sh call and tick fragment the conductor types from $skill_md, byte-identical (#437)" \
  scan_conductor_titles

scan_prompt_titles() {
  local title="$EXPANDING_STEP"
  local md_lines hits numbered lineno line launch script cmd stage seen tree err got argv
  local i=0 rec k want failed first
  mapfile -t md_lines < "$md"
  hits="$(grep -nE '\$S/(build-develop-prompt|add-ledger-step)\.sh' "$md" |
          grep -vE '^[0-9]+:- `')"
  if [[ -z "$hits" ]]; then
    no_launch "build-develop-prompt.sh or add-ledger-step.sh"
    return
  fi
  stage_recorder prompt-title
  stage_title_recorders build-develop-prompt add-ledger-step
  while IFS= read -r numbered; do
    [[ -n "$numbered" ]] || continue
    lineno="${numbered%%:*}"
    [[ "$numbered" =~ \$S/(build-develop-prompt|add-ledger-step)\.sh ]] && script="${BASH_REMATCH[1]}"
    cmd="$(conductor_command "$lineno" "$script")"
    line="$cmd"
    [[ "$cmd" == *"$script.sh "* ]] || continue
    fill_title
    beside_every_ledger prompt-title check_prompt_title
    [[ -z "$failed" ]] ||
      problem "passes $script.sh <$title>, which arrived as $first beside every ledger state"
  done <<< "$hits"
}

check_prompt_title() {
  mapfile -t rec < "$seen.$script"
  want='<none>'
  for (( k = 1; k + 1 < ${#rec[@]}; k++ )); do
    case "$script:${rec[k]}" in
      build-develop-prompt:*-spec.md|add-ledger-step:after|add-ledger-step:before|add-ledger-step:instead-of)
        want="${rec[k+1]}"; break ;;
    esac
  done
  [[ "$want" == "$title" ]] || failed="title argument <$want> "
}

run_case "a step title carrying a dollar sign, a backtick and a double quote reaches every build-develop-prompt.sh prompt and add-ledger-step.sh anchor the conductor types from $skill_md, byte-identical (#437)" \
  scan_prompt_titles

scan_reverted_step_title() {
  local md="$md" reverted="$WORK/reverted-431-SKILL.md" hit n
  local -a doc
  scan_step_title "$EXPANDING_STEP" reverted-431-as-is
  if (( ${#problems[@]} )); then
    problems=("the document's own develop-red line already fails the probe, so its #431 revert shows nothing: ${problems[*]}")
    return
  fi
  hit="$(head -1 < <(grep -nE '\$S/supervise\.sh develop-red \$S/run-leaf\.sh' "$md"))"
  n="${hit%%:*}"
  mapfile -t doc < "$md"
  doc[n - 1]="${doc[n - 1]/VERI_STEP=* \$S\/detach-leaf.sh/VERI_STEP=\"<STEP>\" \$S/detach-leaf.sh}"
  printf '%s\n' "${doc[@]}" > "$reverted"
  md="$reverted"
  scan_step_title "$EXPANDING_STEP" reverted-431
  only_complaint_about "whose leaf saw VERI_STEP=" \
    "the develop-red line put back to #431's hand-typed VERI_STEP=\"<STEP>\""
}

run_case "the step-title probe, with one title carrying a dollar sign, a backtick and a double quote, goes red on a launch line put back to #431's hand-typed double quotes (#437)" \
  scan_reverted_step_title

scan_late_completion() {
  local lineno line launch leaf prompt stage
  developer_launch_fixture late-completion || return
  stage="$WORK/late-completion-scripts"
  mkdir -p "$stage"
  cat > "$stage/detach-leaf.sh" <<'STUB'
#!/bin/sh
printf '%s\n' "${VERI_TEST_CMD-<unset>}" > "$SEEN"
printf '%s\n' "$$" > ".tdd/$2.pid"
( sleep 1; printf '0\n' > ".tdd/$2.exit" ) </dev/null >/dev/null 2>&1 &
STUB
  chmod +x "$stage/detach-leaf.sh"
  SCRIPTS="$stage" expect_sentinel "$leaf" "$launch" "$prompt"
}

run_case "a launch whose completion file lands after its last recorded pid has exited is reported by what its leaf saw (#457)" \
  scan_late_completion

scan_late_wrong_leaf_name() {
  local lineno line launch leaf prompt stage started elapsed got want
  developer_launch_fixture late-wrong-leaf-name || return
  stage="$WORK/late-wrong-leaf-name-scripts"
  mkdir -p "$stage"
  cat > "$stage/detach-leaf.sh" <<'STUB'
#!/bin/sh
printf '%s\n' "${VERI_TEST_CMD-<unset>}" > "$SEEN"
printf '%s\n' "$$" > ".tdd/$2.pid"
( sleep 1; printf '0\n' > ".tdd/$2.exit" ) </dev/null >/dev/null 2>&1 &
STUB
  chmod +x "$stage/detach-leaf.sh"
  want="<no completion file under leaf $leaf-no-such-leaf>"
  started=$SECONDS
  got="$(SCRIPTS="$stage" launched_test_cmd "$leaf-no-such-leaf" "$launch" "$prompt")"
  elapsed=$(( SECONDS - started ))
  [[ "$got" == "$want" && elapsed -lt ANSWER_CEILING ]] ||
    problem "launches under a leaf name no completion file is written under, reported as <$got> after ${elapsed}s, want <$want> under ${ANSWER_CEILING}s"
}

run_case "a launch whose leaf name no completion file is written under is still reported as a naming fault, well inside the wait budget, when its own file lands late (#457)" \
  scan_late_wrong_leaf_name

scan_no_leaf_ran() {
  local lineno line launch leaf prompt stage got
  developer_launch_fixture no-leaf-ran || return
  stage="$WORK/no-leaf-ran-scripts"
  mkdir -p "$stage"
  cat > "$stage/detach-leaf.sh" <<'STUB'
#!/bin/sh
exit 0
STUB
  chmod +x "$stage/detach-leaf.sh"
  got="$(sleep() { SECONDS=$(( SECONDS + 3600 )); }
         SCRIPTS="$stage" launched_test_cmd "$leaf" "$launch" "$prompt")"
  [[ "$got" == '<no leaf ran>' ]] ||
    problem "launches nothing, reported as <$got>, want <no leaf ran>"
}

run_case "a launch line that reaches no supervisor at all is reported as <no leaf ran> (#457)" \
  scan_no_leaf_ran

scan_launch_record() {
  local counted count rest lineno shape line
  [[ -f "$LAUNCH_RECORD" ]] || { problems+=("no launch was recorded"); return; }
  while IFS= read -r counted; do
    read -r count rest <<< "$counted"
    (( count > 1 )) || continue
    IFS=$'\t' read -r lineno shape line <<< "$rest"
    problem "launched $count times beside a ledger of shape $shape, want at most once"
  done < <(sort "$LAUNCH_RECORD" | uniq -c)
}

run_case "no launch line in $skill_md is launched more than once per ledger shape the suite plants" \
  scan_launch_record

scan_scripts_untouched() {
  local now name
  now="$(scripts_fingerprint)"
  [[ "$now" == "$SCRIPTS_BEFORE" ]] && return
  while read -r name; do
    problems+=("$name changed while the suite ran, want every script under test byte-identical")
  done < <(diff <(printf '%s\n' "$SCRIPTS_BEFORE") <(printf '%s\n' "$now") |
             sed -n 's/^[<>] [0-9]* [0-9]* //p' | LC_ALL=C sort -u)
}

run_case "a recorder replaces a stage's link rather than writing through it, so the suite leaves every script under skills/tdd/scripts byte-identical" \
  scan_scripts_untouched

finish
