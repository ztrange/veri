"""`<issue>.metrics.json`, the published metrics file `event.sh` keeps beside each issue's journal (PRD 035.2, MF1 to
MF6)."""
import importlib
import json

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
