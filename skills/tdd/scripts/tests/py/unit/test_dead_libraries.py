"""Source-text audit of skills/tdd/scripts/lib: every library is named by something that runs it.

Each case's subject is source text: it reads the files of the repository as text and never runs them.
"""
import sys

import pytest

from conftest import ROOT, SCRIPTS


def read(path):
    return path.read_bytes().decode("utf-8", "surrogateescape")


def carriers():
    shell = sorted(p for p in SCRIPTS.rglob("*.sh") if SCRIPTS / "tests" / "py" not in p.parents)
    return shell + [SCRIPTS.parent / "SKILL.md", ROOT / "Makefile"] + sorted((ROOT / ".github").rglob("*"))


def dead_libraries(libs, texts):
    """Libraries no chain of names reaches from a text outside the library directory."""
    lib_texts = {lib: texts[lib] for lib in libs if lib in texts}
    live = {lib for lib in libs if any(f"lib/{lib.name}" in t for p, t in texts.items() if p not in lib_texts)}
    grew = True
    while grew:
        grew = False
        for lib in libs:
            if lib not in live and any(f"lib/{lib.name}" in lib_texts[other] for other in live if other in lib_texts):
                live.add(lib)
                grew = True
    return [f"lib/{lib.name} is named by nothing that runs it" for lib in libs if lib not in live]


@pytest.mark.parametrize("entry, dead", [
    ("", ["lib/a.sh is named by nothing that runs it", "lib/b.sh is named by nothing that runs it"]),
    (". lib/b.sh", []),
])
def test_a_library_is_live_only_through_a_chain_from_an_entry_point(tmp_path, entry, dead):
    lib = tmp_path / "lib"
    lib.mkdir()
    a, b, main = lib / "a.sh", lib / "b.sh", tmp_path / "main.sh"
    texts = {a: "echo a", b: ". lib/a.sh", main: entry}
    assert dead_libraries([a, b], texts) == dead


@pytest.mark.tree_audit("every .sh file under skills/tdd/scripts and the files of .github")
def test_every_library_is_named_by_a_script_a_suite_the_skill_or_the_makefile():
    """Its subject is source text: the library files and the files that may source them, read as text."""
    texts = {p: read(p) for p in carriers() if p.is_file()}
    libs = sorted((SCRIPTS / "lib").glob("*.sh"))
    texts.update({lib: read(lib) for lib in libs})

    assert dead_libraries(libs, texts) == []
