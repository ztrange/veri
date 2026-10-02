#!/usr/bin/env bash
# Tests for scripts/workqueue.sh — the only writer of `.tdd/workqueue`, the file that assigns
# issues to named workers and records what happened to each.
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
source "$HERE/../lib/background.sh"
source "$HERE/lib/harness.sh"
work="$(scratch_dir)"

make_repo() {
  new_repo -b main "$1" >/dev/null 2>&1
  git -C "$1" -c user.name=veri -c user.email=veri@example.test \
    commit -q --allow-empty -m initial >/dev/null 2>&1
}

seed_queue() {
  mkdir -p "$1/.tdd"
  printf "$2" > "$1/.tdd/workqueue"
}

issues_fixture() {
  mkdir -p "$work/$1.gh"
  cat > "$work/$1.gh/issues.json"
}

expect_next() {
  local name="$1" want_code="$2" want="$3" what="$4" out code
  shift 4
  out="$(cd "$work/$name" && env "$@" VERI_GH_JSON="$work/$name.gh" "$SCRIPT" next alpha \
    2>"$work/$name.err")" && code=0 || code=$?
  if [[ "$code" -eq "$want_code" && "$out" == "$want" ]]; then
    ok
  else
    no "$what"
    echo "    exit: $code (want $want_code), stdout: '$out' (want '$want')"
    echo "    stderr: $(cat "$work/$name.err")"
  fi
}

expect_show() {
  local name="$1" want what="$3" out code
  want="$(printf "$2")"
  shift 3
  out="$(cd "$work/$name" && "$SCRIPT" show "$@" 2>"$work/$name.err")" && code=0 || code=$?
  if [[ "$code" -eq 0 && "$out" == "$want" ]]; then
    ok
  else
    no "$what"
    echo "    exit: $code (want 0), stderr: $(cat "$work/$name.err")"
    diff <(printf '%s\n' "$want") <(printf '%s\n' "$out") | sed 's/^/    /'
  fi
}

expect_queue() {
  local name="$1" want what="$3" out code got
  want="$(printf "$2")"
  shift 3
  out="$(cd "$work/$name" && "$SCRIPT" "$@" 2>&1)" && code=0 || code=$?
  got="$(cat "$work/$name/.tdd/workqueue" 2>/dev/null || printf '<no .tdd/workqueue>')"
  if [[ "$code" -eq 0 && "$got" == "$want" ]]; then
    ok
  else
    no "$what"
    echo "    exit: $code (want 0), output: $out"
    diff <(printf '%s\n' "$want") <(printf '%s\n' "$got") | sed 's/^/    /'
  fi
}

expect_unchanged() {
  local name="$1" want_code="$2" what="$3" out code
  shift 3
  cp "$work/$name/.tdd/workqueue" "$work/$name.before"
  out="$(cd "$work/$name" && "$SCRIPT" "$@" 2>&1)" && code=0 || code=$?
  if [[ "$code" -eq "$want_code" ]] && cmp -s "$work/$name.before" "$work/$name/.tdd/workqueue"; then
    ok
  else
    no "$what"
    echo "    exit: $code (want $want_code), output: $out"
    diff "$work/$name.before" "$work/$name/.tdd/workqueue" 2>&1 | sed 's/^/    /'
  fi
}

expect_usage() {
  local name="$1" what="$2" code
  shift 2
  make_repo "$work/$name"
  (cd "$work/$name" && "$SCRIPT" "$@" > /dev/null 2>"$work/$name.err") && code=0 || code=$?
  if [[ "$code" -eq 2 ]] &&
    grep -F 'workqueue.sh: usage: workqueue.sh assign <worker> <issue>...' "$work/$name.err" > /dev/null &&
    grep -F 'workqueue.sh show [<worker>]' "$work/$name.err" > /dev/null; then
    ok
  else
    no "$what"
    echo "    exit: $code (want 2), stderr: $(printf '%q' "$(cat "$work/$name.err")")"
  fi
}

repo="$work/assign-order"
make_repo "$repo"
expect_queue assign-order 'alpha\t12\tqueued\t\nalpha\t7\tqueued\t\nalpha\t30\tqueued\t' \
  "assign appends one queued line per issue, in the order given" assign alpha 12 7 30

repo="$work/unknown-subcommand"
make_repo "$repo"
seed_queue "$repo" 'beta\t4\tqueued\t\n'
expect_unchanged unknown-subcommand 2 \
  "an unknown subcommand exits 2 and leaves the queue file byte-identical" frobnicate alpha 12

