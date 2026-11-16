"""PUBLISHED.md and JOURNAL.md state the journal path event.py writes to (PRD 030.2, PB7, PB8)."""
import ast
import os
import re

import pytest

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


def _literal(node):
    value = node.value if isinstance(node, ast.Constant) else None
    return value.decode() if isinstance(value, bytes) else value if isinstance(value, str) else None


def _issueless_writes(index):
    """{event: 'file:line'} for the events a veri module writes with no issue in their context: `event.append` or
    `event.mark` given a literal `{}` context, and every `event.line([kind, …], …)` (its caller writes the line itself,
    to the worktree's log only)."""
    found = {}
    for module in index.names:
        for call in ast.walk(ast.parse(index.text(module))):
            if not (isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute)
                    and isinstance(call.func.value, ast.Name) and call.func.value.id == "event"):
                continue
            if (call.func.attr in ("append", "mark") and len(call.args) > 2 and isinstance(call.args[1], ast.Dict)
                    and not call.args[1].keys):
                kind = _literal(call.args[2])
            elif call.func.attr == "line" and call.args and isinstance(call.args[0], (ast.List, ast.Tuple)):
                kind = _literal(call.args[0].elts[0]) if call.args[0].elts else None
            else:
                continue
            if kind:
                found.setdefault(kind, f"{module}.py:{call.lineno}")
    return found


def _listed_as_log_only(text):
    """The backticked event names of the bullets under PUBLISHED.md's `### Events that never reach the journal`."""
    section = text.split("### Events that never reach the journal", 1)[1].split("\n#", 1)[0] if \
        "### Events that never reach the journal" in text else ""
    return {m.group(1) for m in re.finditer(r"^- `([a-z][a-z0-9-]*)`", section, re.M)}


@pytest.mark.tree_audit("skills/tdd/scripts/veri, for the event writers that pass no issue")
def test_published_md_lists_exactly_the_events_a_writer_sends_to_the_worktrees_log_only(veri_modules_index):
    written = _issueless_writes(veri_modules_index)
    listed = _listed_as_log_only(PUBLISHED.read_text(encoding="utf-8"))

    assert written, "the walk found no writer that passes no issue"
    assert sorted(set(written) - listed) == [], f"PUBLISHED.md does not list as log-only: {written}"
    assert sorted(listed - set(written)) == [], "PUBLISHED.md lists as log-only an event every writer sends to the journal"


def test_journal_md_opens_with_the_journal_path_a_link_to_published_md_and_the_runs_own_copy(tmp_path, monkeypatch):
    path, _ = journal_path_and_default(tmp_path, monkeypatch)
    opening = JOURNAL.read_text(encoding="utf-8").split("\n|")[0]

    assert f"`{path}`" in opening, f"JOURNAL.md's text above its table does not hold the journal path `{path}`"
    assert "](PUBLISHED.md)" in opening, "JOURNAL.md's text above its table does not link PUBLISHED.md"
    assert "`.tdd/events.jsonl`" in opening, "JOURNAL.md's text above its table no longer names the run's own copy"
