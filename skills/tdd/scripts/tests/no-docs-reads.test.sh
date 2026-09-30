#!/usr/bin/env bash
# Unit tests for the suites in this directory — a development suite must not reach into the
# generated-documentation tree. Like hermetic-suites.test.sh and count-line-guard.test.sh
# this suite has no script as its subject: its subject is the tree it is run in.
# Zero-dependency plain-shell asserts, same idiom as count-line-guard.test.sh.
#
# Why this exists (issue #143): `make test` is what preflight reads its baseline off, what
# every Green leaf runs and what both blind verifiers run, three times per step. A suite
# here that opens a file in the documentation tree puts that prose on the development
# lane's critical path — rewording a figure turns the baseline red, and a script change
# owes a page rebuild to stay green. #143 deletes the four sites that did it; this suite is
# what stops the fifth from being written, and it is in `make test` rather than beside the
# documentation suites because the tree it guards is this one.
#
# Contract under test:
#   No suite under this directory names a path in the documentation tree, except in a
#   comment or as text it writes into a fixture of its own. A path it writes out is not
#   that, and this suite must have nothing to say about it: detect-test-command.test.sh:171
#   and :201 seed two such paths into issue bodies as the very prose #75 mis-parsed, and a
#   check that refused those would be deleted by the first author it blocked, taking the
#   real one with it.
#
#   And the same asked of `make test` itself: no suite that target would run names one
#   either. That is the sentence the rule exists for — the baseline preflight reads, the
#   Green leaf runs and both blind verifiers run cannot go red over a file in that tree.
#
# The rule is "names one", not "opens one on this line", and the difference is the whole
# check. Every site #143 deletes binds the path somewhere and opens it somewhere else:
# supervise.test.sh:203 and refactor-budget.test.sh:255 put it in a `|`-separated heredoc
# row that a `while read` later hands to a helper; solvable-issues.test.sh:601 and
# skill-identity.test.sh:189 assign it to a variable that a `sed` three lines down resolves
# against $ROOT; skill-identity.test.sh:175 makes it a word of a `for`. A check that asked
# each line whether it carried both a path and a read verb would find none of the five, and
# the shapes have nothing in common but the path itself — so the path itself is what is
# asked about, and a line that merely names one is treated as the read it is one variable
# away from being.
#
# That leaves exactly two things a suite may legitimately do with such a path, and both are
# recognised without a list of files:
#
#   - say it in a comment. A comment cannot open anything, and the prose in this tree
#     discusses the documentation lane at length — a check that read comments would fire on
#     every suite explaining why its own documentation half was moved out.
#   - write it out as fixture text. The line carries a redirect into a file of the suite's
#     own and no read verb, which is `printf '…docs/…' > "$body"` and nothing else.
#
# Anything else is reported, including a path named only to be excluded from a sweep: git
# grep spells such an exclusion as a directory rather than a path (`':!docs'`), so the one
# site in this tree that needs one is not a path in the first place.
#
# This suite reads itself along with the rest, which is the discipline it asks for: no line
# of code below spells that tree's name with its slash — the regexes build the slash on —
# and the failure message quotes the offending line rather than spelling a path of its own.
#
# Run: skills/tdd/scripts/tests/no-docs-reads.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"

ROOT="$(cd "$HERE/../../../.." && pwd)"

DOCS_DIR='docs'

DOCS_PATH="(^|[^[:alnum:]_.-])$DOCS_DIR/"

WRITES_OUT='>[[:space:]]*["'"'"'$]'

READ_VERB='(^|[^[:alnum:]_./-])(grep|egrep|fgrep|cat|sed|awk|head|tail|wc|cmp|diff|source|python3|python|bash)[[:space:]]'

pass=0 fail=0

source "$HERE/lib/harness.sh"

flat() { printf '%s' "$1" | tr '\n' '/'; }

exempt() {
  local text="$1"
  [[ "$text" =~ ^[[:space:]]*# ]] && return 0
  [[ "$text" =~ $WRITES_OUT ]] && ! [[ "$text" =~ $READ_VERB ]]
}

roster() { make -C "$ROOT" -n "$1" 2>&1 | grep -o '[^ ]*\.test\.sh' | sort -u; }

probe_no_suite_reaches_into_the_tree() {
  local f name hit lineno text
  for f in "$HERE"/*.test.sh; do
    [[ -e "$f" ]] || continue
    name="$(basename "$f")"
    while IFS= read -r hit; do
      lineno="${hit%%:*}"
      text="${hit#*:}"
      exempt "$text" && continue
      problems+=("$name:$lineno names a path in the generated-documentation tree outside a comment and outside fixture text, which puts that tree's prose on every leaf's critical path: $(flat "$text")")
    done < <(grep -nE "$DOCS_PATH" "$f")
  done
  return 0
}

name="no suite under skills/tdd/scripts/tests/ names a path in the generated-documentation tree outside a comment or fixture text"
problems=()

probe_no_suite_reaches_into_the_tree

report "$name"

probe_no_suite_the_target_runs_reaches_into_the_tree() {
  local rel hit lineno text
  local -a listed=()
  while IFS= read -r rel; do
    [[ -n "$rel" ]] || continue
    listed+=("$rel")
    while IFS= read -r hit; do
      lineno="${hit%%:*}"
      text="${hit#*:}"
      exempt "$text" && continue
      problems+=("$rel:$lineno names a path in the generated-documentation tree outside a comment and outside fixture text, so \`make test\` — the baseline preflight reads, the Green leaf runs and both blind verifiers run — opens that tree: $(flat "$text")")
    done < <(grep -nE "$DOCS_PATH" "$ROOT/$rel")
  done < <(roster test)
  [[ "${#listed[@]}" -gt 0 ]] ||
    problems+=("\`make -n test\` named no suite at all, so nothing was read: the roster this case asks about could not be obtained")
  return 0
}

name="no suite \`make test\` runs names a path in the generated-documentation tree outside a comment or fixture text"
problems=()

probe_no_suite_the_target_runs_reaches_into_the_tree

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
