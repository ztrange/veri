# Plan for #3980 — PRD 021.14: `queued-merge.sh` releases the lock when it crashes before the merge call

- [x] an exception escaping after the lock is taken and before the merge call (`gh pr view --json body` answering text that is not JSON) releases the lock once and exits 2 with one stderr line naming it in `entry.refusal`'s form ⟦criterion 1⟧
- [ ] a rebase stop and a refused push still exit with git's code and the lock kept, by the existing cases unchanged ⟦criterion 2⟧
- [ ] the `queued-merge.sh` entry of `skills/tdd/SCRIPTS.md` states the release on a crash before the merge call ⟦criterion 3⟧
