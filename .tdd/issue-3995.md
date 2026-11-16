# Plan for #3995 — PRD 021.5: `merge-lock.sh take` gives up after a bound

- [x] `merge-lock.sh take`, once `VERI_MERGE_LOCK_WAIT` seconds have passed while another holder's lock stands, exits 2 with one stderr line naming the holder record and the limit, the lock directory and record in place and no `.merge.lock.*` staging directory left ⟦criterion 1⟧
- [x] `VERI_MERGE_LOCK_WAIT` is a `TUNABLES` entry defaulting to `1800` ⟦criterion 3⟧
- [x] a `VERI_MERGE_LOCK_WAIT` that is not a non-negative whole number makes `take` exit 2 naming the variable before it creates or reads anything, and `0` gives up at the first poll that finds the lock held ⟦criterion 3⟧
- [x] `skills/vmerge/SKILL.md` says a non-zero `take` means the lock was not taken, and the `merge-lock.sh` entry of `SCRIPTS.md` states the bounded wait, its knob and default ⟦criterion 5⟧ ⟦criterion 6⟧
