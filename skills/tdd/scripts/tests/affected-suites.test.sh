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

counts_suite() { printf '# counts suite\n' > "$repo/skills/tdd/scripts/tests/claude-md-counts.test.sh"; }

write_ledger() {
  mkdir -p "$repo/.tdd"
  printf -- '- [%s] step one\n' "$1" > "$repo/.tdd/issue-416.md"
}
write_refactor_owed() {
  mkdir -p "$repo/.tdd"
  printf 'refactor owed [%s]\n' "$1" > "$repo/.tdd/issue-416-refactor-owed.md"
}

make_repo sorted
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

make_repo malformed
mkdir -p "$s"
printf 'wolf\n' > "$s/wolf.sh"
commit_head
bad=""
for arg in "$head..no-such-rev" "no-such-rev..$head"; do
  err="$(run_affected "$arg" 2>&1 >/dev/null)"; code=$?
  if [[ "$code" != 2 || "$err" != *"usage: affected-suites.sh"* ]]; then
    bad="${arg/$head/<head>}: code=$code, stderr=${err:-<empty>}"
    break
  fi
done
if [[ -z "$bad" ]]; then ok; else
  no "malformed argument → exit 2 with the usage line ($bad)"
fi

make_repo empty
mkdir -p "$s/tests"
printf 'wolf\n' > "$s/wolf.sh"
printf '# wolf suite\n' > "$s/tests/wolf.test.sh"
commit_base
git_q "$repo" commit -q --allow-empty -m "head" >/dev/null 2>&1
head="$(git -C "$repo" rev-parse HEAD)"
expect_nothing_to_do "empty diff → exit 3 and prints nothing"

make_repo rule1
foo_bar_tree
commit_base
printf 'foo 2\n' > "$s/foo.sh"
commit_head
expect_suites "rule 1: a change to scripts/foo.sh prints exactly tests/foo.test.sh" \
  "skills/tdd/scripts/tests/foo.test.sh"

make_repo rule1-unit
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

venv_suite=run-suite-venv
make_repo rule1-no-suite
mkdir -p "$s/tests"
printf 'run\n' > "$s/run-suite.sh"
printf '#!/usr/bin/env bash\nRUN="$HERE/../run-suite.sh"\n' > "$s/tests/$venv_suite.test.sh"
commit_base
printf 'run 2\n' > "$s/run-suite.sh"
commit_head
out="$(run_affected 2>/dev/null)"; code=$?
missing=""
while IFS= read -r line; do
  [[ -n "$line" && ! -e "$repo/$line" ]] && missing+="$line "
done <<< "$out"
if [[ ( "$code" == 0 || "$code" == 3 ) && -z "$missing" ]]; then ok; else
  no "#1011: a change to a script with no same-named suite prints no path that does not exist (code=$code, missing=${missing:-<none>})"
fi

make_repo rule1-naming-suites
mkdir -p "$s/tests"
printf 'run\n' > "$s/run-suite.sh"
printf 'gamma\n' > "$s/gamma.sh"
printf '#!/usr/bin/env bash\nRUN="$HERE/../run-suite.sh"\n' > "$s/tests/$venv_suite.test.sh"
printf '#!/usr/bin/env bash\nGAMMA="$HERE/../gamma.sh"\n' > "$s/tests/gamma.test.sh"
commit_base
printf 'run 2\n' > "$s/run-suite.sh"
commit_head
expect_suites "#1011: a change to a script with no same-named suite prints the existing suites that name its file" \
  skills/tdd/scripts/tests/run-suite-venv.test.sh

make_repo rule2
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

make_repo rule3-suite
foo_bar_tree
commit_base
printf '# foo suite 2\n' > "$s/tests/foo.test.sh"
commit_head
expect_suites "rule 3: a change to the suite tests/foo.test.sh itself prints exactly that suite" \
  "skills/tdd/scripts/tests/foo.test.sh"

make_repo rule3-fixture
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

make_repo rule4
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

