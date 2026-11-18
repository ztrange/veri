# Plan for #4303 — supervise tracks the launching leaf and held signal in a named holder, not a sentinel list

- [x] a signal after a failed launch exits 2 at once, killing nothing
- [x] a signal during a retry's launch is held, then kills only the new leaf
- [x] attempt_once and trap share a named launch holder: no started list sentinels ⟦diff-checked⟧ ⟦criterion 1⟧
- [x] on_signal tells launching from a live leaf with no isinstance test on the holder ⟦diff-checked⟧ ⟦criterion 2⟧
- [x] a signal during launch is still held and raised once the leaf exists, and one with a live leaf still kills its tree ⟦criterion 3⟧
- [ ] exit codes, .rc and .pid files and events unchanged; make test green ⟦full-suite⟧ ⟦criterion 4⟧
