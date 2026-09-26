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

# run_affected [range] — affected-suites.sh inside $repo, on the case's $base..$head unless the
# caller names a range of its own (case 2 hands it malformed ones). Every caller invokes it
# inside a command substitution, and that subshell is what keeps the `cd` from reaching the rest
# of the suite; the caller attaches whatever redirections it wants.
run_affected() { cd "$repo" && "$AFFECTED" "${1:-$base..$head}"; }

# expect_suites <name> <suite>… — run affected-suites.sh on $base..$head inside $repo and pass
# when it exits 0 printing exactly those suites, one per line, in the order given; otherwise fail
# <name>, with a diff. Every case's expectation is a list of paths, so the joining belongs here
# rather than in a `$(printf …)` at each call site.
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

# expect_nothing_to_do <name> — run affected-suites.sh on $base..$head inside $repo and pass when
# it exits 3 printing nothing: the answer cases 3 and 17 share, an empty diff and a range of run
# state alone being the two ways of having no suite to run.
expect_nothing_to_do() {
  local name="$1" out code
  out="$(run_affected 2>/dev/null)"; code=$?
  if [[ "$code" == 3 && -z "$out" ]]; then ok; else
    no "$name (code=$code, stdout=${out:-<empty>})"
  fi
}

# expect_widening_names <name> <file>… — run affected-suites.sh on $base..$head inside $repo and
# pass when it exits 0 with stderr naming every <file>: the widening diagnostic cases 15 and 19
# assert on. Every <file> is required rather than any, since what case 19 asks is that a second
# unplaced file does not fall off the line the first one put there.
expect_widening_names() {
  local name="$1" err code f named=1
  shift
  err="$(run_affected 2>&1 >/dev/null)"; code=$?
  for f in "$@"; do [[ "$err" == *"$f"* ]] || named=0; done
  if [[ "$code" == 0 && "$named" == 1 ]]; then ok; else
    no "$name (code=$code, stderr=${err:-<empty>})"
  fi
}

# foo_tree — the smallest tree a case can assert a narrow answer against: foo.sh under $s with
# a suite of its own under tests/. Cases 15, 17, 19 and 21 build on it directly; the first three
# expect an answer that is not foo's suite, so tests/foo.test.sh is what says the answer widened
# or wandered.
foo_tree() {
  mkdir -p "$s/tests"
  printf 'foo\n' > "$s/foo.sh"
  printf '# foo suite\n' > "$s/tests/foo.test.sh"
}

# foo_bar_tree — foo_tree with a second script, bar.sh, and a suite of its own, which cases 4, 7,
# 16, 18 and 20 share. All but case 18 expect tests/foo.test.sh alone, so bar's untouched suite is
# the one an answer that widened, or that read the change as the neighbour's, would carry; case 18
# expects both, bar's being what says the answer did widen.
foo_bar_tree() {
  foo_tree
  printf 'bar\n' > "$s/bar.sh"
  printf '# bar suite\n' > "$s/tests/bar.test.sh"
}

# counts_suite — tests/claude-md-counts.test.sh, which cases 21–23 all hold steady across their
# range: it is the suite the add-or-delete rule names, so a case that wrote it only at the head end
# would be adding a suite rather than keeping one there throughout. The path is spelled in full
# rather than through $s because no-nested-suites.test.sh reads a real suite's basename after a
# $-prefixed path as one being launched; the repo-relative form is the shape it knows is data.
counts_suite() { printf '# counts suite\n' > "$repo/skills/tdd/scripts/tests/claude-md-counts.test.sh"; }

