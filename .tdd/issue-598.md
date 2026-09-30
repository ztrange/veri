# Plan for #598 — a suite-run artifact, skills/tdd/scripts/.tdd/events.jsonl, is tracked in git and dirties the tree

- [x] A suite's tracked-artifact check names the path of any tracked file under a nested `.tdd/` directory (the place a suite run writes its event log) and goes red on a planted one ⟦criterion 2⟧
- [x] No file under a nested `.tdd/` directory is tracked on the branch (`skills/tdd/scripts/.tdd/events.jsonl` and `skills/tdd/scripts/tests/.tdd/events.jsonl` are untracked) and git ignores what a suite run writes there, so `git status --porcelain` stays empty ⟦criterion 1⟧
- [x] Repair the red full suite: claude-md-counts.test.sh — FAIL - CLAUDE.md's stated script and suite counts match the scripts and suites on disk (CLAUDE.md says the *Testing idiom* suite count is '127'; there are 128 on disk, since no-tracked-artifacts.test.sh was added) ⟦added⟧ ⟦criterion 1⟧ ⟂ refactor pending
- [ ] `git status --porcelain` is empty after a full `make test` ⟦full-suite⟧ ⟦criterion 1⟧
