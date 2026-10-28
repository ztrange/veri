# Plan for #2579 — restore-production.sh deletes more than production, is not atomic, and its only failure path is unpinned

- [x] restore-production.sh exits 2 with git's stderr when git refuses its checkout (run outside a git repository), pinned by a case in skills/tdd/scripts/tests/py/test_restore_production_process.py that fails when the return-code check in veri/restore_production.py is removed ⟦criterion 1⟧
- [x] When git clean fails after a successful git checkout, restore-production.sh exits 2 and names a partial restore on stderr — production reverted, untracked files not removed — distinguishable from having done nothing ⟦criterion 2⟧ ⟂ refactor pending
- [ ] restore-production.sh never reverts or deletes a ledger .tdd/issue-*.md or any */GRADED, whatever paths the caller passes: with both left dirty, they are untouched after the script runs ⟦criterion 3⟧
- [ ] restore-production.sh refuses a pytest node id argument (<file>::<case>) with exit 2 and restores nothing ⟦criterion 4⟧
- [ ] restore-production.sh refuses an argument carrying a pathspec magic prefix such as :(bogus)x with exit 2 and restores nothing ⟦criterion 4⟧
- [ ] Run from a subdirectory of the worktree, restore-production.sh restores the whole worktree or refuses with exit 2, never restores only the subtree and exits 0 ⟦criterion 5⟧
- [ ] An untracked test file the Red leaf wrote outside the named test path (a file under a tests/ directory) survives restore-production.sh ⟦criterion 6⟧
- [ ] Go-red control: with the return-code check in veri/restore_production.py reverted, the first criterion's case goes red — watched red by hand and restored ⟦human-owed⟧ ⟦criterion 7⟧
