# Plan for #2922 — A revised beside phase gets no test-freeze rule, though the freeze check rejects a beside commit that touches tests

- [ ] `build-develop-prompt.sh revise dual-stub …` prints the `_develop-revise-freeze-production.md` rule and not the `_develop-revise-freeze-test.md` rule (a pin guarding the fix against widening the wrong tuple; no production change) ⟦criterion 2⟧
- [ ] `build-develop-prompt.sh revise beside …` prints the `_develop-revise-freeze-test.md` rule ("Redoing an interface phase freezes the test files") and not the `_develop-revise-freeze-production.md` rule ⟦criterion 1⟧
- [ ] _develop-revise-freeze-test.md's second sentence names beside among the phases whose redone commit the conductor's freeze check rejects: a redone expand, beside, migrate or contract-b that touches a test file (FT2), in skills/tdd/scripts/prompts/_develop-revise-freeze-test.md ⟦skill-edit⟧ ⟦criterion 3⟧
