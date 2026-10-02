This issue is a refactor: its spec carries a `## Refactor` section, so each step is one
Cover → Transform → Verify cycle rather than a Red → Green → Refactor one. Three more checks
apply to every step tagged with a criterion:

- REJECT a step that does not name one refactoring — the single transformation, by name, that
  its Transform applies, such as Extract Function or Move Function — rather than paraphrasing
  the issue ("tidy the helpers").
- REJECT a step whose smell is not stated as a runnable shell predicate in its criterion: a
  command that is false before the step and true after it, which the verifier can run.
- REJECT a step that makes code dead but leaves a no-op in place — a caller passing a no-op,
  a prop or effect kept "for now" — for a later step to delete. The deletion belongs in the
  same step: by the later step nothing reaches the code, so its Cover has nothing to mutate.