repo="$work/unknown-subcommand-no-queue"
make_repo "$repo"
out="$(cd "$repo" && "$SCRIPT" frobnicate alpha 12 2>&1)" && code=0 || code=$?
if [[ "$code" -eq 2 && ! -e "$repo/.tdd/workqueue" ]]; then
  ok
else
  no "an unknown subcommand in a repo with no queue exits 2 and creates no queue file"
  echo "    exit: $code (want 2), output: $out"
  echo "    .tdd/workqueue: $([[ -e "$repo/.tdd/workqueue" ]] && echo present || echo absent) (want absent)"
fi

expect_usage no-subcommand "workqueue.sh with no subcommand exits 2 with its own usage text on stderr"

expect_usage empty-issue-usage "workqueue.sh given an empty issue exits 2 with its own usage text on stderr" \
  assign alpha ''

expect_usage twice-issue-usage "workqueue.sh given an issue named twice exits 2 with its own usage text on stderr" \
  assign alpha 12 12

bad_reasons=()
for reason in "$(printf 'first\tsecond')" "$(printf 'first\nsecond')"; do
  make_repo "$work/park-reason-usage"
  (cd "$work/park-reason-usage" && "$SCRIPT" park alpha 12 "$reason" > /dev/null 2>"$work/park-reason-usage.err") &&
    code=0 || code=$?
  if ! { [[ "$code" -eq 2 ]] &&
    grep -F 'workqueue.sh: usage: workqueue.sh assign <worker> <issue>...' "$work/park-reason-usage.err" > /dev/null &&
    grep -F 'workqueue.sh show [<worker>]' "$work/park-reason-usage.err" > /dev/null; }; then
    bad_reasons+=("$(printf '%q' "$reason") exit: $code (want 2), stderr: $(printf '%q' "$(cat "$work/park-reason-usage.err")")")
  fi
  rm -rf "$work/park-reason-usage"
done
if [[ "${#bad_reasons[@]}" -eq 0 ]]; then
  ok
else
  no "workqueue.sh given a park reason holding a tab or a newline exits 2 with its own usage text on stderr"
  printf '    %s\n' "${bad_reasons[@]}"
fi

repo="$work/assign-held"
make_repo "$repo"
seed_queue "$repo" 'beta\t4\tqueued\t\ngamma\t9\trunning\t\n'
expect_unchanged assign-held 2 \
  "assign refuses with exit 2 an issue already queued for another worker" assign alpha 4
expect_unchanged assign-held 2 \
  "assign refuses with exit 2 an issue already running for another worker" assign alpha 9

repo="$work/assign-finished"
make_repo "$repo"
seed_queue "$repo" 'beta\t4\tmerged\tabc1234\ngamma\t9\tparked\tsecond bail\nbeta\t11\tskipped\t\n'
expect_queue assign-finished \
  'beta\t4\tmerged\tabc1234\ngamma\t9\tparked\tsecond bail\nbeta\t11\tskipped\t\nalpha\t4\tqueued\t\nalpha\t9\tqueued\t\nalpha\t11\tqueued\t' \
  "assign takes an issue held only as merged, parked or skipped" assign alpha 4 9 11

repo="$work/next-unblocked"
make_repo "$repo"
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

repo="$work/next-foreign-url"
make_repo "$repo"
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

repo="$work/next-own-url"
make_repo "$repo"
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

repo="$work/next-ssh-origin"
make_repo "$repo"
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

repo="$work/next-none"
make_repo "$repo"
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

repo="$work/next-graphql-refused"
new_repo "$repo"
git -C "$repo" remote add origin https://github.com/ztrange/veri.git
seed_queue "$repo" 'alpha\t20\tqueued\t\nalpha\t22\tqueued\t\n'
issues_fixture next-graphql-refused <<'JSON'
[
  {"number": 5, "title": "open blocker", "labels": [], "body": "", "state": "OPEN"},
  {"number": 6, "title": "closed blocker", "labels": [], "body": "", "state": "CLOSED"},
  {"number": 20, "title": "blocked", "labels": [], "state": "OPEN",
   "body": "Work.\n\n## Blocked by\n\n- #5\n"},
  {"number": 22, "title": "unblocked", "labels": [], "state": "OPEN",
   "body": "Work.\n\n## Blocked by\n\n- #6\n"}
]
JSON
python3 -c '
import json, sys
fx = sys.argv[1]
filler = [{"number": 100 + k, "title": "filler", "labels": [], "body": "", "state": "CLOSED"} for k in range(110)]
issues = filler + json.load(open(fx + "/issues.json"))
json.dump(issues, open(fx + "/issues.json", "w"))
for i in issues:
    i["state"] = i["state"].lower()
    i["body"] = i["body"] or None
