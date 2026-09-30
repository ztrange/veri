#!/usr/bin/env bash
# Unit tests for scripts/push-branch.sh — the push the conductor makes after each step's
# green commit and after each verify-refactor PASS clears the mark, so a run's commits stop
# living on one disk until the draft PR is opened (issue #191).
# Zero-dependency plain-shell asserts, same idiom as event.test.sh.
#
# Why a failed push is not a bail — and therefore why all three halves of the failing-push
# contract below are about the run being untouched — is said in the script's header
# (push-branch.sh:12-19), once.
#
# Contract under test:
#   push-branch.sh, run from the worktree with an origin that cannot be reached
#                       → exit 0, the exit status the conductor branches on.
#                       → HEAD, the commit count and the ledger file are exactly what they
#                         were before the call.
#                       → one line appended to `.tdd/events.jsonl` whose `event` says the
#                         push failed.
#   push-branch.sh, run from the worktree with an origin it can reach
#                       → the run's branch is on that remote, at the commit HEAD is on.
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
source "$HERE/lib/harness.sh"
PUSH="$HERE/../push-branch.sh"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
pass=0 fail=0

unchanged() {
  local label="$1" before="$2" after="$3"
  [[ "$after" == "$before" ]] ||
    problems+=("$label: want it unchanged at $(printf '%q' "$before"), got $(printf '%q' "$after")")
}

run_fixture() {
  local repo="$1" branch="$2" issue="$3"
  mkdir -p "$repo/.tdd"
  git init -q -b main "$repo" >/dev/null 2>&1
  git_q "$repo" commit -q --allow-empty -m "initial" >/dev/null 2>&1
  git_q "$repo" checkout -q -b "$branch" >/dev/null 2>&1
  cat > "$repo/.tdd/issue-$issue.md"
  git_q "$repo" add -A >/dev/null 2>&1
  git_q "$repo" commit -q -m "feat: a step's green commit (#$issue)" >/dev/null 2>&1
}

git_q() { local repo="$1"; shift; git -C "$repo" -c user.name=veri -c user.email=veri@example.test "$@"; }

remote_at() { git_q "$1" rev-parse --verify -q "refs/heads/$2" 2>/dev/null || echo '<<absent>>'; }

push_counting_git() {
  local stubdir="$1" calls="$2"
  mkdir -p "$stubdir"
  : > "$calls"
  cat > "$stubdir/git" <<STUB
for a in "\$@"; do
  if [ "\$a" = push ]; then echo push >> "$calls"; break; fi
done
exec "$(command -v git)" "\$@"
STUB
  chmod +x "$stubdir/git"
}

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

name="push-branch.sh: a failing push exits 0 and leaves HEAD, the commit count and the ledger unchanged, recording an event that says the push failed"
problems=()
repo="$work/run"
ledger="$repo/.tdd/issue-191.md"
run_fixture "$repo" tdd/191-run-commits-live-on-one-disk 191 <<'LEDGER'

- [x] A push that fails leaves the run's exit status, ledger and commits unchanged ⟂ refactor pending
- [ ] After a step's green commit and tick, the branch exists on the remote at that commit
LEDGER
git_q "$repo" remote add origin "$work/no-such-remote.git" >/dev/null 2>&1

head_before="$(git_q "$repo" rev-parse HEAD)"
count_before="$(git_q "$repo" rev-list --count HEAD)"
ledger_before="$(cat "$ledger")"

unreachable_started="$SECONDS"
( cd "$repo" && env VERI_ISSUE=191 VERI_ACTOR=conductor VERI_PUSH_BACKOFF=0 \
    VERI_STEP='A push that fails leaves the run unchanged' "$PUSH" ) >/dev/null 2>&1 && code=0 || code=$?
unreachable_seconds=$((SECONDS - unreachable_started))

[[ "$code" == 0 ]] ||
  problems+=("want exit 0 — a failed push is not a bail, so the run's exit status is unchanged — got $code")

