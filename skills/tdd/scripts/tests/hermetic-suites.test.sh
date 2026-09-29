#!/usr/bin/env bash
# Unit tests for the suites themselves — a suite that asserts a script's DEFAULT must not
# inherit an override for that default from the shell that ran it.
# Zero-dependency plain-shell asserts, same idiom as refactor-budget.test.sh.
#
# Why this exists (issue #87): an unattended run exports VERI_STUCK_RETRIES for its outer
# supervisor, the inner `make test` inherits it, and veri's own preflight then reads a red
# baseline on veri's own repo and refuses to start. A suite's answer must be a fact about
# the script, not about the caller's environment.
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
pass=0 fail=0

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
  (cd "$dir" && env "$@" "$HERE/solvable-issues.test.sh" 2>/dev/null)
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

name="solvable-issues.test.sh: an ambient VERI_PRIORITY_LABEL gives the same exit and the same stdout as a cleared run"
problems=()
label_cut="$(mktemp "$HERE/.hermetic-label-slice.XXXXXX")"
awk '
  /^# 1\. / {skip=1}
  /^# 22\. / {skip=0}
  /^# 28\. / {skip=1}
  !skip
' "$HERE/solvable-issues.test.sh" > "$label_cut"
printf '%s\n' 'echo "----"' 'echo "$pass passed, $fail failed"' '[[ "$fail" -eq 0 ]]' >> "$label_cut"
chmod +x "$label_cut"
label_assertions="$(grep -c 'ok || no ' "$label_cut")"
if [[ "$label_assertions" -ne 6 ]]; then
  problems+=("the slice of solvable-issues.test.sh between '# 22. ' and '# 28. ' held $label_assertions assertions, want 6 — the markers may have moved")
else
  cleared_label_out="$(env -u VERI_PRIORITY_LABEL "$label_cut" 2>/dev/null)" && cleared_label_code=0 || cleared_label_code=$?
  ambient_label_out="$(env VERI_PRIORITY_LABEL=ready-for-agent "$label_cut" 2>/dev/null)" && ambient_label_code=0 || ambient_label_code=$?
  same_answer cleared "$cleared_label_code" "$cleared_label_out" "$ambient_label_code" "$ambient_label_out"
fi
rm -f "$label_cut"
report "$name"

lock_work="$(mktemp -d)"
trap 'rm -rf "$lock_work"' EXIT
git init -q -b main "$lock_work/no-lock" >/dev/null 2>&1
unlocked_out="$(solvable_in "$lock_work/no-lock" -u VERI_PRIORITY_LABEL)" && unlocked_code=0 || unlocked_code=$?

name="solvable-issues.test.sh: a live conductor lock in the surrounding repository gives the same exit and the same stdout as a run with none"
git init -q -b main "$lock_work/locked" >/dev/null 2>&1
for n in 108 117 120 124; do
  mkdir -p "$lock_work/locked/.tdd/wt/$n/.tdd"
  printf '%s\n' "$$" > "$lock_work/locked/.tdd/wt/$n/.tdd/conductor.pid"
done

locked_out="$(solvable_in "$lock_work/locked" -u VERI_PRIORITY_LABEL)" && locked_code=0 || locked_code=$?

same_answer no-lock "$unlocked_code" "$unlocked_out" "$locked_code" "$locked_out"
report "$name"

name="solvable-issues.test.sh: a live conductor lock for every number its own fixtures name gives the same exit and the same stdout as a run with none"
git init -q -b main "$lock_work/every-locked" >/dev/null 2>&1
fixture_numbers=($(sed -n 's/.*"number"[[:space:]]*:[[:space:]]*\([0-9][0-9]*\).*/\1/p' "$HERE/solvable-issues.test.sh" | sort -u))
for n in "${fixture_numbers[@]+"${fixture_numbers[@]}"}"; do
  mkdir -p "$lock_work/every-locked/.tdd/wt/$n/.tdd"
  printf '%s\n' "$$" > "$lock_work/every-locked/.tdd/wt/$n/.tdd/conductor.pid"
done

every_locked_out="$(solvable_in "$lock_work/every-locked" -u VERI_PRIORITY_LABEL)" && every_locked_code=0 || every_locked_code=$?

