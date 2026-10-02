# Plan for #692 — status.sh's port tests assert exit codes and behaviour through main, with no new implementation cases

- [x] the pytest replacements for pairs #4 (a run ending in a stop mark, text and --json) and #13 (a run directory is one run, text and --json) assert veri.status.main's return code, 0, as the removed bash cases asserted status.sh's exit code ⟦criterion 1⟧
- [x] the pytest replacements for pairs #8 (--scope counts what solvable-issues.sh lists) and #10 (--json emits scope.solvable as a number) assert veri.status.main's return code, 0, as the removed bash cases asserted status.sh's exit code ⟦criterion 1⟧
- [x] a pytest case run through veri.status.main renders a ledger holding a stray checkbox line outside its steps with the step count of the ledger's steps alone, the stray line not counted ⟦criterion 2⟧
- [x] no case in test_status.py calls a function of veri.status other than main: the run_activity, scope_totals and run_object cases assert their behaviour through veri.status.main(argv), or are removed where an existing main case already asserts it ⟦criterion 3⟧
- [ ] the four "is a module of scripts/veri/" bash cases (tier-usual.test.sh, blocked-by.test.sh, json-documents.test.sh, leaf-log.test.sh) and test_status.py's decoy veri/event_log.py case are gone, while each suite's output and exit-code cases remain ⟦criterion 4⟧
- [ ] status.test.sh no longer carries the dead line counted="$(repo counted)" ⟦criterion 5⟧
- [ ] status.sh's contract cases in status.test.sh are unchanged by this issue: every case name the suite held at the issue's base is still there with the same assertions ⟦criterion 6⟧
