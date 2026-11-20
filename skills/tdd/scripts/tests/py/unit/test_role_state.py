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


def test_issue_3241_set_accepts_each_growth_field_appending_it_to_the_state_file_and_exiting_0(tmp_path, monkeypatch, run_cli):
    role_state = importlib.import_module("veri.role_state")
    monkeypatch.setattr(role_state.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))
    fields = ["session", "transcript", "baseline", "baseline-at", "refused-at", "refused-now-at", "resetter"]

    codes = [run_cli(role_state, ["dev", "set", f, "v-" + f])[0] for f in fields]

    state = (tmp_path / ".tdd" / "role-dev.state").read_text().splitlines()
    assert (codes, state) == ([0] * 7, ["%s=v-%s" % (f, f) for f in fields])


def test_issue_3241_dev_request_reset_after_a_launch_since_recovery_records_the_time_and_writes_the_marker(tmp_path, monkeypatch, run_cli):
    role_state = importlib.import_module("veri.role_state")
    monkeypatch.setattr(role_state.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))
    monkeypatch.setattr(role_state, "now", lambda: "2026-11-12T10:00:00")
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    state = tdd / "role-dev.state"
    state.write_text("recovered-at=2026-11-12T09:00:00\n")
    (tdd / "events.jsonl").write_text('{"ts": 4102444800, "event": "conductor-start", "issue": "7"}\n')

    code, _, _ = run_cli(role_state, ["dev", "request-reset"])

    marker = (tdd / "reset-request-dev").read_text().split()
    recorded = state.read_text().splitlines()[1:]
    assert (code, marker, [l.endswith("2026-11-12T10:00:00") for l in recorded]) == (
        0, ["2026-11-12T10:00:00"], [True])


def test_issue_3241_dev_lane_request_reset_writes_the_marker_with_the_lane_suffix_and_exits_0(tmp_path, monkeypatch, run_cli):
    role_state = importlib.import_module("veri.role_state")
    monkeypatch.setattr(role_state.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))
    monkeypatch.setattr(role_state, "now", lambda: "2026-11-12T10:00:00")
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    (tdd / "role-dev-b.state").write_text("recovered-at=2026-11-12T09:00:00\n")
    (tdd / "events.jsonl").write_text('{"ts": 4102444800, "event": "conductor-start", "issue": "7"}\n')

    code, _, _ = run_cli(role_state, ["dev", "--lane", "b", "request-reset"])

    markers = sorted(p.name for p in tdd.glob("reset-request-*"))
    assert (code, markers) == (0, ["reset-request-dev-b"])


def test_issue_3241_dev_request_reset_with_nothing_launched_merged_or_decided_since_recovery_exits_1_writing_nothing(tmp_path, monkeypatch, run_cli):
    role_state = importlib.import_module("veri.role_state")
    monkeypatch.setattr(role_state.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))
    monkeypatch.setattr(role_state, "now", lambda: "2026-11-12T10:00:00")
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    state = tdd / "role-dev.state"
    state.write_text("recovered-at=2026-11-12T09:00:00\n")
    (tdd / "events.jsonl").write_text(
        '{"ts": 1000, "event": "conductor-start", "issue": "7"}\n'
        '{"ts": 1001, "event": "merged", "issue": "7"}\n')

    code, _, err = run_cli(role_state, ["dev", "request-reset"])

    assert (code, bool(err.strip()), state.read_text(), sorted(p.name for p in tdd.glob("reset-request-*"))) == (
        1, True, "recovered-at=2026-11-12T09:00:00\n", [])


def test_issue_3241_dev_request_reset_accepts_when_only_a_merged_event_in_a_run_journal_is_later_than_recovery(tmp_path, monkeypatch, run_cli):
    role_state = importlib.import_module("veri.role_state")
    monkeypatch.setattr(role_state.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))
    monkeypatch.setattr(role_state, "now", lambda: "2026-11-12T10:00:00")
    tdd = tmp_path / ".tdd"
    run_tdd = tdd / "wt" / "7" / ".tdd"
    run_tdd.mkdir(parents=True)
    (tdd / "role-dev.state").write_text("recovered-at=2026-11-12T09:00:00\n")
    (run_tdd / "events.jsonl").write_text('{"ts": 4102444800, "event": "merged", "issue": "7"}\n')

    code, _, _ = run_cli(role_state, ["dev", "request-reset"])

    marker = (tdd / "reset-request-dev").read_text().split() if (tdd / "reset-request-dev").exists() else None
    assert (code, marker) == (0, ["2026-11-12T10:00:00"])


