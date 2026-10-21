"""Source-text audit of SKILL.md: no `gh issue`, `gh pr`, `gh repo` or `gh auth status` call, each of which goes through GraphQL.

Each case's subject is source text: SKILL.md, planted or shipped, read as text.
"""
import ast
import re

import pytest

from conftest import ROOT

GH_CALL = re.compile(r"(^|[^A-Za-z0-9_.-])gh\s+((issue|pr|repo)(\s|$)|auth\s+status([^A-Za-z0-9_-]|$))")


def calls(skill):
    return [
        f"SKILL.md:{number} calls a gh subcommand that goes through GraphQL: {line}"
        for number, line in enumerate(skill.read_text(encoding="utf-8", errors="surrogateescape").splitlines(), 1)
        if GH_CALL.search(line)
    ]


def plant(tmp_path, call):
    skill = tmp_path / "SKILL.md"
    skill.write_text("\n".join(["# Procedure", "", f"- `{call}` succeeds."]) + "\n", encoding="utf-8")
    return skill


def test_no_gh_issue_pr_or_repo_call_is_left_in_skill_md():
    """Its subject is source text: the shipped SKILL.md, read as text."""
    assert calls(ROOT / "skills" / "tdd" / "SKILL.md") == []


def test_a_gh_auth_status_call_planted_in_skill_md_is_named_as_file_line_and_a_clean_one_passes(tmp_path):
    """Its subject is source text: a planted SKILL.md, read as text."""
    found = calls(plant(tmp_path, "gh auth status"))
    clean = calls(plant(tmp_path, "gh api user"))

    assert ([f.split(" ")[0] for f in found], clean) == (["SKILL.md:3"], [])


def gh_starts(package):
    found = []
    for module in sorted(package.glob("*.py")):
        if module.name == "github.py":
            continue
        for node in ast.walk(ast.parse(module.read_text(encoding="utf-8", errors="surrogateescape"))):
            if isinstance(node, ast.List) and node.elts and isinstance(node.elts[0], ast.Constant) and node.elts[0].value == "gh":
                found.append(f"{module.name}:{node.lineno} starts a gh process outside the GitHub port")
    return found


def test_a_gh_process_started_outside_github_py_is_named_as_file_line_and_the_shipped_tree_passes_1974(tmp_path):
    """Its subject is source text: a planted package, read as text."""
    (tmp_path / "offender.py").write_text("import subprocess\n\nsubprocess.run(['gh', 'api', 'user'])\n", encoding="utf-8")
    (tmp_path / "github.py").write_text("import subprocess\n\nsubprocess.run(['gh', 'api', 'user'])\n", encoding="utf-8")

    assert [f.split(" ")[0] for f in gh_starts(tmp_path)] == ["offender.py:3"]


@pytest.mark.tree_audit("every module under skills/tdd/scripts/veri/")
def test_no_module_but_github_py_starts_a_gh_process_1974():
    assert gh_starts(ROOT / "skills" / "tdd" / "scripts" / "veri") == []
