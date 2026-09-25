# Plan for #391 — SCOPE-LOOP.md: a stopped issue stops the loop

- [x] SCOPE-LOOP.md's Loop 4 stop conditions list an issue that ended in a stop, and say the loop then reports and stops without going back to Loop 1 or selecting another issue ⟦criterion 1⟧
- [x] SCOPE-LOOP.md says a stop, unlike a bail, has no continue-past option — no --continue-on-bail equivalent, because a stop is the operator speaking ⟦criterion 2⟧
- [ ] SCOPE-LOOP.md's Loop 5 report gives a stopped issue a `stopped: <mode>` per-issue line alongside the PR url, bailed and skipped forms, and names the stop and the stopped issue's mode as what stopped the loop ⟦criterion 3⟧
- [ ] SCOPE-LOOP.md says re-invoking the same command after a stop resumes the stopped issue from its committed ledger and then carries on draining the scope
