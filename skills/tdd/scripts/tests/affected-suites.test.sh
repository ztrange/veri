#!/usr/bin/env bash
# Unit tests for scripts/affected-suites.sh — prints the suites one change affects, so a red or
# refactor leaf can run a narrow slice of `make test` instead of all of it (issue #337).
#
# Contract under test:
#   affected-suites.sh <base>..<head>, run inside the repository
#                       → exit 0, and one suite path per line, sorted, with no duplicate.
#
# Every case builds a fixture tree of its own shaped like this repository's
# `skills/tdd/scripts/`, so the answer never depends on the suites the repository `make test`
# was typed in happens to have.
#
# Run: scripts/tests/affected-suites.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
AFFECTED="$HERE/../affected-suites.sh"
pass=0 fail=0
ok() { pass=$((pass + 1)); }
no() { fail=$((fail + 1)); echo "FAIL - $1"; }

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

git_q() { local repo="$1"; shift; git -C "$repo" -c user.name=veri -c user.email=veri@example.test "$@"; }

commit_all() {
  git_q "$1" add -A >/dev/null 2>&1
  git_q "$1" commit -q -m "$2" >/dev/null 2>&1
}

commit_base() { commit_all "$repo" "base"; base="$(git -C "$repo" rev-parse HEAD)"; }
commit_head() { commit_all "$repo" "head"; head="$(git -C "$repo" rev-parse HEAD)"; }

