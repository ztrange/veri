# A bug is a kind of issue, not a new phase

A bug is an issue carrying the `bug` label and a body that says what happened, what was
expected and how to get there; a bug-report skill files exactly that. The conductor copies
those three into the blind spec under a `## Bug` heading, and the existing Red and
verify-red templates each gain one paragraph: for a bug the one failing test is a
**reproduction** — it encodes the expected behaviour and must fail for the *reported*
reason, and the verifier rejects a test that fails for any other. Green fixes it, Refactor
runs as always, and the test stays as the regression test. Selection takes a scope's bugs
before its other issues.

## Context

Nothing in the procedure said "reproduce first": Red was uniformly "write one failing test
for the criterion", which lets a bug's test fail for an unrelated reason and still count.

Rejected: **a separate `reproduce` phase** with its own templates and verifier parameter,
because the verifier is blind by construction — it takes only a phase, the spec, the test
path and a test id — and a new parameter is a new channel from the developer to it; the
spec is the channel that already exists, so the bug goes there. **Inferring a bug from
prose**, because the label is a switch both selection and the prompt builder can read
without parsing, and the human choosing it is the opt-in.

## Consequences

A bug is planned like any issue — one step per manifestation, each a reproduction — so the
ledger, resume and bail need nothing new. Ordering bugs first changes the selection
layer's rule from "lowest number first" to "bugs, then lowest number", which the glossary
records. A fix is tagged like a feature: what veri can do observably changed.
