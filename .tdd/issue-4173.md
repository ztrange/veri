# Plan for #4173 — PRD 034.2b: the session can ask which stack commit is tested and ends an issue

- [x] github.py reads a sha's check runs by sha, GitHub's latest attempt per check, every page within a bound; a failed read, a garbled answer or one past the bound is NoAnswer
- [x] A commit is an issue end when no issue number named in a subject at or before it is named in a subject after it; a subject names the (#n) groups at its very end ⟦criterion 3⟧
- [x] stack-green.sh prints the newest issue end whose check runs are all completed, each success, neutral or skipped, with at least one success, and exits 0 ⟦criterion 1⟧
- [x] Only neutral or skipped, a failure among successes, or no check run at all is not tested ⟦criterion 1⟧
- [ ] It exits 3 when no commit qualifies, a check run in progress making its commit not tested, and when more issue ends than its bound would need reading ⟦criterion 4⟧
- [ ] It exits 2 when GitHub gives no answer or stack-branch.sh does not exit 0 (its own code when that is 3) ⟦criterion 5⟧
- [ ] The module names no CI job or check name ⟦criterion 2⟧
- [ ] stack-green.sh is a /bin/sh shim by the status.sh convention, its contract pinned in test_stack_green_process.py against a real clone and a stub gh, and veri/README.md indexes it ⟦criterion 6⟧
- [ ] SCRIPTS.md lists stack-green.sh with its output and exit codes, graded by SC203 and SC204 ⟦criterion 7⟧