new_repo() {
  repo="$work/$1"
  git init -q -b main "$repo" >/dev/null 2>&1
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

counts_suite() { printf '# counts suite\n' > "$repo/skills/tdd/scripts/tests/claude-md-counts.test.sh"; }

write_ledger() {
  mkdir -p "$repo/.tdd"
  printf -- '- [%s] step one\n' "$1" > "$repo/.tdd/issue-416.md"
}
write_refactor_owed() {
  mkdir -p "$repo/.tdd"
  printf 'refactor owed [%s]\n' "$1" > "$repo/.tdd/issue-416-refactor-owed.md"
}

new_repo sorted
mkdir -p "$s/tests/unit"
printf 'wolf\n' > "$s/wolf.sh"
printf 'zulu\n' > "$s/zulu.sh"
printf '# wolf suite\n' > "$s/tests/wolf.test.sh"
printf '# zulu suite\n' > "$s/tests/unit/zulu.test.sh"
commit_base
printf 'wolf 2\n' > "$s/wolf.sh"
printf 'zulu 2\n' > "$s/zulu.sh"
printf '# wolf suite 2\n' > "$s/tests/wolf.test.sh"
commit_head
expect_suites "resolvable range → one suite per line, sorted, no duplicate" \
  skills/tdd/scripts/tests/unit/zulu.test.sh \
  skills/tdd/scripts/tests/wolf.test.sh

new_repo malformed
mkdir -p "$s"
printf 'wolf\n' > "$s/wolf.sh"
commit_head
bad=""
for arg in "$head" "$head..no-such-rev" "no-such-rev..$head"; do
  err="$(run_affected "$arg" 2>&1 >/dev/null)"; code=$?
  if [[ "$code" != 2 || -z "$err" ]]; then
    bad="${arg/$head/<head>}: code=$code, stderr=${err:-<empty>}"
    break
  fi
done
if [[ -z "$bad" ]]; then ok; else
  no "malformed argument → exit 2 with a diagnostic ($bad)"
fi

new_repo empty
mkdir -p "$s/tests"
printf 'wolf\n' > "$s/wolf.sh"
printf '# wolf suite\n' > "$s/tests/wolf.test.sh"
commit_base
git_q "$repo" commit -q --allow-empty -m "head" >/dev/null 2>&1
head="$(git -C "$repo" rev-parse HEAD)"
expect_nothing_to_do "empty diff → exit 3 and prints nothing"

new_repo rule1
foo_bar_tree
commit_base
printf 'foo 2\n' > "$s/foo.sh"
commit_head
expect_suites "rule 1: a change to scripts/foo.sh prints exactly tests/foo.test.sh" \
  "skills/tdd/scripts/tests/foo.test.sh"

new_repo rule1-unit
mkdir -p "$s/tests/unit"
printf 'foo\n' > "$s/foo.sh"
printf 'bar\n' > "$s/bar.sh"
printf '# foo unit suite\n' > "$s/tests/unit/foo.test.sh"
printf '# bar suite\n' > "$s/tests/bar.test.sh"
commit_base
printf 'foo 2\n' > "$s/foo.sh"
commit_head
expect_suites "rule 1 via tests/unit/: a change to scripts/foo.sh prints exactly tests/unit/foo.test.sh" \
  "skills/tdd/scripts/tests/unit/foo.test.sh"

new_repo rule2
mkdir -p "$s/tests" "$s/lib"
printf 'bar_fn() { :; }\n' > "$s/lib/bar.sh"
for name in alpha beta; do
  printf '#!/usr/bin/env bash\nHERE="$(cd "$(dirname "$0")" && pwd)"\nsource "$HERE/lib/bar.sh"\n' > "$s/$name.sh"
done
printf '#!/usr/bin/env bash\necho gamma\n' > "$s/gamma.sh"
printf '#!/usr/bin/env bash\necho bar\n' > "$s/bar.sh"
for name in alpha beta gamma bar; do printf '# %s suite\n' "$name" > "$s/tests/$name.test.sh"; done
commit_base
printf 'bar_fn() { echo 2; }\n' > "$s/lib/bar.sh"
commit_head
expect_suites "rule 2: a change to scripts/lib/bar.sh prints the suite of every script that sources it, and no others" \
  skills/tdd/scripts/tests/alpha.test.sh \
  skills/tdd/scripts/tests/beta.test.sh

new_repo rule3-suite
foo_bar_tree
commit_base
printf '# foo suite 2\n' > "$s/tests/foo.test.sh"
commit_head
expect_suites "rule 3: a change to the suite tests/foo.test.sh itself prints exactly that suite" \
  "skills/tdd/scripts/tests/foo.test.sh"

new_repo rule3-fixture
mkdir -p "$s/tests/fixtures"
printf '# plan\n' > "$s/tests/fixtures/plan.md"
printf '# other\n' > "$s/tests/fixtures/other.md"
for name in alpha beta gamma; do printf '%s\n' "$name" > "$s/$name.sh"; done
for name in alpha beta; do
  printf '#!/usr/bin/env bash\nHERE="$(cd "$(dirname "$0")" && pwd)"\ncat "$HERE/fixtures/plan.md"\n' > "$s/tests/$name.test.sh"
done
printf '#!/usr/bin/env bash\nHERE="$(cd "$(dirname "$0")" && pwd)"\ncat "$HERE/fixtures/other.md"\n' > "$s/tests/gamma.test.sh"
commit_base
printf '# plan 2\n' > "$s/tests/fixtures/plan.md"
commit_head
expect_suites "rule 3: a change to the fixture tests/fixtures/plan.md prints every suite that references it by name" \
  skills/tdd/scripts/tests/alpha.test.sh \
  skills/tdd/scripts/tests/beta.test.sh

new_repo rule4
mkdir -p "$s/tests"
printf '# veri\n' > "$repo/CLAUDE.md"
printf '# tdd\n' > "$repo/skills/tdd/SKILL.md"
printf 'test:\n\techo hi\n' > "$repo/Makefile"
printf 'gamma\n' > "$s/gamma.sh"
printf '#!/usr/bin/env bash\nclaude_md="CLAUDE.md"\ngrep -q veri "$claude_md"\n' > "$s/tests/claude-md-guard.test.sh"
printf '#!/usr/bin/env bash\nskill_md="skills/tdd/SKILL.md"\ngrep -q tdd "$skill_md"\n' > "$s/tests/skill-md-guard.test.sh"
printf '#!/usr/bin/env bash\nROOT="$(git rev-parse --show-toplevel)"\nMAKEFILE="$ROOT/Makefile"\ngrep -q test: "$MAKEFILE"\n' > "$s/tests/makefile-guard.test.sh"
printf '#!/usr/bin/env bash\necho gamma\n' > "$s/tests/gamma.test.sh"
commit_base
printf '# veri 2\n' > "$repo/CLAUDE.md"
printf '# tdd 2\n' > "$repo/skills/tdd/SKILL.md"
printf 'test:\n\techo hi 2\n' > "$repo/Makefile"
commit_head
expect_suites "rule 4: a change to SKILL.md, CLAUDE.md and Makefile prints their guard suites" \
  skills/tdd/scripts/tests/claude-md-guard.test.sh \
  skills/tdd/scripts/tests/makefile-guard.test.sh \
  skills/tdd/scripts/tests/skill-md-guard.test.sh

new_repo rule5
mkdir -p "$s/tests/unit" "$repo/docs"
printf 'foo\n' > "$s/foo.sh"
printf 'bar\n' > "$s/bar.sh"
printf 'baz\n' > "$s/baz.sh"
printf '# foo suite\n' > "$s/tests/foo.test.sh"
printf '# bar suite\n' > "$s/tests/bar.test.sh"
printf '# baz unit suite\n' > "$s/tests/unit/baz.test.sh"
printf '# notes\n' > "$repo/docs/notes.md"
commit_base
printf 'foo 2\n' > "$s/foo.sh"
printf '# notes 2\n' > "$repo/docs/notes.md"
commit_head
expect_suites "rule 5: a rule-1 file plus a file no rule matches prints every suite, not the rule-1 suite alone" \
  skills/tdd/scripts/tests/bar.test.sh \
  skills/tdd/scripts/tests/foo.test.sh \
  skills/tdd/scripts/tests/unit/baz.test.sh

new_repo rule5-converse
mkdir -p "$s/tests/unit" "$s/tests/fixtures" "$s/lib"
printf '# veri\n' > "$repo/CLAUDE.md"
printf 'foo\n' > "$s/foo.sh"
printf 'bar_fn() { :; }\n' > "$s/lib/bar.sh"
printf '#!/usr/bin/env bash\nHERE="$(cd "$(dirname "$0")" && pwd)"\nsource "$HERE/lib/bar.sh"\n' > "$s/alpha.sh"
for name in beta gamma zeta; do printf '%s\n' "$name" > "$s/$name.sh"; done
printf '# plan\n' > "$s/tests/fixtures/plan.md"
printf '# foo suite\n' > "$s/tests/foo.test.sh"
printf '# alpha suite\n' > "$s/tests/alpha.test.sh"
printf '#!/usr/bin/env bash\nHERE="$(cd "$(dirname "$0")" && pwd)"\ncat "$HERE/fixtures/plan.md"\n' > "$s/tests/beta.test.sh"
printf '#!/usr/bin/env bash\nclaude_md="CLAUDE.md"\ngrep -q veri "$claude_md"\n' > "$s/tests/claude-md-guard.test.sh"
printf '# gamma suite\n' > "$s/tests/gamma.test.sh"
printf '# zeta unit suite\n' > "$s/tests/unit/zeta.test.sh"
commit_base
printf 'foo 2\n' > "$s/foo.sh"
printf 'bar_fn() { echo 2; }\n' > "$s/lib/bar.sh"
printf '# plan 2\n' > "$s/tests/fixtures/plan.md"
printf '# veri 2\n' > "$repo/CLAUDE.md"
commit_head
expect_suites "rule 5: a diff touching only files rules 1–4 match never falls back to the full suite" \
  skills/tdd/scripts/tests/alpha.test.sh \
  skills/tdd/scripts/tests/beta.test.sh \
  skills/tdd/scripts/tests/claude-md-guard.test.sh \
  skills/tdd/scripts/tests/foo.test.sh

new_repo rule6-prompt
mkdir -p "$s/tests" "$s/prompts"
printf '# red template\n' > "$s/prompts/develop-red.md"
printf '# green template\n' > "$s/prompts/develop-green.md"
printf '#!/usr/bin/env bash\nHERE="$(cd "$(dirname "$0")" && pwd)"\ncat "$HERE/../prompts/develop-red.md"\n' > "$s/tests/alpha.test.sh"
printf '#!/usr/bin/env bash\nHERE="$(cd "$(dirname "$0")" && pwd)"\ncat "$HERE/../prompts/develop-green.md"\n' > "$s/tests/beta.test.sh"
printf '# gamma suite\n' > "$s/tests/gamma.test.sh"
commit_base
printf '# red template 2\n' > "$s/prompts/develop-red.md"
commit_head
expect_suites "rule 6: a change to the prompt prompts/develop-red.md prints every suite that names it, and no others" \
  "skills/tdd/scripts/tests/alpha.test.sh"

new_repo rule6-prompt-and-suite
mkdir -p "$s/tests" "$s/prompts"
printf '# red template\n' > "$s/prompts/develop-red.md"
printf '#!/usr/bin/env bash\nHERE="$(cd "$(dirname "$0")" && pwd)"\ncat "$HERE/../prompts/develop-red.md"\n' > "$s/tests/alpha.test.sh"
printf '# delta suite\n' > "$s/tests/delta.test.sh"
printf '# gamma suite\n' > "$s/tests/gamma.test.sh"
commit_base
printf '# red template 2\n' > "$s/prompts/develop-red.md"
printf '# delta suite 2\n' > "$s/tests/delta.test.sh"
commit_head
expect_suites "rule 6: a prompt and a suite in one range print that suite and the prompt's suites, without widening" \
  skills/tdd/scripts/tests/alpha.test.sh \
  skills/tdd/scripts/tests/delta.test.sh

new_repo unplaced-only
mkdir -p "$s/tests/unit" "$s/prompts" "$repo/docs"
printf 'foo\n' > "$s/foo.sh"
printf 'bar\n' > "$s/bar.sh"
printf 'baz\n' > "$s/baz.sh"
printf '# red template\n' > "$s/prompts/develop-red.md"
printf '# foo suite\n' > "$s/tests/foo.test.sh"
printf '# bar suite\n' > "$s/tests/bar.test.sh"
printf '# baz unit suite\n' > "$s/tests/unit/baz.test.sh"
printf '# notes\n' > "$repo/docs/notes.md"
commit_base
printf '# notes 2\n' > "$repo/docs/notes.md"
commit_head
expect_suites "fail-closed: a range whose only changed file matches no rule prints every suite" \
  skills/tdd/scripts/tests/bar.test.sh \
  skills/tdd/scripts/tests/foo.test.sh \
  skills/tdd/scripts/tests/unit/baz.test.sh

new_repo widening-names-the-file
foo_tree
printf '# notes\n' > "$repo/notes.md"
commit_base
printf '# notes 2\n' > "$repo/notes.md"
commit_head
expect_widening_names "a widened answer names on stderr the file that forced the widening" notes.md

new_repo run-state-ledger
foo_bar_tree
write_ledger ' '
commit_base
printf 'foo 2\n' > "$s/foo.sh"
write_ledger x
commit_head
expect_suites "run state: a .tdd/ ledger alongside a script change prints exactly that script's suite" \
  "skills/tdd/scripts/tests/foo.test.sh"

new_repo run-state-only
foo_tree
write_ledger ' '
write_refactor_owed ' '
commit_base
write_ledger x
write_refactor_owed x
commit_head
expect_nothing_to_do "run state alone → exit 3 and prints nothing"

new_repo run-state-with-unplaced
foo_bar_tree
write_ledger ' '
printf '# notes\n' > "$repo/notes.md"
commit_base
write_ledger x
printf '# notes 2\n' > "$repo/notes.md"
commit_head
expect_suites "fail-closed: run state alongside a file no rule places still prints every suite" \
  skills/tdd/scripts/tests/bar.test.sh \
  skills/tdd/scripts/tests/foo.test.sh

new_repo widening-names-every-file
foo_tree
printf '# notes\n' > "$repo/notes.md"
printf '# memo\n' > "$repo/memo.md"
commit_base
printf '# notes 2\n' > "$repo/notes.md"
printf '# memo 2\n' > "$repo/memo.md"
commit_head
expect_widening_names "a widening caused by two unplaced files names both on stderr" notes.md memo.md

new_repo green-commit-shape
foo_bar_tree
write_ledger ' '
write_refactor_owed ' '
commit_base
printf 'foo 2\n' > "$s/foo.sh"
write_ledger x
write_refactor_owed x
commit_head
expect_suites "a green commit's shape — ledger, refactor-owed file and a source change — prints exactly that script's suite" \
  "skills/tdd/scripts/tests/foo.test.sh"

new_repo suite-added-counts
foo_tree
mkdir -p "$s/tests/unit"
counts_suite
commit_base
printf '# newbie suite\n' > "$s/tests/newbie.test.sh"
printf '# rookie unit suite\n' > "$s/tests/unit/rookie.test.sh"
commit_head
expect_suites "a range that adds a suite file under tests/ or tests/unit/ pulls in skills/tdd/scripts/tests/claude-md-counts.test.sh" \
  skills/tdd/scripts/tests/claude-md-counts.test.sh \
  skills/tdd/scripts/tests/newbie.test.sh \
  skills/tdd/scripts/tests/unit/rookie.test.sh

new_repo suite-edited-counts
foo_tree
counts_suite
commit_base
printf '# foo suite 2\n' > "$s/tests/foo.test.sh"
commit_head
expect_suites "editing an existing suite's contents does not pull in skills/tdd/scripts/tests/claude-md-counts.test.sh" \
  "skills/tdd/scripts/tests/foo.test.sh"

new_repo script-added-counts
foo_bar_tree
counts_suite
commit_base
rm "$s/bar.sh"
printf 'newbie\n' > "$s/newbie.sh"
commit_head
expect_suites "a range that adds or deletes a script under scripts/ pulls in skills/tdd/scripts/tests/claude-md-counts.test.sh" \
  skills/tdd/scripts/tests/bar.test.sh \
  skills/tdd/scripts/tests/claude-md-counts.test.sh \
  skills/tdd/scripts/tests/newbie.test.sh

new_repo rule2-continuation
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

new_repo rule2-line-end
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

new_repo rule2-comment
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

new_repo rule2-bug-section
mkdir -p "$s/lib"
for f in "$HERE"/../*.sh "$HERE/../lib/bug-section.sh"; do
  rel="${f#"$HERE"/../}"
  cat "$f" > "$s/$rel"
done
commit_base
printf '# changed\n' >> "$s/lib/bug-section.sh"
commit_head
expect_suites "#487: in the real repo, a change to lib/bug-section.sh selects both build-*-prompt suites" \
  skills/tdd/scripts/tests/build-develop-prompt.test.sh \
  skills/tdd/scripts/tests/build-verify-prompt.test.sh

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
