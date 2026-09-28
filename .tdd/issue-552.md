# Plan for #552 — wait-ci.sh still reads a previous head's green: the PR's head moves before its rollup clears

- [ ] Given a stub whose PR rollup shows a previous head's green while the sha's own check runs (`gh api repos/<owner>/<repo>/commits/<sha>/check-runs`) are still in progress, wait-ci.sh exits 3 ⟦criterion 3⟧
- [ ] wait-ci.sh exits 1 when the given sha's own check runs hold a completed failure, even while the PR rollup reads all green ⟦criterion 1⟧
- [ ] wait-ci.sh reads the sha's legacy status contexts from `gh api repos/<owner>/<repo>/commits/<sha>/status`: a failure or error state there exits 1 and a pending one exits 3, even when the sha's check runs all succeeded ⟦criterion 1⟧
- [ ] No check runs and no statuses for the given sha is pending: wait-ci.sh exits 3, never 0 ⟦criterion 2⟧
- [ ] Called with no head-sha argument, wait-ci.sh reads the PR's current head sha and judges that sha's own check runs and statuses, never the PR rollup
