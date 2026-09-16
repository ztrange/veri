# The contingent half of `SKILL.md` stays resident: declined, not deferred

Issue #202 tabled three cuts to the conductor's preamble and took one — the scope loop, 1,676
tokens, now behind a `Read` on a branch decided at turn 1. **The other two are declined.** They
are not backlog, not "later", not blocked on anyone's time:

- **the once-per-run procedure** — 3,684 tokens, 18.9% of the file;
- **the contingent paths the conductor takes when something has already gone wrong** — pin,
  revise, bail, resume — 3,142 tokens, 16.2%.

Together 6,826 tokens, which at ADR-0018's conductor rate of ~$0.00062 per resident token per
night is **~$4.20 a night** that veri will keep paying. That is the price of this decision,
stated so that nobody has to rediscover it as an argument for reversing it.

## Context

The arithmetic is the half that was already written down, and it is the half that will be
recomputed by the next reader of the step-1 table: ~6,800 tokens is a bigger saving than the one
#202 actually took, and the mechanism is the same one — move a section out, leave a pointer,
`Read` it when the branch is taken. What is not written down anywhere is why the same mechanism
is safe for one and not for the others.

A `Read` can fail. It fails on a wrong path after a rename, on a leaf's tree that is not the
conductor's, on a model that skips it because the turn already looked complete. For the scope
loop that failure is cheap: the branch is chosen at turn 1 from the argument alone, nothing has
started, and a run that cannot begin is a run nobody has paid for.

The contingent paths are read on the turn something is **already broken** — a leaf came back
stuck, a verdict came back `REJECT` past budget, a run is being resumed over a half-done step.
**A conductor that must read a file before it can bail is a conductor that might not bail**, and
the failure mode is not a cheap one: the step's progress is not preserved, the branch is not
pushed, the issue carries no classified diagnosis, and the human who comes to the wreck the next
morning has neither the work nor the reason. The once-per-run procedure fails the same way for
the same reason: what it holds is the run's setup invariants, and a conductor that has skipped
them does not know it has.

The issue's own rule settles it: *a reduction that makes the procedure ambiguous is a
regression*. Trading the bail path's reliability for $4.20 a night is that trade, and #202's
whole point — that a preamble token has a price — cuts both ways, because the price of the bail
path not firing is a whole night's run.

Rejected alongside it: **moving the sections and keeping a summary resident**, which pays the
tokens twice and leaves two statements of one procedure to drift apart; and **deferring the
question** rather than closing it, which is what produces the re-proposal this record exists to
answer.

## Consequences

**That half of `skills/tdd/SKILL.md` is closed.** The once-per-run procedure and the contingent
paths stay resident in every conductor request. A table showing again that they are large is not
a reason to reopen this — largeness is what was weighed. What would reopen it is a **mechanism
that makes the read unfailable**: the harness loading the file for the branch rather than the
conductor choosing to, or a bail that cannot be reached without it. Bring one of those, or the
decision stands.

`CLAUDE.md` is untouched by this — its case histories are reasoning a leaf cannot act on, which
is a different judgement and #202's third step.
