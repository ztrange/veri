"""Small cases for veri.role_state: role-state.sh's verbs, run in-process."""
import importlib


def test_issue_3648_lane_with_no_verb_prints_usage_and_exits_2(tmp_path, monkeypatch, run_cli):
    role_state = importlib.import_module("veri.role_state")
    monkeypatch.setattr(role_state.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))

    code, _, err = run_cli(role_state, ["dev", "--lane", "main"])

    assert (code, err) == (2, role_state.USAGE)


def test_issue_3648_bare_role_with_no_verb_prints_usage_and_exits_2(tmp_path, monkeypatch, run_cli):
    role_state = importlib.import_module("veri.role_state")
    monkeypatch.setattr(role_state.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))

    code, _, err = run_cli(role_state, ["dev"])

    assert (code, err) == (2, role_state.USAGE)


def test_issue_3676_lane_flag_with_no_lane_prints_usage_and_exits_2_writing_no_state(tmp_path, monkeypatch, run_cli):
    role_state = importlib.import_module("veri.role_state")
    monkeypatch.setattr(role_state.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))

    code, _, err = run_cli(role_state, ["dev", "--lane"])

    assert (code, err, list(tmp_path.iterdir())) == (2, role_state.USAGE, [])


def test_issue_3752_add_numbers_items_only_from_list_lines_past_a_spaced_coordinator_line(tmp_path, monkeypatch, run_cli):
    role_state = importlib.import_module("veri.role_state")
    monkeypatch.setattr(role_state.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "role-dev.state").write_text("coordinator=veri coord\nmessage 1 2026-11-13T00:00:00 hello\n")

    code, out, _ = run_cli(role_state, ["dev", "add", "message", "x"])

    assert (code, out) == (0, "2\n")


def test_issue_3752_add_numbers_the_first_item_1_when_only_a_spaced_coordinator_line_is_present(tmp_path, monkeypatch, run_cli):
    role_state = importlib.import_module("veri.role_state")
    monkeypatch.setattr(role_state.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "role-dev.state").write_text("coordinator=veri coord\n")

    code, out, _ = run_cli(role_state, ["dev", "add", "message", "x"])

    assert (code, out) == (0, "1\n")


def test_issue_4100_set_auto_on_and_off_are_recorded_in_order_and_exit_0(tmp_path, monkeypatch, run_cli):
    role_state = importlib.import_module("veri.role_state")
    monkeypatch.setattr(role_state.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))

    codes = [run_cli(role_state, ["dev", "--lane", "mu", "set", "auto", value])[0] for value in ("on", "off", "on")]

    state = (tmp_path / ".tdd" / "role-dev-mu.state").read_text()
    assert (codes, state) == ([0, 0, 0], "auto=on\nauto=off\nauto=on\n")


def test_issue_4100_set_auto_with_a_value_other_than_on_or_off_exits_2_writing_nothing(tmp_path, monkeypatch, run_cli):
    role_state = importlib.import_module("veri.role_state")
    monkeypatch.setattr(role_state.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))

    results = [run_cli(role_state, ["dev", "set", "auto", value]) for value in ("yes", "", "ON", "on ")]

    assert (results, (tmp_path / ".tdd" / "role-dev.state").exists()) == ([(2, "", role_state.USAGE)] * 4, False)


