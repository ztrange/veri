#!/usr/bin/env bash
# Unit tests for scripts/affected-suites.sh — prints the suites one change affects.
#
# Contract under test:
#   affected-suites.sh <base>..<head>, run inside the repository
#                       → exit 0, and one suite path per line, sorted, with no duplicate.
#
# Run: scripts/tests/affected-suites.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
AFFECTED="$HERE/../affected-suites.sh"
source "$HERE/lib/harness.sh"
source "$HERE/../lib/missing-argument-exit.sh"

work="$(scratch_dir)"

git_q() { local repo="$1"; shift; git -C "$repo" -c user.name=veri -c user.email=veri@example.test "$@"; }

commit_all() {
  git_q "$1" add -A >/dev/null 2>&1
  git_q "$1" commit -q -m "$2" >/dev/null 2>&1
}

commit_base() { commit_all "$repo" "base"; base="$(git -C "$repo" rev-parse HEAD)"; }
commit_head() { commit_all "$repo" "head"; head="$(git -C "$repo" rev-parse HEAD)"; }

make_repo() {
  repo="$work/$1"
  new_repo -b main "$repo" >/dev/null 2>&1
  s="$repo/skills/tdd/scripts"
}

run_affected() { cd "$repo" && "$AFFECTED" "${1:-$base..$head}"; }

expect_suites() {
  local name="$1" expected out code
  shift
  expected="$(printf '%s\n' "$@")"
  out="$(run_affected 2>/dev/null)"; code=$?
  if [[ "$code" == 0 && "$out" == "$expected" ]]; then ok; else
    no "$name (code=$code)"
    diff <(printf '%s\n' "$expected") <(printf '%s\n' "$out") | sed 's/^/    /'
  fi
}

expect_suites_unwidened() {
  local name="$1" expected out code err errf="$work/unwidened.err"
  shift
  expected="$(printf '%s\n' "$@")"
  out="$(run_affected 2>"$errf")"; code=$?
  err="$(cat "$errf")"
  if [[ "$code" == 0 && "$out" == "$expected" && "$err" != *widening* ]]; then ok; else
    no "$name (code=$code, stderr=${err:-<empty>})"
    diff <(printf '%s\n' "$expected") <(printf '%s\n' "$out") | sed 's/^/    /'
  fi
}

expect_nothing_to_do() {
  local name="$1" out code
  out="$(run_affected 2>/dev/null)"; code=$?
  if [[ "$code" == 3 && -z "$out" ]]; then ok; else
    no "$name (code=$code, stdout=${out:-<empty>})"
  fi
}

expect_widening_names() {
  local name="$1" err code f named=1
  shift
  err="$(run_affected 2>&1 >/dev/null)"; code=$?
  for f in "$@"; do [[ "$err" == *"$f"* ]] || named=0; done
  if [[ "$code" == 0 && "$named" == 1 ]]; then ok; else
    no "$name (code=$code, stderr=${err:-<empty>})"
  fi
}

foo_tree() {
  mkdir -p "$s/tests"
  printf 'foo\n' > "$s/foo.sh"
  printf '# foo suite\n' > "$s/tests/foo.test.sh"
}

foo_bar_tree() {
  foo_tree
  printf 'bar\n' > "$s/bar.sh"
  printf '# bar suite\n' > "$s/tests/bar.test.sh"
}

counts_suite() { mkdir -p "$repo/skills/tdd/scripts/tests/py/unit"; printf '# counts suite\n' > "$repo/skills/tdd/scripts/tests/py/unit/test_claude_md_counts.py"; }

write_ledger() {
  mkdir -p "$repo/.tdd"
  printf -- '- [%s] step one\n' "$1" > "$repo/.tdd/issue-416.md"
}
write_refactor_owed() {
  mkdir -p "$repo/.tdd"
  printf 'refactor owed [%s]\n' "$1" > "$repo/.tdd/issue-416-refactor-owed.md"
}

make_repo suite-added-counts
foo_tree
mkdir -p "$s/tests/unit"
counts_suite
commit_base
printf '# newbie suite\n' > "$s/tests/newbie.test.sh"
printf '# rookie unit suite\n' > "$s/tests/unit/rookie.test.sh"
commit_head
expect_suites "a range that adds a suite file under tests/ or tests/unit/ pulls in skills/tdd/scripts/tests/py/unit/test_claude_md_counts.py" \
  skills/tdd/scripts/tests/newbie.test.sh \
  skills/tdd/scripts/tests/py/unit/test_claude_md_counts.py \
  skills/tdd/scripts/tests/unit/rookie.test.sh

