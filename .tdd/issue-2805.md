# Plan for #2805 — /vplan does not limit sub-PRD size, so oversized sub-PRDs get filed

- [x] skills/vplan/SKILL.md satisfies VPL16, a sub-PRD holds at most one capability the human can use, graded PASS, the pin file skills/tdd/scripts/tests/py/unit/test_prd_015_prose_signed.py updated in the same commit for the longer VPL list ⟦skill-edit⟧ ⟦criterion 1⟧
- [x] skills/vplan/SKILL.md satisfies VPL17, a sub-PRD holding more than one capability is split or states in the sub-PRD why it cannot be, graded PASS ⟦skill-edit⟧ ⟦criterion 2⟧
- [ ] skills/vplan/SKILL.md satisfies VPL18, an outline sub-PRD expected to hold more than one capability is split while it is still an outline, graded PASS ⟦skill-edit⟧ ⟦criterion 3⟧
- [ ] A case in skills/tdd/scripts/tests/py/unit/test_vplan_sub_prd_cap.py pins that skills/vplan/SKILL.md limits a sub-PRD to one capability the human can use; no production change ⟦criterion 1⟧
- [ ] A case in skills/tdd/scripts/tests/py/unit/test_vplan_sub_prd_cap.py pins that skills/vplan/SKILL.md has a sub-PRD holding more than one capability split, or keeping its size only with the reason written in the sub-PRD; no production change ⟦criterion 2⟧
- [ ] A case in skills/tdd/scripts/tests/py/unit/test_vplan_sub_prd_cap.py pins that skills/vplan/SKILL.md has an outline sub-PRD expected to hold more than one capability split at the outline stage; no production change ⟦criterion 3⟧
