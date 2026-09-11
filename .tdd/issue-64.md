# Plan for #64 — Validate the count argument of refactor-budget.sh and fail closed with exit 2

- [x] a non-numeric, negative or missing count (`abc`, `-1`, no argument) each exit 2, print a diagnostic to stderr, and print nothing to stdout
- [x] a decimal count (`1.5`) exits 2 with a diagnostic on stderr and nothing on stdout, instead of exit 3 plus a shell syntax error
- [ ] the valid counts 0, 1 and 2 keep their current answers — exit 0, 0, 3 with a one-line status on stdout
