# Plan for #3922 — PRD 023.2: CI starts with a warm bytecode cache

- [x] tests/py/unit/test_content_mtimes.py: `content_mtimes.py` run outside a git working tree exits 2 with one stderr line and changes no file ⟦criterion 2⟧
- [ ] tests/py/test_content_mtimes_process.py: `content_mtimes.py` sets the mtime of every file `git ls-files` lists to a value derived from that file's blob id: two clones holding the same content see equal mtimes per file, and a file changed in one sees a different mtime ⟦criterion 1⟧
- [ ] tests/py/test_content_mtimes_process.py: with sources stamped by `content_mtimes.py`, a test file and a `veri/` module each changed after their `.pyc` was cached run their new content in the next leg run, even when the new stamp equals the old one; watched to fail with the manifest check disabled ⟦criterion 3⟧
- [ ] tests/py/unit/test_workflow_bytecode_cache.py: `ci.yml`'s `gates` job runs `content_mtimes.py` after checkout and before `make test`, sets one fixed `VERI_PYCACHE`, restores it with `actions/cache` before `make test` under a key naming the runner OS and the Python version with a restore-keys fallback on that prefix, and saves it only on a push to `main` ⟦criterion 4⟧
- [ ] the comment above `ci.yml`'s cache steps says what is cached, why mtimes are set from content, and that only `main` saves ⟦criterion 5⟧
- [ ] CLAUDE.md's paragraph under the Commands table says CI restores the bytecode cache the last push to `main` saved; row CM84 added and `GRADED`'s `CLAUDE.md` line re-signed ⟦criterion 6⟧
