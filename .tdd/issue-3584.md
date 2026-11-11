# Plan for #3584 — A skill-edit step's deterministic refusal (held requirement id) bails as no-verdict (system) instead of a process failure naming the refusal

- [x] classify-bail.sh skill-edit-refused prints process and exits 0 ⟦added⟧ ⟦criterion 1⟧
- [x] ⟦skill-edit⟧ `skills/tdd/BAIL.md`: the cause list gains a bullet for a skill-edit step whose runner refused with exit 2 and a refusal message: cause `skill-edit-refused`, a **process** failure naming the refusal, while a bare exit 2 with no refusal message stays the `no-verdict` system failure, per BL50 ⟦criterion 1⟧
- [x] ⟦skill-edit⟧ `skills/tdd/SKILL-EDIT.md`: on the runner's exit 2 with a refusal message the step bails at once as a process failure with cause `skill-edit-refused` naming the refusal; a bare exit 2 with no refusal message still bails as a system failure with `cause=no-verdict`; never relaunching the runner or spending `VERI_STUCK_RETRIES`, per SE5 ⟦criterion 1⟧
- [x] `classify-bail.sh no-verdict` — the cause a bare skill-edit exit 2 with no refusal message keeps — still prints `system` and exits 0 (a small in-process case, no production change expected) ⟦criterion 2⟧ ⟂ retired unpinnable
