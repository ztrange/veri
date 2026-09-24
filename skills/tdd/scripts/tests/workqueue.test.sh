#!/usr/bin/env bash
# Tests for scripts/workqueue.sh — the only writer of `.tdd/workqueue`, the file that assigns
# issues to named workers and records what happened to each (issue #271).
#
# Contract under test:
#   workqueue.sh assign <worker> <issue>...  → appends one `<worker>\t<issue>\tqueued\t` line
#                                              per issue to `.tdd/workqueue` in the main
#                                              working tree, in the order given
#   workqueue.sh next <worker>               → prints that worker's first `queued` issue whose
#                                              `## Blocked by` names no open issue, read from
#                                              the VERI_GH_JSON fixtures
#   workqueue.sh start <worker> <issue>      → rewrites that worker's `queued` line for the
#                                              issue to `running`, in place
#   workqueue.sh done <worker> <issue> <sha> → rewrites that worker's `running` line for the
#                                              issue to `merged`, the sha as its detail
#   workqueue.sh park <worker> <issue> <why> → rewrites that worker's `running` line for the
#                                              issue to `parked`, the reason as its detail
#
# Run: scripts/tests/workqueue.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="$HERE/../workqueue.sh"
SKILL_DIR="$HERE/../.."
# shellcheck source=../lib/background.sh
source "$HERE/../lib/background.sh"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
pass=0 fail=0

# new_repo <dir> — a repository with one commit, so the script has a main working tree to
# resolve and nothing in `.tdd/` yet.
new_repo() {
  git init -q -b main "$1" >/dev/null 2>&1
  git -C "$1" -c user.name=veri -c user.email=veri@example.test \
    commit -q --allow-empty -m initial >/dev/null 2>&1
}

# seed_queue <dir> <printf-format> — a `.tdd/workqueue` in <dir> holding the lines the format
# prints, for a case that starts from a queue already written.
seed_queue() {
  mkdir -p "$1/.tdd"
  printf "$2" > "$1/.tdd/workqueue"
}

# issues_fixture <case> — writes stdin to $work/<case>.gh/issues.json, the one fixture
# `next` reads through VERI_GH_JSON.
issues_fixture() {
  mkdir -p "$work/$1.gh"
  cat > "$work/$1.gh/issues.json"
}

# expect_next <case> <want-exit> <want> <description> [<VAR>=<value>...] — runs `next alpha`
# in $work/<case> against the fixtures in $work/<case>.gh, with any assignments given in its
# environment, and counts the case passed when it exits <want-exit> printing exactly <want>.
expect_next() {
  local name="$1" want_code="$2" want="$3" what="$4" out code
  shift 4
  out="$(cd "$work/$name" && env "$@" VERI_GH_JSON="$work/$name.gh" "$SCRIPT" next alpha \
    2>"$work/$name.err")" && code=0 || code=$?
  if [[ "$code" -eq "$want_code" && "$out" == "$want" ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1))
    echo "FAIL - $what"
    echo "    exit: $code (want $want_code), stdout: '$out' (want '$want')"
    echo "    stderr: $(cat "$work/$name.err")"
  fi
}

# expect_show <case> <want-format> <description> [<worker>] — runs `show`, naming <worker>
# when one is given, in $work/<case>, and counts the case passed when it exits 0 printing
# exactly the lines <want-format> prints.
expect_show() {
  local name="$1" want what="$3" out code
  want="$(printf "$2")"
  shift 3
  out="$(cd "$work/$name" && "$SCRIPT" show "$@" 2>"$work/$name.err")" && code=0 || code=$?
  if [[ "$code" -eq 0 && "$out" == "$want" ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1))
    echo "FAIL - $what"
    echo "    exit: $code (want 0), stderr: $(cat "$work/$name.err")"
    diff <(printf '%s\n' "$want") <(printf '%s\n' "$out") | sed 's/^/    /'
  fi
}

