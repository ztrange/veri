## skills/vinstall/SKILL.md

| ID | Requirement | Why |
|---|---|---|
| VI1 | Invoked as `/vinstall [repo-root]`, it runs `install-links.sh` and reports each skill it linked, repaired or removed. | One command sets up a project, and a removed link is a change the operator should see. |
| VI2 | On exit 2 it reports the refusal the script printed and does not work around it. | A path veri did not create is the operator's. |
| VI3 | It says that re-running it is the way to repair an install. | Re-running is the repair path. |
| VI4 | When `install-links.sh` linked, repaired or removed any skill, it runs the readiness check through a subagent on the cheapest model that can do it, briefed to read `<base dir>/../vready/SKILL.md` and follow it (never `/vready`, which is not linked), and to return at most 10 lines, and reports the subagent's answer; when the script changed nothing, it does not. | `vready` is read on demand, not linked; a first install ends with the answer, and the table stays out of a long context (P6). |
| VI5 | During setup, after reporting the links, it runs `$S/stack-branch.sh` and routes each exit: 0 reports the named branch and asks nothing; 2 reports the refusal and writes nothing; 3 asks whether the repository stacks finished runs on a standing branch and, if so, under what branch name. On a name it writes the line `veri: stack branch: <name>` into the repository's `CLAUDE.md` and checks it again with `$S/stack-branch.sh`, taking the line out and asking once more on exit 2; on a no it writes nothing. | PRD 034 D6: stacking is off unless the repository names the branch, and setup is where the operator is asked; a line that cannot name a stack is the operator's to fix, not an answer to overwrite. |
