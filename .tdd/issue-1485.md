# Plan for #1485 — Model defaults ship in the code: Sonnet for first tries and verifiers, Opus for redos and the conductor; an empty model variable never fails a run

- [x] With no model variable set, leaf-model.sh prints sonnet and exits 0 for develop-red, develop-rebase, develop-reconcile, develop-over-budget and verify-green, and opus for revise-green-2 and develop-exhausted; a role variable still beats VERI_MODEL, VERI_MODEL_REVISE still beats VERI_MODEL_DEVELOPER for the redo leaves, and VERI_MODEL beats every default ⟦criterion 1⟧
- [x] With no model variable set, the claude command line of a supervised leaf carries --model sonnet for develop-red and verify-green, and --model opus for revise-green-2 and develop-exhausted ⟦criterion 1⟧
- [x] With no model variable set, run-conductor.sh <issue> launches claude with --model opus ⟦criterion 1⟧ ⟂ refactor pending
- [ ] With no model variable set, in the same .tdd/ directory, a verify-green REJECT is followed by revise-green-1 carrying --model opus, then the next step's develop-red and the same step's develop-refactor each carry --model sonnet ⟦criterion 2⟧
- [ ] Each of VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE set to "" or to whitespace only gives the same model and exit 0 as when unset, for develop-red, revise-green, revise-green-2, develop-exhausted and verify-green (preflight's three leaf-model.sh calls included); a value with internal whitespace (sonnet 5) still exits 2 with nothing on stdout ⟦criterion 3⟧
- [ ] SKILL.md's preflight step 6 says an empty or whitespace-only model variable is treated as unset and that only a value with internal whitespace stops the run ⟦criterion 3⟧
- [ ] With VERIFY_LEAF_ARGS carrying --model x and no model variable set, verify.sh does not exit 2 and the verifier leaf's command line names model x ⟦criterion 4⟧
- [ ] With VERIFY_LEAF_ARGS carrying --model x and VERI_MODEL_VERIFIER also set, verify.sh still exits 2 ⟦criterion 4⟧
- [ ] model-knobs-recorded.test.sh goes red, naming the document, when SKILL.md's supervise.sh bullet or CLAUDE.md's model-knob invariant stops naming VERI_MODEL_REVISE ⟦criterion 5⟧
- [ ] CLAUDE.md's model-knob invariant and SKILL.md's supervise.sh bullet state the shipped defaults (sonnet for first tries and verifiers, opus for redo leaves and the conductor) instead of no --model ⟦criterion 5⟧
- [ ] supervise.sh's Tunables (env) header names all four model knobs and the shipped defaults instead of no --model ⟦criterion 5⟧
- [ ] The metrics footer's sentence on when dollars are comparable names VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE ⟦criterion 5⟧
- [ ] model-knobs-recorded.test.sh was watched red with VERI_MODEL_REVISE removed from SKILL.md's bullet and from CLAUDE.md's invariant in turn ⟦human-owed⟧ ⟦criterion 5⟧