# expect_queue <case> <want-format> <description> <subcommand> [<arg>...] — runs the
# subcommand in $work/<case>, and counts the case passed when it exits 0 leaving
# `.tdd/workqueue` holding exactly the lines <want-format> prints.
expect_queue() {
  local name="$1" want what="$3" out code got
  want="$(printf "$2")"
  shift 3
  out="$(cd "$work/$name" && "$SCRIPT" "$@" 2>&1)" && code=0 || code=$?
  got="$(cat "$work/$name/.tdd/workqueue" 2>/dev/null || printf '<no .tdd/workqueue>')"
  if [[ "$code" -eq 0 && "$got" == "$want" ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1))
    echo "FAIL - $what"
    echo "    exit: $code (want 0), output: $out"
    diff <(printf '%s\n' "$want") <(printf '%s\n' "$got") | sed 's/^/    /'
  fi
}

# expect_unchanged <case> <want-exit> <description> <subcommand> [<arg>...] — runs the
# subcommand in $work/<case>, and counts the case passed when it exits <want-exit> leaving
# `.tdd/workqueue` byte-identical to what it held before the run.
expect_unchanged() {
  local name="$1" want_code="$2" what="$3" out code
  shift 3
  cp "$work/$name/.tdd/workqueue" "$work/$name.before"
  out="$(cd "$work/$name" && "$SCRIPT" "$@" 2>&1)" && code=0 || code=$?
  if [[ "$code" -eq "$want_code" ]] && cmp -s "$work/$name.before" "$work/$name/.tdd/workqueue"; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1))
    echo "FAIL - $what"
    echo "    exit: $code (want $want_code), output: $out"
    diff "$work/$name.before" "$work/$name/.tdd/workqueue" 2>&1 | sed 's/^/    /'
  fi
}

# 1. assign appends one queued line per issue, in the order given.
repo="$work/assign-order"
new_repo "$repo"
expect_queue assign-order 'alpha\t12\tqueued\t\nalpha\t7\tqueued\t\nalpha\t30\tqueued\t' \
  "assign appends one queued line per issue, in the order given" assign alpha 12 7 30

# 2. an unknown subcommand exits 2 and leaves the queue file byte-identical.
repo="$work/unknown-subcommand"
new_repo "$repo"
seed_queue "$repo" 'beta\t4\tqueued\t\n'
expect_unchanged unknown-subcommand 2 \
  "an unknown subcommand exits 2 and leaves the queue file byte-identical" frobnicate alpha 12

# 3. an unknown subcommand in a repo with no queue exits 2 and creates no queue file.
repo="$work/unknown-subcommand-no-queue"
new_repo "$repo"
out="$(cd "$repo" && "$SCRIPT" frobnicate alpha 12 2>&1)" && code=0 || code=$?
if [[ "$code" -eq 2 && ! -e "$repo/.tdd/workqueue" ]]; then
  pass=$((pass + 1))
else
  fail=$((fail + 1))
  echo "FAIL - an unknown subcommand in a repo with no queue exits 2 and creates no queue file"
  echo "    exit: $code (want 2), output: $out"
  echo "    .tdd/workqueue: $([[ -e "$repo/.tdd/workqueue" ]] && echo present || echo absent) (want absent)"
fi

# 4. assign refuses with exit 2 an issue already queued or running for any worker, and
#    leaves the queue file byte-identical.
repo="$work/assign-held"
new_repo "$repo"
seed_queue "$repo" 'beta\t4\tqueued\t\ngamma\t9\trunning\t\n'
expect_unchanged assign-held 2 \
  "assign refuses with exit 2 an issue already queued for another worker" assign alpha 4
expect_unchanged assign-held 2 \
  "assign refuses with exit 2 an issue already running for another worker" assign alpha 9

# 5. an issue held only as merged, parked or skipped is free: assign takes it with exit 0 and
#    appends a queued line — only queued and running hold an issue.
repo="$work/assign-finished"
new_repo "$repo"
seed_queue "$repo" 'beta\t4\tmerged\tabc1234\ngamma\t9\tparked\tsecond bail\nbeta\t11\tskipped\t\n'
expect_queue assign-finished \
  'beta\t4\tmerged\tabc1234\ngamma\t9\tparked\tsecond bail\nbeta\t11\tskipped\t\nalpha\t4\tqueued\t\nalpha\t9\tqueued\t\nalpha\t11\tqueued\t' \
  "assign takes an issue held only as merged, parked or skipped" assign alpha 4 9 11

