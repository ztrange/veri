#!/usr/bin/env bash
# refactor-owed.sh — carry a step's structural leftovers out of its refactor loop.
#
# When a step's refactor stops with structural candidates still listed, nothing had
# recorded them: `.tdd/develop-refactor.out` is overwritten by the next step, so by the
# draft PR every step's leftovers but the last were gone. This
# script appends them to a file that survives the run — `.tdd/issue-<n>-refactor-owed.md`,
# which the ledger's .gitignore rule already tracks — so the work a follow-up owes is in
# front of the human deciding the merge. `render` prints that file back as the
# `## Refactor owed` section SKILL.md's Draft PR step puts in the body.
#
#     refactor-owed.sh append <file> '<STEP>' < leaf-report.txt
#     refactor-owed.sh render <file>
#     refactor-owed.sh list <file>
#
# Reads a finished refactor leaf's report on stdin, the same lines refactor-triage.sh
# reads, and appends the transform of every `CANDIDATES: structural | …` line to <file>
# under the named step. Cosmetic candidates are never written: a reflowed comment put in
# front of the merge decision is a mixed backlog.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/candidate-line.sh"

verb="${1:-}"
file="${2:-}"

case "$verb" in
  append)
    step="${3:-}"

    structural=()
    # hazard: `|| [[ -n "$line" ]]` keeps a last line that has no trailing newline.
    while IFS= read -r line || [[ -n "$line" ]]; do
      if structural_candidate "$line"; then
        structural+=("$STRUCTURAL_TRANSFORM")
      fi
    done

    if [[ "${#structural[@]}" -gt 0 ]]; then
      {
        printf '### %s\n' "$step"
        printf -- '- %s\n' "${structural[@]}"
      } >>"$file"
    fi
    ;;
  render)
    [[ -s "$file" ]] || exit 3

    printf '## Refactor owed\n\n'
    cat "$file"
    ;;
  list)
    [[ -s "$file" ]] || exit 3
    sed -n 's/^- //p' "$file"
    ;;
  *)
    echo "refactor-owed: usage: refactor-owed.sh append <file> '<STEP>' < leaf-report.txt" >&2
    echo "                      refactor-owed.sh render <file>" >&2
    echo "                      refactor-owed.sh list <file>" >&2
    exit 2
    ;;
esac
