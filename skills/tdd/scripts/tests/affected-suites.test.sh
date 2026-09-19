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

# git_q <repo> <args…> — git with a fixed identity, so a commit does not depend on the
# user.name/user.email of the machine running the suite (CI carries none).
git_q() { local repo="$1"; shift; git -C "$repo" -c user.name=veri -c user.email=veri@example.test "$@"; }

# commit_all <repo> <message> — stage everything in <repo> and commit it.
commit_all() {
  git_q "$1" add -A >/dev/null 2>&1
  git_q "$1" commit -q -m "$2" >/dev/null 2>&1
}

# commit_base / commit_head — commit everything in $repo and record the commit as the case's
# $base or $head, the two ends of the range expect_suites hands affected-suites.sh.
commit_base() { commit_all "$repo" "base"; base="$(git -C "$repo" rev-parse HEAD)"; }
commit_head() { commit_all "$repo" "head"; head="$(git -C "$repo" rev-parse HEAD)"; }

# new_repo <name> — a repository of the case's own under $work, set as $repo, with $s the
# path of its skills/tdd/scripts/ (not created: each case makes the directories it needs).
new_repo() {
  repo="$work/$1"
  git init -q -b main "$repo" >/dev/null 2>&1
  s="$repo/skills/tdd/scripts"
}

# expect_suites <name> <expected> — run affected-suites.sh on $base..$head inside $repo and
# pass when it exits 0 printing exactly <expected>; otherwise fail <name>, with a diff.
expect_suites() {
  local name="$1" expected="$2" out code
  out="$(cd "$repo" && "$AFFECTED" "$base..$head" 2>/dev/null)"; code=$?
  if [[ "$code" == 0 && "$out" == "$expected" ]]; then ok; else
    no "$name (code=$code)"
    diff <(printf '%s\n' "$expected") <(printf '%s\n' "$out") | sed 's/^/    /'
  fi
}

# 1. a resolvable range → one suite per line, sorted, no duplicate. The range touches
#    wolf.sh and its own suite, so both name tests/wolf.test.sh and a list that kept every
#    answer would carry it twice; and zulu.sh, whose suite is under tests/unit/, so the diff
#    order (wolf before zulu) puts tests/wolf.test.sh ahead of tests/unit/zulu.test.sh, which
#    sorts first.
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
  "$(printf 'skills/tdd/scripts/tests/unit/zulu.test.sh\nskills/tdd/scripts/tests/wolf.test.sh')"

# 2. a malformed argument → exit 2 and a diagnostic on stderr. Three shapes: a single
#    revision with no `..` (which git diff alone would read as "against the working tree"
#    and answer happily), and a range whose base or head git cannot resolve.
new_repo malformed
mkdir -p "$s"
printf 'wolf\n' > "$s/wolf.sh"
commit_head
bad=""
for arg in "$head" "$head..no-such-rev" "no-such-rev..$head"; do
  err="$(cd "$repo" && "$AFFECTED" "$arg" 2>&1 >/dev/null)"; code=$?
  if [[ "$code" != 2 || -z "$err" ]]; then
    bad="${arg/$head/<head>}: code=$code, stderr=${err:-<empty>}"
    break
  fi
done
if [[ -z "$bad" ]]; then ok; else
  no "malformed argument → exit 2 with a diagnostic ($bad)"
fi

# 3. a range whose diff is empty → exit 3 and nothing on stdout: nothing changed is "nothing
#    to do", not an error and not an empty answer. The head is a real commit of its own, made
#    with --allow-empty, so the range is two distinct revisions git resolves and only the diff
#    between them is empty.
new_repo empty
mkdir -p "$s/tests"
printf 'wolf\n' > "$s/wolf.sh"
printf '# wolf suite\n' > "$s/tests/wolf.test.sh"
commit_base
git_q "$repo" commit -q --allow-empty -m "head" >/dev/null 2>&1
head="$(git -C "$repo" rev-parse HEAD)"
out="$(cd "$repo" && "$AFFECTED" "$base..$head" 2>/dev/null)"; code=$?
if [[ "$code" == 3 && -z "$out" ]]; then ok; else
  no "empty diff → exit 3 and prints nothing (code=$code, stdout=${out:-<empty>})"
