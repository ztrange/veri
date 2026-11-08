"""In-process cases for veri/refactor_candidates.py, the module refactor-candidates.sh is a shim over."""
import importlib

import pytest

OWED = (
    "### step 1\n"
    "- out-of-bounds | rename helper in lib/util.py\n"
    "- test-only | tidy the fixture in tests/a.py\n"
    "applied | abc1234 | extract-function\tsubject\n"
    "not-done | budget-spent | split parse() in src/parse.py\n"
)


@pytest.fixture
def github():
    return importlib.import_module("veri.github")


def test_files_one_issue_with_both_labels_and_every_out_of_bounds_and_not_done_row(
        tmp_path, monkeypatch, github, run_cli):
    created, labelled = [], []

    def create(title, body):
        created.append((title, body))
        return "https://github.com/o/r/issues/77\n"

    monkeypatch.setattr(github, "gh_issue_create", create)
    monkeypatch.setattr(github, "gh_issue_add_label", lambda number, label: labelled.append(label))
    monkeypatch.setattr(github, "gh_label_ensure", lambda label: None)
    monkeypatch.setattr(github, "gh_issue_list", lambda *args: "[]")
    monkeypatch.setattr(github, "gh_rest_list", lambda *args, **kwargs: "[]")
    owed = tmp_path / "owed.md"
    owed.write_text(OWED)
    refactor_candidates = importlib.import_module("veri.refactor_candidates")

    code, out, err = run_cli(refactor_candidates, ["42", str(owed)])

    assert (code, out.strip()) == (0, "https://github.com/o/r/issues/77")
    assert [title for title, _ in created] == ["Refactor candidates left by #42"]
    body = created[0][1]
    assert any("rename helper in lib/util.py" in line for line in body.split("\n"))
    assert any("budget-spent" in line and "split parse() in src/parse.py" in line for line in body.split("\n"))
    assert "tidy the fixture" not in body and "extract-function" not in body
    assert sorted(labelled) == ["refactor", "refactor-owed"]


@pytest.mark.parametrize("argv", [[], ["42"], ["42", "owed.md", "extra"]])
def test_a_wrong_argument_count_prints_usage_on_stderr_and_exits_2_filing_nothing(
        argv, monkeypatch, github, run_cli):
    created = []
    monkeypatch.setattr(github, "gh_issue_create", lambda title, body: created.append(title) or "")
    refactor_candidates = importlib.import_module("veri.refactor_candidates")

    code, out, err = run_cli(refactor_candidates, argv)

    assert (code, out, created) == (2, "", [])
    assert err.startswith("usage:") and "refactor-candidates.sh" in err


def test_body_groups_rows_under_their_module_else_unsorted(tmp_path, monkeypatch, github, run_cli):
    created = []
    monkeypatch.setattr(github, "gh_issue_create", lambda title, body: created.append(body) or "https://github.com/o/r/issues/5\n")
    monkeypatch.setattr(github, "gh_issue_add_label", lambda number, label: None)
    monkeypatch.setattr(github, "gh_label_ensure", lambda label: None)
    monkeypatch.setattr(github, "gh_issue_list", lambda *args: "[]")
    monkeypatch.setattr(github, "gh_rest_list", lambda *args, **kwargs: "[]")
    owed = tmp_path / "owed.md"
    owed.write_text(
        "- out-of-bounds | rename helper in lib/util.py\n"
        "not-done | budget-spent | split parse() in src/parse.py\n"
        "- out-of-bounds | drop dead branch in lib/other.py\n"
        "not-done | no-predicate | simplify the naming overall\n")
    refactor_candidates = importlib.import_module("veri.refactor_candidates")

    code, _, _ = run_cli(refactor_candidates, ["42", str(owed)])

    assert code == 0
    heading_of = {}
    heading = None
    for line in created[0].split("\n"):
        if not line.strip():
            continue
        if line.startswith("- "):
            heading_of[line] = heading
        else:
            heading = line
    expected = {"util.py": "lib", "other.py": "lib", "parse.py": "src", "naming": "unsorted"}
    for needle, module in expected.items():
        (row,) = [r for r in heading_of if needle in r]
        assert heading_of[row] is not None and module in heading_of[row], (row, heading_of[row])
