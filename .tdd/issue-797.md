# Plan for #797 — a port plan pins the branches a step brings in before or with that step, not after it

- [x] SKILL.md's "2. Scope & plan → the ledger" section states that a step bringing in code (a port step, a new module) either comes after the steps that pin every branch it brings in, or brings in only the branches its own test requires, the rest arriving with the steps that pin them ⟦criterion 1⟧ ⟂ refactor pending
- [ ] prompts/verify-plan.md directs a REJECT for a plan whose step introduces a branch (for example a fallback forced by an existing suite) that only a later step's test requires, and requires the REJECT reason to name both the introducing step and the later pinning step ⟦criterion 2⟧
- [ ] prompts/verify-plan.md states that a plan whose step bringing in code comes after the steps pinning its branches, or brings in only the branches its own test requires, is not a REJECT on ordering grounds ⟦criterion 3⟧
- [ ] every plan shape the existing verify-plan cases cover is judged as before: the existing build-verify-prompt.test.sh and skill-plan-verify.test.sh cases stay green ⟦full-suite⟧ ⟦criterion 3⟧