unchanged "HEAD" "$head_before" "$(git_q "$repo" rev-parse HEAD)"
unchanged "the commit count" "$count_before" "$(git_q "$repo" rev-list --count HEAD)"
unchanged ".tdd/issue-191.md (the ledger)" "$ledger_before" "$(cat "$ledger")"

log="$repo/.tdd/events.jsonl"
if [[ ! -f "$log" ]]; then
  problems+=("want an event saying the push failed appended to .tdd/events.jsonl, but no such file under $repo")
else
  events="$(jevents "$log")"
  grep -qiE 'push.*fail|fail.*push' <<< "$events" ||
    problems+=("want an event whose name says the push failed, got: $(printf '%q' "$(tr '\n' ' ' <<< "$events")")")
fi
report "$name"

name="push-branch.sh: a push that lands leaves the branch on the remote at the commit HEAD is on"
problems=()
repo="$work/landed"
remote="$work/origin.git"
git init -q --bare "$remote" >/dev/null 2>&1
branch=tdd/191-run-commits-live-on-one-disk
run_fixture "$repo" "$branch" 191 <<'LEDGER'

- [x] After a step's green commit and tick, the branch exists on the remote at that commit ⟂ refactor pending
LEDGER
git_q "$repo" remote add origin "$remote" >/dev/null 2>&1

head_sha="$(git_q "$repo" rev-parse HEAD)"

( cd "$repo" && env VERI_ISSUE=191 VERI_ACTOR=conductor VERI_PUSH_BACKOFF=0 \
    VERI_STEP='the branch exists on the remote' "$PUSH" ) >/dev/null 2>&1 && code=0 || code=$?

[[ "$code" == 0 ]] || problems+=("want exit 0 from a push that lands, got $code")

remote_sha="$(remote_at "$remote" "$branch")"
[[ "$remote_sha" == "$head_sha" ]] ||
  problems+=("want refs/heads/$branch on the remote at $head_sha (the commit HEAD is on), got $remote_sha")
report "$name"

name="push-branch.sh: an unreachable origin with VERI_PUSH_RETRIES=2 is attempted 3 times, exits 0, prints one stderr line naming the failure and the attempt count, and records one push-failed event, leaving HEAD, the commit count and the ledger unchanged"
problems=()
repo="$work/retried"
ledger="$repo/.tdd/issue-232.md"
run_fixture "$repo" tdd/232-push-retry 232 <<'LEDGER'

- [x] Unreachable origin is retried ⟂ refactor pending
- [ ] Non-fast-forward rejection exits 1
LEDGER
git_q "$repo" remote add origin "$work/no-such-remote-232.git" >/dev/null 2>&1

stubdir="$work/stub-bin"
calls="$work/push-calls"
push_counting_git "$stubdir" "$calls"

head_before="$(git_q "$repo" rev-parse HEAD)"
count_before="$(git_q "$repo" rev-list --count HEAD)"
ledger_before="$(cat "$ledger")"
errfile="$work/retried.stderr"

( cd "$repo" && env PATH="$stubdir:$PATH" VERI_PUSH_RETRIES=2 VERI_PUSH_BACKOFF=0 \
    VERI_ISSUE=232 VERI_ACTOR=conductor VERI_STEP='Unreachable origin is retried' \
    "$PUSH" ) >/dev/null 2>"$errfile" && code=0 || code=$?

attempts="$(grep -c . "$calls" | tr -d ' ')"
[[ "$attempts" == 3 ]] ||
  problems+=("want 3 push attempts (1 + VERI_PUSH_RETRIES=2), got $attempts")
[[ "$code" == 0 ]] ||
  problems+=("want exit 0 — an unreachable origin is not a bail — got $code")

