# lib/bug-section.sh — sourced, not run: defines `spec_has_bug_section`, the one place the
# blind spec is asked whether the issue behind it is a bug (issue #112).
#
# Two callers, and they have to agree. `build-develop-prompt.sh` emits the reproduction
# paragraph a red leaf writes its test from; `build-verify-prompt.sh` emits the matching one
# that makes the verifier's PASS require the failure it observes to match *What happened*.
# Those two paragraphs are one decision — *is this step a reproduction?* — asked from the two
# ends of the same cycle, and the answer has to be the same at both: a spec the developer's
# builder reads as a bug and the verifier's does not is a leaf told to reproduce a report
# against a verifier that never heard of one, which rejects the very failure it was asked for.
# Written out twice, that is one edit away, so the predicate is not allowed to be a
# coincidence between two files.
#
# The spec's own text is what both ask, rather than a new parameter: a fifth parameter to the
# verifier's builder would be a channel the developer's rationale could travel down, and the
# four it takes are the blindness guarantee (ADR-0003). The heading is the one
# `capture-spec.sh` writes, which makes this the third place that word has to match — hence
# one predicate for the two readers of it.
#
# `return`, never `exit`: this runs in the caller's own shell.

# spec_has_bug_section <spec-file> — true when the blind spec carries a `## Bug` heading.
# grep's own stderr is discarded because an unreadable spec is the caller's refusal to make,
# in the one wording every missing file gets there; this answers "no section" for it
# meanwhile, which costs nothing, since the caller refuses the call before reading anything.
spec_has_bug_section() {
  grep -qE '^## Bug[[:space:]]*$' "$1" 2>/dev/null
}
