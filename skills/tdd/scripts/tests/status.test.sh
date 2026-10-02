#!/usr/bin/env bash
# Unit tests for scripts/status.sh — the aggregation layer over every run in a repository.
# Run from a target repo, it discovers runs from `.tdd/wt/*` under the repository's main
# working tree and renders each one.
#
# Contract under test:
#   status.sh            print every run under .tdd/wt/*, exit 0;
#                        print "no runs" and exit 3 when there are none.
#
# Run: scripts/tests/status.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
STATUS="$HERE/../status.sh"
source "$HERE/lib/harness.sh"
work="$(scratch_dir)"

repo() {  # repo <name> -> path
  local dir="$work/$1"
  new_repo -b main "$dir" >/dev/null 2>&1
  echo "$dir"
}

fabricate_run() {  # fabricate_run <repo> <n> <branch> -> path
  local dir="$1/.tdd/wt/$2"
  new_repo -b "$3" "$dir" >/dev/null 2>&1
  mkdir -p "$dir/.tdd"
  echo "$dir"
}

run_in() {  # run_in <dir> [script args…]; sets $out and $code
  local dir="$1"; shift
  out="$(cd "$dir" && "$STATUS" "$@" 2>/dev/null)" && code=0 || code=$?
}

expect_nothing_missing() {  # expect_nothing_missing <case name>; reads $missing, $out, $code
  if [[ ${#missing[@]} -eq 0 && "$code" -eq 0 ]]; then ok; else
    no "$1"
    printf 'missing: %s\n' "${missing[@]:-}"
    printf 'output:\n%s\nexit %s\n' "$out" "$code"
  fi
}

empty="$(repo empty)"
run_in "$empty"
if [[ "$out" == "no runs" && "$code" -eq 3 ]]; then ok; else
  no "no runs under the main working tree prints 'no runs' and exits 3"
  diff <(printf 'no runs\nexit 3\n') <(printf '%s\nexit %s\n' "$out" "$code")
fi

one="$(repo one)"
run="$(fabricate_run "$one" 7 tdd/7-widgets-spin)"
cat > "$run/.tdd/issue-7.md" <<'EOF'
# Plan for #7 — widgets spin when clicked

- [x] a widget exists
- [ ] a clicked widget spins
- [ ] a spinning widget stops
EOF
run_in "$one"
missing=()
for want in "#7" "widgets spin when clicked" "tdd/7-widgets-spin" "step 2 of 3"; do
  [[ "$out" == *"$want"* ]] || missing+=("$want")
done
expect_nothing_missing "a run under .tdd/wt/* is listed with its issue number, title, branch and step n of m"

states="$(repo states)"
now="$(date +%s)"
sleep 0 & dead_pid=$!
wait "$dead_pid" 2>/dev/null
launched_run() {  # launched_run <repo> <n> <ts> -> path; a one-step ledger and one develop-red launch at <ts>
  local dir
  dir="$(fabricate_run "$1" "$2" "tdd/$2-lamps")"
  printf '# Plan for #%s — lamps glow\n\n- [ ] a lamp glows\n' "$2" > "$dir/.tdd/issue-$2.md"
  printf '{"ts": %s, "issue": "%s", "actor": "developer", "phase": "red", "step": "a lamp glows", "event": "launch", "attempt": "1", "skill_commit": "abc", "name": "develop-red"}\n' \
    "$3" "$2" > "$dir/.tdd/events.jsonl"
  echo "$dir"
}
state_run() { launched_run "$states" "$@"; }  # state_run <n> <ts> -> path
run="$(state_run 11 $((now - 10)))"
echo "$$" > "$run/.tdd/conductor.pid"
run="$(state_run 12 $((now - 20)))"
printf '{"ts": %s, "issue": "12", "actor": "conductor", "phase": "", "step": "", "event": "done", "attempt": "", "skill_commit": "abc", "pr": "https://github.com/o/r/pull/12"}\n' \
  "$((now - 15))" >> "$run/.tdd/events.jsonl"
run="$(state_run 13 $((now - 30)))"
printf '{"ts": %s, "issue": "13", "actor": "conductor", "phase": "green", "step": "a lamp glows", "event": "bail", "attempt": "", "skill_commit": "abc", "cause": "stuck", "classification": "system"}\n' \
  "$((now - 25))" >> "$run/.tdd/events.jsonl"
run="$(state_run 14 $((now - 1000)))"
echo "$dead_pid" > "$run/.tdd/conductor.pid"
VERI_TIMEOUT=600 run_in "$states"
line_of() { printf '%s\n' "$out" | grep "^#$1 " || true; }
missing=()
for want in "11 running" "12 done" "12 https://github.com/o/r/pull/12" "13 bailed" "13 green" \
    "13 system" "14 stale"; do
  [[ "$(line_of "${want%% *}")" == *"${want#* }"* ]] || missing+=("#$want")
done
expect_nothing_missing "a run shows its state: running, done with its PR url, bailed with phase and classification, or stale"

watched="$(repo watched)"
now="$(date +%s)"
run="$(launched_run "$watched" 41 $((now - 10)))"
echo "$$" > "$run/.tdd/conductor.pid"
watch_out="$work/watch.out"
(cd "$watched" && exec "$STATUS" --watch 0 > "$watch_out" 2>/dev/null) &
watch_pid=$!
wait_for() {  # wait_for <text>; polls $watch_out for up to 5 s
  local i
  for i in $(seq 50); do
    grep -q -- "$1" "$watch_out" 2>/dev/null && return 0
    sleep 0.1
  done
  return 1
}
missing=()
wait_for "#41" || missing+=("a first render listing #41")
printf '{"ts": %s, "issue": "41", "actor": "conductor", "phase": "", "step": "", "event": "done", "attempt": "", "skill_commit": "abc", "pr": "https://github.com/o/r/pull/41"}\n' \
  "$(date +%s)" >> "$run/.tdd/events.jsonl"
wait_for "done https://github.com/o/r/pull/41" || true
kill -0 "$watch_pid" 2>/dev/null || missing+=("still watching after its first render")
kill "$watch_pid" 2>/dev/null
wait "$watch_pid" 2>/dev/null
out="$(cat "$watch_out")"
code=0
[[ "$out" == *$'\e['* || "$out" == *$'\ec'* ]] || missing+=("a redraw-in-place escape")
[[ "$out" == *"done https://github.com/o/r/pull/41"* ]] || missing+=("#41 done after its event log changed")
expect_nothing_missing "--watch [seconds] redraws in place, recomputing every run from disk on each render"

counted="$(repo counted)"

unreadable="$(repo unreadable)"
run="$(fabricate_run "$unreadable" 9 tdd/9-locked)"
printf '# Plan for #9 — locked\n\n- [ ] a lock\n' > "$run/.tdd/issue-9.md"
chmod 000 "$run/.tdd/issue-9.md"
err="$(cd "$unreadable" && "$STATUS" 2>&1 >/dev/null)" && code=0 || code=$?
chmod 644 "$run/.tdd/issue-9.md"
if [[ "$code" -eq 2 && "$err" == *"PermissionError"* ]]; then ok; else
  no "status.sh run through its entry point exits 2 on a failure veri/status.py turns into exit 2"
  printf 'stderr:\n%s\nexit %s\n' "$err" "$code"
fi

err="$(cd "$one" && "$STATUS" --bogus 2>&1 >/dev/null)" && code=0 || code=$?
if [[ "$err" == "status.sh: unknown option '--bogus'" && "$code" -eq 2 ]]; then ok; else
  no "status.sh given a bad argument names it on stderr"
  diff <(printf "status.sh: unknown option '--bogus'\nexit 2\n") <(printf '%s\nexit %s\n' "$err" "$code")
fi

ln -s "$(cd "$HERE/../.." && pwd)" "$work/linked-skill"
mkdir -p "$one/elsewhere"
in_place="$(cd "$one" && "$STATUS" 2>&1)"; in_place_code=$?
linked="$(cd "$one/elsewhere" && "$work/linked-skill/scripts/status.sh" 2>&1)"; linked_code=$?
if [[ "$linked" == "$in_place" && "$linked_code" -eq "$in_place_code" && "$in_place" == *"#7"* ]]; then ok; else
  no "status.sh run through a symlink to the skill directory and from another working directory answers as it does when run in place"
  diff <(printf '%s\nexit %s\n' "$in_place" "$in_place_code") <(printf '%s\nexit %s\n' "$linked" "$linked_code")
fi
finish
