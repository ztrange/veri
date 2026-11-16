# Plan for #4041 — PRD 025.4: a ratchet on modules that run git themselves

- [ ] a veri/ module that starts git (a call on a list or tuple literal led by "git", or a module-level git/_git) and is not in MODULES_RUNNING_GIT_DIRECTLY fails a case naming it, git.py exempt, and the list holds every module the rule finds today, sorted, one per line with a reason ⟦criterion 1⟧ ⟦criterion 2⟧ ⟦criterion 3⟧
- [ ] a listed module that no longer starts git fails a case naming it ⟦criterion 1⟧
