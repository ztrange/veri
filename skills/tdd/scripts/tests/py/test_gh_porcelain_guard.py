import ast

import pytest

PORCELAIN = {"issue", "pr", "label", "auth"}
GRAPHQL_HOMES = {"github.py", "merge_common.py"}
GH_CALLERS = {"run_gh", "gh_probe"}


def _text(node):
    return node.value if isinstance(node, ast.Constant) and isinstance(node.value, str) else None


def _porcelain_use(node):
    """True for run_gh/gh_probe("<porcelain>", ...) and for a ["gh", "<porcelain>", ...] argv literal."""
    if isinstance(node, ast.Call):
        name = node.func.id if isinstance(node.func, ast.Name) else getattr(node.func, "attr", "")
        if name in GH_CALLERS and node.args and _text(node.args[0]) in PORCELAIN:
            return True
    if isinstance(node, (ast.List, ast.Tuple)) and len(node.elts) > 1:
        return _text(node.elts[0]) == "gh" and _text(node.elts[1]) in PORCELAIN
    return False


def _mentions_graphql(source, node):
    return "graphql" in (ast.get_source_segment(source, node) or "").lower()


def _on_graphql_branch(source, chain):
    """Inside a class naming graphql, or in a function holding an `if` that tests the graphql driver."""
    if any(isinstance(n, ast.ClassDef) and "graphql" in n.name.lower() for n in chain):
        return True
    function = next((n for n in reversed(chain) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))), None)
    if function is None:
        return False
    return any(isinstance(n, ast.If) and _mentions_graphql(source, n.test) for n in ast.walk(function))


def _breaches(path, source, tree):
    found = []

    def visit(node, chain):
        if _porcelain_use(node) and (path.name not in GRAPHQL_HOMES or not _on_graphql_branch(source, chain)):
            found.append("%s:%d" % (path, node.lineno))
        for child in ast.iter_child_nodes(node):
            visit(child, chain + [node])

    visit(tree, [])
    return found


@pytest.mark.tree_audit("skills/tdd/scripts/veri")
def test_issue_4667_no_veri_module_calls_gh_porcelain_off_the_graphql_branch(veri_modules_index):
    index = veri_modules_index
    breaches = [b for name in index.names
                for b in _breaches(index.path(name), index.text(name), index.tree(name))]
    assert not breaches, "gh issue/pr/label/auth porcelain reached off the graphql branch at: " + ", ".join(breaches)
