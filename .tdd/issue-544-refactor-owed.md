### `wait-ci.sh`'s bound is enforced across calls, not within one: the deadline is recorded on the first call for the PR's head commit, and a later call that still finds a check pending past that deadline exits 2 rather than starting a fresh bound ⟦criterion 1⟧
- the headless case in wait-ci.test.sh writes its fixture with its own printf, repeating rollup()'s document format; removing it would need rollup() to accept a missing head, an option no other test needs
### SKILL.md's Draft PR step waits on CI by calling `wait-ci.sh` again on its exit 3, with no wait loop inside one Bash call and no pending test that reads `.status` alone ⟦criterion 1⟧
- skill-draft-pr.test.sh case 25's first check (wait-ci.sh between gh pr ready and the done mark) re-pins what cases 18 and 21 already pin
- SKILL.md's step-added line computes the same last-ticked-step awk twice (not this cycle's code)
