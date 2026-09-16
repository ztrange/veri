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

# unchanged <label> <before> <after> — one probe of the "moved nothing" half of the
# criterion, which the case makes three times over (HEAD, the commit count, the ledger).
# Each measures its own before and after; what is the same every time is the comparison and
# the shape of the problem it files, so it is written once here. `%q` on both values because
# one of the three is a multi-line file: unquoted, a mismatching ledger would break the
# report's one-problem-per-line shape and bury the other probes.
unchanged() {
  local label="$1" before="$2" after="$3"
  [[ "$after" == "$before" ]] ||
    problems+=("$label: want it unchanged at $(printf '%q' "$before"), got $(printf '%q' "$after")")
}

# run_fixture <repo> <branch> <issue> — a run in the shape the conductor leaves behind at a
# green step: <branch> cut from an initial commit on main, carrying one commit that adds the
# ledger `.tdd/issue-<issue>.md`, whose content is read from stdin. No origin: which remote
# the run pushes to is what each case is about, so each case adds its own.
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
ledger="$repo/.tdd/issue-191.md"
run_fixture "$repo" tdd/191-run-commits-live-on-one-disk 191 <<'LEDGER'
# Plan for #191 — A run's commits live on one disk until the draft PR

- [x] A push that fails leaves the run's exit status, ledger and commits unchanged ⟂ refactor pending
- [ ] After a step's green commit and tick, the branch exists on the remote at that commit
LEDGER
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

# 2. The other half of the contract, and this cycle's criterion: a push that CAN land does,
#    so that after a step's green commit and tick the branch exists on the remote at that
#    commit. The fixture is the same shape as case 1 — an issue branch with a commit and a
#    committed ledger — with the one difference that matters: `origin` is a bare repository
#    that really is one, so the copy succeeds.
#
#    A bare repo on disk rather than a real host, for case 1's reason turned around: the
#    push has to land the same way on every machine and inside a sandbox with no network.
#
#    The assertion is the sha, not the branch's mere existence. "The branch exists on the
#    remote" is only worth anything if it is the run's work that is there: a remote branch
#    sitting at an older commit would satisfy existence and still leave the step's commit on
#    one disk, which is the whole of what #191 is about.
name="push-branch.sh: a push that lands leaves the branch on the remote at the commit HEAD is on"
problems=()
repo="$work/landed"
remote="$work/origin.git"
git init -q --bare "$remote" >/dev/null 2>&1
branch=tdd/191-run-commits-live-on-one-disk
run_fixture "$repo" "$branch" 191 <<'LEDGER'
# Plan for #191 — A run's commits live on one disk until the draft PR

- [x] After a step's green commit and tick, the branch exists on the remote at that commit ⟂ refactor pending
LEDGER
git_q "$repo" remote add origin "$remote" >/dev/null 2>&1

head_sha="$(git_q "$repo" rev-parse HEAD)"

( cd "$repo" && env VERI_ISSUE=191 VERI_ACTOR=conductor \
    VERI_STEP='the branch exists on the remote' "$PUSH" ) >/dev/null 2>&1 && code=0 || code=$?

[[ "$code" == 0 ]] || problems+=("want exit 0 from a push that lands, got $code")

# `<<absent>>` rather than an empty string when the ref is not there, so the report
# distinguishes "no branch on the remote at all" from a branch at some other sha.
remote_sha="$(git_q "$remote" rev-parse --verify -q "refs/heads/$branch" 2>/dev/null || echo '<<absent>>')"
[[ "$remote_sha" == "$head_sha" ]] ||
  problems+=("want refs/heads/$branch on the remote at $head_sha (the commit HEAD is on), got $remote_sha")
report "$name"

