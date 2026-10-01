# Plan for #636 — a revise leaf runs the tiers of the phase it redoes, not the full suite

- [x] the prompt `build-develop-prompt.sh revise red …` prints tells the leaf to run the affected suites through timed-test-run.sh under tier `affected`, and names no `all` run ⟦criterion 1⟧
- [ ] the prompt `build-develop-prompt.sh revise refactor …` prints tells the leaf to run the affected suites through timed-test-run.sh under tier `affected`, and names no `all` run ⟦criterion 1⟧
- [ ] the prompt `build-develop-prompt.sh revise green …` prints tells the leaf to run the fast command and then the affected suites through timed-test-run.sh, under tiers `fast` then `affected`, and names no `all` run ⟦criterion 1⟧
- [ ] SKILL.md's revise launch hands `build-develop-prompt.sh revise` the run's fast command, so a revise of green can name the fast command it must run
- [ ] `prompt-test-tiers.test.sh` pins the tiers of the revise prompt for each of red, green and refactor, and goes red against today's `develop-revise.md` ⟦criterion 2⟧
- [ ] the prompt `build-develop-prompt.sh refactor …` prints no longer says the full suite runs at verify-refactor; it says a break outside the affected set surfaces at the PR's one full run and its repair step ⟦criterion 3⟧
- [ ] the rebase leaves are unchanged: the `develop-rebase`, `develop-reconcile` and `verify-rebase` prompts still run the full test command under tier `all` ⟦criterion 4⟧
- [ ] CLAUDE.md's "Testing idiom" paragraph on what runs per step names the revise leaves' tiers — a revise leaf runs the tiers of the phase it redoes ⟦criterion 5⟧
