### `parked-issues.sh` prints a fifth field `ready` for a parked issue whose comment's `Blocked by:` line names only closed issues; a small in-process case in `skills/tdd/scripts/tests/py/unit/test_parked_issues.py` with gh faked ⟦criterion 2⟧
- extract the blocker-state loop in `parked_issues.main` into a helper returning `ready`/`waiting`/`-`
- test-only | the `test_main_3683_*` cases repeat the listing, comments and fake-gh setup; a shared helper or fixture would remove it
### `parked-issues.sh` prints a fifth field `waiting` for a parked issue whose `Blocked by:` line names a pull request closed without being merged; a small in-process case in `skills/tdd/scripts/tests/py/unit/test_parked_issues.py` with gh faked ⟦criterion 2⟧
- extract the blocker-state loop in `main` of `veri/parked_issues.py` into a helper (for example `blockers_status(blocked_by)`), since `main` is long
