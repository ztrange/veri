# Plan for #4093 — PRD 016.9: preflight runs the permission rows only when its record is missing or stale

- [x] `ready-check.sh --no-permissions` prints none of the skipped rows and makes none of their probes, and still prints RD7's `gh auth`, `push access` and `label <VERI_LABEL's value>` rows ⟦criterion 1⟧
- [x] preflight passes `--no-permissions` and prints `permission rows skipped: checked <date>` when `.tdd/permissions-checked` in the main working tree holds the current gh login, origin URL and check version ⟦criterion 2⟧
- [x] a missing, stale, unreadable, malformed or future-dated record, or `VERI_RECHECK_PERMISSIONS=1`, leaves `--no-permissions` off the call ⟦criterion 3⟧
- [x] after a call without `--no-permissions` in which every skipped row was printed and none failed, preflight writes the record; after one in which any failed, it writes none and leaves an existing one byte-for-byte ⟦criterion 4⟧
- [x] the check's version is a constant in `ready_check.py`; a record written under another value runs the rows ⟦criterion 5⟧
- [x] `VERI_RECHECK_PERMISSIONS` is a tunable (default `0`, `0` or `1`); any other value stops preflight at `2 VERI_RECHECK_PERMISSIONS`, exit 2, before `ready-check.sh` and the worktree ⟦criterion 6⟧
- [ ] PREFLIGHT.md step 2 names the record, when the rows are skipped and `VERI_RECHECK_PERMISSIONS` (PF68) ⟦criterion 8⟧
- [ ] README.md `## Install` names the record, `VERI_RECHECK_PERMISSIONS` and the paid re-check (RD33) ⟦criterion 9⟧
- [ ] SCRIPTS.md's `ready-check.sh` and `preflight.sh` entries name `--no-permissions` and the record (SC281, SC282)
