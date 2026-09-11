# "Already satisfied" is a step outcome with its own blind check, not a failure

When a Red leaf reports that its test passes against the unmodified code, the conductor
runs **verify-pin** rather than verify-red: a blind verifier that returns `PASS` only if
the test passes now, *and* fails under a behaviour-removing mutation the verifier applies
itself, *and* is behaviour-level rather than trivial. On `PASS` the test lands as a
regression pin (`test: pin <criterion> (#n)`) with the ledger tick atomic to that commit,
exactly as a green commit is, and the conductor narrates `📌 Already satisfied`. Green
and Refactor are skipped — there is no new production code to write or to tidy. A
`REJECT` enters the bounded revise loop (ADR-0004) like any other verdict; an exhausted
budget bails as a process failure.

## Context

#30's step 3 hit this wall: the criterion was already met by a guard #27 shipped, the
developer leaf wrote a faithful characterization test and said so honestly, verify-red
rejected it twice (a Red step must fail), both revise leaves reported IMPOSSIBLE, and the
run bailed as a process failure — four verifier calls to a foregone conclusion, the good
test discarded by the half-step revert. A passing test proves nothing on its own, so a
pin cannot be waved through; the verifier's own mutation is what makes the verdict mean
anything, on the same blind footing as every other phase (ADR-0003). Rejected: striking
the criterion by hand (loses the pin, needs a human every run), and letting verify-red
accept a passing test (destroys the Red guarantee everywhere).

## Consequences

A criterion covered by earlier work becomes a normal one-verifier outcome instead of a
bail, and the suite keeps the pin the revert would have thrown away. The cost is a fourth
verification phase (`build-verify-prompt.sh pin`, `verify.sh pin`, a prompt template) and
a conductor branch taken on the Red leaf's own report — a routing hint, not a trust
boundary: a mis-routed test is rejected by whichever verifier receives it.
