"""No module of veri/ and no helper module of tests/py/ stands with no user (#2692, PRD 011 R4)."""
import pathlib
import re
import shutil

import pytest

from conftest import ROOT, SCRIPTS

# module stem -> the kept case, in its own suite, that applies it to the real tree: no other file imports it.
KEPT = {
    "fast_tier_guard": "test_fast_tier_guard.py::test_every_guard_clean_pytest_file_lives_under_tests_py_unit_and_every_file_the_guard_names_stays_outside_it",
}

HELPER_DIRS = ("veri", "tests/py")
SELF = pathlib.Path(__file__).name


def _text(path):
    return path.read_text(encoding="utf-8", errors="replace")


def _users_of(stem):
    word = r"(?<![\w])%s(?![\w])" % re.escape(stem)
    return re.compile(
        r"^[ \t]*(?:from|import)[ \t][^\n]*" + word
        + r"|import_module\(\s*[\"'](?:\w+\.)*" + stem + r"[\"']"
        + r"|__import__\(\s*[\"'](?:\w+\.)*" + stem + r"[\"']"
        + r"|^[^\n]*PYTEST_PLUGINS[^\n]*[\"']" + stem + r"[\"']"
        + r"|/" + stem + r"\.py", re.MULTILINE)


def unimported(scripts, makefile=None):
    """Helper modules under `scripts` that only their own suite imports, or nothing does, as paths."""
    sources = [p for p in scripts.rglob("*") if p.suffix in (".py", ".sh") and "__pycache__" not in p.parts]
    if makefile is not None:
        sources.append(makefile)
    texts = {p: _text(p) for p in sources if p.name != SELF}
    found = []
    for directory in HELPER_DIRS:
        for module in sorted((scripts / directory).glob("*.py")):
            stem = module.stem
            if module.name.startswith(("test_", "__")) or module.name == "conftest.py" or stem in KEPT:
                continue
            own = {"test_%s.py" % stem, "test_%s_process.py" % stem}
            pattern = _users_of(stem)
            if not any(pattern.search(text) for p, text in texts.items() if p != module and p.name not in own):
                found.append(module)
    return found


def _named(scripts, makefile=None):
    return sorted(str(p.relative_to(scripts)) for p in unimported(scripts, makefile))


@pytest.mark.tree_audit("every module under skills/tdd/scripts/veri and tests/py, and every file that could import one")
def test_every_veri_module_and_tests_py_helper_has_a_user_besides_its_own_suite_2692():
    assert _named(SCRIPTS, ROOT / "Makefile") == []


@pytest.mark.tree_audit("a copy of skills/tdd/scripts, to plant modules in")
def test_a_helper_with_only_its_own_suite_and_a_veri_module_with_none_are_each_named_by_file_2692(tmp_path):
    scripts = tmp_path / "scripts"
    shutil.copytree(SCRIPTS, scripts, ignore=shutil.ignore_patterns("__pycache__"))
    assert _named(scripts) == []
    (scripts / "tests/py/lonely_helper.py").write_text("VALUE = 1\n")
    (scripts / "tests/py/unit/test_lonely_helper.py").write_text("import lonely_helper\n")
    (scripts / "veri/nobody_calls.py").write_text("VALUE = 2\n")
    assert _named(scripts) == ["tests/py/lonely_helper.py", "veri/nobody_calls.py"]
    (scripts / "veri/nobody_calls.py").unlink()
    (scripts / "tests/py/unit/test_some_use.py").write_text("import nobody_calls\n")
    (scripts / "veri/nobody_calls.py").write_text("VALUE = 2\n")
    assert _named(scripts) == ["tests/py/lonely_helper.py"]
