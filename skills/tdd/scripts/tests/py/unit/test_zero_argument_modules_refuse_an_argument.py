"""A module whose USAGE shows no argument refuses the first one it is handed, so a new zero-argument script cannot ignore it (#3841)."""
import ast
import re

import pytest

# Modules whose USAGE shows no argument although main takes some, each with why. A ratchet: it may shrink, never grow.
USAGE_WRONG = {
    "unreplaced_cases": "its USAGE omits the arguments it requires (<step> <report>…); the shim-usage exemption filed as #3840",
}


def literal_usage(tree):
    """The module's top-level `USAGE` from its first `usage: ` on, as text; None when it is built at import or declared nowhere."""
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "USAGE" for t in node.targets):
            try:
                value = ast.literal_eval(node.value)
            except ValueError:
                return None
            text = value.decode() if isinstance(value, bytes) else str(value)
            return text[text.index("usage: "):] if "usage: " in text else None
    return None


def shows_no_argument(usage):
    """True when `usage` names the script and nothing else but a `(…)` remark or a `< file` redirect."""
    rest = usage.split(None, 2)[2:]
    remainder = re.sub(r"\([^)]*\)|<\s+\S+", "", rest[0] if rest else "")
    return not remainder.strip()


def refuses_an_argument(tree):
    """True when the module's `main` calls `no_arguments` (as `entry.no_arguments` or imported) or tests `if argv:` first-hand."""
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "main":
            for inner in ast.walk(node):
                if isinstance(inner, ast.Call):
                    func = inner.func
                    if (isinstance(func, ast.Name) and func.id == "no_arguments") or \
                            (isinstance(func, ast.Attribute) and func.attr == "no_arguments"):
                        return True
                if isinstance(inner, ast.If) and isinstance(inner.test, ast.Name) and inner.test.id == "argv":
                    return True
    return False


def ignoring(sources):
    """Names, sorted, of the modules (name -> source text) whose USAGE shows no argument and whose main does not refuse one."""
    named = []
    for name, source in sources.items():
        tree = ast.parse(source)
        usage = literal_usage(tree)
        if usage is not None and shows_no_argument(usage) and not refuses_an_argument(tree) and name not in USAGE_WRONG:
            named.append(name)
    return sorted(named)


NO_ARGUMENTS = "import entry\nUSAGE = 'usage: x.sh'\n\ndef main(argv):\n    refused = entry.no_arguments(argv, USAGE)\n    return refused or 0\n"


@pytest.mark.parametrize("usage,expected", [
    ("usage: x.sh", True),
    ("usage: x.sh (the ledger on stdin)", True),
    ("usage: x.sh < leaf-output.txt", True),
    ("usage: x.sh (takes no arguments)", True),
    ("usage: x.sh <file>", False),
    ("usage: x.sh [--flag]", False),
    ("usage: x.sh --report", False),
    ("usage: x.sh (stdin) <file>", False),
])
def test_a_usage_shows_no_argument_only_when_nothing_but_a_remark_or_a_redirect_follows_the_script_name(usage, expected):
    assert shows_no_argument(usage) is expected


def test_a_main_that_calls_no_arguments_either_way_or_tests_if_argv_refuses_and_any_other_does_not():
    imported = "from entry import no_arguments\ndef main(argv):\n    if no_arguments(argv, 'usage: x.sh'):\n        return 2\n"
    own = "def main(argv):\n    if argv:\n        return 2\n    return 0\n"
    ignores = "def main(argv):\n    return 0\n"
    shaped_like_it = "def helper(argv):\n    no_arguments(argv, 'usage: x.sh')\ndef main(argv):\n    return 0\n"

    assert [refuses_an_argument(ast.parse(text)) for text in (NO_ARGUMENTS, imported, own, ignores, shaped_like_it)] == [
        True, True, True, False, False]


def test_a_module_is_named_when_its_usage_shows_no_argument_and_its_main_ignores_one_and_never_otherwise():
    sources = {
        "refuses": NO_ARGUMENTS,
        "ignores": "USAGE = 'usage: ignores.sh'\n\ndef main(argv):\n    return 0\n",
        "ignores_stdin": "USAGE = 'usage: ignores-stdin.sh < in.txt'\n\ndef main(argv):\n    return 0\n",
        "takes_some": "USAGE = 'usage: takes-some.sh <file>'\n\ndef main(argv):\n    return 0\n",
        "built": "USAGE = f'usage: {1}'\n\ndef main(argv):\n    return 0\n",
        "no_usage": "def main(argv):\n    return 0\n",
    }

    assert ignoring(sources) == ["ignores", "ignores_stdin"]


@pytest.mark.tree_audit("every module of skills/tdd/scripts/veri")
def test_every_module_whose_usage_shows_no_argument_refuses_one(veri_modules_index):
    named = ignoring({name: veri_modules_index.text(name) for name in veri_modules_index.names})

    assert not named, "\n".join(f"{name}.py: USAGE shows no argument but main does not refuse one (entry.no_arguments)" for name in named)


@pytest.mark.tree_audit("every module of skills/tdd/scripts/veri")
def test_every_exemption_still_names_a_module_whose_usage_shows_no_argument_and_whose_main_ignores_one(veri_modules_index):
    stale = [name for name in USAGE_WRONG
             if name not in veri_modules_index.names
             or not (usage := literal_usage(veri_modules_index.tree(name)))
             or not shows_no_argument(usage)
             or refuses_an_argument(veri_modules_index.tree(name))]

    assert not stale, f"no longer needed: {stale}"
