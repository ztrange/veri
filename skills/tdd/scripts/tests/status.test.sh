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

# Run the script from inside <dir>, leaving stdout in $out and the exit code in $code.
run_in() {  # run_in <dir> [script args…]; sets $out and $code
  local dir="$1"; shift
  out="$(cd "$dir" && "$STATUS" "$@" 2>/dev/null)" && code=0 || code=$?
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
run="$one/.tdd/wt/7"
git init -q -b tdd/7-widgets-spin "$run" >/dev/null 2>&1
mkdir -p "$run/.tdd"
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
if [[ ${#missing[@]} -eq 0 && "$code" -eq 0 ]]; then ok; else
  no "a run under .tdd/wt/* is listed with its issue number, title, branch and step n of m"
  printf 'missing: %s\n' "${missing[@]:-}"
  printf 'output:\n%s\nexit %s\n' "$out" "$code"
fi

# --- one run mid-Green: phase, actor, current leaf and its elapsed seconds, attempts in step ---
# The event log is what these are read from. The previous step launched three leaves; the
# current one has launched develop-green twice (a stuck retry), the second 100 s ago — so the
# run is in green, driven by the developer, on leaf develop-green for ~100 s, attempt 2.
live="$(repo live)"
run="$live/.tdd/wt/8"
git init -q -b tdd/8-gears-turn "$run" >/dev/null 2>&1
mkdir -p "$run/.tdd"
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
if [[ ${#missing[@]} -eq 0 && "$code" -eq 0 ]]; then ok; else
  no "a run shows its current phase, actor, leaf name, leaf elapsed seconds and attempts in the step, from its event log"
  printf 'missing: %s\n' "${missing[@]:-}"
  printf 'output:\n%s\nexit %s\n' "$out" "$code"
fi

echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
