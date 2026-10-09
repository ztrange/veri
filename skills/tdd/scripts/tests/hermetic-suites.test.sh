#!/usr/bin/env bash
# Unit tests for the suites themselves — a suite that asserts a script's DEFAULT must not
# inherit an override for that default from the shell that ran it.
#
# Contract under test:
#   VERI_STUCK_RETRIES=0 supervise-retry.test.sh → exit 0, "1 passed, 0 failed",
#   exactly as with the variable unset.
#   VERI_MODEL=<x> leaf-model.test.sh → the same exit and the same stdout as a run with
#   the three model variables cleared.
#
# Run: scripts/tests/hermetic-suites.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"

source "$HERE/lib/harness.sh"

same_answer() {
  local baseline="$1" base_code="$2" base_out="$3" other_code="$4" other_out="$5"

  problems=()
  [[ "$base_code" == 0 ]] ||
    problems+=("the $baseline run is not green, so there is nothing to compare against: exit $base_code, stdout: $(printf '%q' "$base_out")")
  [[ "$other_code" == "$base_code" ]] ||
    problems+=("want the $baseline run's exit $base_code, got $other_code")
  [[ "$other_out" == "$base_out" ]] ||
    problems+=("want the $baseline run's stdout $(printf '%q' "$base_out"), got: $(printf '%q' "$other_out")")
}

solvable_in() {
  local dir="$1"; shift
  (cd "$dir" && env "$@" "$label_cut" 2>/dev/null)
}

locked_repo() {
  local dir="$1" n; shift
  new_repo -b main "$dir" >/dev/null 2>&1
  for n in "$@"; do
    mkdir -p "$dir/.tdd/wt/$n/.tdd"
    printf '%s\n' "$$" > "$dir/.tdd/wt/$n/.tdd/conductor.pid"
  done
}

slice_run_conductor() {
  local keep="$1" cut="$2"
  awk -v keep=" $keep " '
    /^tree_clone "\$work\/tree"$/ {skip=1; cut=1}
    cut && /^name="/ {n++; skip = !index(keep, " " n " ")}
    !skip
  ' "$HERE/run-conductor.test.sh" > "$cut"
  printf '%s\n' 'echo "----"' 'echo "${pass:-0} passed, $fail failed"' '[[ "$fail" -eq 0 ]]' >> "$cut"
  chmod +x "$cut"
}

name="supervise-retry.test.sh: ambient VERI_STUCK_RETRIES=0 still gives 1 passed, 0 failed"
problems=()
out="$(VERI_STUCK_RETRIES=0 "$HERE/supervise-retry.test.sh" 2>/dev/null)" && code=0 || code=$?
[[ "$code" == 0 ]] ||
  problems+=("want exit 0, got $code")
[[ "$out" == *'1 passed, 0 failed'* ]] ||
  problems+=("want '1 passed, 0 failed' on stdout, got: $(printf '%q' "$out")")
report "$name"

name="leaf-model.test.sh: an ambient VERI_MODEL gives the same exit and the same stdout as a cleared run"
cleared_out="$(env -u VERI_MODEL -u VERI_MODEL_DEVELOPER -u VERI_MODEL_VERIFIER "$HERE/leaf-model.test.sh" 2>/dev/null)" && cleared_code=0 || cleared_code=$?
ambient_out="$(env -u VERI_MODEL_DEVELOPER -u VERI_MODEL_VERIFIER VERI_MODEL=sonnet "$HERE/leaf-model.test.sh" 2>/dev/null)" && ambient_code=0 || ambient_code=$?
same_answer cleared "$cleared_code" "$cleared_out" "$ambient_code" "$ambient_out"
report "$name"

label_cut="$(mktemp "$HERE/.hermetic-label-slice.XXXXXX")"
awk '
  /^fx="\$\(fixture unblocked\)"$/ {skip=1}
  /^fx="\$\(fixture bug-band\)"$/ {skip=0}
  /^narration="\$\(loop_bullet / {skip=1}
  !skip
