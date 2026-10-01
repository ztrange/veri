# Plan for #612 — claude-md-guards-green checks the four CLAUDE.md guards are in make test's roster, without running them a second time

- [x] claude-md-guards-green.test.sh fails, naming the missing guard, when a planted `make -n test` roster lacks any one of the four CLAUDE.md guards ⟦criterion 1⟧
- [x] claude-md-guards-green.test.sh fails when `make -n test` names no suite at all ⟦criterion 2⟧
- [x] claude-md-guards-green.test.sh starts none of the four guard suites as a child process, and passes on a roster holding all four even when a guard itself would fail ⟦criterion 3⟧
- [ ] claude-md-guards-green.test.sh's header states that it pins the four guards' presence in `make test`'s roster and why the re-run was dropped, and states no cost in seconds ⟦criterion 4⟧
- [ ] the four guard suites are unchanged and still in `make test`'s roster ⟦full-suite⟧ ⟦criterion 5⟧
