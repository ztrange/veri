# Plan for #339 — Migrate one script into the unit tier as the worked example for the pattern

Chosen script: `push-branch.sh` — 72 lines, and its integration suite `tests/push-branch.test.sh`
names git/gh/python3/sleep 61 times (the second-highest process-count proxy of any script's
suite; the highest, issue-worktree.sh, is 348 lines and not small).

- [x] push-branch.sh's logic runs from functions with a `main` entry, and the only top-level code executed when the file is run directly is `[[ "${BASH_SOURCE[0]}" == "$0" ]] && main "$@"`; sourcing it runs nothing ⟦criterion 2⟧
- [x] push-branch.sh's existing integration suite tests/push-branch.test.sh passes unmodified against the refactored script — same stdout, stderr and exit codes for every existing case ⟦criterion 3⟧
- [x] A new skills/tdd/scripts/tests/unit/push-branch.test.sh sources push-branch.sh (never execs it) and mocks git, sleep and the event recording as same-named shell functions, and passes with PATH set to a directory containing none of those binaries ⟦criterion 4⟧
- [x] The new unit suite's header comment records push-branch.sh as the chosen script and the reasoning as a process-count proxy, not measured seconds ⟦criterion 1⟧
- [x] Both the new unit suite and the untouched integration suite pass under `make test`, and the unit suite alone passes under `make unit` ⟦criterion 5⟧
- [x] CLAUDE.md's "Testing idiom" section documents the pattern (main guard, source, mock-as-function, unchanged CLI contract) naming push-branch.sh as the worked example, in wording a guard suite pins ⟦criterion 6⟧
- [ ] claude-md-counts.test.sh's suite-count assertions include the new unit suite file and still pass ⟦criterion 7⟧