json.dump(issues, open(fx + "/rest-issues.json", "w"))
' "$work/next-graphql-refused.gh"
mkdir -p "$work/next-graphql-refused.bin"
cat > "$work/next-graphql-refused.bin/gh" <<'STUB'
#!/bin/sh
refusal='GitHub GraphQL is not available from Claude Code sessions; use the REST API (gh api repos/{owner}/{repo}/...)'
if [ "$GH_GRAPHQL" = refused ]; then
  case "$1" in
    issue|pr|repo) echo "HTTP 403: $refusal" >&2; exit 1 ;;
  esac
  case "$*" in
    "api graphql"*) echo "HTTP 403: $refusal" >&2; exit 1 ;;
  esac
fi
case "$*" in
  "issue list"*) cat "$GH_ISSUES"; exit 0 ;;
  *-q*|*--jq*|*--template*) echo "gh stub: unexpected call: gh $*" >&2; exit 1 ;;
  "api "*"repos/{owner}/{repo}/issues"*|"api "*"repos/ztrange/veri/issues"*) ;;
  *) echo "gh stub: unexpected call: gh $*" >&2; exit 1 ;;
esac
case " $* " in *" --paginate "*) paginate=1 ;; *) paginate=0 ;; esac
per_page="$(printf '%s\n' "$*" | sed -n 's/.*[?&]per_page=\([0-9]*\).*/\1/p')"
page="$(printf '%s\n' "$*" | sed -n 's/.*[?&]page=\([0-9]*\).*/\1/p')"
exec python3 -c '
import json, sys
items = json.load(open(sys.argv[1]))
size = min(int(sys.argv[3] or 30), 100)
pages = [items[k:k + size] for k in range(0, len(items), size)] or [[]]
n = int(sys.argv[4] or 1)
sys.stdout.write("".join(json.dumps(p) for p in (pages if sys.argv[2] == "1" else pages[n - 1:n] or [[]])))
' "$GH_REST_ISSUES" "$paginate" "$per_page" "$page"
STUB
chmod +x "$work/next-graphql-refused.bin/gh"
gh_next() {  # gh_next <working|refused>; sets $out and $code
  out="$(cd "$work/next-graphql-refused" && env -u VERI_GH_JSON \
    PATH="$work/next-graphql-refused.bin:$PATH" GH_GRAPHQL="$1" \
    GH_ISSUES="$work/next-graphql-refused.gh/issues.json" \
    GH_REST_ISSUES="$work/next-graphql-refused.gh/rest-issues.json" \
    "$SCRIPT" next alpha 2>"$work/next-graphql-refused.$1.err")" && code=0 || code=$?
}
gh_next working; working="$out" working_code="$code"
gh_next refused
working_err="$(cat "$work/next-graphql-refused.working.err")"
refused_err="$(cat "$work/next-graphql-refused.refused.err")"
if [[ "$working_code" -eq 0 && "$working" == 22 && "$code" -eq "$working_code" && "$out" == "$working" &&
      "$refused_err" == "$working_err" ]]; then
  pass=$((pass + 1))
else
  fail=$((fail + 1))
  echo "FAIL - next, against a gh that refuses GraphQL with the 403 and answers REST a page at a time, prints the same issue, stderr and exit code as against a working gh, across more than one page of issues (#568)"
  echo "    working gh: exit $working_code (want 0), stdout: '$working' (want '22')"
  echo "    GraphQL refused: exit $code (want $working_code), stdout: '$out' (want '$working')"
  echo "    GraphQL refused stderr: '$refused_err' (want '$working_err')"
fi

repo="$work/start-queued"
make_repo "$repo"
seed_queue "$repo" 'alpha\t12\tparked\tsecond bail\nbeta\t4\tqueued\t\nalpha\t12\tqueued\t\nalpha\t7\tqueued\t\n'
expect_queue start-queued \
  'alpha\t12\tparked\tsecond bail\nbeta\t4\tqueued\t\nalpha\t12\trunning\t\nalpha\t7\tqueued\t' \
  "start moves that worker's queued item to running" start alpha 12

