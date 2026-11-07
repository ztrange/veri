"""Source-text audits of where the ledger's pending mark and step box are spelled.

Each case's subject is source text: it reads the files under skills/tdd/scripts as text and
never runs them.
"""
import pathlib
import pytest

from conftest import SCRIPTS

MARK = " ⟂ refactor pending"
CARRIERS = ("veri/ledger.py",)


def read(path):
    return path.read_bytes().decode("utf-8", "surrogateescape")


def sources():
    found = sorted(p for pattern in ("*.sh", "*.py") for p in SCRIPTS.rglob(pattern))
    return [(str(p.relative_to(SCRIPTS)), p) for p in found if p.relative_to(SCRIPTS).parts[0] != "tests"]


@pytest.mark.tree_audit("every .sh and .py file under skills/tdd/scripts outside tests/")
def test_the_pending_mark_is_spelled_in_veri_ledger_py_only():
    """Its subject is source text: the files under skills/tdd/scripts, read as text."""
    problems = [f"{name} carries the pending mark" for name, path in sources() if name not in CARRIERS and MARK in read(path)]
    if MARK not in read(SCRIPTS / "veri/ledger.py"):
        problems.append("veri/ledger.py does not carry the pending mark")

    assert problems == []
