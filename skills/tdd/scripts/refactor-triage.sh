#!/usr/bin/env bash
# refactor-triage.sh — decide whether another refactor leaf is worth launching.
#
# Reads a finished refactor leaf's report on stdin — its last lines, verbatim, as
# develop-refactor.md asks for them — and answers from the `CANDIDATES:` lines it finds.
# Since #149 every one of those carries the class of the transform it names — `structural`
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
# Usage:   refactor-triage.sh < leaf-report.txt
set -euo pipefail

# `|| [[ -n "$line" ]]` so a report whose last line has no trailing newline is still read:
# `read` returns non-zero at EOF even when it did fill the variable.
while IFS= read -r line || [[ -n "$line" ]]; do
  # `[|]` rather than `\|` — inside [[ … =~ … ]] the pattern is an ERE, where a bare `|`
  # is alternation and a backslashed one is undefined; a bracket expression is neither.
  if [[ "$line" =~ ^CANDIDATES:[[:space:]]*structural[[:space:]]*[|][[:space:]]*(.*)$ ]]; then
    echo "${BASH_REMATCH[1]}"
  fi
done