failure_lines="$(grep -iE 'push' "$errfile" | grep -iE 'fail' | grep -c '3' | tr -d ' ')"
[[ "$failure_lines" == 1 ]] ||
  problems+=("want exactly one stderr line naming the push failure and the attempt count (3), got $failure_lines in: $(printf '%q' "$(cat "$errfile")")")

unchanged "HEAD" "$head_before" "$(git_q "$repo" rev-parse HEAD)"
unchanged "the commit count" "$count_before" "$(git_q "$repo" rev-list --count HEAD)"
unchanged ".tdd/issue-232.md (the ledger)" "$ledger_before" "$(cat "$ledger")"

log="$repo/.tdd/events.jsonl"
if [[ ! -f "$log" ]]; then
  problems+=("want one push-failed event in .tdd/events.jsonl, but no such file under $repo")
else
  events="$(jevents "$log")"
  n_failed="$(grep -cx 'push-failed' <<< "$events" | tr -d ' ')"
  [[ "$n_failed" == 1 ]] ||
    problems+=("want exactly one push-failed event, got $n_failed among: $(printf '%q' "$(tr '\n' ' ' <<< "$events")")")
fi
report "$name"

name="push-branch.sh: an unreachable origin with VERI_PUSH_RETRIES unset is attempted 4 times (the default 3 retries)"
problems=()
repo="$work/default-retries"
run_fixture "$repo" tdd/232-push-default-retries 232 <<'LEDGER'

- [ ] Unreachable origin with VERI_PUSH_RETRIES unset is attempted 4 times
LEDGER
git_q "$repo" remote add origin "$work/no-such-remote-232-default.git" >/dev/null 2>&1

stubdir="$work/stub-bin-default"
calls="$work/push-calls-default"
push_counting_git "$stubdir" "$calls"

( cd "$repo" && env -u VERI_PUSH_RETRIES PATH="$stubdir:$PATH" VERI_PUSH_BACKOFF=0 \
    VERI_ISSUE=232 VERI_ACTOR=conductor VERI_STEP='Unreachable origin uses the default retries' \
    "$PUSH" ) >/dev/null 2>&1 && code=0 || code=$?

attempts="$(grep -c . "$calls" | tr -d ' ')"
[[ "$attempts" == 4 ]] ||
  problems+=("want 4 push attempts (1 + the default 3 retries), got $attempts")
report "$name"

name="push-branch.sh: an origin that fails the first push attempt and accepts the second exits 0, leaves the branch on the remote at HEAD, and records no push-failed event"
problems=()
repo="$work/second-attempt"
remote="$work/origin-second-attempt.git"
git init -q --bare "$remote" >/dev/null 2>&1
branch=tdd/232-push-second-attempt
run_fixture "$repo" "$branch" 232 <<'LEDGER'

- [ ] Origin failing the first attempt and succeeding on the second ends with exit 0
LEDGER
git_q "$repo" remote add origin "$remote" >/dev/null 2>&1

stubdir="$work/stub-bin-second"
calls="$work/push-calls-second"
mkdir -p "$stubdir"
: > "$calls"
cat > "$stubdir/git" <<STUB
for a in "\$@"; do
  if [ "\$a" = push ]; then
    echo push >> "$calls"
    if [ "\$(grep -c . "$calls")" -eq 1 ]; then
      echo "fatal: unable to access origin: simulated blip" >&2
      exit 128
    fi
    break
  fi
done
exec "$(command -v git)" "\$@"
STUB
chmod +x "$stubdir/git"

head_sha="$(git_q "$repo" rev-parse HEAD)"

( cd "$repo" && env -u VERI_PUSH_RETRIES PATH="$stubdir:$PATH" VERI_PUSH_BACKOFF=0 \
    VERI_ISSUE=232 VERI_ACTOR=conductor VERI_STEP='A blip that clears is recovered' \
    "$PUSH" ) >/dev/null 2>&1 && code=0 || code=$?

[[ "$code" == 0 ]] || problems+=("want exit 0 from a push that lands on its second attempt, got $code")

