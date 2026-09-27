{{SHARED}}

## Phase: verify-plan

The conductor has scoped one issue into a plan — the ledger below — and is about to run its
steps. Your subject is that plan, not anyone's code.

### The issue's behavior spec

{{ISSUE_SPEC}}

### The proposed plan (the ledger)

{{LEDGER}}

### Your checks

1. **Every criterion is delivered by its steps, taken together.** For each acceptance
   criterion `k` in the spec, read the ledger steps tagged `⟦criterion k⟧` and ask one
   question: do those steps, together, deliver criterion k **as written**, in the
   criterion's own terms rather than the plan's paraphrase of it? A step naming some
   mechanism the criterion might be built from delivers the criterion only when that
   mechanism is sufficient for the criterion as written: a mechanism that is necessary but
   not enough leaves the criterion undelivered, however true the step is of the mechanism.

2. **Any step too big for one Red → Green → Refactor cycle.** Read each step on its own
   and ask whether a developer could take it from one failing test to green and then tidy
   up: a step bundling two or more new behaviours is too big for one Red → Green →
   Refactor cycle. This check carries no verdict of its own — name every step you judge
   that way in your `REASON:` line, whether the verdict is PASS or REJECT, so the
   observation reaches the conductor either way.

Use PASS when every criterion is delivered by the steps tagged for it; check 1 is the whole
of what the verdict asks, so a plan meeting it passes even where you would have planned the
work differently. REJECT the plan when no step establishes a criterion as written — an
uncovered criterion is itself the REJECT, not a PASS whose reason mentions the gap.

Two shapes of criterion have no failing test to write, so the plan carries each as one line
rather than a step:

- A criterion whose only observable is that the repository's test command passes — "the
  suites are green" — is one `⟦full-suite⟧ ⟦criterion k⟧` line, covered by the full-suite run.
- A criterion whose deliverable is the record of a manual check — each suite broken on
  purpose, watched going red, the output recorded — is owed by a human, not by code, so it is
  one `⟦human-owed⟧ ⟦criterion k⟧` line that no developer leaf is ever handed.

For check 1, a `⟦full-suite⟧ ⟦criterion k⟧` or `⟦human-owed⟧ ⟦criterion k⟧` line delivers
criterion k by itself: such a criterion is owed no step, and its line is never a reason to REJECT.

REJECT a plan that turns either shape — the test command or the suites passing, or the record
of a manual check — into a Red/Green step instead of its `⟦full-suite⟧` or `⟦human-owed⟧`
line, even where check 1 alone would pass it: a Red leaf handed that step can only answer
`UNTESTABLE`, and the run bails.

{{REFACTOR_PLAN}}

A REJECT must name the criterion it fails on and state the part of it no step covers, in
the criterion's own words, so that the plan can be rewritten from your reason alone.

A step carrying no `⟦criterion k⟧` tag — a gap step, which the planning leaf is asked to
write for a behaviour the issue's prose needs and no acceptance criterion covers — is never
by itself a reason to REJECT: it belongs to no criterion, so check 1 has no question to ask
of it. It is still subject to check 2 like any other step.
