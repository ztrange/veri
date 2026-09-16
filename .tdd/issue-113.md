# Plan for #113 — Selection order: priority first, then bugs, then the rest — ascending within each band

- [x] solvable-issues.sh prints a `bug`-labelled issue ahead of a lower-numbered plain one, each band ascending by number
- [x] solvable-issues.sh prints a priority-labelled issue ahead of a lower-numbered bug, and an issue carrying both labels sorts in the priority band
- [x] The priority label without the opt-in label never makes an issue solvable
- [x] A priority or bug issue that is blocked, claimed or closed is still not printed
- [x] VERI_PRIORITY_LABEL set-but-empty exits 2 with a diagnostic; unset defaults to `priority`
- [ ] With no issue carrying either label, solvable-issues.sh output is byte-identical to today's
- [ ] The /tdd loop narration says when it took an issue ahead of a lower-numbered one, and which band did it
- [ ] CONTEXT.md, SKILL.md and CLAUDE.md record the three-band order and the VERI_PRIORITY_LABEL tunable
- [ ] hermetic-suites.test.sh pins the suites' independence from an ambient VERI_PRIORITY_LABEL
