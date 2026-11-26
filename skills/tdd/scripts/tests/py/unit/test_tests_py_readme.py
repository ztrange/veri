"""The map of the test side (tests/py/README.md) lists every helper module and every conftest fixture, and only those.

A helper module is a `.py` file directly under tests/py that is neither a `test_*.py` suite nor conftest.py. The README keeps one
bullet per helper under "## Helper modules" (its first backticked token is `name.py`) and one per fixture under
"## conftest fixtures" (its first backticked token is the fixture name). Detection is pure functions over names and text,
exercised on small inputs below; the tree cases read the real directory and conftest through `VeriModules`.
"""
import ast
import pathlib
import re

import pytest

from tree_index import VeriModules

PY = pathlib.Path(__file__).resolve().parents[1]
README = PY / "README.md"
HELPERS = "Helper modules"
FIXTURES = "conftest fixtures"


def _helper_modules(stems):
    """The stems that are helper modules: not a suite, not conftest."""
    return sorted(stem for stem in stems if stem != "conftest" and not stem.startswith("test_") and stem != "__init__")


def _is_fixture(decorator):
    target = decorator.func if isinstance(decorator, ast.Call) else decorator
    return isinstance(target, ast.Attribute) and target.attr == "fixture" or isinstance(target, ast.Name) and target.id == "fixture"


def _fixture_names(tree):
    """The top-level functions of `tree` decorated `pytest.fixture` or `pytest.fixture(...)`."""
    return sorted(node.name for node in tree.body
                  if isinstance(node, ast.FunctionDef) and any(_is_fixture(d) for d in node.decorator_list))


def _listed(readme, heading):
    """The first backticked token of each `- ` bullet under `## <heading>`, up to the next `## `."""
    found, inside = [], False
    for line in readme.splitlines():
        if line.startswith("## "):
            inside = line[3:].strip() == heading
        elif inside:
            bullet = re.match(r"- `([^`]+)`", line)
            if bullet:
                found.append(bullet.group(1))
    return found


def _problems(defined, listed, kind):
    """What differs between the names that exist and the names the README lists."""
    return ([f"README.md has no `{name}` line for the {kind}" for name in sorted(set(defined) - set(listed))]
            + [f"README.md lists the {kind} `{name}`, which does not exist" for name in sorted(set(listed) - set(defined))])


def test_a_helper_module_is_a_py_file_that_is_neither_a_suite_nor_conftest():
    assert _helper_modules(["conftest", "test_a", "tree_index", "__init__", "pass_marker"]) == ["pass_marker", "tree_index"]


def test_fixtures_are_the_top_level_functions_decorated_with_pytest_fixture_bare_or_called():
    tree = ast.parse(
        "import pytest\n"
        "@pytest.fixture\ndef bare(): pass\n"
        "@pytest.fixture(autouse=True)\ndef called(): pass\n"
        "@fixture\ndef imported(): pass\n"
        "def plain(): pass\n"
        "@other.decorator\ndef decorated(): pass\n"
        "class K:\n    @pytest.fixture\n    def nested(self): pass\n")

    assert _fixture_names(tree) == ["bare", "called", "imported"]


def test_listed_names_are_the_first_backticked_token_of_each_bullet_under_the_heading_only():
    readme = ("# Map\n\n## Helper modules\n\n- `a.py`: one, see `b.py`\n- `b.py`: two\nprose with `c.py`\n\n"
              "## conftest fixtures\n\n- `fx`: three\n\n## Other\n\n- `d.py`: not listed\n")

    assert (_listed(readme, "Helper modules"), _listed(readme, "conftest fixtures"), _listed(readme, "Absent")) == (
        ["a.py", "b.py"], ["fx"], [])


def test_a_name_without_a_line_and_a_line_without_a_name_are_each_a_problem_and_equal_sets_are_none():
    assert _problems(["a", "b"], ["b", "c"], "helper") == [
        "README.md has no `a` line for the helper", "README.md lists the helper `c`, which does not exist"]
    assert _problems(["a"], ["a"], "helper") == []


@pytest.mark.tree_audit("the files directly under skills/tdd/scripts/tests/py")
def test_every_helper_module_has_a_line_in_the_readme_and_the_readme_lists_no_other():
    defined = [stem + ".py" for stem in _helper_modules(VeriModules(PY).names)]

    assert _problems(defined, _listed(README.read_text(), HELPERS), "helper module") == []


@pytest.mark.tree_audit("conftest.py")
def test_every_conftest_fixture_has_a_line_in_the_readme_and_the_readme_lists_no_other():
    defined = _fixture_names(VeriModules(PY).tree("conftest"))

    assert _problems(defined, _listed(README.read_text(), FIXTURES), "fixture") == []
