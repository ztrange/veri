# Plan for #3994 — PRD 021.13: a dead merge-lock holder is handled at once

- [ ] `merge-lock.sh take` on a holder record whose pid is dead exits 2 with no poll wait, one stderr line `stale lock: <record>` naming `merge-lock.sh release --force`, the lock directory and record in place and no `.merge.lock.*` staging directory left ⟦criterion 1⟧
- [ ] `take` on a holder pid alive under a different start time than its record's exits 2 the same way, with no poll wait ⟦criterion 2⟧
- [ ] `queued-merge.sh`, its `take` exiting 2 on a stale holder, exits 2 naming the failed take, with no fetch, push or merge call and no release ⟦criterion 5⟧
- [ ] the `merge-lock.sh` entry of `SCRIPTS.md` adds the dead or reused holder to `take`'s exit 2 ⟦criterion 6⟧
