# Plan for #389 — SKILL.md's stop checkpoints: where the conductor looks, and clearing a stale request at claim time

- [x] SKILL.md's *Launching a leaf* runs `stop-requested.sh` before every leaf launch: exit 3 launches as normal, mode `at-ledger` launches the leaf anyway, and modes `at-leaf` and `now` launch nothing and go to *Stopping* ⟦criterion 1⟧
- [x] SKILL.md runs `stop-requested.sh` immediately after the atomic green commit's push and stops there on any mode ⟦criterion 2⟧
- [x] SKILL.md runs `stop-requested.sh` immediately after the refactor-pending clear's push, and after a pin's `test:` commit, and stops there on any mode ⟦criterion 2⟧
- [x] SKILL.md treats `stop-requested.sh` exit 2 as a stop in mode `at-ledger`, narrating that the request was unreadable ⟦criterion 3⟧
- [x] SKILL.md's three ledger-commit checkpoints (the green push, the refactor-pending clear, the pin's `test:` commit) send a `stop-requested.sh` exit 2 found there to *Stopping* as `at-ledger`, narrating that the request was unreadable ⟦added⟧ ⟦criterion 3⟧
- [x] SKILL.md asks `stop-requested.sh` before reading a leaf's `wait-leaf.sh` exit 2 as `killed-stuck`, and a pending `now` sends the run to *Stopping* instead of *Bailing* ⟦criterion 4⟧ ⟂ refactor pending
- [ ] SKILL.md's *Bailing* keeps a bail condition reached first — a `REJECT` exhausting `REVISE_BUDGET`, or a killed-stuck leaf with no `now` pending — as a bail, and its bail comment says a stop was pending when one was
- [ ] SKILL.md's Draft PR step runs to completion with a stop request pending, clears it with `stop-requested.sh --clear`, and says in the final `### ✅ Done` comment that a stop arrived after the last step ⟦criterion 5⟧
- [ ] SKILL.md checkpoints the repair step a red full run appends at the Draft PR step like any other step — both checkpoints apply to it ⟦criterion 5⟧
- [ ] SKILL.md's step 1.2 runs `stop-requested.sh --clear` beside the `.tdd/conductor.pid` write, so a stale request from a killed run cannot stop the run that resumes it ⟦criterion 6⟧
