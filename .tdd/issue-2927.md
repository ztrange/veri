# Plan for #2927 — A developer or revise leaf can rewrite the committed mutation record, which only mutation-probe should write

- [x] After a `develop-*` or `revise-*` leaf launched through `supervise.sh` exits, a `.tdd/issue-*-mutations.md` the leaf rewrote (its content changed, truncated or appended to) is byte-identical to what it held before the leaf ⟦criterion 1⟧
- [ ] After a `develop-*` or `revise-*` leaf launched through `supervise.sh` exits, a `.tdd/issue-*-mutations.md` the leaf deleted is restored, byte-identical to what it held before the leaf ⟦criterion 1⟧
- [ ] After a `develop-*` or `revise-*` leaf launched through `supervise.sh` exits, a `.tdd/issue-*-mutations.md` that did not exist before the leaf and that the leaf created is removed ⟦criterion 1⟧
- [ ] When the supervisor restores or removes a `.tdd/issue-*-mutations.md` after a `develop-*` or `revise-*` leaf, it writes one event per restored file naming the leaf and the file ⟦criterion 1⟧
- [ ] A verify-pin verifier leaf launched through `supervise.sh` whose probe appends its record to `.tdd/issue-<n>-mutations.md` keeps that append after it exits, with no restore event (#2741's append-only rule unaffected) ⟦criterion 2⟧
