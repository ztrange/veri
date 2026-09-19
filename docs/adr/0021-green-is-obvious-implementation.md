# Green is Obvious Implementation only; generality still comes from triangulation

Supersedes in part **ADR-0009**. The part it replaces is ADR-0009's claim that veri
"matches the reference suite's fake-green + triangulate discipline". Green does **not**
fake. The developer leaf writes the real implementation the one failing test demands, which
Kent Beck calls *Obvious Implementation*. verify-green keeps rejecting a pass bought by
hard-coding the exact expected value. The rest of ADR-0009 stands:
- production code is only added to satisfy a failing test;
- refactor never adds untested branches;
- overfit code is answered with a triangulating test, never generalized by hand.

## Context

Beck's *Test-Driven Development: By Example* (2003) offers three ways to get to green:
- **Fake It:** return a constant, then turn it into real code step by step.
- **Triangulate:** generalize only once a second example forces you to.
- **Obvious Implementation:** type the real code.

A faked green is repaired in Beck's refactor phase, which removes the duplication between the
constant in the test and the constant in the code. ADR-0009 named that discipline, but by
2026-09-19 the prompts forbade both halves of it:
- `verify-green.md` rejects hard-coding the expected value;
- `develop-refactor.md` forbids generalizing overfit code.

The record and the behaviour had drifted apart, and PRD #354 settled which one moves.

## Decision

Keep the prompts, and correct the record.

- **Fake It is rejected on cost.** A veri step costs about 70 minutes of leaves. Faking
  every green would make each overfit green pay a second cycle for a test the plan could
  have asked for at scoping.
- **The blind verifier cannot tell a deliberate fake from a mistake.** Only the developer
  knows which one it is, and that is exactly the rationale the verifier is never given.

Triangulation remains the one route to generality. Overfit code now arises by
accident, not by design, and when the refactor leaf or verify-refactor spots it, the answer
is a new ledger step (ADR-0022), not a hand-written generalization.

## Consequences

- A green that is too big to write directly is split into smaller steps (ADR-0022), not faked.
- Scoping still owns most generality: a plan with too few criteria still leaves code
  overfit, and the refactor leaf's proposals are what catch it.