make_repo skill_section
mkdir -p "$s/tests"
printf '# tdd\n\n## Alpha\n\nalpha text\n\n## Beta\n\nbeta text\n' > "$repo/skills/tdd/SKILL.md"
printf '#!/usr/bin/env bash\nskill_md="skills/tdd/SKILL.md"\nload_section '"'"'Alpha'"'"'\n' > "$s/tests/skill-alpha.test.sh"
printf '#!/usr/bin/env bash\nskill_md="skills/tdd/SKILL.md"\nload_section '"'"'Beta'"'"'\n' > "$s/tests/skill-beta.test.sh"
commit_base
printf '# tdd\n\n## Alpha\n\nalpha text 2\n\n## Beta\n\nbeta text\n' > "$repo/skills/tdd/SKILL.md"
commit_head
expect_suites "an edit inside one ## section of SKILL.md prints the suites reading that section, not one reading only another" \
  skills/tdd/scripts/tests/skill-alpha.test.sh

make_repo skill_whole
mkdir -p "$s/tests"
printf '# tdd\n\n## Alpha\n\nalpha text\n\n## Beta\n\nbeta text\n' > "$repo/skills/tdd/SKILL.md"
printf '#!/usr/bin/env bash\nskill_md="skills/tdd/SKILL.md"\nload_section '"'"'Beta'"'"'\n' > "$s/tests/skill-beta.test.sh"
printf '#!/usr/bin/env bash\nskill_md="skills/tdd/SKILL.md"\ngrep -F text "$skill_md"\n' > "$s/tests/skill-whole.test.sh"
commit_base
printf '# tdd\n\n## Alpha\n\nalpha text 2\n\n## Beta\n\nbeta text\n' > "$repo/skills/tdd/SKILL.md"
commit_head
expect_suites "an edit inside one ## section of SKILL.md still prints a suite reading SKILL.md unsliced" \
  skills/tdd/scripts/tests/skill-whole.test.sh

make_repo skill_subsection
mkdir -p "$s/tests"
printf '# tdd\n\n## Alpha\n\nalpha text\n\n### Sub\n\nsub text\n\n### Sib\n\nsib text\n\n## Beta\n\nbeta text\n' > "$repo/skills/tdd/SKILL.md"
for name in Alpha Sub Sib Beta; do
  printf '#!/usr/bin/env bash\nskill_md="skills/tdd/SKILL.md"\nload_section '"'"'%s'"'"'\n' "$name" > "$s/tests/skill-$(printf '%s' "$name" | tr 'A-Z' 'a-z').test.sh"
done
commit_base
printf '# tdd\n\n## Alpha\n\nalpha text\n\n### Sub\n\nsub text 2\n\n### Sib\n\nsib text\n\n## Beta\n\nbeta text\n' > "$repo/skills/tdd/SKILL.md"
commit_head
expect_suites "an edit inside one ### subsection of SKILL.md prints the suites reading it and its enclosing ## section, not one reading only a sibling" \
  skills/tdd/scripts/tests/skill-alpha.test.sh \
  skills/tdd/scripts/tests/skill-sub.test.sh

base="$head"
printf '# tdd\n\n## Alpha\n\nalpha text\n\n### Sub\n\nsub text 2\n\n### Sib\n\nsib text 2\n\n## Beta\n\nbeta text\n' > "$repo/skills/tdd/SKILL.md"
commit_head
expect_suites "an edit inside a ### subsection after a sibling ### prints the suites reading it and its enclosing ## section, not one reading the earlier sibling" \
  skills/tdd/scripts/tests/skill-alpha.test.sh \
  skills/tdd/scripts/tests/skill-sib.test.sh

make_repo skill_heading
mkdir -p "$s/tests"
printf '# tdd\n\n## Alpha\n\nalpha text\n\n## Beta\n\nbeta text\n' > "$repo/skills/tdd/SKILL.md"
printf '#!/usr/bin/env bash\nskill_md="skills/tdd/SKILL.md"\nload_section '"'"'Alpha'"'"'\n' > "$s/tests/skill-alpha.test.sh"
printf '#!/usr/bin/env bash\nskill_md="skills/tdd/SKILL.md"\nload_section '"'"'Beta'"'"'\n' > "$s/tests/skill-beta.test.sh"
commit_base
printf '# tdd\n\n## Alpha\n\nalpha text\n\n## Gamma\n\nbeta text\n' > "$repo/skills/tdd/SKILL.md"
commit_head
expect_suites "an edit changing a ## heading line of SKILL.md prints every suite naming SKILL.md" \
  skills/tdd/scripts/tests/skill-alpha.test.sh \
  skills/tdd/scripts/tests/skill-beta.test.sh