repo="$work/done-running"
make_repo "$repo"
seed_queue "$repo" 'beta\t4\trunning\t\nalpha\t12\trunning\t\nalpha\t7\tqueued\t\n'
expect_queue done-running \
  'beta\t4\trunning\t\nalpha\t12\tmerged\tabc1234\nalpha\t7\tqueued\t' \
  "done moves that worker's running item to merged, recording the sha" done alpha 12 abc1234

repo="$work/park-running"
make_repo "$repo"
seed_queue "$repo" 'beta\t4\trunning\t\nalpha\t12\trunning\t\nalpha\t7\tqueued\t\n'
expect_queue park-running \
  'beta\t4\trunning\t\nalpha\t12\tparked\tsecond bail\nalpha\t7\tqueued\t' \
  "park moves that worker's running item to parked, recording the reason" \
  park alpha 12 "second bail"

repo="$work/foreign-item"
make_repo "$repo"
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

repo="$work/wrong-state"
make_repo "$repo"
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

repo="$work/never-removed"
make_repo "$repo"
for call in "assign alpha 12 7" "assign beta 30" "assign beta 12" "start alpha 12" \
  "start beta 7" "done alpha 12 abc1234" "start alpha 7" "done alpha 7" "park alpha 7 why" \
  "park alpha 30 why" "start beta 30" "frobnicate beta 30"; do
  (cd "$repo" && "$SCRIPT" $call >/dev/null 2>&1) || true
done
held="$(cut -f2 "$repo/.tdd/workqueue" 2>/dev/null | tr '\n' ' ')"
missing=""
for issue in 12 7 30; do
  [[ " $held" == *" $issue "* ]] || missing="$missing $issue"
done
if [[ -z "$missing" ]]; then
  ok
else
  no "after assign, start, done, park and refused calls, every issue ever assigned is still a line"
  echo "    missing:$missing (want none), queue issues: $held"
fi

repo="$work/parallel-writes"
make_repo "$repo"
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
lines=$'\n'"$(cat "$repo/.tdd/workqueue")"$'\n'
for i in $(seq 1 20); do
  [[ "$lines" == *$'\n'"w$i"$'\t'"$i"$'\t'queued$'\t'$'\n'* ]] || missing="$missing w$i/$i:queued"
  [[ "$lines" == *$'\n'alpha$'\t'"$((100 + i))"$'\t'running$'\t'$'\n'* ]] \
    || missing="$missing alpha/$((100 + i)):running"
done
if [[ -z "$torn" && -z "$missing" ]]; then
  ok
else
  no "N assign and start calls run in parallel leave a well-formed file containing every write"
  echo "    torn lines:${torn:- none} (want none)"
  echo "    writes missing:${missing:- none} (want none)"
fi

repo="$work/lock-held"
make_repo "$repo"
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
  ok
else
  no "a write that cannot take the lock exits 2 without touching the file"
  echo "    exit: $code (want 2), stderr: $(cat "$work/lock-held.err")"
  diff <(printf '%s\n' "$before") <(printf '%s\n' "$after") | sed 's/^/    /'
fi

make_repo "$work/show-grouped"
seed_queue "$work/show-grouped" 'alpha\t12\trunning\t\nbeta\t4\tqueued\t\nalpha\t7\tqueued\t\n'
expect_show show-grouped 'alpha\n\t12\trunning\n\t7\tqueued\nbeta\n\t4\tqueued' \
  "show prints every item grouped by worker, each with its issue and state"

make_repo "$work/show-one"
seed_queue "$work/show-one" 'alpha\t12\trunning\t\nbeta\t4\tqueued\t\nalpha\t7\tqueued\t\n'
expect_show show-one 'alpha\n\t12\trunning\n\t7\tqueued' \
  "show <worker> prints only that worker's items" alpha

repo="$work/linked-worktree"
make_repo "$repo"
git -C "$repo" worktree add -q -b side "$work/linked-worktree.wt" >/dev/null 2>&1
seed_queue "$repo" 'beta\t4\tqueued\t\n'
want_queue="$(printf 'beta\t4\tqueued\t\nalpha\t7\tqueued\t')"
want_show="$(printf 'beta\n\t4\tqueued\nalpha\n\t7\tqueued')"
out="$(cd "$work/linked-worktree.wt" && "$SCRIPT" assign alpha 7 2>&1 \
  && "$SCRIPT" show 2>&1)" && code=0 || code=$?
