"""Small cases for veri.role_state: role-state.sh's verbs, run in-process."""
import importlib


def test_dev_set_coordinator_records_the_session_id_in_the_dev_state_file(tmp_path, monkeypatch, run_cli):
    role_state = importlib.import_module("veri.role_state")
    monkeypatch.setattr(role_state, "main_tree", lambda cwd: str(tmp_path))

    code, _, _ = run_cli(role_state, ["dev", "set", "coordinator", "sess-1234"])

    state = (tmp_path / ".tdd" / "role-dev.state").read_text()
    assert (code, "coordinator=sess-1234" in state.splitlines()) == (0, True)


def test_dev_drop_coordinator_removes_every_coordinator_line_and_keeps_the_rest(tmp_path, monkeypatch, run_cli):
    role_state = importlib.import_module("veri.role_state")
    monkeypatch.setattr(role_state, "main_tree", lambda cwd: str(tmp_path))
    (tmp_path / ".tdd").mkdir()
    state = tmp_path / ".tdd" / "role-dev.state"
    state.write_text("n=2\ncoordinator=sess-old\nlane=mu\ncoordinator=sess-new\n")

    code, _, _ = run_cli(role_state, ["dev", "drop", "coordinator"])

    assert (code, state.read_text()) == (0, "n=2\nlane=mu\n")


def test_dev_drop_coordinator_with_none_recorded_exits_3_and_leaves_the_file_unchanged(tmp_path, monkeypatch, run_cli):
    role_state = importlib.import_module("veri.role_state")
    monkeypatch.setattr(role_state, "main_tree", lambda cwd: str(tmp_path))
    (tmp_path / ".tdd").mkdir()
    state = tmp_path / ".tdd" / "role-dev.state"
    state.write_text("n=2\nlane=mu\n")

    code, _, _ = run_cli(role_state, ["dev", "drop", "coordinator"])

    assert (code, state.read_text()) == (3, "n=2\nlane=mu\n")


def test_issue_3648_lane_with_no_verb_prints_usage_and_exits_2(tmp_path, monkeypatch, run_cli):
    role_state = importlib.import_module("veri.role_state")
    monkeypatch.setattr(role_state, "main_tree", lambda cwd: str(tmp_path))

    code, _, err = run_cli(role_state, ["coord", "--lane", "main"])

    assert (code, err) == (2, role_state.USAGE)


def test_issue_3648_bare_role_with_no_verb_prints_usage_and_exits_2(tmp_path, monkeypatch, run_cli):
    role_state = importlib.import_module("veri.role_state")
    monkeypatch.setattr(role_state, "main_tree", lambda cwd: str(tmp_path))

    code, _, err = run_cli(role_state, ["coord"])

    assert (code, err) == (2, role_state.USAGE)


def test_issue_3676_lane_flag_with_no_lane_prints_usage_and_exits_2_writing_no_state(tmp_path, monkeypatch, run_cli):
    role_state = importlib.import_module("veri.role_state")
    monkeypatch.setattr(role_state, "main_tree", lambda cwd: str(tmp_path))

    code, _, err = run_cli(role_state, ["coord", "--lane"])

    assert (code, err, list(tmp_path.iterdir())) == (2, role_state.USAGE, [])


def test_issue_3752_add_numbers_items_only_from_list_lines_past_a_spaced_coordinator_line(tmp_path, monkeypatch, run_cli):
    role_state = importlib.import_module("veri.role_state")
    monkeypatch.setattr(role_state, "main_tree", lambda cwd: str(tmp_path))
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "role-dev.state").write_text("coordinator=veri coord\nmessage 1 2026-11-13T00:00:00 hello\n")

    code, out, _ = run_cli(role_state, ["dev", "add", "message", "x"])

    assert (code, out) == (0, "2\n")


def test_issue_3752_add_numbers_the_first_item_1_when_only_a_spaced_coordinator_line_is_present(tmp_path, monkeypatch, run_cli):
    role_state = importlib.import_module("veri.role_state")
    monkeypatch.setattr(role_state, "main_tree", lambda cwd: str(tmp_path))
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "role-dev.state").write_text("coordinator=veri coord\n")

    code, out, _ = run_cli(role_state, ["dev", "add", "message", "x"])

    assert (code, out) == (0, "1\n")


def test_issue_3241_set_accepts_each_growth_field_appending_it_to_the_state_file_and_exiting_0(tmp_path, monkeypatch, run_cli):
    role_state = importlib.import_module("veri.role_state")
    monkeypatch.setattr(role_state, "main_tree", lambda cwd: str(tmp_path))
    fields = ["session", "transcript", "baseline", "baseline-at", "refused-at", "resetter"]

    codes = [run_cli(role_state, ["coord", "set", f, "v-" + f])[0] for f in fields]

    state = (tmp_path / ".tdd" / "role-coord.state").read_text().splitlines()
    assert (codes, state) == ([0] * 6, ["%s=v-%s" % (f, f) for f in fields])
