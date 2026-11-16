# Plan for #3990 — PRD 021.11: `dispatch.sh` keeps running when the rate-limit reset cannot be read

- [ ] with a rate-limited queue read and an unreadable reset, `dispatch.step` raises and exits nothing, prints one stderr line saying the reset could not be read, reads no queue for `VERI_DISPATCH_OVERLAP_POLL` seconds, and launches once the clock has passed it ⟦criterion 1⟧
- [ ] the `dispatch.sh` entry of `SCRIPTS.md` states the pause on an unreadable reset ⟦criterion 3⟧
