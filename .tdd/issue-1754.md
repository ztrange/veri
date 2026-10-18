# Plan for #1754 — A develop-green refused by supervise.sh hangs the conductor: wait-leaf.sh never sees the exit 2

- [ ] A develop-green launch supervise.sh refuses for a step with no verify-red PASS after its latest red leaf, run detached through detach-leaf.sh, records exit 2 where wait-leaf.sh reads it: wait-leaf.sh develop-green returns 2, not 3, and no leaf is started ⟦criterion 1⟧
