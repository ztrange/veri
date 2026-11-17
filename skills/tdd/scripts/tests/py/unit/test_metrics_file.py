"""`<issue>.metrics.json`, the published metrics file `event.sh` keeps beside each issue's journal (PRD 035.2, MF1 to
MF6)."""
import errno
import importlib
import json
import os

import pytest


@pytest.fixture
def event():
    return importlib.import_module("veri.event")


@pytest.fixture
def metrics():
    return importlib.import_module("veri.metrics")


def clone_at(root, origin="https://github.com/acme/widgets.git"):
    clone = root / "clone"
    (clone / ".git").mkdir(parents=True)
    config = '[core]\n\tbare = false\n' + ('[remote "origin"]\n\turl = %s\n' % origin if origin else "")
    (clone / ".git" / "config").write_text(config)
    return clone


LEAF = {"issue": "42", "actor": "developer", "phase": "red", "step": "one", "attempt": "1"}


def leaf_exit(event, clone, status="0", ts=1700000100):
    """A red leaf of issue 42 launched then exited with <status>; the codes of both event calls."""
    return (event.append(str(clone), LEAF, "launch", ["name=develop-red", "cmd=run-leaf.sh", "model="], ts=ts),
            event.append(str(clone), LEAF, "exit", ["status=" + status, "secs=30"], ts=ts + 30))


def test_after_a_leafs_exit_the_metrics_file_beside_the_journal_holds_the_json_object_of_the_journal_with_that_line(
        tmp_path, event, metrics):
    clone = clone_at(tmp_path)

    codes = leaf_exit(event, clone, status="2")

    journal = tmp_path / "runs" / "acme-widgets" / "42.jsonl"
    published = json.loads((tmp_path / "runs" / "acme-widgets" / "42.metrics.json").read_text())
    assert codes == (0, 0)
    assert published == metrics.as_json(metrics.fold("42", str(journal), str(clone / ".tdd" / "issue-42.md"), run=str(clone)))
    assert (published["phases"]["red"]["attempts"], published["phases"]["red"]["kills"]) == (1, 1)


USAGE = ["duration_ms=1000", "duration_api_ms=900", "num_turns=4", "total_cost_usd=1.50", "input_tokens=10",
         "output_tokens=20", "cache_read_input_tokens=30", "cache_creation_input_tokens=40", "model=claude-sonnet-4"]


def metrics_file(root, issue="42"):
    return root / "runs" / "acme-widgets" / ("%s.metrics.json" % issue)


def test_an_event_of_any_other_name_leaves_the_files_absence_and_its_bytes_unchanged(tmp_path, event):
    clone = clone_at(tmp_path)

    launched = event.append(str(clone), LEAF, "launch", ["name=develop-red", "cmd=run-leaf.sh", "model="], ts=1700000000)
    absent = metrics_file(tmp_path).exists()
    event.append(str(clone), LEAF, "exit", ["status=0", "secs=30"], ts=1700000030)
    before = metrics_file(tmp_path).read_bytes()
    later = [event.append(str(clone), LEAF, "usage", USAGE, ts=1700000031),
             event.append(str(clone), LEAF, "verdict", ["verdict=PASS", "reason="], ts=1700000032),
             event.append(str(clone), dict(LEAF, step="two"), "step-start", [], ts=1700000033)]

    assert (launched, absent, later) == (0, False, [0, 0, 0])
    assert metrics_file(tmp_path).read_bytes() == before


def test_the_file_is_renamed_into_place_from_its_own_directory_so_a_failed_rename_leaves_the_previous_one_whole(
        tmp_path, event, monkeypatch):
    clone = clone_at(tmp_path)
    leaf_exit(event, clone)
    before = metrics_file(tmp_path).read_bytes()
    renames = []

    def refuse(source, target):
        renames.append((os.path.dirname(source), os.path.basename(source) != os.path.basename(target), target))
        raise OSError(errno.EIO, "rename refused")

    monkeypatch.setattr(os, "replace", refuse)
    monkeypatch.setattr(os, "rename", refuse)
    event.mark(str(clone), LEAF, "exit", ["status=2", "secs=30"], ts=1700000200)

    directory = metrics_file(tmp_path).parent
    assert renames == [(str(directory), True, str(metrics_file(tmp_path)))]
    assert metrics_file(tmp_path).read_bytes() == before
    assert sorted(path.name for path in directory.iterdir()) == ["42.jsonl", "42.metrics.json"]
