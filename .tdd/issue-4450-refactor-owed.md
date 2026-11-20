### skill-edit-half.sh <n> --change "<change>" passes `--change "<change>"` to skill-edit-step.sh after any --added and before the issue body file ⟦criterion 1⟧
- test-only | Duplicated Code: Extract Function — the preflight, ledger and fake-`run_script` setup is repeated across the cases in `test_skill_edit_half.py`; pull it into one helper or fixture
