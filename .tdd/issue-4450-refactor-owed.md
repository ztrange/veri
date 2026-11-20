### skill-edit-half.sh <n> --change "<change>" passes `--change "<change>"` to skill-edit-step.sh after any --added and before the issue body file ⟦criterion 1⟧
- test-only | Duplicated Code: Extract Function — the preflight, ledger and fake-`run_script` setup is repeated across the cases in `test_skill_edit_half.py`; pull it into one helper or fixture
### skill-edit-half.sh called again by the conductor that wrote that wait record only waits on skill-edit-<n>, never making the gh api call or starting skill-edit-step.sh again ⟦criterion 3⟧
- test-only | Duplicated Code: Extract Function — the `fake(name, *args, cwd=None, env=None, **kw)` recorder and its setup, repeated across the cases in test_skill_edit_half.py, into one fixture
### skill-edit-half.sh exits 2 before any call on bad arguments: a non-numeric issue, an unknown option, or --change with no value ⟦criterion 13⟧
- test-only | Duplicated Code: Extract Function — pull the repeated worktree, preflight and ledger setup in `test_skill_edit_half.py` into one fixture
not-done | coupling | mutual reference: skills/tdd/scripts/veri/ledger.py skills/tdd/scripts/veri/run_step.py
