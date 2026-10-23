"""Which modules of veri/ open a run's events.jsonl."""
import ast

import pytest


def opens_events_jsonl(source):
    for call in ast.walk(ast.parse(source)):
        if isinstance(call, ast.Call) and (
                getattr(call.func, "id", None) == "open"
                or getattr(call.func, "attr", None) in ("open", "read_text", "read_bytes")
        ) and any(
                isinstance(node, ast.Constant) and isinstance(node.value, str)
                and node.value.endswith("events.jsonl")
                for node in ast.walk(call)):
            return True
    return False


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
