## skills/vinstall/SKILL.md

| ID | Requirement | Why |
|---|---|---|
| VI1 | Invoked as `/vinstall [repo-root]`, it runs `install-links.sh` and reports each skill it linked, repaired or removed. | One command sets up a project, and a removed link is a change the operator should see. |
| VI2 | On exit 2 it reports the refusal the script printed and does not work around it. | A path veri did not create is the operator's. |
| VI3 | It says that re-running it is the way to repair an install. | Re-running is the repair path. |
| VI4 | When `install-links.sh` linked, repaired or removed any skill, it runs the readiness check through a subagent on the cheapest model that can do it, briefed to read `<base dir>/../vready/SKILL.md` and follow it (never `/vready`, which is not linked), and to return at most 10 lines, and reports the subagent's answer; when the script changed nothing, it does not. | `vready` is read on demand, not linked; a first install ends with the answer, and the table stays out of a long context (P6). |
