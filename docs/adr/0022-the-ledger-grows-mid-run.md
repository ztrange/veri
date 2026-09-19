# The ledger grows mid-run, under a fifth budget: plan growth

Until now the ledger was written once, at scoping, and never grew. From here on a run may add
steps to it. There are three sources:
- the refactor leaf's `NEW_STEP:` lines, naming a test that would force the general version
  of overfit code;
- verify-refactor's `NEW_STEP:` lines, naming an unhandled edge case the spec implies;
- a green leaf's `SPLIT:` lines, naming smaller behaviours for a step too big to do at once
  (Beck's *Child Test*).

`add-ledger-step.sh` is the only writer. How many steps a run may add is capped by
`VERI_STEP_GROWTH`, a **fifth budget axis**.

## Context

Kent Beck keeps a test list that grows as he works: every test he thinks of mid-cycle goes on
it. veri raised the same signals but had nowhere to put them:
- the refactor leaf's `FLAGS:` line was narrated and dropped, although ADR-0009 promised a
  triangulating step;
- verify-refactor could only REJECT a missing edge case, and a behaviour-preserving phase
  cannot meet that objection;
- a step too big for one green could only bail.

PRD #354 settled all three onto one mechanism.

## Decision

- **Placement.** An added step goes **directly after** the step that proposed it. A split
  step goes **directly before** the step being split, which later starts again from red.
- **Criterion.** An added step inherits its anchor's `⟦criterion k⟧`, so the issue's
  criterion is not ticked until the triangulating test also passes. It is marked
  `⟦added⟧`, which is what the budget counts, so the count survives a resume.
- **All or nothing.** A proposal that does not fit the budget is not added. It is written as
  a plain bullet under the ledger's `## Owed steps` heading and reaches the draft PR body. The
  run goes on; a plan that keeps growing is a scoping question for a human, not a reason to
  discard the run. A split that cannot fit is the exception: the step cannot go on without
  its smaller steps, so the run bails as `step-too-big`, a process failure.
- **A fifth axis, never merged with the other four.**

  | Budget | Axis |
  |---|---|
  | `VERI_STUCK_RETRIES` | liveness |
  | `VERI_NO_VERDICT_RETRIES` | protocol compliance |
  | `REVISE_BUDGET` | verdict |
  | `VERI_REFACTOR_BUDGET` | the cost of one step's tidying |
  | `VERI_STEP_GROWTH` | **how much larger than scoped a plan may get** |

  Merging it with `REVISE_BUDGET` would trade "the verifier keeps rejecting" against "the
  plan keeps growing", two failures fixed in different places. It defaults to 3 and is
  checked in preflight.
- **No human in the loop for adding a step.** Proposals are behaviour-level criteria that go
  through the same Red → Green → Refactor cycle and blind verification as scoped steps, so an
  added step earns its code the way every other step does.

## Consequences

- The committed ledger is still the source of truth, and it can now be longer at the end of a
  run than at its start. The `### 🗺️ Plan` comment shows the plan as scoped; the `step-added`
  and `step-split` events show how it grew.
- A proposal that is noise costs one full cycle. The cap bounds that at
  `VERI_STEP_GROWTH` cycles per run.
- verify-refactor may now write `NEW_STEP:` lines before its final `VERDICT:`/`REASON:` pair.
  Proposing a step reveals no developer reasoning, so the verifier stays blind.
