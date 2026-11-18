# Plan for #4373 — merge-lock.sh gate runs its command without checking the caller holds the lock

- [x] `gate` with no lock exits 2 and does not run `<cmd>` ⟦criterion 1⟧
- [x] `gate` with a lock held by another pid or another owner exits 2, does not run `<cmd>`, and names the holder on stderr ⟦criterion 2⟧
- [x] `gate` by the holder runs `<cmd>` as today: its exit code, a release on failure, and `--keep` ⟦criterion 3⟧
- [ ] ⟦skill-edit⟧ `skills/tdd/SCRIPTS.md` states SC593: `gate` exits 2 without running `<cmd>` when the lock is absent or held by another pid or owner, naming the holder
- [ ] ⟦skill-edit⟧ `skills/vmerge/SKILL.md` states M44: a `gate` refused with exit 2 for not holding the lock ran nothing, and the merge stops there as for a failed `take`
