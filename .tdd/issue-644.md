# Plan for #644 — the exit-code contract's owed steps from #497: the audit over the real scripts, three usage exits, six EXIT traps

- [x] the missing-argument audit enumerates the scripts in the real `skills/tdd/scripts/` directory instead of a hand-kept roster, so a script added there is audited by existing ⟦criterion 1⟧
- [x] the missing-argument audit calls only scripts whose usage line names a required argument (a `<…>` outside `[…]`), and every such script called with no arguments exits 2 with a usage line on stderr naming itself ⟦criterion 1⟧
- [x] `build-develop-prompt.sh` called with no arguments exits 2 with a usage line on stderr naming it ⟦criterion 2⟧
- [x] `session-cost.sh` given a nonexistent transcript exits 2 with its own usage text on stderr ⟦criterion 3⟧
- [x] `session-cost.sh` given an unknown option exits 2 with its own usage text on stderr ⟦criterion 3⟧
- [x] `workqueue.sh` with no subcommand exits 2 with its own usage text on stderr ⟦criterion 4⟧
- [x] `workqueue.sh` given an empty issue exits 2 with its own usage text on stderr ⟦criterion 4⟧
- [x] `workqueue.sh` given an issue named twice exits 2 with its own usage text on stderr ⟦criterion 4⟧
- [x] `workqueue.sh` given a park reason holding a tab or a newline exits 2 with its own usage text on stderr ⟦criterion 4⟧ ⟂ refactor pending
- [ ] `preserve-attempt.sh`, made to fail inside its own EXIT trap's lifetime, ends with exit 2 and never with a code outside 0–3 ⟦criterion 5⟧
- [ ] `parallel-conductors.sh`, made to fail inside its own EXIT trap's lifetime, ends with exit 2 and never with a code outside 0–3 ⟦criterion 5⟧
- [ ] `run-suite.sh`, made to fail inside its own EXIT trap's lifetime, ends with exit 2 and never with a code outside 0–3 ⟦criterion 5⟧
- [ ] `run-leaf.sh`, made to fail inside its own EXIT trap's lifetime, ends with exit 2 and never with a code outside 0–3 ⟦criterion 5⟧
- [ ] `run-conductor.sh`, made to fail inside its own EXIT trap's lifetime, ends with exit 2 and never with a code outside 0–3 ⟦criterion 5⟧
- [ ] `workqueue.sh`, made to fail after `take_lock` has armed its EXIT trap, ends with exit 2 and never with a code outside 0–3 ⟦criterion 5⟧