make_repo skill_heading_deleted
mkdir -p "$s/tests"
printf '# tdd\n\n## Alpha\n\nalpha text\n\n## Beta\n\nbeta text\n\n## Gamma\n\ngamma text\n' > "$repo/skills/tdd/SKILL.md"
printf '#!/usr/bin/env bash\nskill_md="skills/tdd/SKILL.md"\nload_section '"'"'Alpha'"'"'\n' > "$s/tests/skill-alpha.test.sh"
printf '#!/usr/bin/env bash\nskill_md="skills/tdd/SKILL.md"\nload_section '"'"'Beta'"'"'\n' > "$s/tests/skill-beta.test.sh"
printf '#!/usr/bin/env bash\nskill_md="skills/tdd/SKILL.md"\nload_section '"'"'Gamma'"'"'\n' > "$s/tests/skill-gamma.test.sh"
commit_base
printf '# tdd\n\n## Alpha\n\nalpha text\n\n\nbeta text\n\n## Gamma\n\ngamma text\n' > "$repo/skills/tdd/SKILL.md"
commit_head
expect_suites "an edit only deleting a ## heading line of SKILL.md prints every suite naming SKILL.md" \
  skills/tdd/scripts/tests/skill-alpha.test.sh \
  skills/tdd/scripts/tests/skill-beta.test.sh \
  skills/tdd/scripts/tests/skill-gamma.test.sh

make_repo skill_two_sections
mkdir -p "$s/tests"
printf '# tdd\n\n## Alpha\n\nalpha text\n\n## Beta\n\nbeta text\n\n## Gamma\n\ngamma text\n' > "$repo/skills/tdd/SKILL.md"
for name in Alpha Beta Gamma; do
  printf '#!/usr/bin/env bash\nskill_md="skills/tdd/SKILL.md"\nload_section '"'"'%s'"'"'\n' "$name" > "$s/tests/skill-$(printf '%s' "$name" | tr 'A-Z' 'a-z').test.sh"
done
commit_base
printf '# tdd\n\n## Alpha\n\nalpha text 2\n\n## Beta\n\nbeta text 2\n\n## Gamma\n\ngamma text\n' > "$repo/skills/tdd/SKILL.md"
commit_head
expect_suites "an edit whose changed lines of SKILL.md span two sections prints every suite naming SKILL.md" \
  skills/tdd/scripts/tests/skill-alpha.test.sh \
  skills/tdd/scripts/tests/skill-beta.test.sh \
  skills/tdd/scripts/tests/skill-gamma.test.sh

make_repo skill_unplaced
mkdir -p "$s/tests"
for name in Alpha Beta; do
  printf '#!/usr/bin/env bash\nskill_md="skills/tdd/SKILL.md"\nload_section '"'"'%s'"'"'\n' "$name" > "$s/tests/skill-$(printf '%s' "$name" | tr 'A-Z' 'a-z').test.sh"
done
commit_base
unplaced_expected="$(printf '%s\n' skills/tdd/scripts/tests/skill-alpha.test.sh skills/tdd/scripts/tests/skill-beta.test.sh)"
unplaced_wrong=""
check_unplaced() {
  local out code
  commit_head
  out="$(run_affected 2>/dev/null)"; code=$?
  [[ "$code" == 0 && "$out" == "$unplaced_expected" ]] || unplaced_wrong+=" $1(code=$code, stdout=${out//$'\n'/,})"
  base="$head"
}
printf '# tdd\n\nintro\n\n## Alpha\n\nalpha text\n\n## Beta\n\nbeta text\n' > "$repo/skills/tdd/SKILL.md"
check_unplaced added
printf '# tdd\n\nintro 2\n\n## Alpha\n\nalpha text\n\n## Beta\n\nbeta text\n' > "$repo/skills/tdd/SKILL.md"
check_unplaced "above the first ##"
rm "$repo/skills/tdd/SKILL.md"
check_unplaced deleted
if [[ -z "$unplaced_wrong" ]]; then ok; else
  no "an edit to SKILL.md that cannot be placed in a section (above the first ##, file added or deleted) prints every suite naming SKILL.md:$unplaced_wrong"
