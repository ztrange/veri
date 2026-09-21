# lib/preserve.sh — sourced, not run: defines `preserve_attempt`, the one call a troubled
# step's evidence is kept through (issue #409).
#
# Two callers today — supervise.sh on a killed-stuck attempt, verify.sh on a verdict that was
# not a PASS — and the issue's list of troubles names five (reject, bail, no-verdict, stuck,
# prediction-diverged), so the sentence a failed preservation prints and the rule that its
# failure is never propagated would otherwise be written out once per trouble and drift apart.
#
# What is deliberately NOT here is the guards: what counts as "there is nothing to pair with"
# differs per caller — verify.sh already holds a tree reading and the role line its event was
# logged under, supervise.sh asks git whether there is a HEAD to hang a commit off — so each
# site still decides whether to call at all.
#
# `preserve-attempt.sh`, the CLI this runs, is resolved from THIS file's own directory rather
# than from a caller's `$HERE`, the way lib/leaf-model.sh finds lib/leaf-role.sh: inside a
# function `${BASH_SOURCE[0]}` is the file the function was defined in, whichever script
# sourced it.

# preserve_attempt <who> <issue> <step> <phase> <attempt> <mark> — snapshot the worktree to
# refs/veri/attempts/<issue>/<step>/<phase>-<attempt> and copy the leaf's own output beside
# it, or say on stderr that it could not be done. <who> is the caller's own name for its
# diagnostics, so a reader of .err knows which script gave up.
#
# ALWAYS returns 0, and its stdout is stderr's: a run that loses its evidence is worse off
# than one that does not, but a run that loses its leaf's status — the verdict, the 0/1/2 —
# to a failed `git update-ref` or to a stray line on a stream piped into parse-verdict.sh has
# lost the step itself. `return`, never `exit`: this runs in the caller's own shell.
preserve_attempt() {
  local who="$1" issue="$2" step="$3" phase="$4" attempt="$5" mark="$6"
  local here
  here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
  "$here/preserve-attempt.sh" "$issue" "$step" "$phase" "$attempt" "$mark" >&2 \
    || echo "$who: could not preserve the $mark attempt (issue $issue step $step $phase attempt $attempt)" >&2
  return 0
}
