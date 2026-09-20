# lib/candidate-line.sh — sourced, not run: defines `structural_candidate`, the one place a
# refactor leaf's `CANDIDATES: structural | <transform>` line is recognised and the transform
# read out of it.
#
# Two scripts read the same report for the same line and answer different questions about it
# — refactor-triage.sh, "is another leaf worth launching?", and refactor-owed.sh, "what does
# this step leave for a follow-up?" — so the line's shape was written out twice (#359). One
# copy drifting from the other would not fail anything loudly: triage would go on ending the
# loop on candidates the owed file never recorded, or the other way round, and the only
# symptom is a PR body missing work nobody deleted. The shape is stated here once instead.
#
# structural_candidate <line> — when <line> is a structural candidate, sets
# STRUCTURAL_TRANSFORM to the transform it names and returns 0; otherwise returns 1 and
# leaves STRUCTURAL_TRANSFORM alone, so a caller reads it only on a 0.
#
# `return`, never `exit`: this runs in the caller's shell once sourced, so an `exit` here
# would tear the caller down where a refusal is meant to be an answer it reads — the same
# rule lib/leaf-role.sh's header states at greater length.
structural_candidate() {
  # `[|]` rather than `\|` — inside [[ … =~ … ]] the pattern is an ERE, where a bare `|` is
  # alternation and a backslashed one is undefined; a bracket expression is neither.
  [[ "$1" =~ ^CANDIDATES:[[:space:]]*structural[[:space:]]*[|][[:space:]]*(.*)$ ]] || return 1
  STRUCTURAL_TRANSFORM="${BASH_REMATCH[1]}"
}
