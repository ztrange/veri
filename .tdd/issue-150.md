# Plan for #150 — One refactor leaf per step applies every structural candidate, one commit each, up to VERI_REFACTOR_BUDGET

- [x] The refactor template tells one leaf to apply the step's structural candidates up to the budget it is given, one `refactor:` commit per transform, running the touched suites after each and reverting one that turns them red, and to report what it applied and what it left, structural and cosmetic separately
- [x] `build-develop-prompt.sh refactor` puts `VERI_REFACTOR_BUDGET` into the prompt
- [x] `SKILL.md` launches one refactor leaf per step, refuses to continue to verify-refactor over a dirty tree or a non-`refactor:` commit since the green commit, and narrates the `refactor:` commit count against the budget, overrun included
- [x] The refactor leaf is launched with a hard timeout of the run's leaf timeout times max(1, `VERI_REFACTOR_BUDGET`), and an explicit `VERI_TIMEOUT` is still used as given
- [x] A resume that re-enters a step's refactor resets uncommitted work and relaunches the leaf with the budget reduced by that step's existing `refactor:` commits
- [x] A new ADR supersedes ADR-0010, and `CONTEXT.md`'s cycle entry and `CLAUDE.md`'s budget invariant describe one refactor leaf per step ⟂ refactor pending
