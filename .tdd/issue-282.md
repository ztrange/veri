# Plan for #282 — make test spends most of its 155 s sleeping: supervise.sh polls and heartbeats in whole seconds

- [x] supervise.sh on a sub-second clock: with fractional VERI_HEARTBEAT/VERI_TIMEOUT/VERI_POLL, a stub leaf that stops writing is killed as stuck and one that keeps writing is not ⟦criterion 3⟧
- [x] wait-leaf.sh accepts a fractional VERI_POLL and returns the recorded code within tens of milliseconds of the completion file landing ⟦criterion 2⟧
- [ ] with no tunables set supervise.sh, wait-leaf.sh and verify.sh keep default heartbeat 180 s, poll 1 s, and a malformed tunable value is still exit 2 ⟦criterion 4⟧
- [ ] verify.test.sh and supervise.test.sh run on the fast clock and together take at most 20 s, with no case removed and every assertion kept ⟦criterion 1⟧
- [ ] wait-leaf.test.sh, detach-leaf.test.sh and hermetic-suites.test.sh each take at most 3 s, with no case removed and every assertion kept ⟦criterion 2⟧
- [ ] hermetic-suites.test.sh still passes: no suite depends on an ambient VERI_* value to be fast ⟦criterion 5⟧