def test_issue_3241_dev_recovered_removes_the_roles_reset_marker_and_keeps_a_lanes(tmp_path, monkeypatch, run_cli):
    role_state = importlib.import_module("veri.role_state")
    monkeypatch.setattr(role_state.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    (tdd / "reset-request-dev").write_text("2026-11-12T10:00:00\n")
    (tdd / "reset-request-dev-mu").write_text("2026-11-12T10:00:00\n")

    code, _, _ = run_cli(role_state, ["dev", "recovered"], env={"CLAUDE_CODE_SESSION_ID": "sess-1"})

    assert (code, sorted(p.name for p in tdd.glob("reset-request-*"))) == (0, ["reset-request-dev-mu"])


def test_issue_3241_dev_recovered_clears_refused_at_and_refused_now_at_from_the_state_file_and_keeps_its_other_lines(tmp_path, monkeypatch, run_cli):
    role_state = importlib.import_module("veri.role_state")
    monkeypatch.setattr(role_state.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))
    monkeypatch.setattr(role_state, "now", lambda: "2026-11-12T10:00:00")
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    state = tdd / "role-dev.state"
    state.write_text("baseline=1000\nrefused-at=2026-11-12T09:30:00\nrefused-now-at=2026-11-12T09:40:00\n")

    code, _, _ = run_cli(role_state, ["dev", "recovered"], env={"CLAUDE_CODE_SESSION_ID": "sess-1"})

    assert (code, state.read_text().splitlines()) == (0, [
        "baseline=1000", "recovered-at=2026-11-12T10:00:00", "session-id=sess-1"])


def test_issue_3241_usage_names_every_set_field(run_cli):
    role_state = importlib.import_module("veri.role_state")

    code, _, err = run_cli(role_state, [])

    missing = [w for w in role_state.SET_FIELDS if w not in err]
    assert (code, missing) == (2, [])


def test_read_lines_returns_the_role_files_lines_or_none_when_missing_for_the_main_trees_lane_file(tmp_path, monkeypatch):
    role_state = importlib.import_module("veri.role_state")
    monkeypatch.setattr(role_state.run_dir, "main_tree", lambda **_: str(tmp_path))
    assert role_state.read_lines("dev", "mu") is None
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "role-dev-mu.state").write_text("n=2\nlane=mu\n")
    (tmp_path / ".tdd" / "role-dev.state").write_text("n=9\n")

    assert role_state.read_lines("dev", "mu") == ["n=2", "lane=mu"]
    assert role_state.read_lines("dev") == ["n=9"]


def _state(lines):
    return importlib.import_module("veri.role_state").State(lines)


def test_state_last_n_is_the_last_n_line_as_an_int():
    assert _state(["n=2", "lane=mu", "n=0007"]).last_n() == 7


def test_state_last_n_with_no_n_line_raises_malformed_of_kind_n_missing():
    role_state = importlib.import_module("veri.role_state")
    try:
        _state(["lane=mu"]).last_n()
    except role_state.Malformed as why:
        assert (why.kind, why.line) == ("n-missing", None)
    else:
        raise AssertionError("no Malformed raised")


def test_state_last_n_that_int_refuses_raises_malformed_of_kind_n_carrying_the_line():
    role_state = importlib.import_module("veri.role_state")
    try:
        _state(["n=2", "n=²"]).last_n()
    except role_state.Malformed as why:
        assert (why.kind, why.line) == ("n", "n=²")
    else:
        raise AssertionError("no Malformed raised")


def test_state_timed_ns_lists_value_and_expiry_of_each_timed_n_line_in_file_order():
    state = _state(["n=1", "timed-n 1 2026-11-07T10:00:00 3 until 2026-11-08T10:00:00",
                    "timed-n 2 2026-11-07T10:01:00 5 until 2026-11-09T10:00:00"])
    assert [value for value, _ in state.timed_ns()] == [3, 5]
    assert state.timed_ns()[0][1] < state.timed_ns()[1][1]


def test_state_timed_ns_raises_malformed_of_kind_timed_n_carrying_the_bad_line():
    role_state = importlib.import_module("veri.role_state")
    for bad in ("timed-n 1 2026-11-07T10:00:00", "timed-n 1 2026-11-07T10:00:00 x until nowhere"):
        try:
            _state([bad]).timed_ns()
        except role_state.Malformed as why:
            assert (why.kind, why.line) == ("timed-n", bad)
        else:
            raise AssertionError("no Malformed raised for " + bad)


def test_state_override_numbers_gives_the_first_number_each_override_names_or_none():
    state = _state(["override dev-1 2026-11-07T10:00:00 take #15 first", "override dev-2 2026-11-07T10:01:00 no number"])
    assert state.override_numbers() == ["15", None]


