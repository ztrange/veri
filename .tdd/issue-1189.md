# Plan for #1189 — detach-leaf.sh starts its command with SIGXFSZ ignored

- [ ] A command started by detach-leaf.sh has SIGXFSZ at its default disposition: past a `ulimit -f` it dies of SIGXFSZ rather than getting EFBIG ⟦criterion 1⟧
