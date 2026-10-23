"""Which modules of veri/ open a run's events.jsonl."""
import ast

import pytest


def _names_events_jsonl(node):
    return any(
        isinstance(part, ast.Constant) and isinstance(part.value, str)
        and part.value.endswith("events.jsonl")
        for part in ast.walk(node)
    )


def _own_nodes(scope):
    pending = list(ast.iter_child_nodes(scope))
    while pending:
        node = pending.pop()
        yield node
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            pending.extend(ast.iter_child_nodes(node))


def _opens_held_or_named(scope):
    held = {
        target.id
        for assign in _own_nodes(scope)
        if isinstance(assign, ast.Assign) and _names_events_jsonl(assign.value)
        for target in assign.targets
        if isinstance(target, ast.Name)
    }
    for call in _own_nodes(scope):
        if isinstance(call, ast.Call) and (
                getattr(call.func, "id", None) == "open"
                or getattr(call.func, "attr", None) in ("open", "read_text", "read_bytes")
        ) and (
                _names_events_jsonl(call)
                or any(isinstance(node, ast.Name) and node.id in held
                       for node in ast.walk(call))
        ):
            return True
    return False


def opens_events_jsonl(source):
    tree = ast.parse(source)
    return any(
        _opens_held_or_named(scope)
        for scope in [tree, *(node for node in ast.walk(tree)
                              if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)))]
    )


@pytest.mark.tree_audit("every module of veri/")
def test_no_module_but_event_and_event_log_opens_events_jsonl():
    from conftest import SCRIPTS

    openers = [
        source.name
        for source in sorted((SCRIPTS / "veri").glob("*.py"))
        if source.name not in ("event.py", "event_log.py")
        and opens_events_jsonl(source.read_text(encoding="utf-8"))
    ]

    assert openers == []
