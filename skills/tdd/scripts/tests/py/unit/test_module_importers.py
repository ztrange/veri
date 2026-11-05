"""Source-text audit: every veri module and every tests/py helper module has an importer besides its own suite.

Each case's subject is source text: it reads the files of the repository as text and never runs them.
"""
import re

import pytest

from conftest import ROOT, SCRIPTS

KEPT = {}

MENTION = re.compile(r"\bimport\b|\bfrom\b|\.py\b|\bveri\.|PYTEST_PLUGINS")
WORD = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def read(path):
    return path.read_bytes().decode("utf-8", "surrogateescape")


def modules(scripts):
    veri = sorted(p for p in (scripts / "veri").glob("*.py") if p.name != "__init__.py")
    helpers = sorted(p for p in (scripts / "tests" / "py").glob("*.py")
                     if p.name != "conftest.py" and not p.name.startswith("test_"))
    return veri + helpers


def carriers(scripts, root):
    files = [p for p in scripts.rglob("*") if p.is_file() and p.suffix in (".py", ".sh") and "__pycache__" not in p.parts]
    return files + [root / "Makefile"]


def orphans(scripts, root, kept):
    """Modules named, on an import-like line, by no file but the module itself and its own suite."""
    mentions = {}
    for path in carriers(scripts, root):
        if path.name == "test_module_importers.py" or not path.is_file():
            continue
        for line in read(path).splitlines():
            if MENTION.search(line):
                for word in set(WORD.findall(line)):
                    mentions.setdefault(word, set()).add(path)
    found = []
    for module in modules(scripts):
        own = {module, module.parent / f"test_{module.stem}.py", scripts / "tests" / "py" / f"test_{module.stem}.py",
               scripts / "tests" / "py" / "unit" / f"test_{module.stem}.py",
               scripts / "tests" / "py" / f"test_{module.stem}_process.py"}
        if not mentions.get(module.stem, set()) - own:
            found.append(module)
    named = {m.relative_to(scripts).as_posix() for m in found}
    unwarranted = sorted(set(kept) - named)
    return ([f"{m.relative_to(scripts).as_posix()} is imported by nothing but its own suite" for m in found
             if m.relative_to(scripts).as_posix() not in kept]
            + [f"KEPT names {k}, which the scan does not find orphaned" for k in unwarranted])


@pytest.mark.tree_audit("every .py and .sh file under skills/tdd/scripts")
def test_every_module_has_an_importer_besides_its_own_suite_or_is_kept():
    assert orphans(SCRIPTS, ROOT, KEPT) == []
