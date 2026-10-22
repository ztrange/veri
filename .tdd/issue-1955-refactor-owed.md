### `report-cache.sh refresh` with no cache yet, `gh` faked, writes `.tdd/report-cache.json` in the main working tree holding every issue, open and closed, each with its number, title, state, labels, `closedAt` and `updatedAt`, plus a top-level `fetched_at`, and exits 0 ⟦criterion 1⟧
- test-only | move the function-level `import json` and `import subprocess` in the refresh case to the module top
### `report-cache.sh refresh` run from a linked git worktree writes `.tdd/report-cache.json` under the repository's main working tree, not under the worktree it was run from ⟦added⟧ ⟦criterion 1⟧
- test-only | hoist the repeated `import json` / `import subprocess` and the fake `gh issue list` runner shared by the two refresh cases in `test_report_cache.py` into module-level imports and a helper