got="$(cat "$repo/.tdd/workqueue")"
if [[ "$code" -eq 0 && "$got" == "$want_queue" && "$out" == "$want_show" \
  && ! -e "$work/linked-worktree.wt/.tdd/workqueue" ]]; then
  ok
else
  no "called from a linked worktree, workqueue.sh reads and writes the main working tree's queue"
  echo "    exit: $code (want 0)"
  echo "    worktree's own .tdd/workqueue: $([[ -e "$work/linked-worktree.wt/.tdd/workqueue" ]] \
    && echo present || echo absent) (want absent)"
  echo "    main tree's queue:"
  diff <(printf '%s\n' "$want_queue") <(printf '%s\n' "$got") | sed 's/^/    /'
  echo "    show, run in the worktree:"
  diff <(printf '%s\n' "$want_show") <(printf '%s\n' "$out") | sed 's/^/    /'
fi

worker_doc="$SKILL_DIR/WORKER.md"
calls_missing=""
for call in next start done park; do
  grep -Eq "workqueue\.sh[[:space:]]+$call([^[:alnum:]_-]|\$)" "$worker_doc" 2>/dev/null \
    || calls_missing="$calls_missing $call"
done
if [[ -f "$worker_doc" && -z "$calls_missing" ]]; then
  ok
else
  no "WORKER.md beside SKILL.md documents the worker loop, naming each workqueue.sh call"
  echo "    WORKER.md: $([[ -f "$worker_doc" ]] && echo present || echo absent) (want present)"
  echo "    calls not named:${calls_missing:- none} (want none)"
fi

skill_doc="$SKILL_DIR/SKILL.md"
if grep -E '`Read`.*`WORKER\.md`' "$skill_doc" > /dev/null 2>&1; then
  ok
else
  no "SKILL.md tells a session born as a worker to Read WORKER.md, the way it points a scope at SCOPE-LOOP.md"
  echo "    lines of SKILL.md naming WORKER.md (want one holding \`Read\` then \`WORKER.md\`):"
  grep -n 'WORKER\.md' "$skill_doc" | sed 's/^/      /'
fi

context_doc="$SKILL_DIR/../../CONTEXT.md"
terms_missing=""
for term in Worker 'Work queue'; do
  grep -Ei "^\*\*$term\*\*:" "$context_doc" > /dev/null 2>&1 \
    || terms_missing="$terms_missing **$term**"
done
if [[ -z "$terms_missing" ]]; then
  ok
else
  no "CONTEXT.md defines worker and work queue"
  echo "    terms not defined:$terms_missing (want none)"
fi

repo="$work/assign-missing-args"
make_repo "$repo"
seed_queue "$repo" 'beta\t4\tqueued\t\ngamma\t9\trunning\t\n'
expect_unchanged assign-missing-args 2 \
  "assign with no worker exits 2 and leaves the queue file byte-identical" assign
expect_unchanged assign-missing-args 2 \
  "assign with a worker and no issue exits 2 and leaves the queue file byte-identical" \
  assign alpha

repo="$work/assign-duplicate-issue"
make_repo "$repo"
seed_queue "$repo" 'beta\t4\tqueued\t\n'
expect_unchanged assign-duplicate-issue 2 \
  "assign naming the same issue twice in one call exits 2 and leaves the queue file byte-identical" \
  assign alpha 12 12

repo="$work/assign-empty-issue"
make_repo "$repo"
seed_queue "$repo" 'beta\t4\tqueued\t\n'
expect_unchanged assign-empty-issue 2 \
  "assign given an empty issue argument exits 2 and leaves the queue file byte-identical" \
  assign alpha ''

repo="$work/done-missing-sha"
make_repo "$repo"
seed_queue "$repo" 'alpha\t12\trunning\t\nbeta\t4\tqueued\t\n'
expect_unchanged done-missing-sha 2 \
  "done with a worker and an issue but no merge sha exits 2 and leaves the queue file byte-identical" \
  done alpha 12

repo="$work/done-empty-sha"
make_repo "$repo"
seed_queue "$repo" 'alpha\t12\trunning\t\nbeta\t4\tqueued\t\n'
expect_unchanged done-empty-sha 2 \
  "done given an empty merge sha argument exits 2 and leaves the queue file byte-identical" \
  done alpha 12 ''

