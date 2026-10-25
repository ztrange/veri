### A queued merge stopped by a rebase conflict onto origin/main exits 1 and keeps the merge lock held; gh and git faked ⟦criterion 1⟧
- extract a shared `_gate(pid, *cmd, keep=False)` helper for the two `merge-lock.sh gate` calls in `queued_merge.py` (only two uses, so not worth it yet)
applied | 072ee09e16d9f81b97d47fbc3da0a7ad958e93a1 | extract a shared `_gate(pid, *cmd, keep=False)` helper for the two `merge-lock.sh gate` calls in `queued_merge.py` (only two uses, so not worth it yet)	refactor: _gate takes the command as varargs (#2372)
