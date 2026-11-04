# Plan for #2928 — supervise.sh writes a launch event for a leaf whose prompt file is missing or empty, so the log shows a launch that never ran

- [x] supervise.sh given a run-leaf.sh launch whose prompt file exists but is empty exits 2, writes a launch-refused event naming the leaf, and writes no launch event; pinned by one case ⟦criterion 1⟧
- [x] supervise.sh given a run-leaf.sh launch whose prompt file does not exist exits 2, writes a launch-refused event naming the leaf, and writes no launch event; pinned by one case ⟦criterion 1⟧
- [x] supervise.sh given a launch whose command is not run-leaf.sh and whose first argument is an empty existing file launches the leaf normally, writing a launch event and no launch-refused event: the empty-prompt refusal applies to run-leaf.sh launches only; pinned by one case ⟦criterion 2⟧
- [x] supervise.sh given a run-leaf.sh launch with no prompt argument exits 2 with a message naming the missing prompt argument on stderr, not a traceback; pinned by one case ⟦criterion 3⟧