def test_state_override_numbers_raises_malformed_of_kind_override_for_a_line_of_fewer_than_4_fields():
    role_state = importlib.import_module("veri.role_state")
    try:
        _state(["override dev-1 2026-11-07T10:00:00"]).override_numbers()
    except role_state.Malformed as why:
        assert (why.kind, why.line) == ("override", "override dev-1 2026-11-07T10:00:00")
    else:
        raise AssertionError("no Malformed raised")


def test_state_field_is_the_last_value_of_a_key_line_or_none():
    state = _state(["n=2", "coordinator=a", "coordinator=b", "decision 1 2026-11-07T10:00:00 x=y"])
    assert (state.field("coordinator"), state.field("lane"), state.field("decision 1 2026-11-07T10:00:00 x")) == ("b", None, "y")


def test_state_values_are_every_value_of_a_key_line_in_file_order():
    state = _state(["reset-at=a", "reset-at-old=x", "recovered-at=b", "reset-at", "decision 1 t reset-at=y", "reset-at=c=d"])

    assert (state.values("reset-at"), state.values("n")) == (["a", "c=d"], [])


def test_state_items_are_the_raw_lines_of_the_named_kinds_in_file_order():
    lines = ["n=1", "timed-n 1 t 3 until x", "override 2 t y", "message 3 t z", "decision 4 t w"]
    state = _state(lines)
    assert (state.items("timed-n", "override"), state.items("decision")) == (lines[1:3], [lines[4]])


def test_dev_set_n_with_a_non_ascii_digit_exits_2_with_the_usage_line_and_writes_nothing(tmp_path, monkeypatch, run_cli):
    role_state = importlib.import_module("veri.role_state")
    monkeypatch.setattr(role_state.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))
    (tmp_path / ".tdd").mkdir()
    state = tmp_path / ".tdd" / "role-dev.state"
    state.write_text("n=2\n")

    code, out, err = run_cli(role_state, ["dev", "set", "n", "²"])

    assert (code, out, err, state.read_text()) == (2, "", role_state.USAGE, "n=2\n")


def test_dev_set_n_zero_and_a_padded_number_are_written(tmp_path, monkeypatch, run_cli):
    role_state = importlib.import_module("veri.role_state")
    monkeypatch.setattr(role_state.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))

    codes = [run_cli(role_state, ["dev", "set", "n", value])[0] for value in ("0", "007")]

    assert (codes, (tmp_path / ".tdd" / "role-dev.state").read_text()) == ([0, 0], "n=0\nn=007\n")


def test_issue_4465_dev_request_reset_exits_2_as_an_unknown_verb_writing_nothing(tmp_path, monkeypatch, run_cli):
    role_state = importlib.import_module("veri.role_state")
    monkeypatch.setattr(role_state.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))

    code, out, err = run_cli(role_state, ["dev", "request-reset"])

    assert (code, out, err, list(tmp_path.iterdir())) == (2, "", role_state.USAGE, [])


def test_issue_4465_dev_set_resetter_exits_2_as_an_unknown_field_writing_nothing(tmp_path, monkeypatch, run_cli):
    role_state = importlib.import_module("veri.role_state")
    monkeypatch.setattr(role_state.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))

    code, out, err = run_cli(role_state, ["dev", "set", "resetter", "sess-1"])

    assert (code, out, err, list(tmp_path.iterdir())) == (2, "", role_state.USAGE, [])


def test_issue_4465_dev_set_refuses_each_role_growth_only_field_as_unknown_and_the_usage_line_names_none(tmp_path, monkeypatch, run_cli):
    role_state = importlib.import_module("veri.role_state")
    monkeypatch.setattr(role_state.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))
    fields = ["session", "transcript", "baseline", "baseline-at", "refused-at", "refused-now-at"]

    results = [run_cli(role_state, ["dev", "set", f, "v"]) for f in fields]

    named = [f for f in fields if f in role_state.USAGE.split(" set ")[1].split(">")[0].split("|")]
    assert (results, named, list(tmp_path.iterdir())) == ([(2, "", role_state.USAGE)] * 6, [], [])
