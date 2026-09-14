# Plan for #143 — No docs test runs during veri development: dev suites never read docs/, and docs targets refuse inside a development run

- [x] a suite under `skills/tdd/scripts/tests/` that reads, sources, executes or greps a path under `docs/` is named with its line by a new guard case, while a `docs/` path appearing only in fixture text is not
- [x] no suite under `skills/tdd/scripts/tests/` reads a path under `docs/`, so changing only `docs/wt/commentary.py` leaves `make test` green
- [x] changing only a script under `skills/tdd/scripts/`, without running `make docs`, leaves `make test` green
- [x] changing `VERI_REFACTOR_BUDGET`'s default without updating `SKILL.md` or the script header still turns `make test` red
- [x] with `VERI_TEST_CMD='make test'`, each of `make docs`, `make docs-test`, `make docs-check` and `make docs-fresh` exits 2 without running anything, and says why on stderr
- [x] with `VERI_TEST_CMD` unset, or set to `make docs-test`, those four targets run as before
- [x] a leaf launched through `supervise.sh` the way `SKILL.md` prescribes sees `VERI_TEST_CMD` in its environment, pinned with a `CLAUDE_BIN` stub
- [ ] `build-verify-prompt.sh` accepts the same arguments as before
- [ ] CLAUDE.md states the rule and where docs checks live