# write_ledger <mark> / write_refactor_owed <mark> — the two `.tdd/` files every green commit
# carries, and which cases 16–18 and 20 span: the ledger with its one step ticked or not, and
# the refactor-owed file beside it. <mark> is ' ' or 'x', and is the whole of what makes either
# end of a case's range differ, so a case calls these once before commit_base and again before
# commit_head. Each makes the `.tdd/` directory, so a case that writes run state needs no
# mkdir of its own for it.
write_ledger() {
  mkdir -p "$repo/.tdd"
  printf -- '- [%s] step one\n' "$1" > "$repo/.tdd/issue-416.md"
}
write_refactor_owed() {
  mkdir -p "$repo/.tdd"
  printf 'refactor owed [%s]\n' "$1" > "$repo/.tdd/issue-416-refactor-owed.md"
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
  skills/tdd/scripts/tests/unit/zulu.test.sh \
  skills/tdd/scripts/tests/wolf.test.sh

# 2. a malformed argument → exit 2 and a diagnostic on stderr. Three shapes: a single
#    revision with no `..` (which git diff alone would read as "against the working tree"
#    and answer happily), and a range whose base or head git cannot resolve.
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
expect_nothing_to_do "empty diff → exit 3 and prints nothing"

# 4. rule 1: a change to a script under skills/tdd/scripts/ → exactly its own suite. The tree
#    also holds a second script with a suite of its own, untouched, so an answer that listed
#    every suite, or the neighbour's, would not pass for "exactly that suite".
new_repo rule1
foo_bar_tree
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
  skills/tdd/scripts/tests/alpha.test.sh \
  skills/tdd/scripts/tests/beta.test.sh

# 7. rule 3: a change to a suite file itself → that suite. Only tests/foo.test.sh changes; the
#    script it covers and a neighbour's suite stay untouched, so the answer must be the suite
#    alone — not read as a change to foo.sh, and not widened to every suite.
new_repo rule3-suite
foo_bar_tree
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
  skills/tdd/scripts/tests/alpha.test.sh \
  skills/tdd/scripts/tests/beta.test.sh

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
  skills/tdd/scripts/tests/claude-md-guard.test.sh \
  skills/tdd/scripts/tests/makefile-guard.test.sh \
  skills/tdd/scripts/tests/skill-md-guard.test.sh

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
  skills/tdd/scripts/tests/bar.test.sh \
  skills/tdd/scripts/tests/foo.test.sh \
  skills/tdd/scripts/tests/unit/baz.test.sh

# 11. rule 5's converse: a change touching only files rules 1–4 place → exactly the suites those
#    rules name, never the full tier. foo.sh is placed by rule 1, lib/bar.sh (sourced by
#    alpha.sh) by rule 2, fixtures/plan.md (read by beta's suite) by rule 3, CLAUDE.md (read by
#    the guard) by rule 4. gamma's suite and the unit suite tests/unit/zeta.test.sh cover nothing
#    that changed, so an answer that fell back to every suite would carry them.
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

# 12. rule 6: a change whose only touched file is a prompt under scripts/prompts/ → the suites
#     that name that prompt, not every suite. alpha's suite reads prompts/develop-red.md the way
#     build-develop-prompt.test.sh reads "$HERE/../prompts/develop-reconcile.md"; beta's names a
#     different prompt and gamma's names none, so neither may appear — and neither may the full
#     tier, which is what an unplaced file falls back to.
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

# 13. rule 6 alongside rule 3: a range touching both a prompt and a suite → that suite and the
#     suites naming the prompt, and no widening. prompts/develop-red.md is named by alpha's
#     suite, and tests/delta.test.sh changes as a file in its own right; gamma's suite names no
#     prompt and did not change, so an answer that widened to the full tier would carry it.
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

# 14. fail-closed: a range whose only changed file matches no rule → every suite, kept whole
#     after rule 6. docs/notes.md is no script, lib file, suite, fixture, prompt or guarded
#     document, and nothing else changed, so there is no placed suite to narrow to: the answer
#     must be all three suites — tests/unit/baz.test.sh included — rather than an empty one.
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

# 15. a widened answer says why: the script names on stderr the file that forced the widening,
#     so the next unplaced kind is visible rather than silent. notes.md at the repository root
#     matches no rule, so the answer is every suite; stderr must name that file, not merely be
#     non-empty. The unplaced fixture is a root file rather than one in the generated-
#     documentation tree — which case 14 uses and may, since it only ever writes the path out —
#     because this case has to quote the path back in an assertion, and no-docs-reads.test.sh
#     rightly refuses a suite line that names that tree outside a comment or fixture text.
new_repo widening-names-the-file
foo_tree
printf '# notes\n' > "$repo/notes.md"
commit_base
printf '# notes 2\n' > "$repo/notes.md"
commit_head
expect_widening_names "a widened answer names on stderr the file that forced the widening" notes.md

# 16. run state: a `.tdd/` ledger alongside one source change → exactly that source change's
#     suite. Every green commit carries `.tdd/issue-<n>.md`, so a range spanning one used to
#     fall to the fail-closed branch and widen the whole answer to every suite (issue #416).
#     foo.sh is placed by rule 1; bar's suite covers nothing that changed, so a widened answer
#     would carry it.
new_repo run-state-ledger
foo_bar_tree
write_ledger ' '
commit_base
printf 'foo 2\n' > "$s/foo.sh"
write_ledger x
commit_head
expect_suites "run state: a .tdd/ ledger alongside a script change prints exactly that script's suite" \
  "skills/tdd/scripts/tests/foo.test.sh"

# 17. run state alone: a range whose every changed file is `.tdd/` run state → exit 3 and
#     nothing on stdout. Placing run state as affecting no suite leaves such a range with no
#     suite to print, and an empty answer would read to a leaf as "the tier is empty" rather
#     than "nothing to do"; exit 3 is the code that already says the latter (case 3), so the
#     two ways of having no suites to run answer alike (issue #416).
new_repo run-state-only
foo_tree
write_ledger ' '
write_refactor_owed ' '
commit_base
write_ledger x
write_refactor_owed x
commit_head
expect_nothing_to_do "run state alone → exit 3 and prints nothing"

# 18. fail-closed survives the run-state rule: a range of `.tdd/` run state alongside a file no
#     rule places → every suite. Placing run state as affecting no suite (cases 16 and 17) must
#     not swallow the widening notes.md owes: the two kinds of "no suite of its own" are
#     different answers, run state being known to affect none and an unplaced path being a file
#     nothing knows about. foo.sh and bar.sh are untouched, so only a widened answer carries
#     their suites (issue #416).
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

# 19. a widening caused by two unplaced files names both of them on stderr, not just one. Case 15
#     pins that the line names the file when there is one; the answer this case asks for is that
#     the list does not lose the rest, so the next unplaced kind stays visible even when it
#     arrives beside another one. notes.md and memo.md at the repository root each match no rule;
#     both are root files rather than ones in the generated-documentation tree for case 15's
#     reason — the assertion quotes the paths back.
new_repo widening-names-every-file
foo_tree
printf '# notes\n' > "$repo/notes.md"
printf '# memo\n' > "$repo/memo.md"
commit_base
printf '# notes 2\n' > "$repo/notes.md"
printf '# memo 2\n' > "$repo/memo.md"
commit_head
expect_widening_names "a widening caused by two unplaced files names both on stderr" notes.md memo.md

# 20. a whole green commit's shape: the ledger, the refactor-owed file and a real source change in
#     one range → exactly that source change's suite. This is the range every green commit makes,
#     and the one the regression was measured on (issue #416): before the run-state rule, the two
#     `.tdd/` files fell through together and widened the answer to all 104 suites in the tier
#     whose whole purpose is not to run them. Case 16 pins the ledger alone beside a change;
#     this pins the pair, so a rule narrowed back to `.tdd/issue-<n>.md` would show up here.
#     bar.sh and its suite are untouched, so a widened answer is the one carrying tests/bar.test.sh.
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

# 21. a suite file added under tests/ or tests/unit/ pulls in claude-md-counts.test.sh, the suite
#     that checks the counts CLAUDE.md hand-types against the files on disk. It asserts on a count
#     of files, not on any file's contents, so no touched path points at it and a run that added a
#     suite used to discover the broken count only in a later full-tier run, one phase too late
#     (issue #416). The range adds one suite under each directory the count covers; foo.sh and its
#     suite are untouched, so tests/foo.test.sh is what a widened answer would carry.
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

# 22. editing an existing suite's *contents* does not pull in claude-md-counts.test.sh: only adding
#     or removing a suite file changes a count on disk, and that suite asserts on the counts, not on
#     any suite's text. Case 21 pins the adding half; this pins that the rule is the file's arrival
#     or departure rather than any touch under tests/, so a range that edits a suite pays for that
#     suite alone. tests/claude-md-counts.test.sh exists at both ends and is untouched, so it is
#     what an answer reading a modification as a count change — or a widened one — would carry.
new_repo suite-edited-counts
foo_tree
counts_suite
commit_base
printf '# foo suite 2\n' > "$s/tests/foo.test.sh"
commit_head
expect_suites "editing an existing suite's contents does not pull in skills/tdd/scripts/tests/claude-md-counts.test.sh" \
  "skills/tdd/scripts/tests/foo.test.sh"

# 23. a script file added or deleted under scripts/ pulls in claude-md-counts.test.sh too: CLAUDE.md
#     hand-types the script count beside the suite count, and that suite checks both against the
#     files on disk. Case 21 pins the suite half of the same rule; this pins the script half, over a
#     range that both adds one script and deletes another, so a rule written for arrivals alone
#     would show up here. tests/bar.test.sh survives the deletion of bar.sh, so nothing under tests/
#     is added or deleted and the suite rule cannot be what supplies the answer; foo.sh and its
#     suite are untouched, so tests/foo.test.sh is what a widened answer would carry.
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

# 24. rule 2 over a `source` line that ends in a `\` continuation, the shape both callers of
#     lib/bug-section.sh use: `source "$HERE/lib/bug-section.sh" \` followed by a `|| { … }`
#     line (issue #487). alpha.sh sources lib/bar.sh that way; gamma.sh does not source it, so
#     its suite is what a widened answer would carry.
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

# 25. rule 2 over a `source` line that ends at the lib path itself, the shape case 24's widening
#     must not have narrowed (issue #487): alpha.sh closes the path with a quote, beta.sh with a
#     quote and trailing spaces, delta.sh leaves it unquoted and epsilon.sh unquoted with trailing
#     spaces. gamma.sh does not source lib/bar.sh, so its suite is what a widened answer would carry.
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

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
