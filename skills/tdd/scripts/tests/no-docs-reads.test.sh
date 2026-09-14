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
      # A comment, by its first non-blank character.
      [[ "$text" =~ ^[[:space:]]*# ]] && continue
      # Fixture text: written out, and not read on the way.
      if [[ "$text" =~ $WRITES_OUT ]] && ! [[ "$text" =~ $READ_VERB ]]; then
        continue
      fi
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

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
