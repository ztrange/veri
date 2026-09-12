# Plan for #86 — Wait for supervised leaves in the foreground so print-mode conductors never orphan a leaf

- [x] supervise.sh records its own final status code (0 success, 1 leaf-failure, 2 killed-stuck) in a completion file at .tdd/<name>.exit, written for a killed-stuck leaf too
- [x] wait-leaf.sh <name> exits with the recorded supervisor code as soon as the completion file appears, including when a stub writes that file a second or two after the wait starts
- [ ] wait-leaf.sh <name> 1 exits 3 when no completion file appears within the budget, and its default budget is at most 540 seconds
- [ ] wait-leaf.sh <name> exits 3, never 0, when there is no completion file and no leaf running
- [ ] SKILL.md prescribes the detached launch plus wait-leaf.sh foreground wait for every leaf launch, and warns that a background Bash call awaiting a notification never completes in print mode
