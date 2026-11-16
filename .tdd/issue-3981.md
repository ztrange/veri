# Plan for #3981 — PRD 021.4: cutting the tag cannot stop the cleanup

- [ ] in a clone holding v1.2.3, release-1 and v0.10, queued-merge.sh cuts v0.11 ⟦criterion 1⟧
- [ ] in a clone holding only release-1, no tag is cut, stderr says no vN.M tag to bump from; no tag cut, the cleanup runs and the exit is 2 naming tag ⟦criterion 2⟧
- [ ] an exception raised while cutting the tag counts as the tag step failing: every later cleanup step runs and the exit is 2 with merged, but cleanup failed: tag ⟦criterion 3⟧
- [ ] the queued-merge.sh entry of SCRIPTS.md states the tag set and the failure handling (SC158) ⟦criterion 4⟧