make_repo suite-edited-counts
foo_tree
counts_suite
commit_base
printf '# foo suite 2\n' > "$s/tests/foo.test.sh"
commit_head
expect_suites "editing an existing suite's contents does not pull in skills/tdd/scripts/tests/py/unit/test_claude_md_counts.py" \
  "skills/tdd/scripts/tests/foo.test.sh"

make_repo script-added-counts
foo_bar_tree
counts_suite
commit_base
rm "$s/bar.sh"
printf 'newbie\n' > "$s/newbie.sh"
printf '# newbie suite\n' > "$s/tests/newbie.test.sh"
commit_head
expect_suites "a range that adds or deletes a script under scripts/ pulls in skills/tdd/scripts/tests/py/unit/test_claude_md_counts.py" \
  skills/tdd/scripts/tests/bar.test.sh \
  skills/tdd/scripts/tests/newbie.test.sh \
  skills/tdd/scripts/tests/py/unit/test_claude_md_counts.py

make_repo rule2-continuation
mkdir -p "$s/tests" "$s/lib"
printf 'bar_fn() { :; }\n' > "$s/lib/bar.sh"
printf '#!/usr/bin/env bash\nHERE="$(cd "$(dirname "$0")" && pwd)"\nsource "$HERE/lib/bar.sh" \\\n  || { echo "alpha: cannot read lib/bar.sh" >&2; exit 2; }\n' > "$s/alpha.sh"
printf '#!/usr/bin/env bash\necho gamma\n' > "$s/gamma.sh"
for name in alpha gamma; do printf '# %s suite\n' "$name" > "$s/tests/$name.test.sh"; done
commit_base
printf 'bar_fn() { echo 2; }\n' > "$s/lib/bar.sh"
commit_head
expect_suites "#487: a lib file whose caller's source line ends in a \\ continuation maps to that caller's suite" \
  skills/tdd/scripts/tests/alpha.test.sh

make_repo rule2-line-end
mkdir -p "$s/tests" "$s/lib"
printf 'bar_fn() { :; }\n' > "$s/lib/bar.sh"
hdr='#!/usr/bin/env bash\nHERE="$(cd "$(dirname "$0")" && pwd)"\n'
printf "${hdr}"'source "$HERE/lib/bar.sh"\n' > "$s/alpha.sh"
printf "${hdr}"'source "$HERE/lib/bar.sh"   \n' > "$s/beta.sh"
printf "${hdr}"'source $HERE/lib/bar.sh\n' > "$s/delta.sh"
printf "${hdr}"'source $HERE/lib/bar.sh  \n' > "$s/epsilon.sh"
printf '#!/usr/bin/env bash\necho gamma\n' > "$s/gamma.sh"
for name in alpha beta delta epsilon gamma; do printf '# %s suite\n' "$name" > "$s/tests/$name.test.sh"; done
commit_base
printf 'bar_fn() { echo 2; }\n' > "$s/lib/bar.sh"
commit_head
expect_suites "#487: a caller whose source line ends at the lib path, with or without a trailing quote and spaces, still maps to its suite" \
  skills/tdd/scripts/tests/alpha.test.sh \
  skills/tdd/scripts/tests/beta.test.sh \
  skills/tdd/scripts/tests/delta.test.sh \
  skills/tdd/scripts/tests/epsilon.test.sh

make_repo rule2-comment
mkdir -p "$s/tests" "$s/lib"
printf 'bar_fn() { :; }\n' > "$s/lib/bar.sh"
hdr='#!/usr/bin/env bash\nHERE="$(cd "$(dirname "$0")" && pwd)"\n'
printf "${hdr}"'source "$HERE/lib/bar.sh"\n' > "$s/alpha.sh"
printf "${hdr}"'# source "$HERE/lib/bar.sh" \\\n' > "$s/beta.sh"
printf "${hdr}"'  # . "$HERE/lib/bar.sh"\n' > "$s/gamma.sh"
for name in alpha beta gamma; do printf '# %s suite\n' "$name" > "$s/tests/$name.test.sh"; done
commit_base
printf 'bar_fn() { echo 2; }\n' > "$s/lib/bar.sh"
commit_head
expect_suites "#487: a comment that names a lib file is still not a dependency" \
  skills/tdd/scripts/tests/alpha.test.sh