# 6. next prints the worker's first queued issue whose `## Blocked by` names no open issue:
#    another worker's item is not its own, and an issue blocked by an open one is skipped
#    while one blocked only by a closed one is launchable.
repo="$work/next-unblocked"
new_repo "$repo"
seed_queue "$repo" 'beta\t21\tqueued\t\nalpha\t20\tqueued\t\nalpha\t22\tqueued\t\n'
issues_fixture next-unblocked <<'JSON'
[
  {"number": 5, "title": "open blocker", "labels": [], "body": "", "state": "OPEN"},
  {"number": 6, "title": "closed blocker", "labels": [], "body": "", "state": "CLOSED"},
  {"number": 20, "title": "blocked", "labels": [], "state": "OPEN",
   "body": "Work.\n\n## Blocked by\n\n- #5\n"},
  {"number": 21, "title": "beta's", "labels": [], "body": "", "state": "OPEN"},
  {"number": 22, "title": "unblocked", "labels": [], "state": "OPEN",
   "body": "Work.\n\n## Blocked by\n\n- #6\n"}
]
JSON
expect_next next-unblocked 0 22 \
  "next prints the worker's first queued issue whose Blocked by names no open issue"

# 7. next does not read a `## Blocked by` URL naming another repository's issue as a blocker:
#    this repository is the one its `origin` names, and only a URL naming that one blocks. #131
#    names https://github.com/ztrange/veri-demo-node/issues/120, and #120 is also a real, open
#    issue HERE — so a reading that ignores the owner/name in the URL finds 120 open and
#    withholds #131, printing nothing.
repo="$work/next-foreign-url"
new_repo "$repo"
git -C "$repo" remote add origin https://github.com/ztrange/veri.git
seed_queue "$repo" 'alpha\t131\tqueued\t\n'
issues_fixture next-foreign-url <<'JSON'
[
  {"number": 120, "title": "open here", "labels": [], "body": "", "state": "OPEN"},
  {"number": 131, "title": "blocked elsewhere", "labels": [], "state": "OPEN",
   "body": "Work.\n\n## Blocked by\n\n- https://github.com/ztrange/veri-demo-node/issues/120\n"}
]
JSON
expect_next next-foreign-url 0 131 \
  "next does not read a Blocked by URL naming another repository's issue as a blocker"

# 8. an `origin` URL ending in `.git` still names this repository: a `## Blocked by` URL to an
#    open issue HERE blocks, so #131 is skipped and #132 is the one printed. Read with `.git`
#    left on, the repository would be `ztrange/veri.git`, the URL would look foreign, and #131
#    would be printed.
repo="$work/next-own-url"
new_repo "$repo"
git -C "$repo" remote add origin https://github.com/ztrange/veri.git
seed_queue "$repo" 'alpha\t131\tqueued\t\nalpha\t132\tqueued\t\n'
issues_fixture next-own-url <<'JSON'
[
  {"number": 120, "title": "open here", "labels": [], "body": "", "state": "OPEN"},
  {"number": 131, "title": "blocked here", "labels": [], "state": "OPEN",
   "body": "Work.\n\n## Blocked by\n\n- https://github.com/ztrange/veri/issues/120\n"},
  {"number": 132, "title": "unblocked", "labels": [], "body": "", "state": "OPEN"}
]
JSON
expect_next next-own-url 0 132 \
  "next reads a Blocked by URL naming this repository, origin ending in .git, as a blocker"

# 9. an SSH `origin` — `git@github.com:<owner>/<name>.git` — names this repository too, so a
#    URL to another repository's #120 does not block #131 even though #120 is open here. Read
#    as no repository at all, any github.com URL would count as local and #131 would be held.
#    The script runs with no global or system git config, so an ambient `url.<x>.insteadOf`
#    rule cannot rewrite the SSH URL into the HTTPS form case 7 already covers.
repo="$work/next-ssh-origin"
new_repo "$repo"
git -C "$repo" remote add origin git@github.com:ztrange/veri.git
seed_queue "$repo" 'alpha\t131\tqueued\t\n'
issues_fixture next-ssh-origin <<'JSON'
[
  {"number": 120, "title": "open here", "labels": [], "body": "", "state": "OPEN"},
  {"number": 131, "title": "blocked elsewhere", "labels": [], "state": "OPEN",
   "body": "Work.\n\n## Blocked by\n\n- https://github.com/ztrange/veri-demo-node/issues/120\n"}
]
JSON
expect_next next-ssh-origin 0 131 \
  "next reads an SSH origin as this repository when weighing a Blocked by URL" \
  GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1