remote_sha="$(remote_at "$remote" "$branch")"
[[ "$remote_sha" == "$head_sha" ]] ||
  problems+=("want refs/heads/$branch on the remote at $head_sha (the commit HEAD is on), got $remote_sha")

log="$repo/.tdd/events.jsonl"
if [[ -f "$log" ]]; then
  events="$(jevents "$log")"
  n_failed="$(grep -cx 'push-failed' <<< "$events" | tr -d ' ')"
  [[ "$n_failed" == 0 ]] ||
    problems+=("want no push-failed event, got $n_failed among: $(printf '%q' "$(tr '\n' ' ' <<< "$events")")")
fi
report "$name"

name="push-branch.sh: backoff is VERI_PUSH_BACKOFF seconds doubled per retry, and with VERI_PUSH_BACKOFF=0 a 3-retry failure completes in under 2 s"
problems=()
repo="$work/backoff"
run_fixture "$repo" tdd/232-push-backoff 232 <<'LEDGER'

- [ ] Backoff is VERI_PUSH_BACKOFF seconds doubled per retry
LEDGER
git_q "$repo" remote add origin "$work/no-such-remote-232-backoff.git" >/dev/null 2>&1

stubdir="$work/stub-bin-sleep"
sleeps="$work/sleep-calls"
mkdir -p "$stubdir"
: > "$sleeps"
cat > "$stubdir/sleep" <<STUB
echo "\$*" >> "$sleeps"
STUB
chmod +x "$stubdir/sleep"

( cd "$repo" && env PATH="$stubdir:$PATH" VERI_PUSH_RETRIES=3 VERI_PUSH_BACKOFF=1 \
    VERI_ISSUE=232 VERI_ACTOR=conductor VERI_STEP='Backoff doubles per retry' \
    "$PUSH" ) >/dev/null 2>&1

got_sleeps="$(tr '\n' ' ' < "$sleeps" | sed 's/ *$//')"
[[ "$got_sleeps" == "1 2 4" ]] ||
  problems+=("want sleeps of '1 2 4' seconds between 4 attempts with VERI_PUSH_BACKOFF=1, got $(printf '%q' "$got_sleeps")")

start="$(python3 -c 'import time; print(time.time())')"
( cd "$repo" && env VERI_PUSH_RETRIES=3 VERI_PUSH_BACKOFF=0 \
    VERI_ISSUE=232 VERI_ACTOR=conductor VERI_STEP='Zero backoff waits on nothing' \
    "$PUSH" ) >/dev/null 2>&1
end="$(python3 -c 'import time; print(time.time())')"
elapsed="$(python3 -c "print('%.2f' % ($end - $start))")"
python3 -c "import sys; sys.exit(0 if $elapsed < 2 else 1)" ||
  problems+=("want a 3-retry failure with VERI_PUSH_BACKOFF=0 to complete in under 2 s, took ${elapsed} s")
report "$name"

name="push-branch.sh: a non-integer VERI_PUSH_RETRIES or VERI_PUSH_BACKOFF exits 2 without attempting a push"
problems=()
for bad in VERI_PUSH_RETRIES=abc VERI_PUSH_BACKOFF=1.5; do
  var="${bad%%=*}"
  repo="$work/bad-$var"
  remote="$work/origin-bad-$var.git"
  git init -q --bare "$remote" >/dev/null 2>&1
  run_fixture "$repo" tdd/232-push-bad-arguments 232 <<'LEDGER'

