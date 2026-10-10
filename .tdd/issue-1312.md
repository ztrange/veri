# Plan for #1312 — PRD 009 C3-4: the conductor runs an interface change as one phased step, and proves group steps by its own mutation run

- [x] `build-develop-prompt.sh` accepts an expand phase and a migrate phase, each printing a prompt that states what that phase changes (expand: production gains the new interface and the old one becomes a proxy; migrate: callers move to the new interface) and that test files stay frozen ⟦criterion 1⟧
- [x] `build-develop-prompt.sh` accepts a contract (a) phase and a contract (b) phase, the contract (a) prompt stating that tests are rewritten or deleted while production stays frozen, the contract (b) prompt stating that the old interface's proxy is deleted while test files stay frozen ⟦criterion 1⟧
- [x] `build-verify-prompt.sh` accepts an expand phase and a migrate phase, each printing a prompt that states what that phase changes and that test files must be left frozen ⟦criterion 1⟧
- [x] `build-verify-prompt.sh` accepts a contract (a) phase and a contract (b) phase, the contract (a) prompt stating that production must be left frozen, the contract (b) prompt stating that the proxy is deleted and test files must be left frozen ⟦criterion 1⟧
- [x] `build-verify-prompt.sh`'s expand, migrate, contract (a) and contract (b) phases take only a phase, the spec file, the test path and a base sha, and exit 2 when that base sha does not match `^[0-9a-f]{7,40}$`, as the `refactor` phase does ⟦criterion 1⟧
- [x] An unknown phase given to `build-develop-prompt.sh` or to `build-verify-prompt.sh` exits 2 with a message naming the expand, migrate, contract (a) and contract (b) phases among the phases it accepts ⟦criterion 1⟧
- [x] `SKILL.md` plans an interface change as one ledger step listing its phases (`⟦phases: …⟧`) and runs the phases it lists in order, each as a developer leaf then a blind verifier, ticking that phase's mark (`tick-ledger.sh --phase`) with that phase's commit ⟦criterion 2⟧
- [x] `SKILL.md` rejects an expand, migrate or contract (b) phase's commit that `transform-touches-tests.sh` exits 1 on, and a contract (a) phase's commit that `production-frozen.sh` exits 1 on ⟦criterion 2⟧
- [x] `SKILL.md` starts a phased step's contract only once `no-product-caller.sh` on the old interface exits 0 ⟦criterion 2⟧ ⟂ refactor pending
- [ ] `SKILL.md` spends one refactor of the budget for a whole phased step, not one per phase ⟦criterion 2⟧
- [ ] `SKILL.md`: a contract phase that exhausts `REVISE_BUDGET` is reset to its own base sha, the expand and migrate commits are kept, and the contract is filed under the ledger's `## Owed steps` ⟦criterion 2⟧
- [ ] `SKILL.md` accepts a `⟦replaces-case⟧` group step's Green only once the conductor's own run of `mutation-parity.sh` on that step's pairs table exits 0 ⟦criterion 3⟧
- [ ] `SKILL.md` accepts a contract (a) phase only once the conductor's own run of `mutation-parity.sh` on that phase's pairs table exits 0 ⟦criterion 3⟧
- [ ] `SKILL.md` puts `mutation-parity.sh`'s report into the PR body as the pairs table, and each row it reports `owed` into the PR body under `## Owed by a human` ⟦criterion 3⟧
