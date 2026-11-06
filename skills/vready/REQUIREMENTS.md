## skills/vready/SKILL.md

| ID | Requirement | Why |
|---|---|---|
| VR1 | Invoked as `/vready [repo-root]`, it runs `ready-check.sh`, passing the argument through, and prints the script's table and last line. | One command answers "can veri run here?". |
| VR2 | It never fixes a failing row: it creates no label, edits no file, and runs no fix command it printed. | Granting is the human's. |
| VR3 | On exit 2 it reports what the script printed and stops. | No answer is not a verdict. |
| VR4 | It obeys `operator/PRINCIPLES.md` and names no project fact. | P12. |