- [ ] Non-integer VERI_PUSH_RETRIES or VERI_PUSH_BACKOFF exits 2 without attempting a push
LEDGER
  git_q "$repo" remote add origin "$remote" >/dev/null 2>&1

  stubdir="$work/stub-bin-bad-$var"
  calls="$work/push-calls-bad-$var"
  push_counting_git "$stubdir" "$calls"

  ( cd "$repo" && env -u VERI_PUSH_RETRIES -u VERI_PUSH_BACKOFF PATH="$stubdir:$PATH" \
      VERI_PUSH_RETRIES=0 VERI_PUSH_BACKOFF=0 "$bad" \
      VERI_ISSUE=232 VERI_ACTOR=conductor VERI_STEP='Bad push tunables exit 2' \
      "$PUSH" ) >/dev/null 2>&1 && code=0 || code=$?

  [[ "$code" == 2 ]] ||
    problems+=("$bad: want exit 2 — a non-integer value is bad arguments — got $code")
  attempts="$(grep -c . "$calls" | tr -d ' ')"
  [[ "$attempts" == 0 ]] ||
    problems+=("$bad: want no push attempt, got $attempts")
done
report "$name"

name="push-branch.sh: a non-fast-forward rejection exits 1 after exactly one attempt, names the remote branch's full sha on stderr, and records a push-rejected event with remote_sha"
problems=()
repo="$work/non-ff"
remote="$work/origin-non-ff.git"
git init -q --bare "$remote" >/dev/null 2>&1
branch=tdd/232-push-non-ff
run_fixture "$repo" "$branch" 232 <<'LEDGER'

- [ ] Non-fast-forward rejection exits 1 after exactly one attempt
LEDGER
git_q "$repo" remote add origin "$remote" >/dev/null 2>&1
git_q "$repo" push -q origin "$branch" >/dev/null 2>&1
remote_before="$(remote_at "$remote" "$branch")"
git_q "$repo" commit -q --amend -m "feat: the step's green commit, rewritten (#232)" >/dev/null 2>&1

stubdir="$work/stub-bin-non-ff"
calls="$work/push-calls-non-ff"
push_counting_git "$stubdir" "$calls"
errfile="$work/non-ff.stderr"

( cd "$repo" && env -u VERI_PUSH_RETRIES PATH="$stubdir:$PATH" VERI_PUSH_BACKOFF=0 \
    VERI_ISSUE=232 VERI_ACTOR=conductor VERI_STEP='Non-fast-forward rejection exits 1' \
    "$PUSH" ) >/dev/null 2>"$errfile" && code=0 || code=$?

[[ "$code" == 1 ]] ||
  problems+=("want exit 1 — a non-fast-forward rejection is a clean negative — got $code")
attempts="$(grep -c . "$calls" | tr -d ' ')"
[[ "$attempts" == 1 ]] ||
  problems+=("want exactly 1 push attempt — a rejection is never retried — got $attempts")
grep -qF "$remote_before" "$errfile" ||
  problems+=("want stderr to contain the remote branch's sha $remote_before, got: $(printf '%q' "$(cat "$errfile")")")

log="$repo/.tdd/events.jsonl"
if [[ ! -f "$log" ]]; then
  problems+=("want a push-rejected event in .tdd/events.jsonl, but no such file under $repo")
else
  got_sha="$(python3 -c '
import sys, json
for line in open(sys.argv[1]).read().splitlines():
    try:
        obj = json.loads(line)
    except Exception:
        continue
    if isinstance(obj, dict) and obj.get("event") == "push-rejected":
        print(obj.get("remote_sha", "<<missing>>"))
' "$log" 2>/dev/null)"
  [[ "$got_sha" == "$remote_before" ]] ||
    problems+=("want one push-rejected event with remote_sha=$remote_before, got $(printf '%q' "$got_sha") among events: $(printf '%q' "$(jevents "$log" | tr '\n' ' ')")")
fi
report "$name"

name="push-branch.sh: a push that lands exits 0, writes nothing to stderr beyond git's own output, and appends no event"
problems=()
repo="$work/quiet-success"
remote="$work/origin-quiet-success.git"
git init -q --bare "$remote" >/dev/null 2>&1
branch=tdd/232-push-quiet-success
run_fixture "$repo" "$branch" 232 <<'LEDGER'

