"""The audit that every issue or PR comment a veri/ module posts passes its body through github.published (#4270)."""
import ast

import pytest

WRITERS = {"gh_issue_comment", "gh_comment_post", "gh_comment_edit"}
# github.py's own writer implementations: their body arrives already published from the caller.
WRITER_IMPLEMENTATIONS = WRITERS | {"issue_comment"}
CLI_VERBS = {("issue", "comment"), ("pr", "comment")}


def _named(func, names):
    return (isinstance(func, ast.Name) and func.id in names) or (isinstance(func, ast.Attribute) and func.attr in names)


def _published(node):
    return isinstance(node, ast.Call) and _named(node.func, {"published"})


def _text(node):
    return node.value if isinstance(node, ast.Constant) and isinstance(node.value, str) else None


def _pieces(node):
    """The string constants an argument is built from: itself, the left side of a `%` or `+`, an f-string's parts."""
    if _text(node) is not None:
        return [_text(node)]
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Mod, ast.Add)):
        return _pieces(node.left)
    if isinstance(node, ast.JoinedStr):
        return [_text(value) for value in node.values if _text(value) is not None]
    return []


def _body_value(node):
    """(True, value) when an argument is a `body=` piece: `"body=" + x`, `"body=%s" % x` or f"body={x}"."""
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Mod, ast.Add)) and (_text(node.left) or "").startswith("body="):
        return True, node.right
    if isinstance(node, ast.JoinedStr) and node.values and (_text(node.values[0]) or "").startswith("body="):
        formatted = [value.value for value in node.values if isinstance(value, ast.FormattedValue)]
        return True, formatted[0] if len(formatted) == 1 else None
    return False, None


def _verb_pairs(node):
    runs = [node.args] + [arg.elts for arg in node.args if isinstance(arg, (ast.List, ast.Tuple))]
    return any((_text(a), _text(b)) in CLI_VERBS for run in runs for a, b in zip(run, run[1:]))


class _Audit(ast.NodeVisitor):
    def __init__(self, stem):
        self.stem, self.scope, self.sites = stem, [], []

    def _flag(self, node, why):
        self.sites.append("%s.py:%d (%s)" % (self.stem, node.lineno, why))

    def _in_writer(self):
        return self.stem == "github" and any(name in WRITER_IMPLEMENTATIONS for name in self.scope)

    def visit_FunctionDef(self, node):
        self.scope.append(node.name)
        self.generic_visit(node)
        self.scope.pop()

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Constant(self, node):
        if isinstance(node.value, str) and "addComment" in node.value and not self._in_writer():
            self._flag(node, "posts through GraphQL addComment")

    def visit_Call(self, node):
        if _named(node.func, WRITERS):
            body = [k.value for k in node.keywords if k.arg == "body"] or node.args[1:2]
            if not body or not _published(body[0]):
                self._flag(node, "a comment writer's body is not a direct published() call")
        elif not self._in_writer():
            arguments = node.args + [k.value for k in node.keywords]
            if any("/comments" in piece for arg in arguments for piece in _pieces(arg)):
                for arg in arguments:
                    is_body, value = _body_value(arg)
                    if is_body and not _published(value):
                        self._flag(node, "posts to /comments with a body= that is not a direct published() call")
            if _verb_pairs(node):
                self._flag(node, "runs a gh issue/pr comment verb")
        self.generic_visit(node)


@pytest.mark.tree_audit("the modules under veri/, for every call that posts an issue or PR comment")
def test_every_comment_a_veri_module_posts_passes_its_body_through_github_published_4270(veri_modules_index):
    stray = []
    for stem in veri_modules_index.names:
        audit = _Audit(stem)
        audit.visit(veri_modules_index.tree(stem))
        stray += audit.sites

    assert stray == [], "a comment posted without github.published would publish local paths: " + ", ".join(stray)
