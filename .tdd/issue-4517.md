# Plan for #4517 — PRD 042.2: a test caps CLAUDE.md's bytes

- [x] the cap check, handed a text at or under the cap, reports no failure ⟦criterion 2⟧
- [x] the cap check, handed a text over the cap, fails naming the text's size in bytes, the cap, and the `##` section whose byte count grew most over its recorded baseline ⟦criterion 1⟧
- [x] the test file holds the cap as one constant, 19215 + 1000 B (root `CLAUDE.md` on branch base 8cc6b5d1bc), beside a per-`##`-section byte baseline from the same commit, and a case run against the real root `CLAUDE.md` passes on the tip and goes red with the cap below its size (watched, restored); no git, network, subprocess, `sleep`, `process` or `tree_audit` mark ⟦criterion 3⟧ ⟦criterion 4⟧ ⟦criterion 5⟧
