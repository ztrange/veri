"""The events.jsonl openers audit catches each shape of opener."""
import pytest


@pytest.mark.tree_audit("none: feeds the audit a source string")
def test_openers_audit_reports_a_module_opening_events_jsonl_through_path_open():
    from test_events_jsonl_openers import opens_events_jsonl

    source = (
        "from pathlib import Path\n"
        "def read(run):\n"
        "    return Path(run, 'events.jsonl').open(encoding='utf-8')\n"
    )

    assert opens_events_jsonl(source)


@pytest.mark.tree_audit("none: feeds the audit a source string")
@pytest.mark.parametrize("call", ["read_text", "read_bytes"])
def test_openers_audit_reports_a_module_reading_events_jsonl_through_path_read(call):
    from test_events_jsonl_openers import opens_events_jsonl

    source = (
        "from pathlib import Path\n"
        "def read(run):\n"
        f"    return Path(run, 'events.jsonl').{call}()\n"
    )

    assert opens_events_jsonl(source)


@pytest.mark.tree_audit("none: feeds the audit a source string")
def test_openers_audit_reports_a_module_opening_an_events_jsonl_path_held_in_a_variable():
    from test_events_jsonl_openers import opens_events_jsonl

    source = (
        "from pathlib import Path\n"
        "def read(run):\n"
        "    log = Path(run) / 'events.jsonl'\n"
        "    return open(log, encoding='utf-8')\n"
    )

    assert opens_events_jsonl(source)