def test_issue_3241_dev_request_reset_accepts_when_only_a_conductor_start_in_a_run_journal_is_later_than_recovery(tmp_path, monkeypatch, run_cli):
    role_state = importlib.import_module("veri.role_state")
    monkeypatch.setattr(role_state.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))
    monkeypatch.setattr(role_state, "now", lambda: "2026-11-12T10:00:00")
    tdd = tmp_path / ".tdd"
    run_tdd = tdd / "wt" / "7" / ".tdd"
    run_tdd.mkdir(parents=True)
    (tdd / "role-dev.state").write_text("recovered-at=2026-11-12T09:00:00\n")
    (run_tdd / "events.jsonl").write_text('{"ts": 4102444800, "event": "conductor-start", "issue": "7"}\n')

    code, _, _ = run_cli(role_state, ["dev", "request-reset"])

    marker = (tdd / "reset-request-dev").read_text().split() if (tdd / "reset-request-dev").exists() else None
    assert (code, marker) == (0, ["2026-11-12T10:00:00"])


def test_issue_3241_dev_request_reset_accepts_when_only_a_decision_added_to_the_state_file_is_later_than_recovery(tmp_path, monkeypatch, run_cli):
    role_state = importlib.import_module("veri.role_state")
    monkeypatch.setattr(role_state.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))
    monkeypatch.setattr(role_state, "now", lambda: "2026-11-12T10:00:00")
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    (tdd / "role-dev.state").write_text("recovered-at=2026-11-12T09:00:00\n")
    monkeypatch.setattr(role_state, "now", lambda: "2026-11-12T09:30:00")
    run_cli(role_state, ["dev", "add", "decision", "use the bus"])
    monkeypatch.setattr(role_state, "now", lambda: "2026-11-12T10:00:00")

    code, _, _ = run_cli(role_state, ["dev", "request-reset"])

    marker = (tdd / "reset-request-dev").read_text().split() if (tdd / "reset-request-dev").exists() else None
    assert (code, marker) == (0, ["2026-11-12T10:00:00"])


def test_issue_3241_dev_request_reset_accepts_when_only_a_decision_dropped_from_the_state_file_is_later_than_recovery(tmp_path, monkeypatch, run_cli):
    role_state = importlib.import_module("veri.role_state")
    monkeypatch.setattr(role_state.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    monkeypatch.setattr(role_state, "now", lambda: "2026-11-12T08:30:00")
    run_cli(role_state, ["dev", "add", "decision", "use the bus"])
    with open(tdd / "role-dev.state", "a") as f:
        f.write("recovered-at=2026-11-12T09:00:00\n")
    monkeypatch.setattr(role_state, "now", lambda: "2026-11-12T09:30:00")
    run_cli(role_state, ["dev", "drop", "decision", "1"])
    monkeypatch.setattr(role_state, "now", lambda: "2026-11-12T10:00:00")

    code, _, _ = run_cli(role_state, ["dev", "request-reset"])

    marker = (tdd / "reset-request-dev").read_text().split() if (tdd / "reset-request-dev").exists() else None
    assert (code, marker) == (0, ["2026-11-12T10:00:00"])


def test_issue_3241_dev_request_reset_refuses_when_only_a_message_was_dropped_since_recovery_but_accepts_once_a_decision_is_too(tmp_path, monkeypatch, run_cli):
    role_state = importlib.import_module("veri.role_state")
    monkeypatch.setattr(role_state.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    monkeypatch.setattr(role_state, "now", lambda: "2026-11-12T08:30:00")
    run_cli(role_state, ["dev", "add", "message", "hello"])
    run_cli(role_state, ["dev", "add", "decision", "use the bus"])
    with open(tdd / "role-dev.state", "a") as f:
        f.write("recovered-at=2026-11-12T09:00:00\n")
    monkeypatch.setattr(role_state, "now", lambda: "2026-11-12T09:30:00")
    run_cli(role_state, ["dev", "drop", "message", "1"])
    monkeypatch.setattr(role_state, "now", lambda: "2026-11-12T10:00:00")
    marker = tdd / "reset-request-dev"

    refused = run_cli(role_state, ["dev", "request-reset"])[0], marker.exists()
    run_cli(role_state, ["dev", "drop", "decision", "2"])
    accepted = run_cli(role_state, ["dev", "request-reset"])[0], marker.exists()

    assert (refused, accepted) == ((1, False), (0, True))


def test_dev_request_reset_judges_a_decision_against_the_last_of_several_recoveries(tmp_path, monkeypatch, run_cli):
    role_state = importlib.import_module("veri.role_state")
    monkeypatch.setattr(role_state.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))
    monkeypatch.setattr(role_state, "now", lambda: "2026-11-12T10:00:00")
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    state = tdd / "role-dev.state"
    before = ("recovered-at=2026-11-12T09:00:00\n"
              "decision 1 2026-11-12T09:30:00 use the bus\n"
              "recovered-at=2026-11-12T09:45:00\n")
    state.write_text(before)

    code, _, err = run_cli(role_state, ["dev", "request-reset"])

    assert (code, err, state.read_text(), sorted(p.name for p in tdd.glob("reset-request-*"))) == (
        1, "request-reset refused: nothing launched, merged or decided since the last recovery\n", before, [])


def test_issue_3241_dev_request_reset_with_two_resets_in_the_last_hour_exits_1_writing_nothing_even_after_a_later_launch(tmp_path, monkeypatch, run_cli):
    role_state = importlib.import_module("veri.role_state")
    monkeypatch.setattr(role_state.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))
    monkeypatch.setattr(role_state, "now", lambda: "2026-11-12T10:00:00")
    monkeypatch.delenv("VERI_RESET_MAX_PER_HOUR", raising=False)
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    state = tdd / "role-dev.state"
    before = "recovered-at=2026-11-12T09:00:00\nreset-at=2026-11-12T09:20:00\nreset-at=2026-11-12T09:40:00\n"
    state.write_text(before)
    (tdd / "events.jsonl").write_text('{"ts": 4102444800, "event": "conductor-start", "issue": "7"}\n')

    code, _, err = run_cli(role_state, ["dev", "request-reset"])

    assert (code, bool(err.strip()), state.read_text(), sorted(p.name for p in tdd.glob("reset-request-*"))) == (
        1, True, before, [])


