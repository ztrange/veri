# Plan for #4088 — PRD 016.5b: /vready runs both test tiers on the default branch's tip

- [x] a tier RD2 resolves runs in a detached worktree of the default tip through detach-command.sh start and wait, its `<tier> tier run` row ok on exit 0 ⟦criterion 1⟧
- [ ] a non-zero exit fails the `<tier> tier run` row, carrying the exit code and the output's last non-empty line ⟦criterion 1⟧
- [ ] each `<tier> tier run` row carries its wall time in whole seconds ⟦criterion 2⟧
- [ ] a tier resolving to nothing prints no `<tier> tier run` row and starts nothing ⟦criterion 3⟧
- [ ] every exit leaves the repo's branches, index, tree and worktree list as found ⟦criterion 4⟧
- [ ] a red tier's whole output is kept at `.tdd/ready-<tier>.out` in the main tree ⟦criterion 5⟧
- [ ] a green tier leaves no `.tdd/ready-<tier>.out`, an older one included ⟦criterion 5⟧
- [ ] a tier still running at wait's bound prints `waiting on ready-<tier>` last and exits 3, its worktree left ⟦criterion 6⟧
- [ ] a re-run waits on the running tier instead of starting it, reporting its exit and wall time ⟦criterion 7⟧
- [ ] vready SKILL.md `## Run` says to re-run on exit 3 and to summarise a red tier through a haiku subagent ⟦criterion 8⟧
- [ ] vinstall SKILL.md's readiness brief says it runs as a subagent and starts none ⟦criterion 9⟧