' "$HERE/solvable-issues.test.sh" > "$label_cut"
printf '%s\n' 'echo "----"' 'echo "${pass:-0} passed, $fail failed"' '[[ "$fail" -eq 0 ]]' >> "$label_cut"
chmod +x "$label_cut"
name="solvable-issues.test.sh: an ambient VERI_PRIORITY_LABEL gives the same exit and the same stdout as a cleared run"
problems=()
label_assertions="$(grep -c 'ok || no ' "$label_cut")"
if [[ "$label_assertions" -ne 6 ]]; then
  problems+=("the slice of solvable-issues.test.sh from the bug-band fixture to the narration case held $label_assertions assertions, want 6 — the markers may have moved")
else
  cleared_label_out="$(env -u VERI_PRIORITY_LABEL "$label_cut" 2>/dev/null)" && cleared_label_code=0 || cleared_label_code=$?
  ambient_label_out="$(env VERI_PRIORITY_LABEL=ready-for-agent "$label_cut" 2>/dev/null)" && ambient_label_code=0 || ambient_label_code=$?
  same_answer cleared "$cleared_label_code" "$cleared_label_out" "$ambient_label_code" "$ambient_label_out"
fi
report "$name"

lock_work="$(scratch_dir)"
new_repo -b main "$lock_work/no-lock" >/dev/null 2>&1
unlocked_out="$(solvable_in "$lock_work/no-lock" -u VERI_PRIORITY_LABEL)" && unlocked_code=0 || unlocked_code=$?

name="solvable-issues.test.sh: a live conductor lock in the surrounding repository gives the same exit and the same stdout as a run with none"
locked_repo "$lock_work/locked" 108 117 120 124

locked_out="$(solvable_in "$lock_work/locked" -u VERI_PRIORITY_LABEL)" && locked_code=0 || locked_code=$?

same_answer no-lock "$unlocked_code" "$unlocked_out" "$locked_code" "$locked_out"
report "$name"

name="solvable-issues.test.sh: a live conductor lock for every number its own fixtures name gives the same exit and the same stdout as a run with none"
fixture_numbers=($(sed -n 's/.*"number"[[:space:]]*:[[:space:]]*\([0-9][0-9]*\).*/\1/p' "$HERE/solvable-issues.test.sh" | sort -u))
locked_repo "$lock_work/every-locked" "${fixture_numbers[@]+"${fixture_numbers[@]}"}"

every_locked_out="$(solvable_in "$lock_work/every-locked" -u VERI_PRIORITY_LABEL)" && every_locked_code=0 || every_locked_code=$?

same_answer no-lock "$unlocked_code" "$unlocked_out" "$every_locked_code" "$every_locked_out"
[[ "${#fixture_numbers[@]}" -gt 0 ]] ||
  problems+=("no \"number\": <n> fixture was found in solvable-issues.test.sh, so no lock was written and the two arms cannot differ")
report "$name"

rm -f "$label_cut"

name="solvable-issues.test.sh, tick-issue-criterion.test.sh, parallel-conductors.test.sh and invisible-work.test.sh: an ambient VERI_GH_DRIVER of auto, rest or graphql gives the same exit and the same stdout as a cleared run"
problems=()
driver_solvable="$(mktemp "$HERE/.hermetic-driver-slice.XXXXXX")"
driver_parallel="$(mktemp "$HERE/.hermetic-driver-slice.XXXXXX")"
driver_invisible="$(mktemp "$HERE/.hermetic-driver-slice.XXXXXX")"
awk '
  /^fx="\$\(fixture ordering\)"$/ {skip=1}
  /^fx="\$\(fixture gh\)"$/ {skip=0}
  /^fx="\$\(fixture default-label\)"$/ {skip=1}
  /^fx="\$\(fixture graphql-refused\)"$/ {skip=0}
  !skip
