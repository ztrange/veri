### `parked-issues.sh` prints a fifth field `ready` for a parked issue whose comment's `Blocked by:` line names only closed issues; a small in-process case in `skills/tdd/scripts/tests/py/unit/test_parked_issues.py` with gh faked ⟦criterion 2⟧
- extract the blocker-state loop in `parked_issues.main` into a helper returning `ready`/`waiting`/`-`
- test-only | the `test_main_3683_*` cases repeat the listing, comments and fake-gh setup; a shared helper or fixture would remove it