# 10. next exits 3 printing nothing when none of the worker's queued items is launchable: its
#     one queued issue is blocked by an open one, its running item is not queued, and another
#     worker's unblocked item is not its own.
repo="$work/next-none"
new_repo "$repo"
seed_queue "$repo" 'alpha\t30\tqueued\t\nalpha\t31\trunning\t\nbeta\t32\tqueued\t\n'
issues_fixture next-none <<'JSON'
[
  {"number": 5, "title": "open blocker", "labels": [], "body": "", "state": "OPEN"},
  {"number": 30, "title": "blocked", "labels": [], "state": "OPEN",
   "body": "Work.\n\n## Blocked by\n\n- #5\n"},
  {"number": 31, "title": "running", "labels": [], "body": "", "state": "OPEN"},
  {"number": 32, "title": "beta's", "labels": [], "body": "", "state": "OPEN"}
]
JSON
expect_next next-none 3 '' \
  "next exits 3 with empty stdout when none of the worker's queued items is launchable"

# 11. start moves that worker's queued item to running, in place: the line keeps its position
#     and every other line — another worker's queued item, the worker's own other queued
#     item, and an earlier parked line for the same issue, which is the record of a finished
#     attempt and not the item being started — is left as it was.
repo="$work/start-queued"
new_repo "$repo"
seed_queue "$repo" 'alpha\t12\tparked\tsecond bail\nbeta\t4\tqueued\t\nalpha\t12\tqueued\t\nalpha\t7\tqueued\t\n'
expect_queue start-queued \
  'alpha\t12\tparked\tsecond bail\nbeta\t4\tqueued\t\nalpha\t12\trunning\t\nalpha\t7\tqueued\t' \
  "start moves that worker's queued item to running" start alpha 12

# 12. done moves that worker's running item to merged, recording the sha as its detail, in
#     place: another worker's running item and the worker's own queued item are left as they
#     were.
repo="$work/done-running"
new_repo "$repo"
seed_queue "$repo" 'beta\t4\trunning\t\nalpha\t12\trunning\t\nalpha\t7\tqueued\t\n'
expect_queue done-running \
  'beta\t4\trunning\t\nalpha\t12\tmerged\tabc1234\nalpha\t7\tqueued\t' \
  "done moves that worker's running item to merged, recording the sha" done alpha 12 abc1234

# 13. park moves that worker's running item to parked, recording the reason — spaces and all —
#     as its detail, in place: another worker's running item and the worker's own queued item
#     are left as they were.
repo="$work/park-running"
new_repo "$repo"
seed_queue "$repo" 'beta\t4\trunning\t\nalpha\t12\trunning\t\nalpha\t7\tqueued\t\n'
expect_queue park-running \
  'beta\t4\trunning\t\nalpha\t12\tparked\tsecond bail\nalpha\t7\tqueued\t' \
  "park moves that worker's running item to parked, recording the reason" \
  park alpha 12 "second bail"

# 14. start, done and park naming an item another worker owns each exit 1 — a clean refusal —
#     and leave the queue file byte-identical: alpha's queued 12 is not beta's to start, and
#     alpha's running 13 is not beta's to merge or park.
repo="$work/foreign-item"
new_repo "$repo"
seed_queue "$repo" 'alpha\t12\tqueued\t\nalpha\t13\trunning\t\n'
expect_unchanged foreign-item 1 \
  "start naming another worker's queued item exits 1 and leaves the file byte-identical" \
  start beta 12
expect_unchanged foreign-item 1 \
  "done naming another worker's running item exits 1 and leaves the file byte-identical" \
  done beta 13 abc1234
expect_unchanged foreign-item 1 \
  "park naming another worker's running item exits 1 and leaves the file byte-identical" \
  park beta 13 "second bail"

# 15. start on the worker's own item that is not queued, and done or park on its own item that
#     is not running, each exit 1 and leave the queue file byte-identical: alpha's 13 is
#     already running, so it cannot be started again, and alpha's 12 is still queued, so it
#     cannot be merged or parked before it has started.
repo="$work/wrong-state"
new_repo "$repo"
seed_queue "$repo" 'alpha\t12\tqueued\t\nalpha\t13\trunning\t\n'
expect_unchanged wrong-state 1 \
  "start on an item not queued exits 1 and leaves the file byte-identical" \
  start alpha 13
