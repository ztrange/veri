# Plan for #3331 — pin_recheck applies a pin's mutant to any matching text, so a moved or duplicated match silently disarms the pin

- [x] pin-recheck.sh reports a mutation pin whose old text occurs more than once in its file with a `needs a look` line and does not mutate the file; reproduced by a fixture holding the old text twice in one file, which fails on the current code (it mutates every occurrence) ⟦criterion 1⟧
- [x] pin-recheck.sh still mutates and replays a pin whose record carries a `context` field equal to the one line holding its old text, which occurs exactly once (no `needs a look` line, the replay's outcome reported as before) ⟦criterion 4⟧
- [x] pin-recheck.sh reports a pin whose old text occurs exactly once but not on a line equal to its recorded `context` as moved with a `needs a look` line and does not mutate the file; reproduced by a fixture whose recorded site was refactored away, the same text left on an unrelated line ⟦criterion 2⟧
- [x] mutation-probe.sh records a `context` field with each mutation pin: the full source line holding the old text ⟦criterion 3⟧
- [x] pin-recheck.sh gives a mutation record written without a `context` field the duplicate check only: its old text occurring twice is reported with a `needs a look` line and not mutated ⟦criterion 3⟧
