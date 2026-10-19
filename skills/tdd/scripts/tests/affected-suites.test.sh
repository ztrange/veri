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