make_repo harness-adopters
mkdir -p "$s/tests/lib" "$s/tests/unit"
printf 'ok() { :; }\n' > "$s/tests/lib/harness.sh"
printf '#!/usr/bin/env bash\nHERE="$(cd "$(dirname "$0")" && pwd)"\nsource "$HERE/lib/harness.sh"\n' > "$s/tests/alpha.test.sh"
printf '#!/usr/bin/env bash\nHERE="$(cd "$(dirname "$0")" && pwd)"\nsource "$HERE/../lib/harness.sh"\n' > "$s/tests/unit/beta.test.sh"
printf '#!/usr/bin/env bash\necho gamma\n' > "$s/tests/gamma.test.sh"
commit_base
printf 'ok() { echo 2; }\n' > "$s/tests/lib/harness.sh"
commit_head
expect_suites "#496: a change to tests/lib/harness.sh prints every suite that sources it, and no others" \
  skills/tdd/scripts/tests/alpha.test.sh \
  skills/tdd/scripts/tests/unit/beta.test.sh

make_repo veri-module
mkdir -p "$s/tests/py" "$s/veri"
printf 'def main(): pass\n' > "$s/veri/event_log.py"
printf 'def test_main(): pass\n' > "$s/tests/py/test_event_log.py"
printf '#!/bin/sh\nexec python3 -m veri.event_log "$@"\n' > "$s/event-log.sh"
printf '# event-log suite\n' > "$s/tests/event-log.test.sh"
printf 'bar\n' > "$s/bar.sh"
printf '# bar suite\n' > "$s/tests/bar.test.sh"
commit_base
printf 'def main(): return 2\n' > "$s/veri/event_log.py"
commit_head
expect_suites_unwidened "a touched veri/event_log.py prints tests/py/test_event_log.py and tests/event-log.test.sh, without widening" \
  skills/tdd/scripts/tests/event-log.test.sh \
  skills/tdd/scripts/tests/py/test_event_log.py

make_repo veri-module-no-py
mkdir -p "$s/tests" "$s/veri"
printf 'def main(): pass\n' > "$s/veri/probe_queue.py"
printf '#!/bin/sh\nexec python3 -m veri.probe_queue "$@"\n' > "$s/probe-queue.sh"
printf '# probe-queue suite\n' > "$s/tests/probe-queue.test.sh"
commit_base
printf 'def main(): return 2\n' > "$s/veri/probe_queue.py"
commit_head
expect_suites_unwidened "a touched veri/probe_queue.py with no tests/py/test_probe_queue.py prints only tests/probe-queue.test.sh, without widening" \
  skills/tdd/scripts/tests/probe-queue.test.sh

make_repo veri-pytest
foo_bar_tree
mkdir -p "$s/tests/py"
printf 'def test_main(): pass\n' > "$s/tests/py/test_status.py"
commit_base
printf 'def test_main(): assert False\n' > "$s/tests/py/test_status.py"
commit_head
expect_suites_unwidened "a touched tests/py/test_status.py prints that file, without widening" \
  skills/tdd/scripts/tests/py/test_status.py

ln -s "$(cd "$HERE/../.." && pwd)" "$work/linked-skill"
in_place="$(cd "$repo" && "$AFFECTED" "$base..$head" 2>&1)"; in_place_code=$?
linked="$(cd "$repo" && "$work/linked-skill/scripts/affected-suites.sh" "$base..$head" 2>&1)"; linked_code=$?
if [[ "$linked" == "$in_place" && "$linked_code" -eq "$in_place_code" && "$in_place" == *"test_status.py"* ]]; then ok; else
  no "affected-suites.sh run through a symlink to the skill directory from the repository root answers as it does when run in place"
  diff <(printf '%s\nexit %s\n' "$in_place" "$in_place_code") <(printf '%s\nexit %s\n' "$linked" "$linked_code")
fi

