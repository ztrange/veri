"""In-process cases for veri/ci_on_pr.py, the one reader of VERI_CI_ON_PR."""
import importlib

import pytest


@pytest.fixture
def ci_on_pr():
    return importlib.import_module("veri.ci_on_pr")


def test_declared_returns_the_variable_when_it_is_1_over_a_claude_md_line_of_0(tmp_path, monkeypatch, ci_on_pr):
    (tmp_path / "CLAUDE.md").write_text("# notes\n\nveri: ci on pr: 0\n")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VERI_CI_ON_PR", "1")

    assert ci_on_pr.declared() == "1"


def test_declared_returns_the_variable_when_it_is_0_over_a_claude_md_line_of_1(tmp_path, monkeypatch, ci_on_pr):
    (tmp_path / "CLAUDE.md").write_text("# notes\n\nveri: ci on pr: 1\n")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VERI_CI_ON_PR", "0")

    assert ci_on_pr.declared() == "0"


def test_declared_returns_empty_when_claude_md_has_other_veri_lines_but_no_ci_on_pr_line(tmp_path, monkeypatch, ci_on_pr):
    (tmp_path / "CLAUDE.md").write_text("# notes\n\nveri: fast tests: make unit\nveri: all tests: make test\n")
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("VERI_CI_ON_PR", raising=False)

    assert ci_on_pr.declared() == ""


@pytest.mark.tree_audit("every module under skills/tdd/scripts/veri, to find a read of VERI_CI_ON_PR")
def test_no_module_under_veri_other_than_ci_on_pr_reads_the_variable(veri_modules_index):
    import re

    reader = re.compile(r"""(?:read|get|getenv)\(\s*["']VERI_CI_ON_PR["']|environ\[\s*["']VERI_CI_ON_PR["']""")
    readers = [name for name in veri_modules_index.names if reader.search(veri_modules_index.text(name))]
    assert "ci_on_pr" in veri_modules_index.names
    assert readers == ["ci_on_pr"]


def test_issue_4570_triggers_on_pull_request_answers_true_for_a_quoted_on_key_a_json_document_or_a_flow_mapping_root(
        tmp_path, monkeypatch, ci_on_pr):
    forms = {
        "double-quoted on": "\"on\":\n  pull_request:\n",
        "single-quoted on": "'on':\n  pull_request:\n",
        "json": "{\"on\": {\"pull_request\": {}}, \"jobs\": {}}\n",
        "flow root scalar": "{on: pull_request, jobs: {}}\n",
        "flow root list": "{on: [pull_request], jobs: {}}\n",
    }
    answers = {}
    for name, text in forms.items():
        root = tmp_path / name.replace(" ", "-")
        (root / ".github" / "workflows").mkdir(parents=True)
        (root / ".github" / "workflows" / "ci.yml").write_text(text)
        monkeypatch.chdir(root)
        answers[name] = ci_on_pr.triggers_on_pull_request()

    assert answers == {name: True for name in forms}


def test_issue_4570_pull_request_trigger_answers_false_only_for_a_workflow_read_in_full_and_none_for_one_it_did_not_read(
        ci_on_pr):
    texts = {
        "block push only": "on:\n  push:\n",
        "double-quoted push only": "\"on\":\n  push:\n",
        "single-quoted push only": "'on':\n  push:\n",
        "json push only": "{\"on\": {\"push\": {}}}\n",
        "json without on": "{\"jobs\": {}}\n",
        "flow root": "{on: push, jobs: {}}\n",
        "empty": "",
    }
    answers = {name: ci_on_pr.pull_request_trigger(text) for name, text in texts.items()}

    assert answers == {
        "block push only": False,
        "double-quoted push only": False,
        "single-quoted push only": False,
        "json push only": False,
        "json without on": None,
        "flow root": None,
        "empty": None,
    }


def test_issue_4570_triggers_on_pull_request_ignores_a_workflows_entry_that_is_not_a_yml_or_yaml_file(
        tmp_path, monkeypatch, ci_on_pr):
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (workflows / "ci.yml").write_text("on: push\n")
    (workflows / ".gitkeep").write_text("")
    (workflows / "README.md").write_text("# workflows\n")
    (workflows / "notes.yml.bak").write_text("")
    monkeypatch.chdir(tmp_path)

    assert ci_on_pr.triggers_on_pull_request() is False