expect_unchanged wrong-state 1 \
  "done on an item not running exits 1 and leaves the file byte-identical" \
  done alpha 12 abc1234
expect_unchanged wrong-state 1 \
  "park on an item not running exits 1 and leaves the file byte-identical" \
  park alpha 12 "second bail"

# 16. no command ever removes a line: after assigns for two workers, each transition — start,
#     done, park — and refused calls of every kind (an issue already held, another worker's
#     item, an item in the wrong state, an unknown subcommand), every issue ever assigned is
#     still the issue of some line in the queue file.
repo="$work/never-removed"
new_repo "$repo"
for call in "assign alpha 12 7" "assign beta 30" "assign beta 12" "start alpha 12" \
  "start beta 7" "done alpha 12 abc1234" "start alpha 7" "done alpha 7" "park alpha 7 why" \
  "park alpha 30 why" "start beta 30" "frobnicate beta 30"; do
  # shellcheck disable=SC2086
  (cd "$repo" && "$SCRIPT" $call >/dev/null 2>&1) || true
done
held="$(cut -f2 "$repo/.tdd/workqueue" 2>/dev/null | tr '\n' ' ')"
missing=""
for issue in 12 7 30; do
  [[ " $held" == *" $issue "* ]] || missing="$missing $issue"
done
if [[ -z "$missing" ]]; then
  pass=$((pass + 1))
else
  fail=$((fail + 1))
  echo "FAIL - after assign, start, done, park and refused calls, every issue ever assigned is still a line"
  echo "    missing:$missing (want none), queue issues: $held"
fi

# 17. N assign and start calls run in parallel leave a well-formed file containing every
#     write: twenty workers each assign their own issue while alpha starts twenty of its own
#     queued items, all at once, and afterwards every line is four tab-separated fields with a
#     known state, every assigned issue is queued for its worker, and every started item is
#     running — no write lost to another's rewrite, none interleaved into a torn line.
repo="$work/parallel-writes"
new_repo "$repo"
seed=""
for i in $(seq 1 20); do
  seed="${seed}alpha\t$((100 + i))\tqueued\t\n"
done
seed_queue "$repo" "$seed"
pids=()
for i in $(seq 1 20); do
  (cd "$repo" && "$SCRIPT" assign "w$i" "$i" >/dev/null 2>&1) &
  pids+=("$!")
  (cd "$repo" && "$SCRIPT" start alpha "$((100 + i))" >/dev/null 2>&1) &
  pids+=("$!")
done
for pid in "${pids[@]}"; do
  wait "$pid" || true
done
torn="" missing=""
while IFS= read -r line; do
  [[ "$line" =~ ^[^$'\t']+$'\t'[0-9]+$'\t'(queued|running|merged|parked|skipped)$'\t'[^$'\t']*$ ]] \
    || torn="$torn [$line]"
done < "$repo/.tdd/workqueue"
# Every line fenced by newlines on both sides, so a whole line matches as `*\n<line>\n*`.
lines=$'\n'"$(cat "$repo/.tdd/workqueue")"$'\n'
for i in $(seq 1 20); do
  [[ "$lines" == *$'\n'"w$i"$'\t'"$i"$'\t'queued$'\t'$'\n'* ]] || missing="$missing w$i/$i:queued"
  [[ "$lines" == *$'\n'alpha$'\t'"$((100 + i))"$'\t'running$'\t'$'\n'* ]] \
    || missing="$missing alpha/$((100 + i)):running"
done
if [[ -z "$torn" && -z "$missing" ]]; then
  pass=$((pass + 1))
else
  fail=$((fail + 1))
  echo "FAIL - N assign and start calls run in parallel leave a well-formed file containing every write"
  echo "    torn lines:${torn:- none} (want none)"
  echo "    writes missing:${missing:- none} (want none)"
fi

# 18. a write that cannot take the lock exits 2 without touching the file: another writer holds
#     `.tdd/workqueue.lock`, and `assign` — told by VERI_WORKQUEUE_LOCK_WAIT=0 to wait no
#     seconds for it — gives up rather than waiting on, leaving the queue byte-identical. The
#     write runs in the background under a watchdog, so a writer that waits forever is killed
#     and read as `still waiting` instead of hanging the suite; one that answers is never
#     waited on.
repo="$work/lock-held"
new_repo "$repo"
seed_queue "$repo" 'alpha\t12\tqueued\t\n'
before="$(cat "$repo/.tdd/workqueue")"
mkdir "$repo/.tdd/workqueue.lock"
record="$work/lock-held.bg"
bg_start "$record" env VERI_WORKQUEUE_LOCK_WAIT=0 sh -c 'cd "$1" && exec "$2" assign beta 7' \
  _ "$repo" "$SCRIPT" 2>"$work/lock-held.err"
