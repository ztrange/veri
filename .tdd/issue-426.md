# Plan for #426 — The documented verifier launch line breaks on a step title containing an apostrophe, and leaves a stale REJECT behind

- [ ] A verdict launcher script runs verify.sh with the step title passed as an argument, so a title containing an apostrophe reaches the verifier intact ⟦criterion 1⟧
- [ ] Every documented verifier launch line in SKILL.md invokes that verdict launcher rather than an inlined bash -c command string ⟦criterion 1⟧
- [ ] A verdict launcher that cannot start the verifier records 2, the no-answer code, and never 1 ⟦criterion 2⟧
- [ ] The verdict launcher clears the phase reason file before the verifier runs, so a reason left by an earlier step can never be read as this verdict ⟦criterion 3⟧
