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
# When none is left — every candidate cosmetic, or `CANDIDATES: none` — the answer is
# exit 3, "nothing to do" in the four-code convention (CLAUDE.md, *Exit codes are the
# API*): a real answer, and the refactor loop's third stop condition, not a failure.
#
# Usage:   refactor-triage.sh < leaf-report.txt
set -euo pipefail

structural=0

# `|| [[ -n "$line" ]]` so a report whose last line has no trailing newline is still read:
# `read` returns non-zero at EOF even when it did fill the variable.
while IFS= read -r line || [[ -n "$line" ]]; do
  # `[|]` rather than `\|` — inside [[ … =~ … ]] the pattern is an ERE, where a bare `|`
  # is alternation and a backslashed one is undefined; a bracket expression is neither.
  if [[ "$line" =~ ^CANDIDATES:[[:space:]]*structural[[:space:]]*[|][[:space:]]*(.*)$ ]]; then
    echo "${BASH_REMATCH[1]}"
    structural=$((structural + 1))
  fi
done

# The loop is not a pipeline, so its body ran in this shell and `structural` survives it —
# `cat report | while …` would have counted in a subshell and left 0 here.
if [[ "$structural" -eq 0 ]]; then
  exit 3
fi
