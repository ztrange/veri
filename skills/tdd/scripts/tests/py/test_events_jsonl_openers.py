"""Which modules of veri/ open a run's events.jsonl."""
import pytest


@pytest.mark.tree_audit("every module of veri/")
def test_no_module_but_event_and_event_log_opens_events_jsonl():
    import ast

    from conftest import SCRIPTS

    openers = []
    for source in sorted((SCRIPTS / "veri").glob("*.py")):
        if source.name in ("event.py", "event_log.py"):
            continue
        for call in ast.walk(ast.parse(source.read_text(encoding="utf-8"))):
            if isinstance(call, ast.Call) and getattr(call.func, "id", None) == "open" and any(
                    isinstance(node, ast.Constant) and isinstance(node.value, str)
                    and node.value.endswith("events.jsonl")
                    for node in ast.walk(call)):
                openers.append(source.name)

    assert openers == []
