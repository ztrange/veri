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


def test_issue_3241_dev_request_reset_after_a_launch_since_recovery_records_the_time_and_writes_the_marker(tmp_path, monkeypatch, run_cli):
    role_state = importlib.import_module("veri.role_state")
    monkeypatch.setattr(role_state, "main_tree", lambda cwd: str(tmp_path))
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


def test_issue_3241_dev_request_reset_idle_writes_the_marker_holding_the_time_and_the_word_idle(tmp_path, monkeypatch, run_cli):
    role_state = importlib.import_module("veri.role_state")
    monkeypatch.setattr(role_state, "main_tree", lambda cwd: str(tmp_path))
    monkeypatch.setattr(role_state, "now", lambda: "2026-11-12T10:00:00")
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    (tdd / "role-dev.state").write_text("recovered-at=2026-11-12T09:00:00\n")
    (tdd / "events.jsonl").write_text('{"ts": 4102444800, "event": "conductor-start", "issue": "7"}\n')

    code, _, _ = run_cli(role_state, ["dev", "request-reset", "--idle"])

    marker = (tdd / "reset-request-dev").read_text().split()
    assert (code, marker) == (0, ["2026-11-12T10:00:00", "idle"])


def test_issue_3241_dev_lane_request_reset_writes_the_marker_with_the_lane_suffix_and_exits_0(tmp_path, monkeypatch, run_cli):
    role_state = importlib.import_module("veri.role_state")
    monkeypatch.setattr(role_state, "main_tree", lambda cwd: str(tmp_path))
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
    monkeypatch.setattr(role_state, "main_tree", lambda cwd: str(tmp_path))
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
    monkeypatch.setattr(role_state, "main_tree", lambda cwd: str(tmp_path))
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
    monkeypatch.setattr(role_state, "main_tree", lambda cwd: str(tmp_path))
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
    monkeypatch.setattr(role_state, "main_tree", lambda cwd: str(tmp_path))
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
    monkeypatch.setattr(role_state, "main_tree", lambda cwd: str(tmp_path))
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
    monkeypatch.setattr(role_state, "main_tree", lambda cwd: str(tmp_path))
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


def test_issue_3241_dev_request_reset_with_two_resets_in_the_last_hour_exits_1_writing_nothing_even_after_a_later_launch(tmp_path, monkeypatch, run_cli):
    role_state = importlib.import_module("veri.role_state")
    monkeypatch.setattr(role_state, "main_tree", lambda cwd: str(tmp_path))
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
    monkeypatch.setattr(role_state, "main_tree", lambda cwd: str(tmp_path))
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
    monkeypatch.setattr(role_state, "main_tree", lambda cwd: str(tmp_path))
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


def test_issue_3241_dev_recovered_removes_the_roles_reset_marker_and_keeps_the_other_roles(tmp_path, monkeypatch, run_cli):
    role_state = importlib.import_module("veri.role_state")
    monkeypatch.setattr(role_state, "main_tree", lambda cwd: str(tmp_path))
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    (tdd / "reset-request-dev").write_text("2026-11-12T10:00:00\n")
    (tdd / "reset-request-coord").write_text("2026-11-12T10:00:00\n")

    code, _, _ = run_cli(role_state, ["dev", "recovered"], env={"CLAUDE_CODE_SESSION_ID": "sess-1"})

    assert (code, sorted(p.name for p in tdd.glob("reset-request-*"))) == (0, ["reset-request-coord"])