fi

# 4. rule 1: a change to a script under skills/tdd/scripts/ → exactly its own suite. The tree
#    also holds a second script with a suite of its own, untouched, so an answer that listed
#    every suite, or the neighbour's, would not pass for "exactly that suite".
new_repo rule1
mkdir -p "$s/tests"
printf 'foo\n' > "$s/foo.sh"
printf 'bar\n' > "$s/bar.sh"
printf '# foo suite\n' > "$s/tests/foo.test.sh"
printf '# bar suite\n' > "$s/tests/bar.test.sh"
commit_base
printf 'foo 2\n' > "$s/foo.sh"
commit_head
expect_suites "rule 1: a change to scripts/foo.sh prints exactly tests/foo.test.sh" \
  "skills/tdd/scripts/tests/foo.test.sh"

# 5. rule 1 via tests/unit/: a change to a script whose suite lives under tests/unit/ → that
#    unit suite, not a tests/<script>.test.sh that does not exist. A neighbour script with a
#    suite under tests/ is left untouched, so the answer must be the unit suite alone.
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

# 6. rule 2: a change to a file under skills/tdd/scripts/lib/ → the suite of every script that
#    sources it, and no others. alpha.sh and beta.sh source lib/bar.sh the way event.sh sources
#    lib/json-escape.sh; gamma.sh does not, and a top-level bar.sh shares the lib file's name,
#    so neither gamma's suite nor tests/bar.test.sh may appear.
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
  "$(printf 'skills/tdd/scripts/tests/alpha.test.sh\nskills/tdd/scripts/tests/beta.test.sh')"

# 7. rule 3: a change to a suite file itself → that suite. Only tests/foo.test.sh changes; the
#    script it covers and a neighbour's suite stay untouched, so the answer must be the suite
#    alone — not read as a change to foo.sh, and not widened to every suite.
new_repo rule3-suite
mkdir -p "$s/tests"
printf 'foo\n' > "$s/foo.sh"
printf 'bar\n' > "$s/bar.sh"
printf '# foo suite\n' > "$s/tests/foo.test.sh"
printf '# bar suite\n' > "$s/tests/bar.test.sh"
commit_base
printf '# foo suite 2\n' > "$s/tests/foo.test.sh"
commit_head
expect_suites "rule 3: a change to the suite tests/foo.test.sh itself prints exactly that suite" \
  "skills/tdd/scripts/tests/foo.test.sh"

# 8. rule 3: a change to a fixture under tests/fixtures/ → every suite that references that
#    fixture by name. alpha's and beta's suites read fixtures/plan.md the way count-line-guard
#    reads fixtures/silent-death/…; gamma's reads a different fixture, other.md, so it must not
#    appear, and neither may the suites' scripts, which did not change.
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
  "$(printf 'skills/tdd/scripts/tests/alpha.test.sh\nskills/tdd/scripts/tests/beta.test.sh')"

# 9. rule 4: a change to SKILL.md, CLAUDE.md and the Makefile → their guard suites, the suites
#    whose own contract is to read that document. Each guard names its document the way this
#    repository's do: claude_md="CLAUDE.md" as model-knobs-recorded does, skill_md=
#    "skills/tdd/SKILL.md" as skill-commit does, MAKEFILE="$ROOT/Makefile" as count-line-guard
#    does. gamma's suite reads none of the three, so it must not appear.
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
  "$(printf 'skills/tdd/scripts/tests/claude-md-guard.test.sh\nskills/tdd/scripts/tests/makefile-guard.test.sh\nskills/tdd/scripts/tests/skill-md-guard.test.sh')"

# 10. rule 5: a change to one file rule 1 places and one file no rule places → every suite, the
#    full tier, not rule 1's suite alone. foo.sh is placed by rule 1; docs/notes.md is no script,
#    lib file, suite, fixture or guarded document, so it widens the whole answer to all three
#    suites — tests/bar.test.sh and tests/unit/baz.test.sh included, though nothing they cover
#    changed.
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
  "$(printf 'skills/tdd/scripts/tests/bar.test.sh\nskills/tdd/scripts/tests/foo.test.sh\nskills/tdd/scripts/tests/unit/baz.test.sh')"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
