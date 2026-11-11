"""Small cases for veri.role_state: role-state.sh's verbs, run in-process."""
import importlib


def test_dev_set_coordinator_records_the_session_id_in_the_dev_state_file(tmp_path, monkeypatch, run_cli):
    role_state = importlib.import_module("veri.role_state")
    monkeypatch.setattr(role_state, "main_tree", lambda cwd: str(tmp_path))

    code, _, _ = run_cli(role_state, ["dev", "set", "coordinator", "sess-1234"])

    state = (tmp_path / ".tdd" / "role-dev.state").read_text()
    assert (code, "coordinator=sess-1234" in state.splitlines()) == (0, True)
