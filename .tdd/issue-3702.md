# Plan for #3702 — park-issue.sh: a malformed --blocked-by names the one-number form, not the comma list

- [ ] A malformed `--blocked-by` value (e.g. `x9`) makes `park-issue.sh` exit 2 with a stderr message naming the comma-separated `<n>[,<n>…]` form rather than "takes one issue number, once"; a new case in `skills/tdd/scripts/tests/py/unit/test_park_issue.py` pins that message and fails on the current code ⟦criterion 1⟧
