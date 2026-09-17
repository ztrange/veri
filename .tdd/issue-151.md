# Plan for #151 — verify-refactor reviews the refactor's diff from the green commit, given only its sha

- [x] build-verify-prompt.sh refactor takes a base sha as its 4th argument and puts it in the prompt ⟦criterion 1⟧
- [x] build-verify-prompt.sh refactor exits 2 with a stderr diagnostic when the base sha is missing or is not 7–40 lowercase hex characters ⟦criterion 1⟧
- [x] verify-refactor.md has the verifier review git diff <base-sha>..HEAD and tells it not to read the range's commit messages ⟦criterion 2⟧
- [x] verify-refactor.md makes a removed or weakened test assertion a REJECT naming it, names cosmetic-only hunks in REASON without rejecting on them, and does not reject an empty range by itself ⟦criterion 2⟧
- [x] verify.sh refactor passes the base sha through to the verifier prompt ⟦criterion 3⟧
- [x] SKILL.md passes the step's green commit sha to verify.sh refactor at both call sites, the cycle loop and Resume sub-step 2's $green ⟦criterion 3⟧ ⟂ refactor pending
- [ ] CLAUDE.md's blind-verifier invariant names the base-sha parameter and why a sha cannot leak rationale ⟦criterion 3⟧
