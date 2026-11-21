# Plan for #4479 — A stale green-half wait record left by a revised step is loaded by a later step, which ticks on the old verdict

- [x] `green-half.sh` run on open step B, with a green-half wait record naming step A saved at `verdict-green` and step A's `.tdd/verdict-green.exit` (0) on disk, ignores that record: it launches develop-green for step B and never reads step A's `verdict-green.exit` ⟦criterion 1⟧ ⟂ refactor pending
- [ ] `green-half.sh` run on open step B, with a green-half wait record naming step B itself saved at `verdict-green`, still resumes at its verdict: it launches no develop-green and finishes on that verdict ⟦criterion 1⟧
- [ ] The green-half wait record `revise.sh <n> green` re-saves on its PASS is not loaded by `green-half.sh` once a later step is the open one: after step A's revised PASS is closed per REVISE.md (step A ticked), `green-half.sh` on step B launches develop-green for step B ⟦criterion 2⟧
