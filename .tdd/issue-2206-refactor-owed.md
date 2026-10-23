### `tests-frozen.sh check-earlier` exiting 2 (not inside a git repository, or an unreadable ledger) removes an existing pass marker for that step, leaving markers of other steps in place ⟦added⟧ ⟦criterion 1⟧
- test-only | none
### `supervise.sh verify-red …` or `supervise.sh verify-green …` with no check-earlier pass marker for the current step exits 2, its stderr naming the missing check-earlier check, writes `.tdd/<name>.exit` and launches no leaf process ⟦criterion 2⟧
- fold the `write_line(exitfile, 2); return refuse(...)` pair, repeated across the launch guards in `main`, into one helper (the earlier guards predate this cycle, so it is out of scope here)
- out-of-scope | make `tests_frozen._pass_marker_path` public, since `supervise.py` now calls a private name from another module (a rename across files)
not-done | transform-rejected | fold the `write_line(exitfile, 2); return refuse(...)` pair, repeated across the launch guards in `main`, into one helper (the earlier guards predate this cycle, so it is out of scope here)
not-done | transform-rejected | make `tests_frozen._pass_marker_path` public, since `supervise.py` now calls a private name from another module (a rename across files)