- [ ] A successful push exits 0, writes nothing to stderr beyond git's own output, and appends no event
LEDGER
git_q "$repo" remote add origin "$remote" >/dev/null 2>&1

stubdir="$work/stub-bin-quiet"
gitout="$work/git-own-output-quiet"
mkdir -p "$stubdir"
: > "$gitout"
cat > "$stubdir/git" <<STUB
o="\$(mktemp)" e="\$(mktemp)"
"$(command -v git)" "\$@" >"\$o" 2>"\$e"; rc=\$?
cat "\$o"; cat "\$e" >&2
cat "\$o" "\$e" >> "$gitout"
rm -f "\$o" "\$e"
exit \$rc
STUB
chmod +x "$stubdir/git"

log="$repo/.tdd/events.jsonl"
events_before="$( [[ -f "$log" ]] && grep -c . "$log" | tr -d ' ' || echo 0)"
errfile="$work/quiet-success.stderr"

( cd "$repo" && env PATH="$stubdir:$PATH" VERI_PUSH_BACKOFF=0 \
    VERI_ISSUE=232 VERI_ACTOR=conductor VERI_STEP='A successful push is quiet' \
    "$PUSH" ) >/dev/null 2>"$errfile" && code=0 || code=$?

[[ "$code" == 0 ]] || problems+=("want exit 0 from a push that lands, got $code")

while IFS= read -r line; do
  [[ -z "$line" ]] && continue
  grep -qxF -- "$line" "$gitout" ||
    problems+=("want no stderr line beyond git's own output, got $(printf '%q' "$line")")
done < "$errfile"

events_after="$( [[ -f "$log" ]] && grep -c . "$log" | tr -d ' ' || echo 0)"
[[ "$events_after" == "$events_before" ]] ||
  problems+=("want no event appended to .tdd/events.jsonl, got $((events_after - events_before)): $(printf '%q' "$(jevents "$log" | tr '\n' ' ')")")
report "$name"


push_unwritable_tdd() {
  local repo="$1"
  chmod 555 "$repo/.tdd"
  ( cd "$repo" && env VERI_PUSH_RETRIES=0 VERI_PUSH_BACKOFF=0 \
      VERI_ISSUE=232 VERI_ACTOR=conductor VERI_STEP='A failing event write exits 2' \
      "$PUSH" ) >/dev/null 2>&1 && code=0 || code=$?
  chmod 755 "$repo/.tdd"
}

name="push-branch.sh: a failing event write exits 2 for both an unreachable origin and a non-fast-forward rejection"
problems=()
repo="$work/event-fails-unreachable"
run_fixture "$repo" tdd/232-event-fails-unreachable 232 <<'LEDGER'

- [ ] A failing event write exits 2
LEDGER
git_q "$repo" remote add origin "$work/no-such-origin-event-fails" >/dev/null 2>&1
push_unwritable_tdd "$repo"
[[ "$code" == 2 ]] ||
  problems+=("unreachable origin: want exit 2 when the push-failed event cannot be written, got $code")

repo="$work/event-fails-non-ff"
remote="$work/origin-event-fails-non-ff.git"
git init -q --bare "$remote" >/dev/null 2>&1
branch=tdd/232-event-fails-non-ff
run_fixture "$repo" "$branch" 232 <<'LEDGER'

- [ ] A failing event write exits 2
LEDGER
git_q "$repo" remote add origin "$remote" >/dev/null 2>&1
git_q "$repo" push -q origin "$branch" >/dev/null 2>&1
git_q "$repo" commit -q --amend -m "feat: the step's green commit, rewritten (#232)" >/dev/null 2>&1
push_unwritable_tdd "$repo"
[[ "$code" == 2 ]] ||
  problems+=("non-fast-forward rejection: want exit 2 when the push-rejected event cannot be written, got $code")
report "$name"