make_repo base-gains-suite
mkdir -p "$s/tests/py"
printf '# a suite\n' > "$s/tests/py/test_a.py"
commit_base
git_q "$repo" checkout -q -b topic
printf '# a suite 2\n' > "$s/tests/py/test_a.py"
commit_head
git_q "$repo" checkout -q main
printf '# orchestrate suite\n' > "$s/tests/py/test_orchestrate.py"
commit_all "$repo" "main gains a suite"
git_q "$repo" checkout -q topic
base=main head=HEAD
expect_suites "#1138: a suite the base gained after the branch point is not printed by affected-suites.sh <base>..HEAD, only the branch's own" \
  skills/tdd/scripts/tests/py/test_a.py

make_repo base-changes-non-suite
foo_tree
mkdir -p "$s/prompts"
printf 'bar\n' > "$s/bar.sh"
printf '# bar suite\n' > "$s/tests/bar.test.sh"
printf 'a prompt\n' > "$s/prompts/p.md"
printf '# reads prompts/p.md\n' > "$s/tests/baz.test.sh"
commit_base
git_q "$repo" checkout -q -b topic
printf 'foo 2\n' > "$s/foo.sh"
commit_head
git_q "$repo" checkout -q main
printf 'bar 2\n' > "$s/bar.sh"
rm "$s/prompts/p.md"
commit_all "$repo" "main changes a script and deletes a prompt"
git_q "$repo" checkout -q topic
base=main head=HEAD
expect_suites "#1138: a non-suite file the base changed or deleted after the branch point contributes no suite to affected-suites.sh <base>..HEAD" \
  skills/tdd/scripts/tests/foo.test.sh

make_repo base-adds-deletes-suite
foo_bar_tree
counts_suite
commit_base
git_q "$repo" checkout -q -b topic
printf 'foo 2\n' > "$s/foo.sh"
commit_head
git_q "$repo" checkout -q main
printf '# baz suite\n' > "$s/tests/baz.test.sh"
rm "$s/tests/bar.test.sh"
commit_all "$repo" "main adds one suite and deletes another"
git_q "$repo" checkout -q topic
base=main head=HEAD
expect_suites "#1138: a suite the base added or deleted after the branch point does not make affected-suites.sh <base>..HEAD print skills/tdd/scripts/tests/py/unit/test_claude_md_counts.py" \
  skills/tdd/scripts/tests/foo.test.sh

make_repo branch-deletes-suite
foo_bar_tree
counts_suite
commit_base
git_q "$repo" checkout -q -b topic
printf 'foo 2\n' > "$s/foo.sh"
rm "$s/tests/bar.test.sh"
commit_head
base=main head=HEAD
expect_suites "#1138: a suite the branch itself deleted is not printed by affected-suites.sh <base>..HEAD" \
  skills/tdd/scripts/tests/foo.test.sh \
  skills/tdd/scripts/tests/py/unit/test_claude_md_counts.py

git_state() { git -C "$repo" stash list; git -C "$repo" worktree list; git -C "$repo" rev-parse HEAD; }

make_repo working-tree
foo_bar_tree
commit_base
printf 'foo 2\n' > "$s/foo.sh"
before="$(git_state)"
out="$(run_affected "$base" 2>/dev/null)"; code=$?
after="$(git_state)"
if [[ "$code" == 0 && "$out" == "skills/tdd/scripts/tests/foo.test.sh" && "$after" == "$before" ]]; then ok; else
  no "affected-suites.sh <base> with an uncommitted edit to a script prints its suite, exits 0, and leaves stash, worktrees and HEAD as they were (code=$code, stdout=${out:-<empty>})"
  diff <(printf '%s\n' "$before") <(printf '%s\n' "$after") | sed 's/^/    /'
fi

