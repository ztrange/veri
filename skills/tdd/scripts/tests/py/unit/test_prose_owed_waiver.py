"""A unit a pending skill-edit step will regrade is waived, not owed."""
import prose_owed


def test_2081_unit_named_on_an_unchecked_skill_edit_step_is_waived_and_no_longer_owed():
    step = "- [ ] ⟦added⟧ ⟦skill-edit⟧ regrade `skills/vstop/SKILL.md` against X1"
    ledger = "- [x] an earlier step\n" + step + "\n"
    owed, waived = prose_owed.waive(ledger, ["skills/vstop/SKILL.md"])
    assert owed == []
    assert waived == [("skills/vstop/SKILL.md", step)]


def test_2081_unit_without_an_unchecked_skill_edit_step_naming_it_stays_owed():
    unit = "skills/vstop/SKILL.md"
    ledgers = [
        "- [x] an earlier step\n",
        "- [x] ⟦added⟧ ⟦skill-edit⟧ regrade `" + unit + "` against X1\n",
        "- [ ] ⟦added⟧ ⟦skill-edit⟧ regrade `skills/other/SKILL.md` against X1\n",
    ]
    for ledger in ledgers:
        assert prose_owed.waive(ledger, [unit]) == ([unit], [])


def test_2081_only_the_unit_a_pending_skill_edit_step_names_is_waived_and_another_stays_owed():
    u, v = "skills/vstop/SKILL.md", "skills/veri-go/SKILL.md"
    step = "- [ ] ⟦added⟧ ⟦skill-edit⟧ regrade `" + u + "` against X1"
    owed, waived = prose_owed.waive(step + "\n", [u, v])
    assert owed == [v]
    assert waived == [(u, step)]
