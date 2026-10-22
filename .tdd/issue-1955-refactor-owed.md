### `report-cache.sh refresh` with no cache yet, `gh` faked, writes `.tdd/report-cache.json` in the main working tree holding every issue, open and closed, each with its number, title, state, labels, `closedAt` and `updatedAt`, plus a top-level `fetched_at`, and exits 0 ⟦criterion 1⟧
- test-only | move the function-level `import json` and `import subprocess` in the refresh case to the module top