park_outcome() {
  local name="$1" reason="$2" queue="$work/$1/.tdd/workqueue" code lines
  make_repo "$work/$name"
  seed_queue "$work/$name" 'alpha\t12\trunning\t\nbeta\t4\tqueued\t\n'
  cp "$queue" "$work/$name.before"
  (cd "$work/$name" && "$SCRIPT" park alpha 12 "$reason" >/dev/null 2>&1) && code=0 || code=$?
  if [[ "$code" -ne 0 ]]; then
    if cmp -s "$work/$name.before" "$queue"; then
      echo refused
    else
      echo "corrupt (exit $code, file changed)"
    fi
    return
  fi
  lines="$(wc -l < "$queue" | tr -d ' ')"
  if [[ "$lines" == 2 ]] && awk -F '\t' 'NF != 4 { bad = 1 } END { exit bad }' "$queue"; then
    echo well-formed
  else
    echo "corrupt (exit 0, $lines lines, fields per line: $(awk -F '\t' '{ printf "%s ", NF }' "$queue"))"
  fi
}
tab_outcome="$(park_outcome park-reason-tab "$(printf 'first\tsecond')")"
newline_outcome="$(park_outcome park-reason-newline "$(printf 'first\nsecond')")"
if [[ "$tab_outcome" == "$newline_outcome" &&
  ( "$tab_outcome" == refused || "$tab_outcome" == well-formed ) ]]; then
  ok
else
  no "park given a reason holding a tab or a newline treats both the same way, leaving the queue well-formed or refusing with the file untouched"
  echo "    tab: $tab_outcome"
  echo "    newline: $newline_outcome"
fi

make_repo "$work/show-no-items"
seed_queue "$work/show-no-items" 'alpha\t12\trunning\t\nbeta\t4\tqueued\t\nalpha\t7\tqueued\t\n'
(cd "$work/show-no-items" && "$SCRIPT" show beta > "$work/show-no-items.beta" \
  2>"$work/show-no-items.err") && beta_code=0 || beta_code=$?
(cd "$work/show-no-items" && "$SCRIPT" show gamma > "$work/show-no-items.gamma" \
  2>>"$work/show-no-items.err") && gamma_code=0 || gamma_code=$?
if [[ "$beta_code" -eq 0 && "$(cat "$work/show-no-items.beta")" == "$(printf 'beta\n\t4\tqueued')" &&
  "$gamma_code" -eq 0 && ! -s "$work/show-no-items.gamma" ]]; then
  ok
else
  no "show <worker> prints only that worker's group, and nothing with exit 0 for a worker with no items"
  echo "    show beta: exit $beta_code (want 0), stdout: '$(cat "$work/show-no-items.beta")'"
  echo "    show gamma: exit $gamma_code (want 0), stdout bytes: $(wc -c < "$work/show-no-items.gamma" | tr -d ' ') (want 0)"
  echo "    stderr: $(cat "$work/show-no-items.err")"
fi

argcapdir="$work/argcap-bin"
argcap_python3_stub "$argcapdir"

repo="$work/next-large-doc"
make_repo "$repo"
seed_queue "$repo" 'alpha\t2\tqueued\t\nalpha\t3\tqueued\t\n'
mkdir -p "$work/next-large-doc.short" "$work/next-large-doc.long"
python3 -c '
import json, sys
def issues(pad):
    return [{"number": n, "title": "issue %d" % n, "labels": [], "state": "OPEN",
             "body": "## What to build\n\n" + pad + "\n\n## Blocked by\n\n"
                     + ("- #1\n" if n == 2 else "None.\n")}
            for n in range(1, 41)]
json.dump(issues("short"), open(sys.argv[1] + "/issues.json", "w"))
json.dump(issues("x" * 8192), open(sys.argv[2] + "/issues.json", "w"))
' "$work/next-large-doc.short" "$work/next-large-doc.long"
long_size="$(wc -c < "$work/next-large-doc.long/issues.json" | tr -d ' ')"
large_next() {  # large_next <short|long>; sets $out and $code
  out="$(cd "$repo" && PATH="$argcapdir:$PATH" VERI_GH_JSON="$work/next-large-doc.$1" \
    "$SCRIPT" next alpha 2>"$work/next-large-doc.$1.err")" && code=0 || code=$?
}
large_next short; short_out="$out" short_code="$code"
large_next long
if [[ "$long_size" -gt 262144 && "$short_code" == 0 && "$short_out" == 3 &&
  "$code" == "$short_code" && "$out" == "$short_out" ]]; then
  ok
