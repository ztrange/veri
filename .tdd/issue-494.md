# Plan for #494 — the comment sweep across the test suites

Scope: every shell file under `skills/tdd/scripts/tests/` — the `*.sh` files (top level, `unit/`, `fixtures/`) and the shims `unit-guard/git` and `offline/gh`. "The sweepable report" is `skills/tdd/scripts/comment-class.sh --sweepable <files>`; it is empty when it prints nothing.

- [x] The text of every class 3 `#` line in the suites (24 lines, in capture-spec, orchestrate, parallel-conductors, run-verdict, skill-refactor-pending and solvable-issues) is pinned, so a sweep that edits, moves or deletes one turns a suite red ⟦criterion 3⟧
- [x] comment-class.sh does not report a `#`-led line inside a multi-line single- or double-quoted string as a comment ⟦added⟧ ⟦criterion 1⟧
- [x] comment-class.sh --sweepable omits the `#!` line that opens a heredoc's body ⟦added⟧ ⟦criterion 1⟧
- [x] comment-class.sh classes a `#` line inside a heredoc written to a `.md` file as class 3 ⟦added⟧ ⟦criterion 1⟧
- [x] The sweepable report is empty for every top-level `tests/*.sh` whose name starts with a or b ⟦criterion 1⟧
- [x] The sweepable report is empty for every top-level `tests/*.sh` whose name starts with c or d ⟦criterion 1⟧
- [x] The sweepable report is empty for every top-level `tests/*.sh` whose name starts with e through j ⟦criterion 1⟧
- [x] The sweepable report is empty for every top-level `tests/*.sh` whose name starts with k through m ⟦criterion 1⟧
- [x] The sweepable report is empty for every top-level `tests/*.sh` whose name starts with n through r ⟦criterion 1⟧
- [ ] The sweepable report is empty for `tests/supervise.test.sh` and `tests/supervise-retry.test.sh` ⟦criterion 1⟧
- [ ] The sweepable report is empty for every top-level `tests/*.sh` whose name starts with s, other than the `skill-*` and `supervise*` files ⟦criterion 1⟧
- [ ] The sweepable report is empty for every top-level `tests/*.sh` whose name starts with t through z ⟦criterion 1⟧
- [ ] The sweepable report is empty for every `tests/skill-*.test.sh` whose name after `skill-` starts with a through l ⟦criterion 1⟧
- [ ] The sweepable report is empty for every `tests/skill-*.test.sh` whose name after `skill-` starts with m through z ⟦criterion 1⟧
- [ ] The sweepable report is empty for every shell file under `tests/unit/` and `tests/fixtures/`, and for `tests/unit-guard/git` and `tests/offline/gh` ⟦criterion 1⟧
- [ ] No class 1 comment line in any shell file under `skills/tdd/scripts/tests/`, a leading contract header included, cites an issue number (`#<digits>`), so headers keep the contract and drop the rationale ⟦criterion 1⟧
- [ ] Class 2 lines are swept only where the writing suite stays green: `make test` passes on the swept tree ⟦full-suite⟧ ⟦criterion 2⟧
- [ ] Every suite still ends with its count line, and `make test` is green ⟦full-suite⟧ ⟦criterion 4⟧

## Owed steps

- a tab-indented `#!` opening a `<<-` heredoc body is omitted from the sweepable report, since bash strips the tabs before writing it
