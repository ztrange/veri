# Plan for #552 — wait-ci.sh still reads a previous head's green: the PR's head moves before its rollup clears

- [x] Given a stub whose PR rollup shows a previous head's green while the sha's own check runs (`gh api repos/<owner>/<repo>/commits/<sha>/check-runs`) are still in progress, wait-ci.sh exits 3 ⟦criterion 3⟧
- [x] wait-ci.sh exits 1 when the given sha's own check runs hold a completed failure, even while the PR rollup reads all green ⟦criterion 1⟧
- [x] wait-ci.sh reads every page of the given sha's check runs, so a failed run beyond the first page of results still exits 1 ⟦added⟧ ⟦criterion 1⟧ ⟂ refactor pending
- [ ] wait-ci.sh exits 0 when the given sha's own check runs and statuses have all succeeded, even while the PR rollup still shows a previous head's failed or pending checks ⟦criterion 1⟧
- [ ] wait-ci.sh exits 1 when a legacy status context of the sha, read from `gh api repos/<owner>/<repo>/commits/<sha>/status`, is in a failure or error state, even when the sha's check runs all succeeded ⟦criterion 1⟧
- [ ] wait-ci.sh exits 3 when a legacy status context of the sha, read from its `/status` endpoint, is still pending, even when the sha's check runs all succeeded ⟦criterion 1⟧
- [ ] No check runs and no statuses for the given sha is pending: wait-ci.sh exits 3, never 0 ⟦criterion 2⟧
- [ ] Called with no head-sha argument, wait-ci.sh reads the PR's current head sha and judges that sha's own check runs and statuses, never the PR rollup
