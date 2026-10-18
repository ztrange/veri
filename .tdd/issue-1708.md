# Plan for #1708 — The conductor spends a whole turn re-calling wait-leaf.sh every 540 s while a leaf runs

The harness limit this plan names: a foreground Bash call lasts at most 600 s (600000 ms), and a conductor may not end its turn while a leaf runs, so one wait can cost no fewer than one call per ~590 s of leaf time.

- [x] wait-leaf.sh called with no max-seconds argument keeps waiting until 590 s have passed (the most that fits inside the Bash tool's 600 s cap on one foreground call) before it exits 3; a small pytest case with a faked clock, no real wait ⟦criterion 1⟧
- [x] SKILL.md tells the conductor to make every foreground wait-leaf.sh call with no max-seconds argument and the Bash tool's maximum timeout of 600000 ms, naming the 600 s foreground cap as the limit that makes a wait cost one call per 590 s and no fewer; a small pytest case over SKILL.md's text ⟦criterion 1⟧
- [x] wait-leaf.sh waiting with its default budget exits 0, 1 or 2 as soon as the supervisor records that code, and exits 2 once the supervisor dies without recording one, never 3 while an answer is available; a small pytest case with a faked clock ⟦criterion 2⟧
- [x] detach-command.sh wait called with no max-seconds argument keeps waiting until 590 s have passed before it exits 3; a small pytest case with a faked clock, no real wait ⟦criterion 3⟧
- [ ] SKILL.md's full-suite and baseline waits call detach-command.sh wait with no max-seconds argument and the Bash tool's 600000 ms timeout, never a fixed 500; a small pytest case over SKILL.md's text ⟦criterion 3⟧