make_repo working-tree-skill-section
mkdir -p "$s/tests"
printf '# tdd\n\n## Alpha\n\nalpha text\n\n## Beta\n\nbeta text\n' > "$repo/skills/tdd/SKILL.md"
printf '#!/usr/bin/env bash\nskill_md="skills/tdd/SKILL.md"\nload_section '"'"'Alpha'"'"'\n' > "$s/tests/skill-alpha.test.sh"
printf '#!/usr/bin/env bash\nskill_md="skills/tdd/SKILL.md"\nload_section '"'"'Beta'"'"'\n' > "$s/tests/skill-beta.test.sh"
printf '#!/usr/bin/env bash\nskill_md="skills/tdd/SKILL.md"\ngrep -F text "$skill_md"\n' > "$s/tests/skill-whole.test.sh"
commit_base
printf '# tdd\n\n## Alpha\n\nalpha text 2\n\n## Beta\n\nbeta text\n' > "$repo/skills/tdd/SKILL.md"
out="$(run_affected "$base" 2>/dev/null)"; code=$?
expected=$'skills/tdd/scripts/tests/skill-alpha.test.sh\nskills/tdd/scripts/tests/skill-whole.test.sh'
if [[ "$code" == 0 && "$out" == "$expected" ]]; then ok; else
  no "affected-suites.sh <base> with an uncommitted edit inside one ## section of SKILL.md prints the suites reading that section or SKILL.md unsliced, not one reading only another (code=$code)"
  diff <(printf '%s\n' "$expected") <(printf '%s\n' "$out") | sed 's/^/    /'
fi

make_repo working-tree-untracked
foo_tree
commit_base
printf '# baz suite\n' > "$s/tests/baz.test.sh"
out="$(run_affected "$base" 2>/dev/null)"; code=$?
if [[ $'\n'"$out"$'\n' == *$'\nskills/tdd/scripts/tests/baz.test.sh\n'* ]]; then ok; else
  no "affected-suites.sh <base> with a new, untracked suite prints that suite (code=$code, stdout=${out:-<empty>})"
fi

make_repo working-tree-untracked-counts
foo_tree
counts_suite
commit_base
printf '# baz suite\n' > "$s/tests/baz.test.sh"
out="$(run_affected "$base" 2>/dev/null)"; code=$?
expected=$'skills/tdd/scripts/tests/baz.test.sh\nskills/tdd/scripts/tests/py/unit/test_claude_md_counts.py'
if [[ "$code" == 0 && "$out" == "$expected" ]]; then ok; else
  no "affected-suites.sh <base> with a new, untracked suite also prints skills/tdd/scripts/tests/py/unit/test_claude_md_counts.py (code=$code)"
  diff <(printf '%s\n' "$expected") <(printf '%s\n' "$out") | sed 's/^/    /'
fi

make_repo working-tree-committed-counts
foo_tree
counts_suite
commit_base
printf '# baz suite\n' > "$s/tests/baz.test.sh"
commit_all "$repo" "add baz"
out="$(run_affected "$base" 2>/dev/null)"; code=$?
expected=$'skills/tdd/scripts/tests/baz.test.sh\nskills/tdd/scripts/tests/py/unit/test_claude_md_counts.py'
if [[ "$code" == 0 && "$out" == "$expected" ]]; then ok; else
  no "affected-suites.sh <base> with a committed added suite and no untracked file still prints skills/tdd/scripts/tests/py/unit/test_claude_md_counts.py (code=$code)"
  diff <(printf '%s\n' "$expected") <(printf '%s\n' "$out") | sed 's/^/    /'
fi

make_repo working-tree-unchanged
foo_tree
commit_base
out="$(run_affected "$base" 2>/dev/null)"; code=$?
if [[ "$code" == 3 && -z "$out" ]]; then ok; else
  no "affected-suites.sh <base> with no committed and no uncommitted change since <base> exits 3 and prints nothing (code=$code, stdout=${out:-<empty>})"
fi

make_repo working-tree-unresolvable
foo_tree
commit_base
out="$(run_affected no-such-revision 2>"$work/unresolvable.err")"; code=$?
err="$(cat "$work/unresolvable.err")"
if [[ "$code" == 2 && -z "$out" && "$err" == *no-such-revision* ]]; then ok; else
  no "affected-suites.sh <base> with an unresolvable <base> exits 2 with a diagnostic on stderr and nothing on stdout (code=$code, stdout=${out:-<empty>}, stderr=${err:-<empty>})"
fi

make_repo no-range
foo_tree
commit_base
offender="$(cd "$repo" && named_usage_offender "$HERE/.." affected-suites.sh no-range)"; code=$?
if [[ "$code" == 0 ]]; then ok; else
  no "affected-suites.sh with an argument that is not a <base>..<head> range exits 2 with its own usage text on stderr ($offender)"
fi

finish
