# Plan for #1406 — The replaces-case green prompt permits deleting the named cases instead of requiring it, so the green leaf often deletes nothing

- [x] The replaces-case green template states that deleting exactly the named cases is required for the step to pass, not merely permitted, and still forbids deleting or modifying any other case ⟦criterion 1⟧
- [x] A develop-green prompt built for a `⟦replaces-case⟧` step carries the deletion requirement, pinned by a case in the prompt-builder tests ⟦criterion 2⟧
- [x] A conductor-run check, given a `⟦replaces-case⟧` step's text, exits 0 when every case the step names is gone from its suite, and exits 1 naming each named case still present ⟦criterion 3⟧ ⟂ refactor pending
- [ ] A develop-green prompt rebuilt for a `⟦replaces-case⟧` step whose named cases survived the first green names those surviving cases as still owed for deletion ⟦criterion 3⟧
- [ ] SKILL.md says that before a `⟦replaces-case⟧` step's green goes to verify-green the conductor runs that check, and on survivors relaunches the green leaf naming them, records the relaunch as an event, and launches no verifier, pinned by a prose case that goes red without that paragraph ⟦criterion 3⟧