' "$HERE/solvable-issues.test.sh" > "$driver_solvable"
awk '
  /^timeline="\$work\/timeline"$/ {skip=1}
  /^refusing_gh="\$work\/graphql-refusing-bin"$/ {skip=0}
  /^failing_cat="\$work\/failing-cat-bin"$/ {skip=1}
  /^finish$/ {skip=0}
  !skip
' "$HERE/parallel-conductors.test.sh" > "$driver_parallel"
awk '
  /^name="invisible-work\.sh: a branch on origin with no PR / {skip=1}
  /^run_both_ghs\(\) / {skip=0}
  /^name="invisible-work\.sh reads issues and PR documents larger / {skip=1}
  /^name="invisible-work\.sh: against a gh that serves issues and PRs over three pages / {skip=0}
  /^name="invisible-work\.sh, run through a symlink / {skip=1}
  /^finish$/ {skip=0}
  !skip
' "$HERE/invisible-work.test.sh" > "$driver_invisible"
chmod +x "$driver_solvable" "$driver_parallel" "$driver_invisible"
slice_problems=()
for slice in "solvable-issues.test.sh:$driver_solvable:ok || no :11" \
  "parallel-conductors.test.sh:$driver_parallel:ok || no :4" \
  "invisible-work.test.sh:$driver_invisible:^report :5"; do
  IFS=: read -r slice_suite slice_path slice_pattern slice_want <<< "$slice"
  slice_got="$(grep -c -- "$slice_pattern" "$slice_path")"
  [[ "$slice_got" == "$slice_want" ]] ||
    slice_problems+=("the slice of $slice_suite held $slice_got assertions, want $slice_want — the markers may have moved")
