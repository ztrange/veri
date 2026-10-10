# Plan for #1287 — SKILL.md: wait for rebase-onto-default.sh's exit code before starting the post-rebase make test

- [x] The Draft PR step's sub-step 1 in skills/tdd/SKILL.md, where it runs rebase-onto-default.sh, says that script's exit code decides the next action, so nothing after it — in particular the rebased tip's full test run — is started until it has returned, and never in the same message as the rebase ⟦criterion 1⟧
- [ ] The CI step's conflict rebase in skills/tdd/SKILL.md, where it runs rebase-onto-default.sh again, says the same: its exit code decides the next action, so nothing after it — in particular the rebased tip's full test run — is started until it has returned, and never in the same message as the rebase ⟦criterion 1⟧
