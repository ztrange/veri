# Plan for #4172 — PRD 034.2a: one tracking pull request makes CI test each push to the stack

- [x] github.py reads the open pull requests from one head branch to one base, paginated, kept only when the answer itself names both, and opens a ready pull request through bounded gh; an unreadable or garbled answer is NoAnswer
- [x] With the stack ahead and one open pull request from it to the default branch, stack-pr.sh prints its url and exits 0, opening nothing ⟦criterion 1⟧
- [x] With the stack ahead and none open, stack-pr.sh opens one, ready and not a draft, prints its url and exits 0 ⟦criterion 2⟧
- [x] The body of the pull request it opens says it is never merged itself and that slices are cut from it, and holds no Closes, Fixes or Resolves line ⟦criterion 5⟧
- [ ] With the stack not ahead of the default branch, or origin holding no stack branch, stack-pr.sh opens nothing and exits 3 ⟦criterion 3⟧
- [ ] stack-pr.sh exits 2 when GitHub gives no answer, two open pull requests track the stack, or the open read's answer is garbled, opening nothing; and exits what stack-branch.sh exits when that is not 0 ⟦criterion 4⟧
- [ ] A join calls stack-pr.sh after its push to the stack and its merged read, and a merge where stack-branch.sh exits 3 does not ⟦criterion 6⟧
- [ ] When the join's stack-pr.sh call exits non-zero, the join prints one stderr line naming it and keeps its own exit code ⟦criterion 7⟧
- [ ] stack-pr.sh is a /bin/sh shim by the status.sh convention, its entry-point contract pinned in test_stack_pr_process.py, and veri/README.md indexes it ⟦criterion 8⟧
- [ ] SCRIPTS.md lists stack-pr.sh and says a join calls it, graded by SC201 and SC202 ⟦criterion 9⟧
