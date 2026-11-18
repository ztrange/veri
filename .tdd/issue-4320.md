# Plan for #4320 — PRD 034.5a: the status report shows the stack and no longer lists a joined run as ready to merge

- [x] a run whose done event's `(#n)` subject is on origin/<stack> only gives no `ready to merge` line under Waiting ⟦criterion 4⟧
- [x] a run whose landing cannot be told because the stack's subjects could not be read is listed as merge state unknown, never as ready to merge and never hidden ⟦criterion 4⟧
- [x] a stack named but not yet on origin reads as nothing joined, so a done run is listed as ready to merge, not as merge state unknown ⟦added⟧ ⟦criterion 4⟧
- [x] `--report` prints a Stack section between Landed and Running: `<stack>: joined <j>, tested <t>, landed <l> in 24h` ⟦criterion 1⟧
- [x] the Stack section adds the open tracking pull request's url and, when stack-red.sh exits 0, `frozen: <sha> <run-url>` ⟦criterion 1⟧
- [x] where no stack branch is named the report has no Stack section and reads no stack ⟦criterion 1⟧
- [x] a stack figure that could not be read prints `?`, never `0`, the rest of the section still printed and the exit code unchanged ⟦criterion 2⟧
- [x] `status.sh --json` carries `stack` with branch, joined, tested, landed, tracking_pr, frozen, `null` for an unread one, and no key where no stack is named ⟦criterion 3⟧
- [x] the landed count names the issues of only the slice pull requests of this repository merged into the default branch in the last 24 hours, reading pages until one ends before the window ⟦added⟧ ⟦criterion 1⟧
- [ ] SCRIPTS.md's status.sh entry and the shim's header name the Stack section and its figures, graded by row SC574 ⟦criterion 5⟧
- [ ] skills/vstatus/SKILL.md lists the Stack section and says a `?` is not a zero, graded by row A13 ⟦criterion 6⟧
- [ ] skills/vhandoff/SKILL.md's dev handoff carries the Stack section's lines, or says no stack is named, graded by row H12 ⟦criterion 7⟧
