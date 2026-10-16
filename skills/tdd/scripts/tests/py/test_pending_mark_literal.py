"""Source-text audits of where the ledger's pending mark and step box are spelled.

Each case's subject is source text: it reads the files under skills/tdd/scripts as text and
never runs them.
"""
import pathlib
import pytest
import re

from conftest import SCRIPTS

MARK = " ⟂ refactor pending"
CARRIERS = ("lib/ledger.sh", "veri/ledger.py")
COMMENT = re.compile(r"^\s*#")
BOX = (
    r"\\\[\(?([ xX]|\[[^]]*\])\)?\\\]",
    r"'\[x\]'",
    r'"- \[[ x]\] "',
)


def read(path):
    return path.read_bytes().decode("utf-8", "surrogateescape")


def sources():
    found = sorted(p for pattern in ("*.sh", "*.py") for p in SCRIPTS.rglob(pattern))
    return [(str(p.relative_to(SCRIPTS)), p) for p in found if p.relative_to(SCRIPTS).parts[0] != "tests"]


@pytest.mark.tree_audit("every .sh and .py file under skills/tdd/scripts outside tests/")
def test_the_pending_mark_is_spelled_in_lib_ledger_sh_and_veri_ledger_py_only():
    """Its subject is source text: the files under skills/tdd/scripts, read as text."""
    problems = [f"{name} carries the pending mark" for name, path in sources() if name not in CARRIERS and MARK in read(path)]
    if MARK not in read(SCRIPTS / "lib/ledger.sh"):
        problems.append("lib/ledger.sh does not carry the pending mark")

    assert problems == []


def test_the_step_line_pattern_is_spelled_on_one_line_of_lib_ledger_sh():
    """Its subject is source text: lib/ledger.sh, read as text."""
    spellers = [
        f"lib/ledger.sh:{number}:{line}"
        for number, line in enumerate(read(SCRIPTS / "lib/ledger.sh").split("\n"), 1)
        if any(box in line for box in ("\\[", "[x]", "[X]", "[ ]")) and not COMMENT.match(line)
    ]

    assert len(spellers) == 1, spellers


@pytest.mark.tree_audit("every .sh and .py file under skills/tdd/scripts outside tests/")
def test_no_script_or_module_but_lib_ledger_sh_and_veri_ledger_py_and_no_line_of_skill_md_spells_a_box():
    """Its subject is source text: the files under skills/tdd/scripts and SKILL.md, read as text."""
    pattern = re.compile("|".join(f"(?:{b})" for b in BOX))
    problems = []
    for name, path in sources():
        if name in CARRIERS:
            continue
        for number, line in enumerate(read(path).split("\n"), 1):
            if pattern.search(line) and not COMMENT.match(line):
                problems.append(f"{name}:{number} spells a box")
    for number, line in enumerate(read(SCRIPTS.parent / "SKILL.md").split("\n"), 1):
        if pattern.search(line):
            problems.append(f"SKILL.md:{number} spells a box")

    assert problems == []
