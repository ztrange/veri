#!/usr/bin/env bash
# refactor-triage.sh — decide whether another refactor leaf is worth launching.
#
# Reads a finished refactor leaf's report on stdin — its last lines, verbatim, as
# develop-refactor.md asks for them — and answers from the `CANDIDATES:` lines it finds.
# Every one of those carries the class of the transform it names — `structural`
# or `cosmetic`, as prompts/develop-refactor.md's *The two classes of candidate* defines
# them:
#
#     CANDIDATES: structural | <transform>
#     CANDIDATES: cosmetic   | <transform>
#
# This is the other axis of the refactor loop from refactor-budget.sh: that script answers
# "may another leaf run?" from the count, this one answers "is another leaf worth running?"
# from what the last leaf reported. Only a structural candidate is worth a leaf, so the
# structural ones go to stdout, one transform per line, for the conductor to mirror into
# its `### 🛠️ Refactor` comment.
#
# When none is left — every candidate cosmetic, or `CANDIDATES: none` — the answer is
# exit 3, "nothing to do" in the four-code convention (CLAUDE.md, *Exit codes are the
# API*): a real answer, and the refactor loop's third stop condition, not a failure.
#
# A report this script cannot read is the other half of that convention: a candidate line
# carrying no class or one the two-class vocabulary does not have, or a report with no
# `CANDIDATES:` line at all, is a leaf that did not report what develop-refactor.md's
# *Report* asks for. That is exit 2, "no answer could be obtained" — a diagnostic on
# stderr and nothing on stdout, so the conductor mirroring stdout into its `### 🛠️
# Refactor` comment cannot seed it with a candidate nothing classed. Exit 3 would be the
# wrong answer there: it would end the loop quietly, as if the leaf had said there was
# nothing worth doing.
#
# Usage:   refactor-triage.sh < leaf-report.txt
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/exit-contract.sh"
source "$HERE/lib/candidate-line.sh"

structural=()
candidates_seen=0

# hazard: `read` fails at EOF on a last line with no newline, even though it filled the variable.
while IFS= read -r line || [[ -n "$line" ]]; do
  [[ "$line" =~ ^CANDIDATES:[[:space:]]*(.*)$ ]] || continue
  candidates_seen=1
  class_and_transform="${BASH_REMATCH[1]}"

  if structural_candidate "$line"; then
    structural+=("$STRUCTURAL_TRANSFORM")
  elif test_only_candidate "$line" ||
       cosmetic_candidate "$line" ||
       candidate_of_class out-of-scope "$line" ||
       [[ "$class_and_transform" =~ ^none[[:space:]]*$ ]]; then
    :
  else
    echo "refactor-triage: candidate line has no class, or one that is neither structural nor cosmetic: $line" >&2
    exit 2
  fi
done

# hazard: `cat report | while …` would fill these variables in a subshell and leave them empty here.
if [[ "$candidates_seen" -eq 0 ]]; then
  echo "refactor-triage: the report has no CANDIDATES: line" >&2
  exit 2
fi

if [[ "${#structural[@]}" -eq 0 ]]; then
  exit 3
fi

printf '%s\n' "${structural[@]}"
