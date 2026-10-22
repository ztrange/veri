"""A unit a pending skill-edit step will regrade is waived, not owed."""
import prose_owed


def test_2081_unit_named_on_an_unchecked_skill_edit_step_is_waived_and_no_longer_owed():
    step = "- [ ] ⟦added⟧ ⟦skill-edit⟧ regrade `skills/veri-stop/SKILL.md` against X1"
    ledger = "- [x] an earlier step\n" + step + "\n"
    owed, waived = prose_owed.waive(ledger, ["skills/veri-stop/SKILL.md"])
    assert owed == []
    assert waived == [("skills/veri-stop/SKILL.md", step)]
