# Plan for #4088 — PRD 016.5b: /vready runs both test tiers on the default branch's tip

- [x] a tier RD2 resolves runs in a detached worktree of the default tip through detach-command.sh start and wait, its `<tier> tier run` row ok on exit 0 ⟦criterion 1⟧
- [x] a non-zero exit fails the `<tier> tier run` row, carrying the exit code and the output's last non-empty line ⟦criterion 1⟧
- [x] each `<tier> tier run` row carries its wall time in whole seconds ⟦criterion 2⟧
- [x] a tier resolving to nothing prints no `<tier> tier run` row and starts nothing ⟦criterion 3⟧
- [x] every exit leaves the repo's branches, index, tree and worktree list as found ⟦criterion 4⟧
- [x] a red tier's whole output is kept at `.tdd/ready-<tier>.out` in the main tree ⟦criterion 5⟧
- [x] a green tier leaves no `.tdd/ready-<tier>.out`, an older one included ⟦criterion 5⟧
- [x] a tier still running at wait's bound prints `waiting on ready-<tier>` last and exits 3, its worktree left ⟦criterion 6⟧
- [x] a re-run waits on the running tier instead of starting it, reporting its exit and wall time ⟦criterion 7⟧
- [x] vready SKILL.md `## Run` says to re-run on exit 3 and to summarise a red tier through a haiku subagent ⟦criterion 8⟧
- [x] vinstall SKILL.md's readiness brief says it runs as a subagent and starts none ⟦criterion 9⟧
- [x] a tier whose run died without recording an exit fails its row saying no answer was obtained
- [x] both tiers share one wait bound per call, so one call never outlasts detach-command.sh wait's 590 s
- [x] a tier's wall time ends when its command recorded its exit, not when a later call read it
- [x] a default tip that does not resolve, or a failing worktree add, fails the tier run row, starting and creating nothing
- [x] a tier worktree is reused only when git lists it and its record names the tip and command of now
- [ ] one deadline counted from the call's start bounds the permission probe and both tiers
- [ ] an exception after a tier started leaves its worktree and record for the re-run