done
if (( ${#slice_problems[@]} )); then
  problems=("${slice_problems[@]}")
else
  driver_findings=()
  for driver_suite in "solvable-issues.test.sh:$driver_solvable" "tick-issue-criterion.test.sh:$HERE/tick-issue-criterion.test.sh" \
    "parallel-conductors.test.sh:$driver_parallel" "invisible-work.test.sh:$driver_invisible"; do
    cleared_driver_out="$(env -u VERI_GH_DRIVER "${driver_suite#*:}" 2>/dev/null)" && cleared_driver_code=0 || cleared_driver_code=$?
    for driver in auto rest graphql; do
      ambient_driver_out="$(env VERI_GH_DRIVER="$driver" "${driver_suite#*:}" 2>/dev/null)" && ambient_driver_code=0 || ambient_driver_code=$?
      same_answer cleared "$cleared_driver_code" "$cleared_driver_out" "$ambient_driver_code" "$ambient_driver_out"
      for problem in ${problems[@]+"${problems[@]}"}; do
        driver_findings+=("${driver_suite%%:*} under VERI_GH_DRIVER=$driver: $problem")
      done
    done
  done
  problems=(${driver_findings[@]+"${driver_findings[@]}"})
fi
rm -f "$driver_solvable" "$driver_parallel" "$driver_invisible"
report "$name"

name="capture-spec.test.sh: an ambient VERI_GH_DRIVER of auto, rest or graphql gives the same exit and the same stdout as a cleared run (#1114)"
driver_findings=()
cleared_driver_out="$(env -u VERI_GH_DRIVER "$HERE/capture-spec.test.sh" 2>/dev/null)" && cleared_driver_code=0 || cleared_driver_code=$?
for driver in auto rest graphql; do
  ambient_driver_out="$(env VERI_GH_DRIVER="$driver" "$HERE/capture-spec.test.sh" 2>/dev/null)" && ambient_driver_code=0 || ambient_driver_code=$?
  same_answer cleared "$cleared_driver_code" "$cleared_driver_out" "$ambient_driver_code" "$ambient_driver_out"
  for problem in ${problems[@]+"${problems[@]}"}; do
    driver_findings+=("capture-spec.test.sh under VERI_GH_DRIVER=$driver: $problem")
  done
done
problems=(${driver_findings[@]+"${driver_findings[@]}"})
report "$name"

name="every suite that invokes push-branch.sh sets VERI_PUSH_BACKOFF in its environment"
problems=()
push_invocations=0
for suite in "$HERE"/*.test.sh; do
  while IFS= read -r row; do
    case "$row" in
      invoked) push_invocations=$((push_invocations + 1)) ;;
      *) problems+=("$(basename "$suite"):$row invokes push-branch.sh without VERI_PUSH_BACKOFF in its environment, so a push to an unreachable origin waits the default backoff on wall time") ;;
    esac
  done < <(awk '
    BEGIN { assigns_script = "^[[:space:]]*(local[[:space:]]+)?[A-Za-z_][A-Za-z0-9_]*=.*/push-branch\\.sh[\"'"'"']?[[:space:]]*$" }
    NR == FNR {
      if ($0 ~ assigns_script) {
        v = $0
        sub(/^[[:space:]]*(local[[:space:]]+)?/, "", v)
        sub(/=.*/, "", v)
        vars[v] = 1
      }
      next
    }
    {
      if (!joining) start = FNR
      if ($0 ~ /\\$/) { cmd = cmd substr($0, 1, length($0) - 1) " "; joining = 1; next }
      cmd = cmd $0; joining = 0
      line = cmd; cmd = ""
      if (line ~ /^[[:space:]]*#/) next
      if (line ~ assigns_script) next
      invokes = (line ~ /\/push-branch\.sh"/)
      for (v in vars)
        if (index(line, "\"$" v "\"") || index(line, "${" v "}")) invokes = 1
      if (!invokes) next
      print "invoked"
      if (line !~ /VERI_PUSH_BACKOFF=/) print start
    }
  ' "$suite" "$suite")
done
[[ "$push_invocations" -gt 0 ]] ||
  problems+=("no suite here was recognised as invoking push-branch.sh, so nothing was checked")
report "$name"

name="hermetic-suites.test.sh re-runs no suite for the offline or own-origin cases"
if [[ -z "${HERMETIC_RERUN_PROBE:-}" ]]; then
  problems=()
  rerun_work="$(scratch_dir)"
  rerun_log="$rerun_work/runs"
  mkdir -p "$rerun_work/scripts/tests"
  : > "$rerun_log"
  for stand_in in "run-conductor:fetch origin main" "push-branch:push origin HEAD"; do
    printf '#!/usr/bin/env bash\ngit %s\n' "${stand_in#*:}" > "$rerun_work/scripts/${stand_in%%:*}.sh"
  done
  {
    printf '#!/usr/bin/env bash\n'
    printf '# Names run-conductor.sh and push-branch.sh, and runs neither.\n'
    printf 'printf "%%s\\n" ran >> %q\n' "$rerun_log"
    printf 'echo "1 passed, 0 failed"\n'
  } > "$rerun_work/scripts/tests/probe.test.sh"
  cp "$HERE/$(basename "$0")" "$rerun_work/scripts/tests/"
  mkdir -p "$rerun_work/scripts/tests/lib" && cp "$HERE/lib/harness.sh" "$rerun_work/scripts/tests/lib/"
  chmod +x "$rerun_work/scripts/"*.sh "$rerun_work/scripts/tests/"*.test.sh
  HERMETIC_RERUN_PROBE=1 "$rerun_work/scripts/tests/$(basename "$0")" >/dev/null 2>&1
  reruns="$(wc -l < "$rerun_log" | tr -d ' ')"
  [[ "$reruns" == 0 ]] ||
    problems+=("$(basename "$0") ran probe.test.sh $reruns time(s), want 0: a suite that names a network-capable script was re-run")
  report "$name"
fi

name="run-conductor.test.sh: an ambient VERI_NEW_SKILL=1 still leaves it green"
problems=()
newskill_cases=(
  "a resume with VERI_NEW_SKILL=1 is re-pinned to the clone's current commit and logs a skill-repin event"
  "a resume with VERI_NEW_SKILL=1 re-pins to origin/<default> as just fetched, not to the clone's HEAD"
  "an unresolvable recorded skill commit refuses with exit 2 unless VERI_NEW_SKILL=1, which re-pins and logs a skill-repin event"
  "the skill-repin event lands in the run worktree's .tdd/wt/<n>/.tdd/events.jsonl, never the caller's .tdd/events.jsonl"
  "a re-pinning launch with VERI_NEW_SKILL=1 hands the conductor no VERI_NEW_SKILL"
)
newskill_cut="$(mktemp "$HERE/.hermetic-newskill-slice.XXXXXX")"
slice_run_conductor "9 17 18 19 24" "$newskill_cut"
newskill_missing=()
for newskill_case in "${newskill_cases[@]}"; do
  grep -qF "name=\"$newskill_case\"" "$newskill_cut" || newskill_missing+=("$newskill_case")
done
if [[ "${#newskill_missing[@]}" -gt 0 ]]; then
  problems+=("no case could be asked from run-conductor.test.sh under VERI_NEW_SKILL=1 — the slice is missing case(s): $(printf '%s | ' "${newskill_missing[@]}") — cases 9, 17, 18, 19 and 24, counted by name= line, may have moved")
else
  out="$(VERI_NEW_SKILL=1 "$newskill_cut" 2>/dev/null)" && code=0 || code=$?
  [[ "$code" == 0 ]] ||
    problems+=("want exit 0 from run-conductor.test.sh under VERI_NEW_SKILL=1, got $code: $(printf '%q' "$(tail -n 1 <<< "$out")")")
  [[ "$(tail -n 1 <<< "$out")" == "5 passed, 0 failed" ]] ||
    problems+=("want '5 passed, 0 failed' last from run-conductor.test.sh under VERI_NEW_SKILL=1 (one per case that sets it), got: $(printf '%q' "$(tail -n 1 <<< "$out")")")
fi
rm -f "$newskill_cut"
report "$name"

name="a suite whose answer changes with an ambient VERI_* value or a live conductor lock fails hermetic-suites.test.sh, named"
if [[ -z "${HERMETIC_LEAK_PROBE:-}" && -z "${HERMETIC_RERUN_PROBE:-}" ]]; then
  problems=()
  leak_work="$(scratch_dir)"
  mkdir -p "$leak_work/scripts/tests"
  for stand_in in \
    'supervise-retry:[ -z "${VERI_STUCK_RETRIES:-}" ]' \
    'leaf-model:[ -z "${VERI_MODEL:-}" ]' \
    'solvable-issues:[ -z "${VERI_PRIORITY_LABEL:-}" ] && ! ls .tdd/wt/*/.tdd/conductor.pid' \
    'run-conductor:[ -z "${VERI_NEW_SKILL:-}" ]'; do
    {
      printf '#!/bin/sh\n'
      printf '# Fixture numbers, read as text by case 5: {"number": 108} {"number": 117}\n'
      printf 'if %s >/dev/null 2>&1; then echo "1 passed, 0 failed"; exit 0; fi\n' "${stand_in#*:}"
      printf 'echo "0 passed, 1 failed"; exit 1\n'
    } > "$leak_work/scripts/tests/${stand_in%%:*}.test.sh"
  done
  cp "$HERE/$(basename "$0")" "$leak_work/scripts/tests/"
  mkdir -p "$leak_work/scripts/tests/lib" && cp "$HERE/lib/harness.sh" "$leak_work/scripts/tests/lib/"
  chmod +x "$leak_work/scripts/tests/"*.test.sh
  leak_out="$(HERMETIC_LEAK_PROBE=1 HERMETIC_RERUN_PROBE=1 "$leak_work/scripts/tests/$(basename "$0")" 2>/dev/null)" &&
    leak_code=0 || leak_code=$?
  [[ "$leak_code" != 0 ]] ||
    problems+=("want the copy to exit non-zero with every stand-in leaking, got 0: $(printf '%q' "$leak_out")")
  for leaked in \
    "supervise-retry.test.sh: ambient VERI_STUCK_RETRIES=0" \
    "leaf-model.test.sh: an ambient VERI_MODEL" \
    "solvable-issues.test.sh: an ambient VERI_PRIORITY_LABEL" \
    "solvable-issues.test.sh: a live conductor lock in the surrounding repository" \
    "solvable-issues.test.sh: a live conductor lock for every number" \
    "run-conductor.test.sh: an ambient VERI_NEW_SKILL=1"; do
    [[ "$leak_out" == *"FAIL - $leaked"* ]] ||
      problems+=("want a FAIL line naming '$leaked', got: $(printf '%q' "$leak_out")")
  done
  [[ "$leak_out" == *"from run-conductor.test.sh under VERI_NEW_SKILL=1"* ]] ||
    problems+=("want case 9 to fail on its own finding, run-conductor.test.sh red under VERI_NEW_SKILL=1, not on problems an earlier case left; got: $(printf '%q' "$leak_out")")
  report "$name"
fi

name="hermetic-suites.test.sh runs solvable-issues.test.sh's reference arm once, shared by its ambient and lock cases"
if [[ -z "${HERMETIC_SHARE_PROBE:-}" && -z "${HERMETIC_LEAK_PROBE:-}" && -z "${HERMETIC_RERUN_PROBE:-}" ]]; then
  problems=()
  share_work="$(scratch_dir)"
  share_log="$share_work/reference-runs"
  mkdir -p "$share_work/scripts/tests" "$share_work/cwd"
  : > "$share_log"
  {
    printf '#!/bin/sh\n'
    printf '# Fixture numbers, read as text by case 5: {"number": 108} {"number": 117}\n'
    printf 'if [ -z "${VERI_PRIORITY_LABEL:-}" ] && ! ls .tdd/wt/*/.tdd/conductor.pid >/dev/null 2>&1; then\n'
    printf '  printf "%%s\\n" reference >> %q\n' "$share_log"
    printf 'fi\n'
    printf 'echo "1 passed, 0 failed"\n'
  } > "$share_work/scripts/tests/solvable-issues.test.sh"
  cp "$HERE/$(basename "$0")" "$share_work/scripts/tests/"
  mkdir -p "$share_work/scripts/tests/lib" && cp "$HERE/lib/harness.sh" "$share_work/scripts/tests/lib/"
  chmod +x "$share_work/scripts/tests/"*.test.sh
  (cd "$share_work/cwd" &&
    HERMETIC_SHARE_PROBE=1 HERMETIC_LEAK_PROBE=1 HERMETIC_RERUN_PROBE=1 \
      "$share_work/scripts/tests/$(basename "$0")" >/dev/null 2>&1)
  reference_runs="$(wc -l < "$share_log" | tr -d ' ')"
  [[ "$reference_runs" == 1 ]] ||
    problems+=("$(basename "$0") ran solvable-issues.test.sh's reference arm $reference_runs time(s), want 1: cases 3, 4 and 5 each paid for their own")
  report "$name"
fi

name="hermetic-suites.test.sh runs no whole copy of solvable-issues.test.sh for its lock cases"
if [[ -z "${HERMETIC_WHOLE_PROBE:-}" && -z "${HERMETIC_SHARE_PROBE:-}" && -z "${HERMETIC_LEAK_PROBE:-}" && -z "${HERMETIC_RERUN_PROBE:-}" && -z "${HERMETIC_SKILLCOMMIT_PROBE:-}" ]]; then
  problems=()
  whole_work="$(scratch_dir)"
  whole_log="$whole_work/runs"
  mkdir -p "$whole_work/scripts/tests" "$whole_work/cwd"
  : > "$whole_log"
  {
    printf '#!/bin/sh\n'
    printf '# Fixture numbers, read as text by case 5: {"number": 108} {"number": 117}\n'
    printf 'printf "%%s\\n" "$(basename "$0")" >> %q\n' "$whole_log"
    printf 'echo "1 passed, 0 failed"\n'
  } > "$whole_work/scripts/tests/solvable-issues.test.sh"
  cp "$HERE/$(basename "$0")" "$whole_work/scripts/tests/"
  mkdir -p "$whole_work/scripts/tests/lib" && cp "$HERE/lib/harness.sh" "$whole_work/scripts/tests/lib/"
  chmod +x "$whole_work/scripts/tests/"*.test.sh
  (cd "$whole_work/cwd" &&
    HERMETIC_WHOLE_PROBE=1 HERMETIC_SHARE_PROBE=1 HERMETIC_LEAK_PROBE=1 HERMETIC_RERUN_PROBE=1 HERMETIC_SKILLCOMMIT_PROBE=1 \
      "$whole_work/scripts/tests/$(basename "$0")" >/dev/null 2>&1)
  whole_runs="$(grep -cx 'solvable-issues.test.sh' "$whole_log")"
  [[ "$whole_runs" == 0 ]] ||
    problems+=("$(basename "$0") ran a whole copy of solvable-issues.test.sh $whole_runs time(s), want 0: each lock case runs a slice")
  report "$name"
fi

name="run-conductor.test.sh: an ambient VERI_NEW_SKILL=1 with a VERI_SKILL_COMMIT still leaves it green"
problems=()
skillcommit_case="every event a launched run writes carries origin's tip as skill_commit, and the prompt names it"
skillcommit_cut="$(mktemp "$HERE/.hermetic-skillcommit-slice.XXXXXX")"
slice_run_conductor 15 "$skillcommit_cut"
if ! grep -qF "name=\"$skillcommit_case\"" "$skillcommit_cut"; then
  problems+=("no case could be asked from run-conductor.test.sh under VERI_NEW_SKILL=1 and VERI_SKILL_COMMIT — the slice is missing the case: $skillcommit_case — case 15, counted by name= line, may have moved")
else
  out="$(VERI_NEW_SKILL=1 VERI_SKILL_COMMIT=deadbeefdeadbeefdeadbeefdeadbeefdeadbeef "$skillcommit_cut" 2>/dev/null)" && code=0 || code=$?
  [[ "$code" == 0 ]] ||
    problems+=("want exit 0 from run-conductor.test.sh under VERI_NEW_SKILL=1 and VERI_SKILL_COMMIT, got $code: $(printf '%q' "$(tail -n 1 <<< "$out")")")
  [[ "$(tail -n 1 <<< "$out")" == "1 passed, 0 failed" ]] ||
    problems+=("want '1 passed, 0 failed' last from run-conductor.test.sh under VERI_NEW_SKILL=1 and VERI_SKILL_COMMIT (the one case that can observe the sha), got: $(printf '%q' "$(tail -n 1 <<< "$out")")")
fi
rm -f "$skillcommit_cut"
report "$name"

name="a suite whose answer changes with an ambient VERI_SKILL_COMMIT fails hermetic-suites.test.sh, named"
if [[ -z "${HERMETIC_SKILLCOMMIT_PROBE:-}" ]]; then
  problems=()
  sha_work="$(scratch_dir)"
  mkdir -p "$sha_work/scripts/tests"
  {
    printf '%s\n' \
      '#!/usr/bin/env bash' \
      'set -uo pipefail' \
      'pass=0 fail=0' \
      'tree_clone "$work/tree"'
    for filler in $(seq 1 14); do
      printf '%s\n' "name=\"filler $filler\"" 'exit 9'
    done
    printf '%s\n' \
      'name="every event a launched run writes carries origin'\''s tip as skill_commit, and the prompt names it"' \
      'if [[ -z "${VERI_SKILL_COMMIT:-}" ]]; then pass=$((pass + 1)); else fail=$((fail + 1)); echo "FAIL - $name"; fi' \
      'name="past the cut"' \
      'exit 9'
  } > "$sha_work/scripts/tests/run-conductor.test.sh"
  cp "$HERE/$(basename "$0")" "$sha_work/scripts/tests/"
  mkdir -p "$sha_work/scripts/tests/lib" && cp "$HERE/lib/harness.sh" "$sha_work/scripts/tests/lib/"
  chmod +x "$sha_work/scripts/tests/"*.test.sh
  sha_out="$(HERMETIC_SKILLCOMMIT_PROBE=1 HERMETIC_SHARE_PROBE=1 HERMETIC_LEAK_PROBE=1 HERMETIC_RERUN_PROBE=1 \
    "$sha_work/scripts/tests/$(basename "$0")" 2>/dev/null)" && sha_code=0 || sha_code=$?
  [[ "$sha_code" != 0 ]] ||
    problems+=("want the copy to exit non-zero with the stand-in leaking VERI_SKILL_COMMIT, got 0: $(printf '%q' "$sha_out")")
  [[ "$sha_out" == *"FAIL - run-conductor.test.sh: an ambient VERI_NEW_SKILL=1 with a VERI_SKILL_COMMIT"* ]] ||
    problems+=("want a FAIL line naming 'run-conductor.test.sh: an ambient VERI_NEW_SKILL=1 with a VERI_SKILL_COMMIT', got: $(printf '%q' "$sha_out")")
  [[ "$sha_out" == *"(the one case that can observe the sha), got"* ]] ||
    problems+=("want case 12 to fail on its own finding, the sliced case red under the ambient sha, not on a slice it could not cut; got: $(printf '%q' "$sha_out")")
  report "$name"
fi

name="#954: leaf-timeout.test.sh run inside a run worktree with VERI_ISSUE=954 in its environment, as a leaf's test run is, leaves no .tdd/issue-954-timeout in that worktree"
problems=()
run_wt="$(scratch_dir)"
new_repo -b main "$run_wt" >/dev/null 2>&1
mkdir -p "$run_wt/skills/tdd/scripts/veri" "$run_wt/skills/tdd/scripts/tests/lib"
cp "$HERE/../leaf-timeout.sh" "$run_wt/skills/tdd/scripts/"
cp "$HERE/../veri/leaf_timeout.py" "$HERE/../veri/entry.py" "$run_wt/skills/tdd/scripts/veri/"
cp "$HERE/leaf-timeout.test.sh" "$run_wt/skills/tdd/scripts/tests/"
cp "$HERE"/lib/*.sh "$run_wt/skills/tdd/scripts/tests/lib/"
leaf_out="$(cd "$run_wt" && env -u VERI_TIMEOUT VERI_ISSUE=954 skills/tdd/scripts/tests/leaf-timeout.test.sh 2>/dev/null)" && leaf_code=0 || leaf_code=$?
[[ "$leaf_code" == 0 && "$(tail -n 1 <<< "$leaf_out")" == *" passed, 0 failed" ]] ||
  problems+=("want leaf-timeout.test.sh green under VERI_ISSUE=954, got exit $leaf_code: $(printf '%q' "$(tail -n 1 <<< "$leaf_out")")")
[[ ! -e "$run_wt/.tdd/issue-954-timeout" ]] ||
  problems+=("want no .tdd/issue-954-timeout in the run worktree, found one holding $(printf '%q' "$(cat "$run_wt/.tdd/issue-954-timeout")")")
report "$name"

finish
