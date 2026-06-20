# Refactor is a loop of single transformations, blind-verified once after it settles

The refactor step applies **one** behavior-preserving transformation per leaf invocation
(extract, rename, guard clause, etc.), re-running the full suite each time (must stay
green — objective gate), and the conductor **loops** the refactor leaf until it reports
"no refactor warranted." After the loop settles, a single blind verifier renders one
verdict on the final result: suite still green AND code up to standard (conventions,
typing, robustness). The verdict is **not** run per transformation.

## Context

The user wants refactor to "run several times until no applicable refactors remain" (the
reference suite's `fast-refactor` loop) and wants the result verified ("yes"). Per-
transformation blind verification would multiply cost without proportional signal, since
each transformation is already suite-gated. One verdict after the loop captures the
standards judgment at the point it matters — the committed state — for one verifier's cost.

## Consequences

Each cycle spends three blind verifiers at most (red, green, refactor) but the refactor
one fires once regardless of how many transformations ran. A REJECT on the refactor
verdict follows the bounded revise loop (ADR-0004). Overfit detected during refactor is a
triangulation signal, not a transformation (ADR-0009). Placement (post-loop vs per-
transformation) is tunable if the post-loop verdict proves too coarse.
