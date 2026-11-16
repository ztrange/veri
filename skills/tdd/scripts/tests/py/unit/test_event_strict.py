"""VERI_EVENT_STRICT=1: event.sh and event.mark refuse an event veri/event_table.py does not allow (PRD 030.1, ET3, ET4)."""
import pytest

from veri import event


@pytest.fixture
def clone(tmp_path):
    clone = tmp_path / "clone"
    (clone / ".git").mkdir(parents=True)
    (clone / ".git" / "config").write_text('[remote "origin"]\n\turl = https://github.com/acme/widgets.git\n')
    return clone


def journals(clone, tmp_path):
    return [clone / ".tdd" / "events.jsonl", tmp_path / "runs" / "acme-widgets" / "7.jsonl"]


def write(how, clone, monkeypatch, run_cli, name, fields):
    """Writes one event through event.mark or event.sh's main, issue 7; returns (exit, stderr)."""
    if how == "mark":
        code = event.mark(str(clone), {"issue": "7"}, name, fields)
        return code, None
    code, _, err = run_cli(event, [name, *fields], env={"VERI_ISSUE": "7"}, cwd=clone)
    return code, err


@pytest.mark.parametrize("how", ["mark", "sh"])
def test_strict_refuses_an_event_name_the_table_does_not_hold(how, clone, tmp_path, monkeypatch, run_cli, capfd):
    monkeypatch.setenv("VERI_EVENT_STRICT", "1")

    code, err = write(how, clone, monkeypatch, run_cli, "no-such-event", ["pr=1"])
    err = capfd.readouterr().err if err is None else err

    assert code == 2
    assert [path for path in journals(clone, tmp_path) if path.exists() and path.read_bytes()] == []
    assert "no-such-event" in err