name="push-branch.test.sh: case 1's push to a missing origin completes in under 5 s of wall time"
problems=()
[[ "$unreachable_seconds" -lt 5 ]] ||
  problems+=("want the push to a missing origin to complete in under 5 s — a case pushing to a missing origin sets VERI_PUSH_BACKOFF=0 — took ${unreachable_seconds} s")
report "$name"

name="push-branch.sh --force-with-lease=<branch>:<sha> replaces a remote still at <sha>, refuses one that has moved on, and with no argument still replaces nothing"
problems=()
branch=tdd/238-lease
step='push-branch.sh pushes under a lease'

lease_push() {
  ( cd "$repo" && VERI_PUSH_RETRIES=0 VERI_PUSH_BACKOFF=0 VERI_ISSUE=238 VERI_ACTOR=conductor VERI_STEP="$step" \
      "$PUSH" "$@" ) >/dev/null 2>"$work/lease.stderr" && code=0 || code=$?
  got="$(remote_at "$remote" "$branch")"
}

lease_fixture() {
  repo="$work/lease-$1"
  remote="$work/origin-lease-$1.git"
  git init -q --bare "$remote" >/dev/null 2>&1
  run_fixture "$repo" "$branch" 238 <<'LEDGER'

- [ ] push-branch.sh pushes under a lease
LEDGER
  git_q "$repo" remote add origin "$remote" >/dev/null 2>&1
  git_q "$repo" push -q origin "$branch" >/dev/null 2>&1
  seen="$(git_q "$repo" rev-parse HEAD)"
}

lease_fixture holds
git_q "$repo" commit -q --amend -m "feat: the step's green commit, rebased (#238)" >/dev/null 2>&1
head="$(git_q "$repo" rev-parse HEAD)"
lease_push "--force-with-lease=$branch:$seen"
[[ "$code" == 0 ]] ||
  problems+=("lease that holds: want exit 0, got $code; stderr: $(printf '%q' "$(cat "$work/lease.stderr")")")
[[ "$got" == "$head" ]] ||
  problems+=("lease that holds: want origin/$branch replaced by HEAD $head, got $got (the leased sha was $seen)")

lease_fixture stale
moved="$(git_q "$repo" commit-tree -p "$seen" -m "someone else's push (#238)" "$seen^{tree}")"
git_q "$repo" push -q origin "$moved:refs/heads/$branch" >/dev/null 2>&1
git_q "$repo" commit -q --amend -m "feat: the step's green commit, rebased (#238)" >/dev/null 2>&1
lease_push "--force-with-lease=$branch:$seen"
[[ "$code" == 1 ]] ||
  problems+=("stale lease: want exit 1 — the remote moved on, a clean refusal — got $code")
[[ "$got" == "$moved" ]] ||
  problems+=("stale lease: want origin/$branch left at $moved, where it moved to, got $got")
lease_push
[[ "$code" == 1 ]] ||
  problems+=("no argument: want exit 1 — pushed exactly as before, so rejected — got $code")
[[ "$got" == "$moved" ]] ||
  problems+=("no argument: want origin/$branch left at $moved — never a bare force — got $got")
lease_push --force
[[ "$code" == 2 ]] ||
  problems+=("bare --force: want exit 2 — bad arguments, the one force allowed is pinned to a sha — got $code")
[[ "$got" == "$moved" ]] ||
  problems+=("bare --force: want origin/$branch left at $moved, got $got")
for args in "--force-with-lease" "--force-with-lease=$branch" \
            "--force-with-lease=$branch:origin/$branch" \
            "--force-with-lease=$branch:$moved --force"; do
  lease_push $args
  [[ "$code" == 2 ]] ||
    problems+=("'$args': want exit 2 — bad arguments, the one force allowed is a single lease pinned to a sha — got $code")
  [[ "$got" == "$moved" ]] ||
    problems+=("'$args': want origin/$branch left at $moved, got $got")
done
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
