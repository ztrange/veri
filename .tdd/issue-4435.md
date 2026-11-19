# Plan for #4435 — PRD 038.3: step-tick.sh and a diff-step stage

- [x] step-tick.sh closes an open ⟦diff-checked⟧ step: tick-ledger.sh without --refactor-pending, the `chore: diff-checked — <summary> (#<n>)` commit, push, stop ask, step-done comment, criterion tick, step-done mark, last line next= ⟦criterion 6⟧
- [x] step-tick.sh exits 2 before any commit on a missing pin-recheck receipt, preflight or ledger, or bad arguments ⟦criterion 11⟧ ⟦criterion 15⟧
- [x] diff-step.sh runs a ⟦diff-checked⟧ step's clean path in order, each leaf wait sliced, printing call lines only and never passing FLIP to the verifier ⟦criterion 1⟧ ⟦criterion 5⟧ ⟦criterion 12⟧ ⟦criterion 13⟧
- [ ] diff-step.sh with diff switched off launches no verifier, marks the skip, writes skipped and goes on ⟦criterion 4⟧
- [ ] diff-step.sh on a ⟦test-quality⟧ step probes the FLIP line before pin-recheck; probe 1 or no FLIP is a REJECT, probe or detect 2 is exit 2 ⟦criterion 2⟧ ⟦criterion 3⟧ ⟦criterion 15⟧
- [ ] diff-step.sh's verify, flip and pin-recheck REJECTs leave the step's rejected record and exit 1 ⟦criterion 8⟧
- [ ] revise.sh takes phase diff: no cost or prediction check, suite-reported and diff-leaf-deviation, re-verify on the original bases, a renamed-and-changed REJECT a stop ⟦criterion 8⟧
- [ ] run-step.sh runs diff-step as a ⟦diff-checked⟧ step's one stage, --hand diff-step stops before it, other kinds stay reason=kind ⟦criterion 9⟧ ⟦criterion 10⟧
- [ ] DIFF-CHECKED.md opens with the call line and names the tick subject; SCRIPTS.md, REQUIREMENTS.md rows and regrades ⟦criterion 7⟧ ⟦criterion 14⟧
