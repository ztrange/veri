"""Every row of every tracked REQUIREMENTS.md splits into exactly ID, Requirement and Why (#4754).

`skill_edit_step.malformed_row` and `requirements_preflight` refuse a row that does not, since #4753, so a tracked row
splitting otherwise could never be amended: an unescaped `|` inside a code span makes an extra cell.
"""
import importlib
import re
import subprocess

import pytest

import conftest
from conftest import ROOT


def row_problems(path, requirements):
    lines = requirements.read_lines(str(ROOT / path))
    for number, (line, fenced) in enumerate(zip(lines, requirements.fence_flags(lines)), 1):
        if fenced or not line.startswith("|") or not requirements.is_row(line):
            continue
        cells = requirements.table_cells(line)
        if cells == requirements.COLUMNS or all(re.fullmatch(r":?-+:?", c) for c in cells):
            continue
        # Counted as skill_edit_step.malformed_row counts a raw row: a leading and a trailing empty cell around three.
        split = requirements.split_cells(line)
        if len(split) != 5:
            yield "%s:%d %s splits into %d cells" % (path, number, split[1], len(split) - 2)


@pytest.mark.process("git: git ls-files over the repository's tracked REQUIREMENTS.md files")
@pytest.mark.tree_audit("every tracked REQUIREMENTS.md in the repository")
def test_4754_every_row_of_every_tracked_requirements_md_splits_into_id_requirement_and_why(monkeypatch, request):
    monkeypatch.setitem(conftest.STARTS_GIT_IN_REPOSITORY_EXEMPT, conftest.case_tail(request),
                        "the repository's own tracked files are the subject")
    requirements = importlib.import_module("veri.requirements")
    listed = subprocess.run(["git", "-C", str(ROOT), "ls-files", "*REQUIREMENTS.md"],
                            capture_output=True, text=True, check=True).stdout.split()
    problems = [p for path in listed for p in row_problems(path, requirements)]

    assert listed and problems == [], "\n".join(problems)
