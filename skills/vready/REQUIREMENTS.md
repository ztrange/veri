## skills/vready/SKILL.md

| ID | Requirement | Why |
|---|---|---|
| VR1 | Invoked as `/vready [repo-root]`, it runs `ready-check.sh`, passing the argument through, and prints the script's table and last line. | One command answers "can veri run here?". |
| VR2 | It never fixes a failing row: it creates no label, edits no file, and runs no fix command it printed. | Granting is the human's. |
| VR3 | On exit 2 it reports what the script printed and stops. | No answer is not a verdict. |
| VR4 | It obeys `operator/PRINCIPLES.md` and names no project fact. | P12. |
| VR5 | `## Run` says: on exit 3, run `ready-check.sh` again with the same argument, until it exits 0, 1 or 2. | The skill must not report `waiting on …` as the answer. |
| VR6 | `## Run` says: for each failing `<tier> tier run` row, have a subagent on the cheapest model that can do it (haiku) read `.tdd/ready-<tier>.out` and return at most 10 lines on why the tier failed, and print them after the table; the skill run that way never reads the file. When the skill itself runs as a subagent (its brief says so, as `/vinstall`'s does), it starts no subagent: it reads the file itself and puts why the tier failed in its answer. | The output stays out of the operator's context (P6); a subagent cannot start a subagent. |
| VR7 | `## Run` says the check makes one paid Haiku call, about $0.004, to prove a leaf may bypass permission prompts. | Spend is said before it is made. |
| VR8 | `## Run` says a row checks that the dev session's subagents may run git, the repo's test command and `$S` scripts without a permission prompt, and that its failure prints the allow rules to add. | The leaf row proves nothing for the dev session's own subagents, so an away human was prompted mid-run. |
