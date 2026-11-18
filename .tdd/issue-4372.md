# Plan for #4372 — A successful merge-lock take deletes the owner tokens of merges still waiting

- [ ] a successful `take` leaves the token file of another owner that is still waiting on the lock in place ⟦criterion 1⟧
- [ ] `release` by the owner still removes the releaser's own token file, while a waiting owner's token file stays ⟦criterion 2⟧
- [ ] a `take` that finds the lock held by a dead or reused holder removes the token file holding that holder's owner, and only that one ⟦criterion 3⟧
- [ ] a `take` whose read of the holder's start time fails removes no token file
- [ ] ⟦skill-edit⟧ `skills/tdd/SCRIPTS.md` states SC575: a successful `take` leaves waiting owners' token files and removes only a dead or reused holder's
- [ ] ⟦skill-edit⟧ `skills/vmerge/SKILL.md` states M39: a waiting merge's token file survives another merge's `take`