same_answer no-lock "$unlocked_code" "$unlocked_out" "$every_locked_code" "$every_locked_out"
[[ "${#fixture_numbers[@]}" -gt 0 ]] ||
  problems+=("no \"number\": <n> fixture was found in solvable-issues.test.sh, so no lock was written and the two arms cannot differ")
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
  rerun_work="$(mktemp -d)"
  trap 'rm -rf "$lock_work" "$rerun_work"' EXIT
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
awk '
  /^tree_clone "\$work\/tree"$/ {skip=1}
  /^# 9\. / {skip=0}
  /^# 10\. / {skip=1}
  /^# 17\. / {skip=0}
  /^# 20\. / {skip=1}
  /^# 24\. / {skip=0}
  /^# 25\. / {skip=1}
  !skip
' "$HERE/run-conductor.test.sh" > "$newskill_cut"
printf '%s\n' 'echo "----"' 'echo "$pass passed, $fail failed"' '[[ "$fail" -eq 0 ]]' >> "$newskill_cut"
chmod +x "$newskill_cut"
newskill_missing=()
for newskill_case in "${newskill_cases[@]}"; do
  grep -qF "name=\"$newskill_case\"" "$newskill_cut" || newskill_missing+=("$newskill_case")
done
if [[ "${#newskill_missing[@]}" -gt 0 ]]; then
  problems+=("no case could be asked from run-conductor.test.sh under VERI_NEW_SKILL=1 — the slice is missing case(s): $(printf '%s | ' "${newskill_missing[@]}") — the '# 9. '/'# 10. '/'# 17. '/'# 20. '/'# 24. '/'# 25. ' markers may have moved")
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
  leak_work="$(mktemp -d)"
  trap 'rm -rf "$lock_work" "${rerun_work:-}" "$leak_work"' EXIT
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
  share_work="$(mktemp -d)"
  trap 'rm -rf "$lock_work" "${rerun_work:-}" "${leak_work:-}" "$share_work"' EXIT
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
  chmod +x "$share_work/scripts/tests/"*.test.sh
  (cd "$share_work/cwd" &&
    HERMETIC_SHARE_PROBE=1 HERMETIC_LEAK_PROBE=1 HERMETIC_RERUN_PROBE=1 \
      "$share_work/scripts/tests/$(basename "$0")" >/dev/null 2>&1)
  reference_runs="$(wc -l < "$share_log" | tr -d ' ')"
  [[ "$reference_runs" == 1 ]] ||
    problems+=("$(basename "$0") ran solvable-issues.test.sh's reference arm $reference_runs time(s), want 1: cases 3, 4 and 5 each paid for their own")
  report "$name"
fi

name="run-conductor.test.sh: an ambient VERI_NEW_SKILL=1 with a VERI_SKILL_COMMIT still leaves it green"
problems=()
skillcommit_case="every event a launched run writes carries origin's tip as skill_commit, and the prompt names it"
skillcommit_cut="$(mktemp "$HERE/.hermetic-skillcommit-slice.XXXXXX")"
awk '
  /^tree_clone "\$work\/tree"$/ {skip=1}
  /^# 15\. / {skip=0}
  /^# 16\. / {skip=1}
  !skip
' "$HERE/run-conductor.test.sh" > "$skillcommit_cut"
printf '%s\n' 'echo "----"' 'echo "$pass passed, $fail failed"' '[[ "$fail" -eq 0 ]]' >> "$skillcommit_cut"
chmod +x "$skillcommit_cut"
if ! grep -qF "name=\"$skillcommit_case\"" "$skillcommit_cut"; then
  problems+=("no case could be asked from run-conductor.test.sh under VERI_NEW_SKILL=1 and VERI_SKILL_COMMIT — the slice is missing the case: $skillcommit_case — the '# 15. '/'# 16. ' markers may have moved")
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
  sha_work="$(mktemp -d)"
  trap 'rm -rf "$lock_work" "${rerun_work:-}" "${leak_work:-}" "${share_work:-}" "$sha_work"' EXIT
  mkdir -p "$sha_work/scripts/tests"
  printf '%s\n' \
    '#!/usr/bin/env bash' \
    'set -uo pipefail' \
    'pass=0 fail=0' \
    'tree_clone "$work/tree"' \
    '# 15. The one case of this suite that can observe the sha.' \
    'name="every event a launched run writes carries origin'\''s tip as skill_commit, and the prompt names it"' \
    'if [[ -z "${VERI_SKILL_COMMIT:-}" ]]; then pass=$((pass + 1)); else fail=$((fail + 1)); echo "FAIL - $name"; fi' \
    '# 16. Past the cut, and never run.' \
    'exit 9' \
    > "$sha_work/scripts/tests/run-conductor.test.sh"
  cp "$HERE/$(basename "$0")" "$sha_work/scripts/tests/"
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

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
