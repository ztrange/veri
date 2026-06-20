# The independent verifier is blind and establishes ground truth itself

Each verification step is performed by a fresh leaf that receives **only** the test
code, the issue's behavior spec, and the repo — never the developer leaf's rationale or
report. The verifier **runs the test itself** (exit code is the objective ground truth:
it really fails / really passes) and renders a structured verdict (`PASS | REJECT` +
reason) covering both the objective result and the judgment (right-reason failure; test
not trivial / over-coupled / too complex).

## Context

The reference suite has `red` predict and verify its *own* failure. The whole point of
this framework's separation is that the verifier cannot rubber-stamp the author's work.
Independence is enforced by **withholding the author's framing**: a verifier that never
sees "I wrote this to check X, here's why it fails" cannot anchor on it, and a verifier
that runs the test itself does not have to trust a reported result.

## Consequences

Verification costs a full leaf with its own repo exploration (more tokens than re-using
the developer's context) — accepted, because a blind re-derivation is the source of the
quality signal. The developer leaf's rationale is intentionally discarded at the leaf
boundary; anything the verifier must know has to be in the test or the issue spec, which
pressures the developer to make tests self-explanatory.