else
  no "next reads an issues document larger than 256 KiB and prints the same issue and exit code as for a small one, under a python3 that refuses any argument over 128 KiB the way Linux does (#591)"
  echo "    long issues.json: $long_size bytes (want >262144)"
  echo "    short: exit $short_code (want 0), stdout: '$short_out' (want '3')"
  echo "    long: exit $code (want $short_code), stdout: '$out' (want '$short_out')"
  echo "    long stderr: $(cat "$work/next-large-doc.long.err")"
fi


repo="$work/next-three-pages"
make_repo "$repo"
seed_queue "$repo" 'alpha\t71\tqueued\t\nalpha\t73\tqueued\t\n'
issue_pages=(
  '{"number": 70, "title": "a", "labels": [], "body": "", "state": "closed"}, {"number": 71, "title": "b", "labels": [], "body": "Work.\n\n## Blocked by\n\n- #74\n", "state": "open"}'
  '{"number": 72, "title": "c", "labels": [], "body": "", "state": "closed"}, {"number": 73, "title": "d", "labels": [], "body": "Work.\n\n## Blocked by\n\n- #72\n", "state": "open"}'
  '{"number": 74, "title": "e", "labels": [], "body": "", "state": "open"}, {"number": 75, "title": "f", "labels": [], "body": "", "state": "closed"}'
)
mkdir -p "$work/next-three-pages.one" "$work/next-three-pages.three" "$work/next-three-pages.bin"
for i in 0 1 2; do
  printf '[%s]\n' "${issue_pages[i]}" > "$work/next-three-pages.three/issues-$((i + 1)).json"
done
(IFS=,; printf '[%s]\n' "${issue_pages[*]}" > "$work/next-three-pages.one/issues-1.json")
cat > "$work/next-three-pages.bin/gh" <<'STUB'
#!/bin/sh
proxy='gh: Numeric-ID repository paths (repositories/{id}/...) are not supported through this proxy. Use repos/{owner}/{repo}/... endpoints instead. (HTTP 403)'
case "$1" in
  api) shift ;;
  *) echo "gh stub: unexpected call: gh $*" >&2; exit 1 ;;
esac
paginate="" path=""
for arg in "$@"; do
  case "$arg" in
    --paginate) paginate=1 ;;
    -*) echo "gh stub: unsupported flag $arg" >&2; exit 1 ;;
    *) path="$arg" ;;
  esac
done
case "$path" in
  *repositories/*) echo "$proxy" >&2; exit 1 ;;
  "repos/{owner}/{repo}/issues"*) ;;
  *) echo "gh stub: unexpected path $path" >&2; exit 1 ;;
esac
page="$(printf '%s\n' "$path" | sed -n 's/.*[?&]page=\([0-9][0-9]*\).*/\1/p')"
[ -n "$page" ] || page=1
if [ -f "$GH_FX/issues-$page.json" ]; then cat "$GH_FX/issues-$page.json"; else echo '[]'; fi
if [ -n "$paginate" ] && [ -f "$GH_FX/issues-$((page + 1)).json" ]; then echo "$proxy" >&2; exit 1; fi
exit 0
STUB
chmod +x "$work/next-three-pages.bin/gh"
paged_next() {  # paged_next <one|three>; sets $out and $code
  out="$(cd "$repo" && env -u VERI_GH_JSON PATH="$work/next-three-pages.bin:$PATH" \
    GH_FX="$work/next-three-pages.$1" "$SCRIPT" next alpha 2>"$work/next-three-pages.$1.err")" &&
    code=0 || code=$?
}
paged_next one; one_out="$out" one_code="$code"
paged_next three
if [[ "$one_code" == 0 && "$one_out" == 73 && "$code" == "$one_code" && "$out" == "$one_out" ]]; then
  ok
else
  no "next, against a gh that serves issues over three pages on repos/{owner}/{repo} and refuses repositories/{id} with the proxy's 403, prints the same issue and exit code as against a single-page fixture holding the same issues (#592)"
  echo "    single page: exit $one_code (want 0), stdout: '$one_out' (want '73')"
  echo "    three pages: exit $code (want $one_code), stdout: '$out' (want '$one_out')"
  echo "    three pages stderr: $(cat "$work/next-three-pages.three.err")"
fi

finish
