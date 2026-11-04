# Plan for #2928 — supervise.sh writes a launch event for a leaf whose prompt file is missing or empty, so the log shows a launch that never ran

- [x] supervise.sh given a run-leaf.sh launch whose prompt file exists but is empty exits 2, writes a launch-refused event naming the leaf, and writes no launch event; pinned by one case ⟦criterion 1⟧
- [ ] supervise.sh given a run-leaf.sh launch whose prompt file does not exist exits 2, writes a launch-refused event naming the leaf, and writes no launch event; pinned by one case ⟦criterion 1⟧
