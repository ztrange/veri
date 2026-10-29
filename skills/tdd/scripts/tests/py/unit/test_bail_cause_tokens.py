"""BAIL.md's cause-token list against the classification veri/classify_bail.py prints."""
import importlib
import re

from conftest import ROOT


def test_bail_md_names_rebase_unresolved_with_the_classification_classify_bail_prints_2194(capsys):
    assert importlib.import_module("veri.classify_bail").main(["rebase-unresolved"]) == 0
    classification = capsys.readouterr().out.strip()

    text = (ROOT / "skills" / "tdd" / "BAIL.md").read_text()
    section = text.split("a **cause token**", 1)[1]
    bullets = re.split(r"\n(?=- )", section.split("\n\n", 1)[1])
    bullet = next((b for b in bullets if b.startswith("- `rebase-unresolved`")), "")

    assert bullet, "BAIL.md's cause-token list has no `rebase-unresolved` bullet"
    assert "**%s**" % classification in bullet


def test_bail_md_names_missing_reroutes_exhausted_with_the_classification_classify_bail_prints_2573(capsys):
    assert importlib.import_module("veri.classify_bail").main(["missing-reroutes-exhausted"]) == 0
    classification = capsys.readouterr().out.strip()

    text = (ROOT / "skills" / "tdd" / "BAIL.md").read_text()
    section = text.split("a **cause token**", 1)[1]
    bullets = re.split(r"\n(?=- )", section.split("\n\n", 1)[1])
    bullet = next((b for b in bullets if b.startswith("- `missing-reroutes-exhausted`")), "")

    assert bullet, "BAIL.md's cause-token list has no `missing-reroutes-exhausted` bullet"
    assert "**%s**" % classification in bullet


def test_bail_md_names_pr_ready_failed_with_the_classification_classify_bail_prints_2581(capsys):
    assert importlib.import_module("veri.classify_bail").main(["pr-ready-failed"]) == 0
    classification = capsys.readouterr().out.strip()

    text = (ROOT / "skills" / "tdd" / "BAIL.md").read_text()
    section = text.split("a **cause token**", 1)[1]
    bullets = re.split(r"\n(?=- )", section.split("\n\n", 1)[1])
    bullet = next((b for b in bullets if b.startswith("- `pr-ready-failed`")), "")

    assert bullet, "BAIL.md's cause-token list has no `pr-ready-failed` bullet"
    assert "**%s**" % classification in bullet


def test_bail_md_names_graded_edit_outside_skill_edit_with_the_classification_classify_bail_prints_2653(capsys):
    assert importlib.import_module("veri.classify_bail").main(["graded-edit-outside-skill-edit"]) == 0
    classification = capsys.readouterr().out.strip()

    text = (ROOT / "skills" / "tdd" / "BAIL.md").read_text()
    section = text.split("a **cause token**", 1)[1]
    bullets = re.split(r"\n(?=- )", section.split("\n\n", 1)[1])
    bullet = next((b for b in bullets if b.startswith("- `graded-edit-outside-skill-edit`")), "")

    assert bullet, "BAIL.md's cause-token list has no `graded-edit-outside-skill-edit` bullet"
    assert "**%s**" % classification in bullet
