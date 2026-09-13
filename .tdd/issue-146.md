# Plan for #146 — Docs lane holds the docs facts make test guards today, and an ADR-only docs/ change owes no docs gate at merge

- [x] `make docs-test` turns red, naming the file and the figure, when the VERI_HEARTBEAT or VERI_REFACTOR_BUDGET default stated in `docs/wt/commentary.py` disagrees with the script that encodes it
- [x] `make docs-test` turns red when `docs/build-walkthrough.py`'s or `docs/check-walkthrough.py`'s `SCRIPTS_DIR` names another directory, or the commentary documents a script that does not exist
- [x] A fact about the committed page's own content — an old command name, a script's quoted line count — is reported by the docs lane's page check, not by `build-guards.test.sh`
- [x] `make merge-gates` runs no docs gate for a branch whose changes are only under `skills/` and `docs/adr/`, pinned in `docs/tests/merge-gates.test.sh`, with the `docs/merge-gates.sh` header and the CLAUDE.md merge-gates row saying why
- [ ] `make merge-gates` on a branch changing `docs/wt/` still runs every docs suite and `docs-fresh`
- [ ] The other committed-page fact of the table's fourth row — the page naming an old command — has a docs-lane home too, so #143 deletes no unguarded fact