fi

make_repo rule5
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

make_repo rule5-converse
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

make_repo rule6-prompt
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

make_repo rule6-prompt-and-suite
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

make_repo unplaced-only
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

make_repo widening-names-the-file
foo_tree
printf '# notes\n' > "$repo/notes.md"
commit_base
printf '# notes 2\n' > "$repo/notes.md"
commit_head
expect_widening_names "a widened answer names on stderr the file that forced the widening" notes.md

make_repo run-state-ledger
foo_bar_tree
write_ledger ' '
commit_base
printf 'foo 2\n' > "$s/foo.sh"
write_ledger x
commit_head
expect_suites "run state: a .tdd/ ledger alongside a script change prints exactly that script's suite" \
  "skills/tdd/scripts/tests/foo.test.sh"

make_repo run-state-only
foo_tree
write_ledger ' '
write_refactor_owed ' '
commit_base
write_ledger x
write_refactor_owed x
commit_head
expect_nothing_to_do "run state alone → exit 3 and prints nothing"

make_repo run-state-with-unplaced
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

make_repo widening-names-every-file
foo_tree
printf '# notes\n' > "$repo/notes.md"
printf '# memo\n' > "$repo/memo.md"
commit_base
printf '# notes 2\n' > "$repo/notes.md"
printf '# memo 2\n' > "$repo/memo.md"
commit_head
expect_widening_names "a widening caused by two unplaced files names both on stderr" notes.md memo.md

make_repo green-commit-shape
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

make_repo suite-added-counts
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

make_repo suite-edited-counts
foo_tree
counts_suite
commit_base
printf '# foo suite 2\n' > "$s/tests/foo.test.sh"
commit_head
expect_suites "editing an existing suite's contents does not pull in skills/tdd/scripts/tests/claude-md-counts.test.sh" \
  "skills/tdd/scripts/tests/foo.test.sh"

make_repo script-added-counts
foo_bar_tree
counts_suite
commit_base
rm "$s/bar.sh"
printf 'newbie\n' > "$s/newbie.sh"
printf '# newbie suite\n' > "$s/tests/newbie.test.sh"
commit_head
expect_suites "a range that adds or deletes a script under scripts/ pulls in skills/tdd/scripts/tests/claude-md-counts.test.sh" \
  skills/tdd/scripts/tests/bar.test.sh \
  skills/tdd/scripts/tests/claude-md-counts.test.sh \
  skills/tdd/scripts/tests/newbie.test.sh

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
expect_suites "#1138: a suite the base added or deleted after the branch point does not make affected-suites.sh <base>..HEAD print skills/tdd/scripts/tests/claude-md-counts.test.sh" \
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
  skills/tdd/scripts/tests/claude-md-counts.test.sh \
  skills/tdd/scripts/tests/foo.test.sh

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
expected=$'skills/tdd/scripts/tests/baz.test.sh\nskills/tdd/scripts/tests/claude-md-counts.test.sh'
if [[ "$code" == 0 && "$out" == "$expected" ]]; then ok; else
  no "affected-suites.sh <base> with a new, untracked suite also prints skills/tdd/scripts/tests/claude-md-counts.test.sh (code=$code)"
  diff <(printf '%s\n' "$expected") <(printf '%s\n' "$out") | sed 's/^/    /'
fi

make_repo working-tree-committed-counts
foo_tree
counts_suite
commit_base
printf '# baz suite\n' > "$s/tests/baz.test.sh"
commit_all "$repo" "add baz"
out="$(run_affected "$base" 2>/dev/null)"; code=$?
expected=$'skills/tdd/scripts/tests/baz.test.sh\nskills/tdd/scripts/tests/claude-md-counts.test.sh'
if [[ "$code" == 0 && "$out" == "$expected" ]]; then ok; else
  no "affected-suites.sh <base> with a committed added suite and no untracked file still prints skills/tdd/scripts/tests/claude-md-counts.test.sh (code=$code)"
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

finish
