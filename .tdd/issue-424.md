# Plan for #424 — A background job killed by job spec survives its parent: two leaked busy-loops burned ~988% CPU for 12 hours

- [x] A background process a veri script or test starts is killed by its recorded PID, never by a job spec, so it dies whether or not the starting shell is still alive ⟦criterion 1⟧ ⟂ refactor pending
- [ ] A background process that is still running when its starting shell exits is reported, naming its PID and what started it, rather than being left silently ⟦criterion 2⟧
- [ ] A guard names `<file>:<line>` and fails the run when a file under `skills/` kills a background process by job spec (`kill %…`), with an exemption table carrying a reason per entry ⟦criterion 3⟧
- [ ] A planted offender turns that guard red naming it, and the guard is green again once the plant is removed ⟦criterion 4⟧
- [ ] The rule is stated once in `CLAUDE.md`, next to the existing note that a killed process's cleanup never runs ⟦criterion 5⟧