writer="$(tail -n 1 "$record" | cut -d' ' -f1)"
for _ in $(seq 1 60); do
  kill -0 "$writer" 2>/dev/null || break
  sleep 0.05
done
if kill -0 "$writer" 2>/dev/null; then
  bg_kill "$record"
  wait "$writer" 2>/dev/null
  code="still waiting"
else
  wait "$writer" && code=0 || code=$?
fi
after="$(cat "$repo/.tdd/workqueue")"
if [[ "$code" == 2 && "$after" == "$before" ]]; then
  pass=$((pass + 1))
else
  fail=$((fail + 1))
  echo "FAIL - a write that cannot take the lock exits 2 without touching the file"
  echo "    exit: $code (want 2), stderr: $(cat "$work/lock-held.err")"
  diff <(printf '%s\n' "$before") <(printf '%s\n' "$after") | sed 's/^/    /'
fi

# 19. show prints every item grouped by worker, each with its issue and state: a line naming
#     the worker, then one tab-indented `<issue>\t<state>` line per item of that worker's, in
#     file order. Workers come in the order they first appear, so alpha's 12 and 7 are printed
#     together although beta's 4 sits between them in the file.
new_repo "$work/show-grouped"
seed_queue "$work/show-grouped" 'alpha\t12\trunning\t\nbeta\t4\tqueued\t\nalpha\t7\tqueued\t\n'
expect_show show-grouped 'alpha\n\t12\trunning\n\t7\tqueued\nbeta\n\t4\tqueued' \
  "show prints every item grouped by worker, each with its issue and state"

# 20. show <worker> prints only that worker's items, in the same shape: beta's 4, which sits
#     between alpha's two lines in the file, is left out, and so is its heading.
new_repo "$work/show-one"
seed_queue "$work/show-one" 'alpha\t12\trunning\t\nbeta\t4\tqueued\t\nalpha\t7\tqueued\t\n'
expect_show show-one 'alpha\n\t12\trunning\n\t7\tqueued' \
  "show <worker> prints only that worker's items" alpha

# 21. called from a linked worktree, the script reads and writes `.tdd/workqueue` under the
#     repository's main working tree, not the worktree's own: `assign` run in the worktree
#     appends to the main tree's queue, which already holds beta's 4, `show` run there prints
#     both items, and the worktree is left with no `.tdd/workqueue` of its own.
repo="$work/linked-worktree"
new_repo "$repo"
git -C "$repo" worktree add -q -b side "$work/linked-worktree.wt" >/dev/null 2>&1
seed_queue "$repo" 'beta\t4\tqueued\t\n'
want_queue="$(printf 'beta\t4\tqueued\t\nalpha\t7\tqueued\t')"
want_show="$(printf 'beta\n\t4\tqueued\nalpha\n\t7\tqueued')"
out="$(cd "$work/linked-worktree.wt" && "$SCRIPT" assign alpha 7 2>&1 \
  && "$SCRIPT" show 2>&1)" && code=0 || code=$?
got="$(cat "$repo/.tdd/workqueue")"
if [[ "$code" -eq 0 && "$got" == "$want_queue" && "$out" == "$want_show" \
  && ! -e "$work/linked-worktree.wt/.tdd/workqueue" ]]; then
  pass=$((pass + 1))
else
  fail=$((fail + 1))
  echo "FAIL - called from a linked worktree, workqueue.sh reads and writes the main working tree's queue"
  echo "    exit: $code (want 0)"
  echo "    worktree's own .tdd/workqueue: $([[ -e "$work/linked-worktree.wt/.tdd/workqueue" ]] \
    && echo present || echo absent) (want absent)"
  echo "    main tree's queue:"
  diff <(printf '%s\n' "$want_queue") <(printf '%s\n' "$got") | sed 's/^/    /'
  echo "    show, run in the worktree:"
  diff <(printf '%s\n' "$want_show") <(printf '%s\n' "$out") | sed 's/^/    /'
