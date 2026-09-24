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

# 1. assign appends one queued line per issue, in the order given.
repo="$work/assign-order"
new_repo "$repo"
expect_queue assign-order 'alpha\t12\tqueued\t\nalpha\t7\tqueued\t\nalpha\t30\tqueued\t' \
  "assign appends one queued line per issue, in the order given" assign alpha 12 7 30

# 2. an unknown subcommand exits 2 and leaves the queue file byte-identical.
repo="$work/unknown-subcommand"
new_repo "$repo"
seed_queue "$repo" 'beta\t4\tqueued\t\n'
cp "$repo/.tdd/workqueue" "$work/unknown-subcommand.before"
out="$(cd "$repo" && "$SCRIPT" frobnicate alpha 12 2>&1)" && code=0 || code=$?
if [[ "$code" -eq 2 ]] && cmp -s "$work/unknown-subcommand.before" "$repo/.tdd/workqueue"; then
  pass=$((pass + 1))
else
  fail=$((fail + 1))
  echo "FAIL - an unknown subcommand exits 2 and leaves the queue file byte-identical"
  echo "    exit: $code (want 2), output: $out"
  diff "$work/unknown-subcommand.before" "$repo/.tdd/workqueue" 2>&1 | sed 's/^/    /'
fi

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
cp "$repo/.tdd/workqueue" "$work/assign-held.before"
out_q="$(cd "$repo" && "$SCRIPT" assign alpha 4 2>&1)" && code_q=0 || code_q=$?
out_r="$(cd "$repo" && "$SCRIPT" assign alpha 9 2>&1)" && code_r=0 || code_r=$?
if [[ "$code_q" -eq 2 && "$code_r" -eq 2 ]] \
  && cmp -s "$work/assign-held.before" "$repo/.tdd/workqueue"; then
  pass=$((pass + 1))
else
  fail=$((fail + 1))
  echo "FAIL - assign refuses with exit 2 an issue already queued or running for any worker"
  echo "    queued issue: exit $code_q (want 2), output: $out_q"
  echo "    running issue: exit $code_r (want 2), output: $out_r"
  diff "$work/assign-held.before" "$repo/.tdd/workqueue" 2>&1 | sed 's/^/    /'
fi

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
cp "$repo/.tdd/workqueue" "$work/foreign-item.before"
out_s="$(cd "$repo" && "$SCRIPT" start beta 12 2>&1)" && code_s=0 || code_s=$?
out_d="$(cd "$repo" && "$SCRIPT" done beta 13 abc1234 2>&1)" && code_d=0 || code_d=$?
out_p="$(cd "$repo" && "$SCRIPT" park beta 13 "second bail" 2>&1)" && code_p=0 || code_p=$?
if [[ "$code_s" -eq 1 && "$code_d" -eq 1 && "$code_p" -eq 1 ]] \
  && cmp -s "$work/foreign-item.before" "$repo/.tdd/workqueue"; then
  pass=$((pass + 1))
else
  fail=$((fail + 1))
  echo "FAIL - start, done and park naming another worker's item exit 1 and leave the file byte-identical"
  echo "    start: exit $code_s (want 1), output: $out_s"
  echo "    done: exit $code_d (want 1), output: $out_d"
  echo "    park: exit $code_p (want 1), output: $out_p"
  diff "$work/foreign-item.before" "$repo/.tdd/workqueue" 2>&1 | sed 's/^/    /'
fi

echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
