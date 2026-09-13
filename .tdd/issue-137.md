# Plan for #137 — Docs gates stay in the docs lane: no docs suite in make test, docs-test never judges the committed page, merge-gates runs every docs suite for a docs change

- [ ] a new file under `docs/tests/` runs under `make docs-test` with no Makefile edit (docs-test globs `docs/tests/*.test.sh`)
- [ ] `docs-gap-adr.test.sh` lives in `docs/tests/` and runs under `make docs-test`, its header's rationale updated, and `make test` runs no file whose subject is the docs pipeline
- [ ] `docs-owed.test.sh` asserts docs-owed.sh's zero-debt exit against a sandbox it builds, not the real tree, so a script change leaving lines uncovered or a new tag leaves that suite green
- [ ] the generator's suite no longer judges the committed page: `page_is_current` and `page_checks_out` leave `make docs-test`, so a tag or an uncovered-line script commit leaves `make docs-test` green
- [ ] `make merge-gates` on a branch changing anything under `docs/` except `docs/walkthrough.html` alone (e.g. only `docs/docs-owed.sh`) runs every docs suite plus docs-fresh, pinned in `docs/tests/merge-gates.test.sh`
- [ ] `make merge-gates` on a branch changing `docs/wt/` still fails on a stale page
- [ ] CLAUDE.md (Commands, Testing idiom) and the `Makefile` / `docs/merge-gates.sh` headers say where each suite lives and which gate runs it, including the widened merge-gates selection