# 3. Issue #232's first criterion: an unreachable origin is retried, not tried once. With
#    VERI_PUSH_RETRIES=2 — two extra attempts after the first — the push is attempted 3
#    times; when all three fail the call still exits 0, says so on ONE stderr line that
#    names the failure and the attempt count, and records ONE `push-failed` event, however
#    many attempts it took. VERI_PUSH_BACKOFF=0 so nothing waits on wall time.
#
#    The attempts are counted by a `git` stub first on PATH that logs each `push` it sees
#    and then execs the real git, so the push still really fails against a path that is not
#    a repository — case 1's origin, for case 1's reason.
name="push-branch.sh: an unreachable origin with VERI_PUSH_RETRIES=2 is attempted 3 times, exits 0, prints one stderr line naming the failure and the attempt count, and records one push-failed event, leaving HEAD, the commit count and the ledger unchanged"
problems=()
repo="$work/retried"
ledger="$repo/.tdd/issue-232.md"
run_fixture "$repo" tdd/232-push-retry 232 <<'LEDGER'
# Plan for #232 — push-branch.sh exits 0 on a rejected push

- [x] Unreachable origin is retried ⟂ refactor pending
- [ ] Non-fast-forward rejection exits 1
LEDGER
git_q "$repo" remote add origin "$work/no-such-remote-232.git" >/dev/null 2>&1

stubdir="$work/stub-bin"
calls="$work/push-calls"
mkdir -p "$stubdir"
: > "$calls"
cat > "$stubdir/git" <<STUB
#!/usr/bin/env bash
for a in "\$@"; do
  if [[ "\$a" == push ]]; then echo push >> "$calls"; break; fi
done
exec "$(command -v git)" "\$@"
STUB
chmod +x "$stubdir/git"

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

# 4. Issue #232's second criterion: the retry count has a default. With VERI_PUSH_RETRIES
#    unset — removed from the environment, not set empty, so an ambient value in the shell
#    running the suite cannot stand in for the default — an unreachable origin is attempted
#    4 times: the first attempt plus the default 3 retries. Counted by the same kind of
#    `git` stub as case 3, with a call log of its own.
name="push-branch.sh: an unreachable origin with VERI_PUSH_RETRIES unset is attempted 4 times (the default 3 retries)"
problems=()
repo="$work/default-retries"
run_fixture "$repo" tdd/232-push-default-retries 232 <<'LEDGER'
# Plan for #232 — push-branch.sh exits 0 on a rejected push

- [ ] Unreachable origin with VERI_PUSH_RETRIES unset is attempted 4 times
LEDGER
git_q "$repo" remote add origin "$work/no-such-remote-232-default.git" >/dev/null 2>&1

stubdir="$work/stub-bin-default"
calls="$work/push-calls-default"
mkdir -p "$stubdir"
: > "$calls"
cat > "$stubdir/git" <<STUB
#!/usr/bin/env bash
for a in "\$@"; do
  if [[ "\$a" == push ]]; then echo push >> "$calls"; break; fi
done
exec "$(command -v git)" "\$@"
STUB
chmod +x "$stubdir/git"

( cd "$repo" && env -u VERI_PUSH_RETRIES PATH="$stubdir:$PATH" VERI_PUSH_BACKOFF=0 \
    VERI_ISSUE=232 VERI_ACTOR=conductor VERI_STEP='Unreachable origin uses the default retries' \
    "$PUSH" ) >/dev/null 2>&1 && code=0 || code=$?

attempts="$(grep -c . "$calls" | tr -d ' ')"
[[ "$attempts" == 4 ]] ||
  problems+=("want 4 push attempts (1 + the default 3 retries), got $attempts")
report "$name"

# 5. Issue #232's third criterion: a blip that clears is recovered by the retry. The `git`
#    stub first on PATH fails the FIRST `push` it sees without running it, and hands every
#    later call to the real git, so the second attempt really lands on a bare repository —
#    case 2's origin, for case 2's reason. The call ends with exit 0, the branch on the
#    remote at the commit HEAD is on, and no `push-failed` event: a push that landed owes
#    the log nothing, whichever attempt it landed on. VERI_PUSH_RETRIES is removed from the
#    environment so the default is what gives the second attempt, and VERI_PUSH_BACKOFF=0
#    so nothing waits on wall time.
name="push-branch.sh: an origin that fails the first push attempt and accepts the second exits 0, leaves the branch on the remote at HEAD, and records no push-failed event"
problems=()
repo="$work/second-attempt"
remote="$work/origin-second-attempt.git"
git init -q --bare "$remote" >/dev/null 2>&1
branch=tdd/232-push-second-attempt
run_fixture "$repo" "$branch" 232 <<'LEDGER'
# Plan for #232 — push-branch.sh exits 0 on a rejected push

