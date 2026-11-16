"""PUBLISHED.md and JOURNAL.md state the journal path event.py writes to (PRD 030.2, PB7, PB8)."""
import os

from conftest import SCRIPTS
from veri import event

PUBLISHED = SCRIPTS.parent / "PUBLISHED.md"
JOURNAL = SCRIPTS.parent / "JOURNAL.md"


def journal_path_and_default(tmp_path, monkeypatch):
    """The path event.journal_path builds, spelled with placeholders, and the VERI_HOME default it falls back to."""
    clone = tmp_path / "clone"
    (clone / ".git").mkdir(parents=True)
    (clone / ".git" / "config").write_text('[remote "origin"]\n\turl = https://github.com/<owner>/<repo>.git\n')
    monkeypatch.setenv("VERI_HOME", "$VERI_HOME")
    path = event.journal_path(str(clone), "<issue>")
    monkeypatch.delenv("VERI_HOME")
    monkeypatch.setenv("HOME", "~")
    default = os.path.dirname(os.path.dirname(os.path.dirname(event.journal_path(str(clone), "<issue>"))))
    return path, default


def test_published_md_states_the_journal_path_and_the_veri_home_default_event_py_builds(tmp_path, monkeypatch):
    path, default = journal_path_and_default(tmp_path, monkeypatch)
    text = PUBLISHED.read_text(encoding="utf-8")

    assert f"`{path}`" in text, f"PUBLISHED.md does not state the journal path event.py builds, `{path}`"
    assert f"`{default}`" in text, f"PUBLISHED.md does not state VERI_HOME's default event.py uses, `{default}`"


def test_journal_md_opens_with_the_journal_path_a_link_to_published_md_and_the_runs_own_copy(tmp_path, monkeypatch):
    path, _ = journal_path_and_default(tmp_path, monkeypatch)
    opening = JOURNAL.read_text(encoding="utf-8").split("\n|")[0]

    assert f"`{path}`" in opening, f"JOURNAL.md's text above its table does not hold the journal path `{path}`"
    assert "](PUBLISHED.md)" in opening, "JOURNAL.md's text above its table does not link PUBLISHED.md"
    assert "`.tdd/events.jsonl`" in opening, "JOURNAL.md's text above its table no longer names the run's own copy"
