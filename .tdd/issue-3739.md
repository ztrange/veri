# Plan for #3739 — parked-issues.sh exits 2 with a TypeError on any parked issue that names a blocker

- [x] the six test_main_3683_* fakes in tests/py/unit/test_parked_issues.py return a CompletedProcess whose stdout holds the JSON, for both the issue-state read and the /pulls/ read ⟦added⟧ ⟦criterion 1⟧
- [x] With github.gh_api faked to return a CompletedProcess whose stdout holds the JSON (what the real one returns), a parked issue whose parked comment says Blocked by an open issue prints its line with the fifth field waiting and parked-issues.sh exits 0 ⟦criterion 1⟧
- [x] With github.gh_api faked to return a CompletedProcess whose stdout holds the JSON, a parked issue whose parked comment says Blocked by a closed, merged pull request prints its line with the fifth field ready and parked-issues.sh exits 0 ⟦criterion 2⟧
