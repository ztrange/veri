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
   criterion's own terms rather than the plan's paraphrase of it? A step that is true of
   some mechanism the criterion might be built from is not the criterion being delivered.

A REJECT must name the criterion it fails on and state the part of it no step covers, in
the criterion's own words, so that the plan can be rewritten from your reason alone.