def test_issue_3241_dev_request_reset_ignores_a_reset_older_than_an_hour_so_one_old_and_one_recent_reset_are_accepted(tmp_path, monkeypatch, run_cli):
    role_state = importlib.import_module("veri.role_state")
    monkeypatch.setattr(role_state.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))
    monkeypatch.setattr(role_state, "now", lambda: "2026-11-12T10:00:00")
    monkeypatch.delenv("VERI_RESET_MAX_PER_HOUR", raising=False)
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    state = tdd / "role-dev.state"
    state.write_text("recovered-at=2026-11-12T07:30:00\nreset-at=2026-11-12T08:00:00\nreset-at=2026-11-12T09:40:00\n")
    (tdd / "events.jsonl").write_text('{"ts": 4102444800, "event": "conductor-start", "issue": "7"}\n')

    code, _, _ = run_cli(role_state, ["dev", "request-reset"])

    marker = (tdd / "reset-request-dev").read_text().split() if (tdd / "reset-request-dev").exists() else None
    assert (code, marker, state.read_text().splitlines()[-1]) == (
        0, ["2026-11-12T10:00:00"], "reset-at=2026-11-12T10:00:00")


def test_issue_3241_dev_request_reset_with_max_per_hour_1_and_one_reset_in_the_last_hour_exits_1_writing_nothing(tmp_path, monkeypatch, run_cli):
    role_state = importlib.import_module("veri.role_state")
    monkeypatch.setattr(role_state.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))
    monkeypatch.setattr(role_state, "now", lambda: "2026-11-12T10:00:00")
    monkeypatch.setenv("VERI_RESET_MAX_PER_HOUR", "1")
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    state = tdd / "role-dev.state"
    before = "recovered-at=2026-11-12T09:00:00\nreset-at=2026-11-12T09:40:00\n"
    state.write_text(before)
    (tdd / "events.jsonl").write_text('{"ts": 4102444800, "event": "conductor-start", "issue": "7"}\n')

    code, _, err = run_cli(role_state, ["dev", "request-reset"])

    assert (code, bool(err.strip()), state.read_text(), sorted(p.name for p in tdd.glob("reset-request-*"))) == (
        1, True, before, [])


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


def test_issue_3241_usage_names_request_reset_and_every_set_field(run_cli):
    role_state = importlib.import_module("veri.role_state")

    code, _, err = run_cli(role_state, [])

    missing = [w for w in ("request-reset", *role_state.SET_FIELDS) if w not in err]
    assert (code, missing) == (2, [])


def test_issue_3241_dev_request_reset_with_no_recovered_at_does_not_crash_and_writes_the_marker(tmp_path, monkeypatch, run_cli):
    role_state = importlib.import_module("veri.role_state")
    monkeypatch.setattr(role_state.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))
    monkeypatch.setattr(role_state, "now", lambda: "2026-11-12T10:00:00")

    code, _, err = run_cli(role_state, ["dev", "request-reset"])

    marker = (tmp_path / ".tdd" / "reset-request-dev").read_text().split()
    assert (code, err, marker) == (0, "", ["2026-11-12T10:00:00"])


