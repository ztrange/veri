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
def test_no_module_under_veri_other_than_ci_on_pr_reads_the_variable():
    import pathlib
    import re

    veri_dir = pathlib.Path(__file__).resolve().parents[3] / "veri"
    reader = re.compile(r"""(?:read|get|getenv)\(\s*["']VERI_CI_ON_PR["']|environ\[\s*["']VERI_CI_ON_PR["']""")
    modules = sorted(veri_dir.glob("*.py"))
    readers = [path.name for path in modules if reader.search(path.read_text(encoding="utf-8"))]
    assert "ci_on_pr.py" in [path.name for path in modules]
    assert readers == ["ci_on_pr.py"]