- [ ] Origin failing the first attempt and succeeding on the second ends with exit 0
LEDGER
git_q "$repo" remote add origin "$remote" >/dev/null 2>&1

stubdir="$work/stub-bin-second"
calls="$work/push-calls-second"
mkdir -p "$stubdir"
: > "$calls"
cat > "$stubdir/git" <<STUB
#!/usr/bin/env bash
for a in "\$@"; do
  if [[ "\$a" == push ]]; then
    echo push >> "$calls"
    if [[ "\$(grep -c . "$calls")" -eq 1 ]]; then
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

remote_sha="$(git_q "$remote" rev-parse --verify -q "refs/heads/$branch" 2>/dev/null || echo '<<absent>>')"
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

# 6. Issue #232's fourth criterion: the wait between attempts is VERI_PUSH_BACKOFF seconds,
#    doubled each retry, and a zero backoff costs no wall time. Two probes of one criterion.
#
#    The doubling is observed through a `sleep` stub first on PATH that logs its argument
#    and returns at once, so VERI_PUSH_BACKOFF=1 with VERI_PUSH_RETRIES=3 must log waits of
#    1, 2 and 4 — one per retry, none after the last attempt — without the suite waiting 7 s.
#    The zero-backoff half runs with no stub at all, the real `sleep`, and times the whole
#    call with python3's clock: under 2 s for a 3-retry failure against case 1's origin.
name="push-branch.sh: backoff is VERI_PUSH_BACKOFF seconds doubled per retry, and with VERI_PUSH_BACKOFF=0 a 3-retry failure completes in under 2 s"
problems=()
repo="$work/backoff"
run_fixture "$repo" tdd/232-push-backoff 232 <<'LEDGER'
# Plan for #232 — push-branch.sh exits 0 on a rejected push

- [ ] Backoff is VERI_PUSH_BACKOFF seconds doubled per retry
LEDGER
git_q "$repo" remote add origin "$work/no-such-remote-232-backoff.git" >/dev/null 2>&1

stubdir="$work/stub-bin-sleep"
sleeps="$work/sleep-calls"
mkdir -p "$stubdir"
: > "$sleeps"
cat > "$stubdir/sleep" <<STUB
#!/usr/bin/env bash
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

# 7. Issue #232's fifth criterion: a non-integer VERI_PUSH_RETRIES or VERI_PUSH_BACKOFF is
#    bad arguments — exit 2, before any push is attempted. One probe per variable, each with
#    the other left at a valid value. The origin is a bare repository the push CAN reach, so
#    a script that ignored the bad value would land the push and exit 0 rather than fail for
#    some unrelated reason; the attempts are counted by case 3's kind of `git` stub, with a
#    call log per probe.
name="push-branch.sh: a non-integer VERI_PUSH_RETRIES or VERI_PUSH_BACKOFF exits 2 without attempting a push"
problems=()
for bad in VERI_PUSH_RETRIES=abc VERI_PUSH_BACKOFF=1.5; do
  var="${bad%%=*}"
  repo="$work/bad-$var"
  remote="$work/origin-bad-$var.git"
  git init -q --bare "$remote" >/dev/null 2>&1
  run_fixture "$repo" tdd/232-push-bad-arguments 232 <<'LEDGER'
# Plan for #232 — push-branch.sh exits 0 on a rejected push

- [ ] Non-integer VERI_PUSH_RETRIES or VERI_PUSH_BACKOFF exits 2 without attempting a push
LEDGER
  git_q "$repo" remote add origin "$remote" >/dev/null 2>&1

  stubdir="$work/stub-bin-bad-$var"
  calls="$work/push-calls-bad-$var"
  mkdir -p "$stubdir"
  : > "$calls"
  cat > "$stubdir/git" <<STUB
#!/usr/bin/env bash
for a in "\$@"; do
  if [[ "\$a" == push ]]; then echo push >> "$calls"; break; fi
done
exec "$(command -v git)" "\$@"
STUB
  chmod +x "$stubdir/git"

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

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
