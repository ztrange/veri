# Plan for #39 — detect-test-command.sh: the test command is detected by a script, and covers more than four stacks

- [x] a .veri/test-command override wins over every inference and is printed verbatim
- [x] package.json with a test script yields npm test, or pnpm test / yarn test when the matching lockfile is present
- [x] a Makefile with a test: target yields make test, and beats a pytest marker present in the same repo
- [x] pytest.ini or a [tool.pytest section in pyproject.toml yields pytest -q
- [x] go.mod yields go test ./... and Cargo.toml yields cargo test
- [x] a tests/ directory of test_*.py with no other marker yields python3 -m unittest discover -q
- [ ] a repo matching nothing prints nothing and exits 3