fi

# 22. the worker loop is documented in `WORKER.md` beside `SKILL.md` — the file a worker
#     session loads, the way a scope run loads `SCOPE-LOOP.md` — and it names each call the
#     loop makes: `workqueue.sh next`, `start`, `done` and `park`. Each call is matched as the
#     command a reader would type, `workqueue.sh <subcommand>`, so the word "done" in a sentence
#     does not count as naming the call; every one missing is listed, so one run says which.
worker_doc="$SKILL_DIR/WORKER.md"
calls_missing=""
for call in next start done park; do
  grep -Eq "workqueue\.sh[[:space:]]+$call([^[:alnum:]_-]|\$)" "$worker_doc" 2>/dev/null \
    || calls_missing="$calls_missing $call"
done
if [[ -f "$worker_doc" && -z "$calls_missing" ]]; then
  pass=$((pass + 1))
else
  fail=$((fail + 1))
  echo "FAIL - WORKER.md beside SKILL.md documents the worker loop, naming each workqueue.sh call"
  echo "    WORKER.md: $([[ -f "$worker_doc" ]] && echo present || echo absent) (want present)"
  echo "    calls not named:${calls_missing:- none} (want none)"
fi

# 23. `SKILL.md` — resident in every session the skill starts — tells a session born as a
#     worker to `Read` `WORKER.md`, the way its *Inputs* point a scope at `SCOPE-LOOP.md`: a
#     file nothing points at is never loaded, so case 22's loop would be written and never run.
#     Matched as one line holding `Read` and then `WORKER.md`, both in backticks, so a mention
#     of the file in passing does not count as the instruction to load it.
skill_doc="$SKILL_DIR/SKILL.md"
if grep -E '`Read`.*`WORKER\.md`' "$skill_doc" > /dev/null 2>&1; then
  pass=$((pass + 1))
else
  fail=$((fail + 1))
  echo "FAIL - SKILL.md tells a session born as a worker to Read WORKER.md, the way it points a scope at SCOPE-LOOP.md"
  echo "    lines of SKILL.md naming WORKER.md (want one holding \`Read\` then \`WORKER.md\`):"
  grep -n 'WORKER\.md' "$skill_doc" | sed 's/^/      /'
fi

# 24. `CONTEXT.md`, the glossary every term in this repository is used by, defines **worker**
#     and **work queue** the way it defines every other term: a line opening `**<Term>**:`
#     that the definition follows. Matched as that heading, so a mention in passing — the
#     `_Avoid_: … worker …` lines under **Leaf** and **Actor** — does not count; every term
#     missing is listed, so one run says which.
context_doc="$SKILL_DIR/../../CONTEXT.md"
terms_missing=""
for term in Worker 'Work queue'; do
  grep -Ei "^\*\*$term\*\*:" "$context_doc" > /dev/null 2>&1 \
    || terms_missing="$terms_missing **$term**"
done
if [[ -z "$terms_missing" ]]; then
  pass=$((pass + 1))
else
  fail=$((fail + 1))
  echo "FAIL - CONTEXT.md defines worker and work queue"
  echo "    terms not defined:$terms_missing (want none)"
fi

# 25. assign with no worker, or with a worker and no issue, exits 2 and leaves the queue file
#     byte-identical: a call missing either argument is refused before anything is written,
#     never read as an assignment of nothing.
repo="$work/assign-missing-args"
new_repo "$repo"
seed_queue "$repo" 'beta\t4\tqueued\t\ngamma\t9\trunning\t\n'
expect_unchanged assign-missing-args 2 \
  "assign with no worker exits 2 and leaves the queue file byte-identical" assign
expect_unchanged assign-missing-args 2 \
  "assign with a worker and no issue exits 2 and leaves the queue file byte-identical" \
  assign alpha

# 26. assign naming the same issue twice in one call exits 2 and leaves the queue file
#     byte-identical: one call cannot queue an issue twice, any more than two calls can.
repo="$work/assign-duplicate-issue"
new_repo "$repo"
seed_queue "$repo" 'beta\t4\tqueued\t\n'
expect_unchanged assign-duplicate-issue 2 \
  "assign naming the same issue twice in one call exits 2 and leaves the queue file byte-identical" \
  assign alpha 12 12

echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
