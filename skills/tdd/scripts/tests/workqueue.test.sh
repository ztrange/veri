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

run_sequence() {
  local script="$1"
  "$script" assign alpha 7 8 2>&1 && "$script" start alpha 7 2>&1 && "$script" show 2>&1
}
make_repo "$work/in-place"
seed_queue "$work/in-place" 'beta\t4\tqueued\t\n'
make_repo "$work/via-link"
git -C "$work/via-link" worktree add -q -b side "$work/via-link.wt" >/dev/null 2>&1
mkdir -p "$work/via-link.wt/sub/dir"
seed_queue "$work/via-link" 'beta\t4\tqueued\t\n'
ln -s "$(cd "$SKILL_DIR" && pwd)" "$work/skill-link"
want_queue="$(printf 'beta\t4\tqueued\t\nalpha\t7\trunning\t\nalpha\t8\tqueued\t')"
want_show="$(printf 'beta\n\t4\tqueued\nalpha\n\t7\trunning\n\t8\tqueued')"
place_out="$(cd "$work/in-place" && run_sequence "$SCRIPT")" && place_code=0 || place_code=$?
link_out="$(cd "$work/via-link.wt/sub/dir" && run_sequence "$work/skill-link/scripts/workqueue.sh")" \
  && link_code=0 || link_code=$?
place_queue="$(cat "$work/in-place/.tdd/workqueue")"
link_queue="$(cat "$work/via-link/.tdd/workqueue" 2>/dev/null || printf '<no .tdd/workqueue>')"
if [[ "$link_code" -eq "$place_code" && "$link_code" -eq 0 && "$link_out" == "$place_out" \
  && "$link_out" == "$want_show" && "$link_queue" == "$place_queue" \
  && "$link_queue" == "$want_queue" && ! -e "$work/via-link.wt/.tdd/workqueue" \
  && ! -e "$work/via-link.wt/sub/dir/.tdd/workqueue" ]]; then
  ok
else
  no "run through a symlink to the skill directory from a subdirectory of a linked worktree, workqueue.sh assigns, starts and shows as in place, on the main working tree's queue"
  echo "    exit: $link_code (in place: $place_code, want 0)"
  echo "    show via the link, against in place:"
  diff <(printf '%s\n' "$place_out") <(printf '%s\n' "$link_out") | sed 's/^/    /'
  echo "    main tree's queue via the link, against in place:"
  diff <(printf '%s\n' "$place_queue") <(printf '%s\n' "$link_queue") | sed 's/^/    /'
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

finish
