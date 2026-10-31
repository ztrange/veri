# Plan for #2734 — verify-red and verify-pin reject a test whose only evidence is a generic error

- [x] skills/tdd/scripts/prompts/verify-red.md satisfies VR19: check 3's REJECT list has a bullet for a test failing on an incidental error, graded PASS ⟦skill-edit⟧ ⟦criterion 1⟧
- [x] skills/tdd/scripts/prompts/verify-pin.md satisfies VP18: check 3's REJECT list has a bullet for a test failing on an incidental error, graded PASS ⟦skill-edit⟧ ⟦criterion 1⟧
- [ ] fix the full-suite failure: skills/tdd/scripts/tests/py/unit/test_emitted_text.py — FAILED skills/tdd/scripts/tests/py/unit/test_emitted_text.py::test_usage_output_on_a_missing_argument_and_prompt_output_for_fixed_inputs_are_unchanged - the rendered red and pin prompt checksums the case pins moved with the new incidental-error bullets ⟦suite-repair⟧ ⟦criterion 1⟧
