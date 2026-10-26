# Plan for #2477 — A verifier may judge a guard untested by probing one test file, and REJECT on the false negative

- [x] The verify-green prompt template gains a clause: a judgement that a change is or is not covered by a case is made by running the fast command it was given ({{FAST_CMD}}) and the affected suites, never one test file alone, and a REJECT on that ground names the exact command that was run ⟦diff-checked⟧ ⟦criterion 1⟧
- [x] A build-verify-prompt case asserts the rendered verify-green prompt carries the coverage-probe clause (fast command plus affected suites, never one test file, a REJECT names the command run) ⟦criterion 1⟧
- [x] The verify-refactor and verify-diff prompt templates gain the same coverage-probe clause the verify-green prompt carries, on their fast command and affected suites ⟦diff-checked⟧ ⟦criterion 2⟧
- [ ] Build-verify-prompt cases assert the rendered verify-refactor and verify-diff prompts each carry the coverage-probe clause ⟦criterion 2⟧
- [ ] Go-red control: a mutation removing only the new clause turns the verify-green clause case red while an existing build-verify-prompt case stays green, recorded as a manual check ⟦human-owed⟧ ⟦criterion 3⟧
