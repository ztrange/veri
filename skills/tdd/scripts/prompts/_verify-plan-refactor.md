This issue is a refactor: its spec carries a `## Refactor` section, so each step is one
Cover → Transform → Verify cycle rather than a Red → Green → Refactor one. Four more checks
apply to every step tagged with a criterion:

- REJECT a step that does not name one refactoring — the single transformation, by name, that
  its Transform applies, such as Extract Function or Move Function — rather than paraphrasing
  the issue ("tidy the helpers").
- REJECT a step whose smell is not stated as a runnable shell predicate in its criterion: a
  command that is false before the step and true after it, which the verifier can run.
- REJECT a step that leaves a no-op in place for a later step to delete — one that makes code
  dead by passing a no-op (`onChange={() => {}}`) while another step deletes it; the deletion
  belongs in the step that makes the code dead.
- REJECT a refactor-kind plan that holds a ⟦phases: …⟧ step — a rename that tests call is an
  interface change, filed without the `refactor` label.
