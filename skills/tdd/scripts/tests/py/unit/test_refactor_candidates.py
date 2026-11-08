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


def test_never_labels_with_the_opt_in_label_or_ready_for_agent(tmp_path, monkeypatch, github, run_cli):
    labelled, ensured = [], []
    monkeypatch.setattr(github, "gh_issue_create", lambda title, body: "https://github.com/o/r/issues/9\n")
    monkeypatch.setattr(github, "gh_issue_add_label", lambda number, label: labelled.append(label))
    monkeypatch.setattr(github, "gh_label_ensure", lambda label: ensured.append(label))
    monkeypatch.setattr(github, "gh_issue_list", lambda *args: "[]")
    monkeypatch.setattr(github, "gh_rest_list", lambda *args, **kwargs: "[]")
    owed = tmp_path / "owed.md"
    owed.write_text(OWED)
    refactor_candidates = importlib.import_module("veri.refactor_candidates")

    code, _, _ = run_cli(refactor_candidates, ["42", str(owed)], env={"VERI_LABEL": "ready-for-agent"})

    assert code == 0
    assert sorted(labelled) == ["refactor", "refactor-owed"]
    assert "ready-for-agent" not in labelled + ensured


@pytest.mark.parametrize("content", [
    "- test-only | tidy the fixture in tests/a.py\napplied | abc1234 | extract-function\tsubject\n",
    None,
    "",
], ids=["applied-and-test-only", "missing", "empty"])
def test_an_owed_file_with_nothing_out_of_bounds_or_not_done_files_nothing_and_exits_3(
        content, tmp_path, monkeypatch, github, run_cli):
    writes = []
    for name in ("gh_issue_create", "gh_issue_add_label", "gh_label_ensure", "gh_issue_edit"):
        monkeypatch.setattr(github, name, lambda *args, **kwargs: writes.append(args) or "", raising=False)
    monkeypatch.setattr(github, "gh_issue_list", lambda *args: "[]")
    monkeypatch.setattr(github, "gh_rest_list", lambda *args, **kwargs: "[]")
    owed = tmp_path / "owed.md"
    if content is not None:
        owed.write_text(content)
    refactor_candidates = importlib.import_module("veri.refactor_candidates")

    code, out, err = run_cli(refactor_candidates, ["42", str(owed)])

    assert (code, out, writes) == (3, "", [])


def test_a_second_run_replaces_the_open_issues_body_found_by_its_exact_title_instead_of_creating(
        tmp_path, monkeypatch, github, run_cli):
    created, edited = [], []
    existing = [
        {"number": 11, "title": "Refactor candidates left by #4"},
        {"number": 12, "title": "Refactor candidates left by #42 and more"},
        {"number": 13, "title": "Refactor candidates left by #42"},
    ]
    monkeypatch.setattr(github, "gh_issue_list", lambda *args: __import__("json").dumps(existing))
    monkeypatch.setattr(github, "gh_rest_list", lambda *args, **kwargs: __import__("json").dumps(existing))
    monkeypatch.setattr(github, "gh_issue_create", lambda title, body: created.append(title) or "https://github.com/o/r/issues/99\n")
    monkeypatch.setattr(github, "gh_issue_add_label", lambda number, label: None)
    monkeypatch.setattr(github, "gh_label_ensure", lambda label: None)

    def edit(number, body_file):
        with open(body_file) as handle:
            edited.append((str(number), handle.read()))

    monkeypatch.setattr(github, "gh_issue_edit", edit)
    owed = tmp_path / "owed.md"
    owed.write_text(OWED)
    refactor_candidates = importlib.import_module("veri.refactor_candidates")

    code, out, err = run_cli(refactor_candidates, ["42", str(owed)])

    assert code == 0
    assert created == []
    assert [number for number, _ in edited] == ["13"]
    assert "rename helper in lib/util.py" in edited[0][1]
    assert out.strip().endswith("/issues/13")


def test_a_closed_issue_with_the_same_title_is_not_found_so_a_new_one_is_created_not_edited(
        tmp_path, monkeypatch, github, run_cli):
    created, edited = [], []
    closed = [{"number": 13, "title": "Refactor candidates left by #42", "url": "https://github.com/o/r/issues/13"}]

    def issue_list(*args):
        wanted = args[args.index("--state") + 1] if "--state" in args else "all"
        return __import__("json").dumps([] if wanted == "open" else closed)

    monkeypatch.setattr(github, "gh_issue_list", issue_list)
    monkeypatch.setattr(github, "gh_rest_list", lambda *args, **kwargs: "[]")
    monkeypatch.setattr(github, "gh_issue_create", lambda title, body: created.append(title) or "https://github.com/o/r/issues/99\n")
    monkeypatch.setattr(github, "gh_issue_add_label", lambda number, label: None)
    monkeypatch.setattr(github, "gh_label_ensure", lambda label: None)
    monkeypatch.setattr(github, "gh_issue_edit", lambda number, body_file: edited.append(number))
    owed = tmp_path / "owed.md"
    owed.write_text(OWED)
    refactor_candidates = importlib.import_module("veri.refactor_candidates")

    code, out, err = run_cli(refactor_candidates, ["42", str(owed)])

    assert (code, edited) == (0, [])
    assert created == ["Refactor candidates left by #42"]
    assert out.strip().endswith("/issues/99")


def test_a_replace_prints_the_url_github_returned_for_the_existing_issue(
        tmp_path, monkeypatch, github, run_cli):
    url = "https://github.example/acme/widgets/issues/13"
    existing = [{"number": 13, "title": "Refactor candidates left by #42", "url": url}]
    monkeypatch.setattr(github, "gh_issue_list", lambda *args: __import__("json").dumps(existing))
    monkeypatch.setattr(github, "gh_issue_edit", lambda number, body_file: None)
    owed = tmp_path / "owed.md"
    owed.write_text(OWED)
    refactor_candidates = importlib.import_module("veri.refactor_candidates")

    code, out, err = run_cli(refactor_candidates, ["42", str(owed)])

    assert code == 0
    assert out.strip() == url
