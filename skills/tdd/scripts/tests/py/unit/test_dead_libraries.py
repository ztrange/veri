"""Source-text audit of skills/tdd/scripts/lib: every library is named by something that runs it.

Each case's subject is source text: it reads the files of the repository as text and never runs them.
"""
import pytest

from conftest import ROOT, SCRIPTS


def read(path):
    return path.read_bytes().decode("utf-8", "surrogateescape")


def carriers():
    shell = sorted(p for p in SCRIPTS.rglob("*.sh") if SCRIPTS / "tests" / "py" not in p.parents)
    return shell + [SCRIPTS.parent / "SKILL.md", ROOT / "Makefile"] + sorted((ROOT / ".github").rglob("*"))


@pytest.mark.tree_audit("every .sh file under skills/tdd/scripts and the files of .github")
def test_every_library_is_named_by_a_script_a_suite_the_skill_or_the_makefile():
    """Its subject is source text: the library files and the files that may source them, read as text."""
    texts = {p: read(p) for p in carriers() if p.is_file()}
    dead = [
        f"lib/{lib.name} is named by nothing that runs it"
        for lib in sorted((SCRIPTS / "lib").glob("*.sh"))
        if not any(f"lib/{lib.name}" in text for path, text in texts.items() if path != lib)
    ]

    assert dead == []
