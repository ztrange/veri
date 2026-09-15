#!/usr/bin/env bash
# Unit tests for scripts/push-branch.sh — the push the conductor makes after each step's
# green commit and after each verify-refactor PASS clears the mark, so a run's commits stop
# living on one disk until the draft PR is opened (issue #191).
# Zero-dependency plain-shell asserts, same idiom as event.test.sh.
#
# Contract under test (this step only — the failing push):
#   push-branch.sh, run from the worktree with an origin that cannot be reached
#                       → exit 0, because a push failure is NOT a bail: a run whose network
#                         is down is still a correct run, and the script's exit code is what
#                         the conductor branches on, so anything but 0 here is the run's
#                         exit status changing for a transport problem.
#                       → HEAD, the commit count and the ledger file are exactly what they
#                         were before the call: the push is a copy, and a failed copy owes
#                         the run nothing.
#                       → one line appended to `.tdd/events.jsonl` whose `event` says the
#                         push failed, so the run's log carries the fact that the branch is
#                         not on the remote — the only record a human gets, since nothing
#                         stops or is narrated as an error.
#
# The origin is a path that does not exist rather than an unreachable host: the failure has
# to be the same failure on every machine and inside a sandbox with no network, and a real
# hostname would make this suite's answer depend on the DNS of whoever ran it.
#
# The event's NAME is matched as a pattern rather than pinned to one string. What the step
# asks for is "an event saying the push failed"; which word this repository ends up using
# for it is the green phase's to choose, and a suite that spelled it here would be pinning
# its own guess rather than the criterion.
#
# Run: scripts/tests/push-branch.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
PUSH="$HERE/../push-branch.sh"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output says which probe broke rather than just that the case did.
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

# git_q <repo> <args...> — git with an identity of its own, so the suite does not depend on
# whatever user.name/user.email the machine running it happens to carry (CI carries none).
git_q() { local repo="$1"; shift; git -C "$repo" -c user.name=veri -c user.email=veri@example.test "$@"; }

# jevents <file> — the `event` value of every line in the file, in file order, one per line:
# the log read the way a reader of a whole run reads it. A line that is not a JSON object
# prints `<<unparseable>>` and one without the key prints `<<missing>>`, so a broken line is
# visible in its own position instead of being mistaken for a call nobody made. python3
# rather than jq: event.sh already execs python3 in production, and jq is not a dependency.
jevents() {
  python3 -c '
import sys, json
for line in open(sys.argv[1]).read().splitlines():
    try:
        obj = json.loads(line)
    except Exception:
        print("<<unparseable>>")
        continue
    print(obj.get("event", "<<missing>>") if isinstance(obj, dict) else "<<unparseable>>")
' "$1" 2>/dev/null
}

# 1. The whole of this step's criterion, as one case. The fixture is a run in the shape the
#    conductor leaves behind at a green step: an issue branch with two commits on it and a
#    committed ledger, with `origin` pointing at a path that is not a repository, so the
#    push cannot succeed and nothing else about the call is unusual.
#
#    Every "unchanged" half is measured before the call as well as after, rather than
#    compared against constants written here: what the criterion promises is that the call
#    moved nothing, and a fixture that drifted would otherwise be asserted against a stale
#    guess. The ledger is compared as bytes, since a tick is a one-character edit.
name="push-branch.sh: a failing push exits 0 and leaves HEAD, the commit count and the ledger unchanged, recording an event that says the push failed"
problems=()
repo="$work/run"
mkdir -p "$repo/.tdd"
git init -q -b main "$repo" >/dev/null 2>&1
git_q "$repo" commit -q --allow-empty -m "initial" >/dev/null 2>&1
git_q "$repo" checkout -q -b tdd/191-run-commits-live-on-one-disk >/dev/null 2>&1
ledger="$repo/.tdd/issue-191.md"
cat > "$ledger" <<'LEDGER'
# Plan for #191 — A run's commits live on one disk until the draft PR

- [x] A push that fails leaves the run's exit status, ledger and commits unchanged ⟂ refactor pending
- [ ] After a step's green commit and tick, the branch exists on the remote at that commit
LEDGER
git_q "$repo" add -A >/dev/null 2>&1
git_q "$repo" commit -q -m "feat: a step's green commit (#191)" >/dev/null 2>&1
# An origin that is not a repository: the push fails locally, identically everywhere, with
# no network involved.
git_q "$repo" remote add origin "$work/no-such-remote.git" >/dev/null 2>&1

head_before="$(git_q "$repo" rev-parse HEAD)"
count_before="$(git_q "$repo" rev-list --count HEAD)"
ledger_before="$(cat "$ledger")"

( cd "$repo" && env VERI_ISSUE=191 VERI_ACTOR=conductor \
    VERI_STEP='A push that fails leaves the run unchanged' "$PUSH" ) >/dev/null 2>&1 && code=0 || code=$?

[[ "$code" == 0 ]] ||
  problems+=("want exit 0 — a failed push is not a bail, so the run's exit status is unchanged — got $code")

head_after="$(git_q "$repo" rev-parse HEAD)"
[[ "$head_after" == "$head_before" ]] ||
  problems+=("HEAD: want it unchanged at $head_before, got $head_after")

count_after="$(git_q "$repo" rev-list --count HEAD)"
[[ "$count_after" == "$count_before" ]] ||
  problems+=("commits: want the count unchanged at $count_before, got $count_after")

ledger_after="$(cat "$ledger")"
[[ "$ledger_after" == "$ledger_before" ]] ||
  problems+=("ledger: want .tdd/issue-191.md unchanged, got: $(printf '%q' "$ledger_after")")

log="$repo/.tdd/events.jsonl"
if [[ ! -f "$log" ]]; then
  problems+=("want an event saying the push failed appended to .tdd/events.jsonl, but no such file under $repo")
else
  events="$(jevents "$log")"
  grep -qiE 'push.*fail|fail.*push' <<< "$events" ||
    problems+=("want an event whose name says the push failed, got: $(printf '%q' "$(tr '\n' ' ' <<< "$events")")")
fi
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
