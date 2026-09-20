#!/usr/bin/env bash
# refactor-owed.sh — carry a step's structural leftovers out of its refactor loop.
#
# When a step's refactor stops with structural candidates still listed, nothing had
# recorded them: `.tdd/develop-refactor.out` is overwritten by the next step, so by the
# draft PR every step's leftovers but the last were gone (#359, part of #354). This
# script appends them to a file that survives the run — `.tdd/issue-<n>-refactor-owed.md`,
# which the ledger's .gitignore rule already tracks — so the work a follow-up owes is in
# front of the human deciding the merge. `render` prints that file back as the
# `## Refactor owed` section SKILL.md's Draft PR step puts in the body.
#
#     refactor-owed.sh append <file> '<STEP>' < leaf-report.txt
#     refactor-owed.sh render <file>
#
# Reads a finished refactor leaf's report on stdin, the same lines refactor-triage.sh
# reads, and appends the transform of every `CANDIDATES: structural | …` line to <file>
# under the named step. Cosmetic candidates are never written: a reflowed comment put in
# front of the merge decision is the mixed backlog #149 already refused once.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=lib/candidate-line.sh
source "$HERE/lib/candidate-line.sh"

verb="${1:-}"

case "$verb" in
  append)
    file="${2:-}"
    step="${3:-}"

    structural=()
    # `|| [[ -n "$line" ]]` so a report whose last line has no trailing newline is still
    # read: `read` returns non-zero at EOF even when it did fill the variable.
    while IFS= read -r line || [[ -n "$line" ]]; do
      # What a structural candidate line looks like is lib/candidate-line.sh's to say:
      # refactor-triage.sh reads the same line for the loop's own answer, and one copy of
      # that shape drifting from the other is a leftover silently recorded by neither.
      if structural_candidate "$line"; then
        structural+=("$STRUCTURAL_TRANSFORM")
      fi
    done

    # The step's name goes in first, and only when it left something behind: the file
    # accumulates across a whole run, so a candidate that does not say which step owes it
    # cannot be acted on.
    if [[ "${#structural[@]}" -gt 0 ]]; then
      {
        printf '### %s\n' "$step"
        printf -- '- %s\n' "${structural[@]}"
      } >>"$file"
    fi
    ;;
  render)
    file="${2:-}"

    # The heading is the only thing render adds: `append` already wrote each step and its
    # candidates in the markdown the PR body wants, in the order they were recorded, so
    # the section is that file under a heading a reader can find it by.
    printf '## Refactor owed\n\n'
    cat "$file"
    ;;
  *)
    echo "refactor-owed: usage: refactor-owed.sh append <file> '<STEP>' < leaf-report.txt" >&2
    echo "                      refactor-owed.sh render <file>" >&2
    exit 2
    ;;
esac
