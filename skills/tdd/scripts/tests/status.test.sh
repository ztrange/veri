#!/usr/bin/env bash
# Unit tests for scripts/status.sh — the aggregation layer over every run in a repository.
# Run from a target repo, it discovers runs from `.tdd/wt/*` under the repository's MAIN
# working tree (resolved as solvable-issues.sh does, #166) and renders each one.
#
# Contract under test (issue #109):
#   status.sh            print every run under .tdd/wt/*, exit 0;
#                        print "no runs" and exit 3 when there are none.
#
# Run: scripts/tests/status.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
STATUS="$HERE/../status.sh"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
pass=0 fail=0
ok() { pass=$((pass + 1)); }
no() { fail=$((fail + 1)); echo "FAIL - $1"; }

# A repository of the case's own, so the answer never depends on the runs live in the
# repository `make test` was typed in. A `git init` with no commit is enough: `git worktree
# list` prints it as the main tree.
repo() {  # repo <name> -> path
  local dir="$work/$1"
  git init -q -b main "$dir" >/dev/null 2>&1
  echo "$dir"
}

# A fabricated run, not a real worktree: .tdd/wt/<n> under <repo> is a repository of its own
# whose unborn branch is the issue branch, with an empty .tdd/ for the ledger and event log.
fabricate_run() {  # fabricate_run <repo> <n> <branch> -> path
  local dir="$1/.tdd/wt/$2"
  git init -q -b "$3" "$dir" >/dev/null 2>&1
  mkdir -p "$dir/.tdd"
  echo "$dir"
}

# Run the script from inside <dir>, leaving stdout in $out and the exit code in $code.
run_in() {  # run_in <dir> [script args…]; sets $out and $code
  local dir="$1"; shift
  out="$(cd "$dir" && "$STATUS" "$@" 2>/dev/null)" && code=0 || code=$?
}

# Pass when every wanted piece was found in $out and the script exited 0; otherwise name the
# case, the pieces missing and what the script did print.
expect_nothing_missing() {  # expect_nothing_missing <case name>; reads $missing, $out, $code
  if [[ ${#missing[@]} -eq 0 && "$code" -eq 0 ]]; then ok; else
    no "$1"
    printf 'missing: %s\n' "${missing[@]:-}"
    printf 'output:\n%s\nexit %s\n' "$out" "$code"
  fi
}

# --- no .tdd/wt/* runs under the main working tree: "no runs", exit 3 ---
empty="$(repo empty)"
run_in "$empty"
if [[ "$out" == "no runs" && "$code" -eq 3 ]]; then ok; else
  no "no runs under the main working tree prints 'no runs' and exits 3"
  diff <(printf 'no runs\nexit 3\n') <(printf '%s\nexit %s\n' "$out" "$code")
fi

# --- one run: issue number and title from the ledger heading, branch, step n of m ---
# A fabricated run, not a real worktree: the run's directory is a repository of its own whose
# unborn branch is the issue branch, and its ledger has one of three steps ticked — so the
# step the run is on is the second.
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

# --- one run mid-Green: phase, actor, current leaf and its elapsed seconds, attempts in step ---
# The event log is what these are read from. The previous step launched three leaves; the
# current one has launched develop-green twice (a stuck retry), the second 100 s ago — so the
# run is in green, driven by the developer, on leaf develop-green for ~100 s, attempt 2.
live="$(repo live)"
run="$(fabricate_run "$live" 8 tdd/8-gears-turn)"
cat > "$run/.tdd/issue-8.md" <<'EOF'
# Plan for #8 — gears turn

- [x] a gear exists
- [ ] a gear turns
EOF
now="$(date +%s)"
ev() {  # ev <ts> <actor> <phase> <step> <event> <attempt> [name]
  printf '{"ts": %s, "issue": "8", "actor": "%s", "phase": "%s", "step": "%s", "event": "%s", "attempt": "%s", "skill_commit": "abc"%s}\n' \
    "$1" "$2" "$3" "$4" "$5" "$6" "${7:+, \"name\": \"$7\"}"
}
{
  ev $((now - 900)) conductor ""     "a gear exists" step-start ""
  ev $((now - 890)) developer red    "a gear exists" launch     1 develop-red
  ev $((now - 800)) developer green  "a gear exists" launch     1 develop-green
  ev $((now - 700)) verifier  green  "a gear exists" launch     1 verify-green
  ev $((now - 600)) conductor ""     "a gear exists" step-done  ""
  ev $((now - 500)) conductor ""     "a gear turns"  step-start ""
  ev $((now - 400)) developer green  "a gear turns"  launch     1 develop-green
  ev $((now - 100)) developer green  "a gear turns"  launch     2 develop-green
} > "$run/.tdd/events.jsonl"
run_in "$live"
missing=()
for want in "green" "developer" "develop-green" "attempt 2"; do
  [[ "$out" == *"$want"* ]] || missing+=("$want")
done
[[ "$out" =~ (^|[^0-9])10[0-5]s([^0-9a-z]|$) ]] || missing+=("elapsed 100s-105s")
expect_nothing_missing "a run shows its current phase, actor, leaf name, leaf elapsed seconds and attempts in the step, from its event log"

# --- one run: cost so far in dollars and tokens, summed from the event log's usage lines ---
# Two leaves have closed with their own accounting (harvest-usage.sh writes one `usage` line
# each, every value a string as event.sh writes it). $0.50 + $1.25 is $1.75; the four token
# kinds of both leaves, 4700 + 6300, are 11000 tokens. Lines that are not `usage` carry no cost.
spent="$(repo spent)"
run="$(fabricate_run "$spent" 9 tdd/9-cogs-mesh)"
cat > "$run/.tdd/issue-9.md" <<'EOF'
# Plan for #9 — cogs mesh

- [x] a cog exists
- [ ] two cogs mesh
EOF
now="$(date +%s)"
cat > "$run/.tdd/events.jsonl" <<EOF
{"ts": $((now - 300)), "issue": "9", "actor": "developer", "phase": "red", "step": "a cog exists", "event": "launch", "attempt": "1", "skill_commit": "abc", "name": "develop-red"}
{"ts": $((now - 250)), "issue": "9", "actor": "developer", "phase": "red", "step": "a cog exists", "event": "usage", "attempt": "1", "skill_commit": "abc", "duration_ms": "50000", "duration_api_ms": "40000", "num_turns": "7", "total_cost_usd": "0.50", "input_tokens": "1000", "output_tokens": "200", "cache_read_input_tokens": "3000", "cache_creation_input_tokens": "500"}
{"ts": $((now - 200)), "issue": "9", "actor": "developer", "phase": "green", "step": "two cogs mesh", "event": "launch", "attempt": "1", "skill_commit": "abc", "name": "develop-green"}
{"ts": $((now - 100)), "issue": "9", "actor": "developer", "phase": "green", "step": "two cogs mesh", "event": "usage", "attempt": "1", "skill_commit": "abc", "duration_ms": "90000", "duration_api_ms": "80000", "num_turns": "9", "total_cost_usd": "1.25", "input_tokens": "2000", "output_tokens": "300", "cache_read_input_tokens": "4000", "cache_creation_input_tokens": "0"}
EOF
run_in "$spent"
missing=()
[[ "$out" == *'$1.75'* ]] || missing+=('$1.75')
[[ "$out" =~ (^|[^0-9])11,?000\ tokens ]] || missing+=("11000 tokens")
expect_nothing_missing "a run shows its cost so far in dollars and tokens, summed from its event log"

echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
