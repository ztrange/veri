# One refactor leaf applies the step's transforms; the conductor checks what it left

Supersedes **ADR-0010**. The refactor step spends **one leaf for the whole step**, not one
per transformation. That leaf triages the touched files' candidates, applies the structural
ones most valuable first up to `VERI_REFACTOR_BUDGET`, runs the suites covering the files
it touched after each transform and reverts one that turns them red, and **commits each
transform itself** as `refactor: <what> (#<n>)`. What ADR-0010 bought with a leaf per
transform — a break traceable to one change — is bought by the commit and the suite run
between transforms, which are still there.

The conductor's job in the phase changes from **producing** that result to **checking** it,
because the blind verifier ahead judges the settled tree and cannot see either way it goes
wrong: it asks `git status --porcelain` and refuses to walk into verify-refactor over a
dirty tree (the half-applied transform a killed leaf left, which no suite run and no
verifier has seen), asks `git log --format=%s <green-sha>..HEAD` and refuses over a commit
whose subject is not a `refactor:` (production code smuggled into a behaviour-preserving
phase, past the verifier that asks whether behaviour was preserved and not whether the code
was earned by a test), and narrates `git rev-list --count <green-sha>..HEAD` against the
budget — an overrun as an overrun, never clamped. The blind post-loop verdict itself is
unchanged: one verifier on the final state, once (ADR-0003), and a REJECT still follows the
bounded revise loop (ADR-0004).

## Context

ADR-0010's price is a cold `claude -p` start and a re-read of the spec and of the touched
files for every transform. Issue #144 cut the suite half of it — a refactor leaf runs the
suites covering the files it touched, not the full suite — and left the rest:

- **#144** (`.tdd/wt/144/.tdd/events.jsonl`, a log that starts mid-run): refactor leaves
  took 79–192 s each, and the refactor loops plus verify-refactor took 2,147 of that run's
  3,735 leaf-seconds — 57%.
- **#137** (`.tdd/wt/137/.tdd/events.jsonl`): one step's five transforms took 358–669 s
  each, 49 minutes for that one step's tidying.

Rejected: **keeping the loop and shrinking the leaf's reading**, because the cold start is
most of what a short leaf costs and no amount of trimming the prompt removes it. **Letting
the leaf apply everything in one commit**, because that is exactly the traceability
ADR-0010 bought and is worth keeping — the commit per transform is cheap, the leaf per
transform was not. **Leaving the refactor commit with the conductor**, because a conductor
that commits what a leaf left on disk cannot tell a transform the leaf finished from one it
was killed part-way through; the leaf commits only after its own suite run is green, so a
commit in the range is a transform that passed, and anything uncommitted is by construction
unfinished.

## Consequences

Three things follow from the leaf owning the commits. The **budget reaches the leaf as a
number** — `build-develop-prompt.sh refactor` carries `VERI_REFACTOR_BUDGET` into the
prompt — so the count is the leaf's to respect and the conductor's to report;
`refactor-budget.sh 0` still decides whether the leaf runs at all. The leaf's **hard timeout
scales with the budget**, `leaf-timeout.sh`'s value × max(1, budget), because at #137's
rates five transforms in one leaf would be killed at ~29.5 min; an explicit `VERI_TIMEOUT`
is still used as given. And **resume** re-entering a step's refactor (the `⟂ refactor
pending` mark, ADR-0007) resets the uncommitted work and relaunches the leaf with the budget
reduced by that step's `refactor:` commits already on the branch.

The cost is that a refactor leaf is now a long-running process whose transforms land one by
one, so a run killed inside it leaves a partially tidied step — which is what the conductor's
dirty-tree check and resume's budget arithmetic exist to settle. The atomic tick-and-commit
stays on green (ADR-0007): that commit carries the ledger tick, and it is only the refactor
commit that moved.
