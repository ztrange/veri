# Plan for #1200 — supervise.sh takes owner pid 0 in .tdd/leaf.owner as a live leaf for ever

- [ ] An owner pid in .tdd/leaf.owner that is not a whole number of at least 1 (0, or a negative number) is never taken as a live leaf: supervise.sh treats the owner file as stale and launches the new leaf ⟦criterion 1⟧
