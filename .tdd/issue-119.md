# Plan for #119 — Docs guard suite: run one case by name, and print each case as it passes with its duration

- [x] `ONLY=<substring> docs/tests/build-guards.test.sh` runs only the cases whose name contains the substring, builds nothing for the rest, and finishes in seconds — pinned by a suite that runs under `make docs-test`
- [x] an `ONLY` value that matches no case exits 3, says so, and runs no case
- [ ] every passing case prints one `ok - <name> (<n>s)` line as it passes, in order, beside the existing `FAIL - <name>` lines and the final count line
- [ ] a failing case still makes `make docs-test` exit non-zero, and `docs/tests/merge-gates.test.sh` still passes
