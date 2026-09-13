# Plan for #157 — make test fails a suite that never reached its count line, even when it exits 0

- [x] A suite that dies from an unbound variable inside a numeric comparison after its first case, and exits 0, makes `make test` exit non-zero and names that suite
- [x] A suite that ends in its count line with `0 failed` and exits 0 still passes, and a suite that prints its count line but exits non-zero still fails
- [x] A suite added under `skills/tdd/scripts/tests/` gets the check with no edit to the runner
- [x] `make test`'s output still shows each suite's lines as they are printed, not only after the suite ends
- [ ] CLAUDE.md "Testing idiom" says the runner enforces the count line, and why an exit code alone is not trusted
