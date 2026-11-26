"""PUBLISHED.md and JOURNAL.md state the journal path event.py writes to (PRD 030.2, PB7, PB8)."""
import ast
import importlib
import json
import os
import re

import pytest
from veri import event

from conftest import SCRIPTS

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


def _owed_example():
    """The JSON example in PUBLISHED.md's `report-owed.json` section, parsed; None when the section holds none."""
    text = PUBLISHED.read_text(encoding="utf-8")
    section = text.split("## `report-owed.json`", 1)[-1].split("\n## ", 1)[0]
    block = re.search(r"```json\n(.*?)```", section, re.S)
    return json.loads(block.group(1)) if block else None


def _key_paths(value, prefix=""):
    """Every key of <value>, at every level, as a dotted path from the top."""
    if not isinstance(value, dict):
        return set()
    paths = set()
    for key, inner in value.items():
        paths |= {prefix + key} | _key_paths(inner, prefix + key + ".")
    return paths


def test_4021_the_report_owed_example_in_published_md_has_the_keys_of_a_file_store_owed_writes(run_cli, tmp_path):
    prd_report = importlib.import_module("veri.prd_report")
    example = _owed_example()
    assert example is not None, "PUBLISHED.md's report-owed.json section holds no ```json example"
    (prd,) = example
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    head = {"number": 5, "title": f"PRD {prd}: example", "state": "OPEN", "labels": [], "closedAt": None,
            "updatedAt": "2026-11-02T10:00:00Z", "body": "", "blockedBy": [], "links": [], "wallSeconds": 0, "lane": None}
    (tmp_path / ".tdd" / "report-cache.json").write_text(json.dumps(
        {"cache_format": 2, "fetched_at": "2026-11-07T10:00:00Z", "issues": [head]}))
    (tmp_path / "answer.json").write_text(json.dumps({"count": 1, "sections": ["Alpha"]}))

    code, _, err = run_cli(prd_report, ["--store-owed", prd, "answer.json"], cwd=tmp_path)
    written = json.loads((tmp_path / ".tdd" / "report-owed.json").read_text())

    assert code == 0, err
    lacking = sorted(_key_paths(written) - _key_paths(example))
    extra = sorted(_key_paths(example) - _key_paths(written))
    assert lacking == [], f"PUBLISHED.md's report-owed.json example lacks the key(s) {lacking}"
    assert extra == [], f"PUBLISHED.md's report-owed.json example has the key(s) {extra}, which --store-owed does not write"


def _metrics_paths(value, prefix=""):
    """Every key of a `metrics.sh --json` object as PUBLISHED.md spells it: `a.b`, `<phase>` for an entry of the map
    keyed by phase name, `[]` for an entry of a list."""
    if isinstance(value, dict):
        paths = set()
        for key, inner in value.items():
            path = prefix + {"phases.": "<phase>", "leaves.": "<kind>", "stages.": "<stage>",
                             "conductor.by_phase.": "<window>"}.get(prefix, key)
            paths |= {path} | _metrics_paths(inner, path + ".")
        return paths
    if isinstance(value, list):
        return {path for inner in value for path in _metrics_paths(inner, prefix.rstrip(".") + "[].")}
    return set()


def _stated_metrics_keys():
    """The backticked keys in the first column of the table under PUBLISHED.md's `## The metrics file`."""
    section = PUBLISHED.read_text(encoding="utf-8").split("## The metrics file", 1)[-1].split("\n## ", 1)[0]
    return {m.group(1) for m in re.finditer(r"^\| `([^`]+)` \|", section, re.M)}


def test_4204_published_md_states_exactly_the_keys_of_the_object_metrics_json_builds(tmp_path, monkeypatch):
    metrics = importlib.import_module("veri.metrics")
    from test_metrics_page import build_rich_root
    build_rich_root(tmp_path)
    log = tmp_path / ".tdd" / "events.jsonl"
    log.write_text(log.read_text() + json.dumps({"ts": 5200, "issue": "108", "actor": "conductor", "phase": "green",
                                                 "step": "two", "event": "bail", "cause": "uncovered",
                                                 "classification": "process"}) + "\n"
                   + json.dumps({"ts": 5300, "issue": "108", "event": "stage-end", "stage": "baseline", "status": "0",
                                 "secs": "9"}) + "\n")
    monkeypatch.chdir(tmp_path)

    built = _metrics_paths(metrics.as_json(metrics.fold("108", ".tdd/events.jsonl", ".tdd/issue-108.md")))
    stated = _stated_metrics_keys()

    assert {"run.bails[].cause", "phases.<phase>.attempts", "steps[].text"} <= built
    assert sorted(built - stated) == [], f"PUBLISHED.md's metrics file section does not state the key(s) {sorted(built - stated)}"
    assert sorted(stated - built) == [], f"PUBLISHED.md's metrics file section states the key(s) {sorted(stated - built)}, which metrics.sh --json does not build"