def test_issue_3241_dev_request_reset_with_no_recovered_at_still_refuses_at_the_hourly_cap(tmp_path, monkeypatch, run_cli):
    role_state = importlib.import_module("veri.role_state")
    monkeypatch.setattr(role_state.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))
    monkeypatch.setattr(role_state, "now", lambda: "2026-11-12T10:00:00")
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    state = tdd / "role-dev.state"
    before = "reset-at=2026-11-12T09:20:00\nreset-at=2026-11-12T09:40:00\n"
    state.write_text(before)

    code, _, err = run_cli(role_state, ["dev", "request-reset"])

    assert (code, bool(err.strip()), state.read_text(), sorted(p.name for p in tdd.glob("reset-request-*"))) == (
        1, True, before, [])


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


def test_request_reset_skips_a_torn_journal_line_and_still_sees_the_launch_after_it(tmp_path, monkeypatch, run_cli):
    role_state = importlib.import_module("veri.role_state")
    monkeypatch.setattr(role_state.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))
    monkeypatch.setattr(role_state, "now", lambda: "2026-11-12T10:00:00")
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    (tdd / "role-dev.state").write_text("recovered-at=2026-11-12T09:00:00\n")
    (tdd / "events.jsonl").write_text('{"ts": 1, "event": "conductor-st\n{"ts": 4102444800, "event": "conductor-start", "issue": "7"}\n')

    code, _, err = run_cli(role_state, ["dev", "request-reset"])

    assert (code, err, (tdd / "reset-request-dev").exists()) == (0, "", True)


def test_request_reset_with_only_a_torn_journal_line_since_recovery_refuses_as_nothing_launched(tmp_path, monkeypatch, run_cli):
    role_state = importlib.import_module("veri.role_state")
    monkeypatch.setattr(role_state.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    (tdd / "role-dev.state").write_text("recovered-at=2026-11-12T09:00:00\n")
    (tdd / "events.jsonl").write_text('{"ts": 4102444800, "event": "conductor-st')

    code, _, err = run_cli(role_state, ["dev", "request-reset"])

    assert (code, err) == (1, "request-reset refused: nothing launched, merged or decided since the last recovery\n")


def test_dev_request_reset_with_an_empty_veri_reset_max_per_hour_reads_it_as_empty_and_fails_not_as_the_default_2(tmp_path, monkeypatch, run_cli):
    role_state = importlib.import_module("veri.role_state")
    monkeypatch.setattr(role_state.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))
    monkeypatch.setattr(role_state, "now", lambda: "2026-11-12T10:00:00")
    monkeypatch.setenv("VERI_RESET_MAX_PER_HOUR", "")
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    state = tdd / "role-dev.state"
    before = "recovered-at=2026-11-12T09:00:00\nreset-at=2026-11-12T09:20:00\nreset-at=2026-11-12T09:40:00\n"
    state.write_text(before)
    (tdd / "events.jsonl").write_text('{"ts": 4102444800, "event": "conductor-start", "issue": "7"}\n')

    code, _, err = run_cli(role_state, ["dev", "request-reset"])

    assert (code, "ValueError" in err, state.read_text()) == (2, True, before)


def test_issue_3890_dev_request_reset_with_the_idle_flag_exits_2_with_a_usage_line_free_of_it_writing_no_marker_or_reset_at(
        tmp_path, monkeypatch, run_cli):
    role_state = importlib.import_module("veri.role_state")
    monkeypatch.setattr(role_state.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))
    monkeypatch.setattr(role_state, "now", lambda: "2026-11-12T10:00:00")
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    state = tdd / "role-dev.state"
    state.write_text("recovered-at=2026-11-12T09:00:00\n")
    (tdd / "events.jsonl").write_text('{"ts": 4102444800, "event": "conductor-start", "issue": "7"}\n')
    flag = "--" + "idle"

    code, out, err = run_cli(role_state, ["dev", "request-reset", flag])

    assert (code, out, err, "request-reset" in err, "[%s]" % flag in err, (tdd / "reset-request-dev").exists(),
            state.read_text()) == (2, "", role_state.USAGE, True, False, False, "recovered-at=2026-11-12T09:00:00\n")


def test_issue_3890_dev_request_reset_with_any_extra_argument_exits_2_with_the_usage_line_writing_no_marker_or_reset_at(
        tmp_path, monkeypatch, run_cli):
    role_state = importlib.import_module("veri.role_state")
    monkeypatch.setattr(role_state.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))
    monkeypatch.setattr(role_state, "now", lambda: "2026-11-12T10:00:00")
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    state = tdd / "role-dev.state"
    state.write_text("recovered-at=2026-11-12T09:00:00\n")
    (tdd / "events.jsonl").write_text('{"ts": 4102444800, "event": "conductor-start", "issue": "7"}\n')

    code, out, err = run_cli(role_state, ["dev", "request-reset", "now"])

    assert (code, out, err, (tdd / "reset-request-dev").exists(), state.read_text()) == (
        2, "", role_state.USAGE, False, "recovered-at=2026-11-12T09:00:00\n")
