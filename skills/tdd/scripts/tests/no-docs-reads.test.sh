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

# The repository itself, four directories up: what case 2 asks `make` about, and what the
# repo-relative paths a roster line carries are resolved against.
ROOT="$(cd "$HERE/../../../.." && pwd)"

# The tree the development lane stays out of, written once and without its trailing slash,
# so that no line of this file is its own first offender.
DOCS_DIR='docs'

# A path in that tree, as an ERE. The character before it may be a slash or a quote — a
# suite spells one as "$ROOT/" followed by the tree's name — but not a word character, so a
# directory whose name merely ends in those letters is not one.
DOCS_PATH="(^|[^[:alnum:]_.-])$DOCS_DIR/"

# A line that writes its path out rather than using it: a redirect whose target is a quoted
# word or a variable, which is how a fixture is written (`> "$body"`, `>> "$work/body.md"`).
# Matching the target and not the bare `>` is what keeps `2>&1` and a `<span…>` quoted out
# of an HTML fixture from reading as one.
WRITES_OUT='>[[:space:]]*["'"'"'$]'

# What disqualifies a line from that exemption even so: it also reads. A line that writes a
# fixture does not open the tree, but `grep … "$ROOT/$p" > "$out"` does, and only the verb
# tells them apart. The verb must start a word and end in whitespace, so
# `solvable-issues.sh as it now stands` is not a command and `commentary.py-budgets-diagram`
# is not a `diff`.
READ_VERB='(^|[^[:alnum:]_./-])(grep|egrep|fgrep|cat|sed|awk|head|tail|wc|cmp|diff|source|python3|python|bash)[[:space:]]'

pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output says which line broke the rule rather than just that some line did.
report() {
  local name="$1"
  if [[ "${#problems[@]}" -eq 0 ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1))
    echo "FAIL - $name"
    printf '    %s\n' "${problems[@]}"
  fi
}

# flat <text> — one line of it, for a failure message: newlines become slashes so a quoted
# line stays one line.
flat() { printf '%s' "$1" | tr '\n' '/'; }

# exempt <line> — true when a line naming a path in that tree is nonetheless allowed to,
# which is the header's two cases and nothing else:
#
#   - a comment, by its first non-blank character. A comment cannot open anything.
#   - fixture text: written out, and not read on the way.
#
# One predicate rather than two tests in the loop, because "may a line name one?" is a
# single question the header answers once, and a third exemption belongs here rather than
# as a third shape inside the sweep.
exempt() {
  local text="$1"
  [[ "$text" =~ ^[[:space:]]*# ]] && return 0
  [[ "$text" =~ $WRITES_OUT ]] && ! [[ "$text" =~ $READ_VERB ]]
}

# roster <target> — the suite paths <target> would run, one repo-relative path per line.
# `make -n` prints the recipe with the target's wildcard already expanded and executes none
# of it, which is the only way to ask this question: running `make test` to find out what
# `make test` runs is the recursion, and it costs 80 s besides. Same idiom as
# suite-lanes.test.sh's roster helper, which reads both targets' lists the same way.
roster() { make -C "$ROOT" -n "$1" 2>&1 | grep -o '[^ ]*\.test\.sh' | sort -u; }

# probe_no_suite_reaches_into_the_tree — the criterion. Every suite beside this one is asked
# for the lines naming a path in that tree, and each of those for one of the two exemptions.
# The suites are found by globbing this directory rather than by a list, because the list is
# what a sixth site would be added outside of; `make test` finds them the same way.
#
# One problem per offending line, naming the suite and the line number, because what sends
# the next author to the site is the address rather than the file.
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

# 1. One criterion, one case: nothing in this directory reaches into that tree. One case
#    rather than one per suite, because the rule is about the directory — a suite added
#    tomorrow is covered by existing, and a per-suite roster would be the list the glob
#    above exists to avoid.
name="no suite under skills/tdd/scripts/tests/ names a path in the generated-documentation tree outside a comment or fixture text"
problems=()

probe_no_suite_reaches_into_the_tree

report "$name"

# probe_no_suite_the_target_runs_reaches_into_the_tree — the same question asked of the
# roster `make test` would run rather than of this directory's glob, and answered the same
# way, line by line through the same exemptions.
#
# An empty roster is a problem rather than a pass: a probe that finds no suite to read has
# not established that none of them names a path, and a recipe reworded past the `-n`
# expansion this reads would otherwise turn the case green by saying nothing.
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

# 2. The same rule asked of the target instead of the directory. Case 1 is the rule an
#    author breaks, and it finds its suites by globbing the directory they are written in.
#    This case is the consequence the rule is for: `make test` is what preflight reads its
#    baseline off, what every Green leaf runs and what both blind verifiers run, so what
#    has to be true is that nothing *that target runs* opens a file in the generated-
#    documentation tree — and rewording a figure in the commentary then cannot turn a
#    development run red over prose no development change touched.
#
#    The two are the same file list today, since the target's `TESTS` is the same wildcard
#    this suite globs, and they are still not the same claim: a roster that stops matching
#    that glob — a suite named into the target from outside this directory, a wildcard
#    narrowed to a list — leaves case 1 reading files the baseline no longer runs and blind
#    to the ones it does, and this sentence is the one that stops being true. Asking the
#    target itself costs one `make -n`.
name="no suite \`make test\` runs names a path in the generated-documentation tree outside a comment or fixture text"
problems=()

probe_no_suite_the_target_runs_reaches_into_the_tree

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
