# Plan for #3134 — Two merges driven from one session exclude each other on the merge lock

- [ ] The owner releases: with the merge lock taken by `take --pid <pid> --owner <token A>`, `release --pid <pid> --owner <token A>` exits 0 and the lock is free (`holder` exits 3) ⟦criterion 2⟧
- [ ] With the merge lock taken by `merge-lock.sh take --pid <pid> --owner <token A>`, a `release --pid <same pid> --owner <token B>` exits 1 and leaves the lock held, `holder` still naming the first taker ⟦criterion 1⟧
- [ ] With the merge lock taken by `take --pid <pid> --owner <token A>`, a `release --pid <same pid>` given no `--owner` exits 1 and leaves the lock held ⟦criterion 1⟧
- [ ] With the merge lock taken by `take --pid <pid> --owner <token A>`, a `gate --pid <same pid> --owner <token B> -- <cmd exiting 1>` exits 1 and leaves the lock held by the first taker ⟦criterion 1⟧
- [ ] While the merge lock is held by `take --pid <pid> --owner <token A>`, a second `take --pid <same pid> --owner <token B>` does not return: it keeps waiting with the first taker's lock in place ⟦criterion 1⟧
- [ ] The owner's failed gate releases: with the merge lock taken by `take --pid <pid> --owner <token A>`, `gate --pid <pid> --owner <token A> -- <cmd exiting 1>` exits 1 and the lock is free ⟦criterion 2⟧
- [ ] A `take` waiting on a lock taken with `--owner <token>` by a pid now dead reports `stale lock:` with the holder record on stderr and keeps waiting with the lock in place ⟦criterion 3⟧
- [ ] A lock taken with `--owner <token>` by a pid now dead is freed by `release --force` (exit 0, `holder` exits 3) ⟦criterion 3⟧
- [ ] skill-edit of skills/vmerge/SKILL.md: a merge takes, gates and releases the merge lock under an owner token of its own (`--owner`, one per merge), so two merges driven from one session exclude each other, with its REQUIREMENTS.md rows M4 and M15 updated ⟦skill-edit⟧ ⟦criterion 1⟧
- [ ] skill-edit of skills/tdd/SCRIPTS.md: the `merge-lock.sh` entry documents `--owner <token>` on take, release and gate, and that a release or failed gate by a different owner (or none) of a lock taken with an owner exits 1 and frees nothing ⟦skill-edit⟧ ⟦criterion 1⟧
