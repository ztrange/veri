# Plan for #164 — merge-gates owes docs-fresh for any Makefile change, so a development PR's merge waits on the docs page

- [ ] On a branch whose only change against `origin/main` is `Makefile`, `make merge-gates` runs no gate, says there is nothing to run, and exits 0, even when the committed page is stale
- [ ] A branch that changes `Makefile` and a script under `docs/` still runs `docs-test` and `docs-fresh`
- [ ] A hand-edited `docs/walkthrough.html` still owes `docs-fresh`
- [ ] `CLAUDE.md`'s `make merge-gates` row and the header of `docs/merge-gates.sh` no longer name a `Makefile` change as owing `docs-fresh`
