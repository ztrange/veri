# Plan for #4343 — PRD 038.2: run-step.sh runs a cycle step in one call, stopping at seams

- [x] run-step.sh <n> runs red-half.sh, green-half.sh, refactor-half.sh and step-close.sh in that order through fused.script(), prints step-close's next= line last and exits 0 ⟦criterion 1⟧
- [ ] at the first stage exiting 1, 2 or 3 it stops, prints seam=<stage> code=<c> next=<anchor or command> and exits c ⟦criterion 2⟧
- [ ] called again with no options it resumes at the seam recorded in .tdd/issue-<n>-step, not calling the stages before it ⟦criterion 3⟧
- [ ] --from <stage> starts at that stage, and an unknown stage name exits 2 ⟦criterion 4⟧
- [ ] --hand <stage>, repeatable, stops before that stage with seam=<stage> code=1 reason=hand next=<anchor> without calling it ⟦criterion 5⟧
- [ ] a ⟦ci-repair⟧ or ⟦replaces-case⟧ step stops before green-half with seam=green-half code=1 reason=unmodelled next=<anchor>, from one kinds table ⟦criterion 6⟧
- [ ] an open step of a kind red_half.REFUSED holds exits 1 with seam=none code=1 reason=kind next=<anchor>, calling no stage ⟦criterion 7⟧
- [ ] a stage's record seam is a designed stop: run-step.sh ends on seam=<stage> code=1 reason=record and exits 1, as every designed stop does ⟦criterion 8⟧
- [ ] it prints each stage's call line with its exit code and never the contents of a leaf's or suite's output file ⟦criterion 9⟧
- [ ] every next= anchor it can print names a heading in its file, watched go red against a renamed heading ⟦criterion 10⟧
- [ ] its CALLS tuple names the four stage scripts and no run-leaf.sh, detach-leaf.sh or supervise.sh ⟦criterion 12⟧
- [ ] `skills/tdd/SKILL.md#Red — one failing test (developer leaf), then verify-red (blind)`, `#Green — …` and `#Refactor loop — …` call run-step.sh once for a cycle step in place of the four fused-call lines, SKILL.md no larger ⟦skill-edit⟧ ⟦criterion 11⟧
