"""Small cases for veri.role_growth: role-growth.sh, run in-process."""
import importlib


def test_no_argument_prints_usage_naming_role_growth_and_exits_2(run_cli):
    role_growth = importlib.import_module("veri.role_growth")

    code, _, err = run_cli(role_growth, [])

    assert (code, "role-growth.sh" in err) == (2, True)


def test_records_session_and_transcript_of_the_session_id_in_the_role_state_file(tmp_path, monkeypatch, run_cli):
    role_growth = importlib.import_module("veri.role_growth")
    monkeypatch.setattr(role_growth, "main_tree", lambda cwd: str(tmp_path), raising=False)
    home = tmp_path / "home"
    transcript = home / ".claude" / "projects" / "-some-repo" / "sess-42.jsonl"
    transcript.parent.mkdir(parents=True)
    transcript.write_text("")

    code, _, _ = run_cli(role_growth, ["coord"], env={"HOME": str(home), "CLAUDE_CODE_SESSION_ID": "sess-42"})

    state = (tmp_path / ".tdd" / "role-coord.state")
    lines = state.read_text().splitlines() if state.exists() else []
    assert (code, "session=sess-42" in lines, "transcript=%s" % transcript in lines) == (0, True, True)


def test_a_role_that_is_neither_coord_nor_dev_prints_usage_exits_2_and_writes_no_state(tmp_path, monkeypatch, run_cli):
    role_growth = importlib.import_module("veri.role_growth")
    monkeypatch.setattr(role_growth, "main_tree", lambda cwd: str(tmp_path), raising=False)
    home = tmp_path / "home"
    transcript = home / ".claude" / "projects" / "-some-repo" / "sess-42.jsonl"
    transcript.parent.mkdir(parents=True)
    transcript.write_text("")

    code, _, err = run_cli(role_growth, ["admin"], env={"HOME": str(home), "CLAUDE_CODE_SESSION_ID": "sess-42"})

    written = sorted(p.name for p in (tmp_path / ".tdd").glob("*")) if (tmp_path / ".tdd").exists() else []
    assert (code, "usage: role-growth.sh" in err, written) == (2, True, [])


def test_unset_session_id_exits_2_with_one_stderr_line_naming_it(tmp_path, monkeypatch, run_cli):
    role_growth = importlib.import_module("veri.role_growth")
    monkeypatch.setattr(role_growth, "main_tree", lambda cwd: str(tmp_path), raising=False)
    monkeypatch.delenv("CLAUDE_CODE_SESSION_ID", raising=False)

    code, _, err = run_cli(role_growth, ["coord"], env={"HOME": str(tmp_path / "home")})

    assert (code, len(err.splitlines()), "CLAUDE_CODE_SESSION_ID" in err) == (2, 1, True)


def test_session_with_no_transcript_exits_2_with_one_stderr_line_naming_the_missing_transcript(tmp_path, monkeypatch, run_cli):
    role_growth = importlib.import_module("veri.role_growth")
    monkeypatch.setattr(role_growth, "main_tree", lambda cwd: str(tmp_path), raising=False)
    home = tmp_path / "home"
    (home / ".claude" / "projects" / "-some-repo").mkdir(parents=True)

    code, _, err = run_cli(role_growth, ["coord"], env={"HOME": str(home), "CLAUDE_CODE_SESSION_ID": "sess-42"})

    assert (code, len(err.splitlines()), "sess-42.jsonl" in err) == (2, 1, True)


def test_dev_with_a_lane_records_session_and_transcript_in_the_lane_state_file(tmp_path, monkeypatch, run_cli):
    role_growth = importlib.import_module("veri.role_growth")
    monkeypatch.setattr(role_growth, "main_tree", lambda cwd: str(tmp_path), raising=False)
    home = tmp_path / "home"
    transcript = home / ".claude" / "projects" / "-some-repo" / "sess-42.jsonl"
    transcript.parent.mkdir(parents=True)
    transcript.write_text("")

    code, _, _ = run_cli(role_growth, ["dev", "--lane", "alpha"], env={"HOME": str(home), "CLAUDE_CODE_SESSION_ID": "sess-42"})

    state = tmp_path / ".tdd" / "role-dev-alpha.state"
    lines = state.read_text().splitlines() if state.exists() else []
    assert (code, "session=sess-42" in lines, "transcript=%s" % transcript in lines) == (0, True, True)


def test_first_call_after_recovery_with_a_transcript_holding_no_usage_line_prints_nothing_and_records_no_baseline(tmp_path, monkeypatch, run_cli):
    role_growth = importlib.import_module("veri.role_growth")
    monkeypatch.setattr(role_growth, "main_tree", lambda cwd: str(tmp_path), raising=False)
    home = tmp_path / "home"
    transcript = home / ".claude" / "projects" / "-some-repo" / "sess-42.jsonl"
    transcript.parent.mkdir(parents=True)
    transcript.write_text('{"type":"user","message":{"role":"user","content":"hello"}}\n')
    state = tmp_path / ".tdd" / "role-coord.state"
    state.parent.mkdir()
    state.write_text("recovered-at=2026-11-13T10:00:00\nbaseline-at=2026-11-13T09:00:00\n")

    code, out, _ = run_cli(role_growth, ["coord"], env={"HOME": str(home), "CLAUDE_CODE_SESSION_ID": "sess-42"})

    baselines = [l for l in state.read_text().splitlines() if l.startswith("baseline=")]
    assert (code, out, baselines) == (0, "", [])


def test_first_call_after_recovery_with_a_usage_line_records_its_context_as_baseline_and_prints_nothing(tmp_path, monkeypatch, run_cli):
    role_growth = importlib.import_module("veri.role_growth")
    monkeypatch.setattr(role_growth, "main_tree", lambda cwd: str(tmp_path), raising=False)
    home = tmp_path / "home"
    transcript = home / ".claude" / "projects" / "-some-repo" / "sess-42.jsonl"
    transcript.parent.mkdir(parents=True)
    transcript.write_text(
        '{"type":"assistant","message":{"id":"m1","usage":{"input_tokens":1,"cache_read_input_tokens":2,"cache_creation_input_tokens":3}}}\n'
        '{"type":"assistant","message":{"id":"m2","usage":{"input_tokens":100,"cache_read_input_tokens":2000,"cache_creation_input_tokens":300}}}\n'
    )
    state = tmp_path / ".tdd" / "role-coord.state"
    state.parent.mkdir()
    state.write_text("recovered-at=2026-11-13T10:00:00\nbaseline-at=2026-11-13T09:00:00\n")

    code, out, _ = run_cli(role_growth, ["coord"], env={"HOME": str(home), "CLAUDE_CODE_SESSION_ID": "sess-42"})

    lines = state.read_text().splitlines()
    stamps = [l for l in lines if l.startswith("baseline-at=")]
    assert (code, out, "baseline=2400" in lines, stamps[-1] != "baseline-at=2026-11-13T09:00:00") == (0, "", True, True)


def test_call_with_baseline_at_later_than_recovered_at_records_no_new_baseline_and_keeps_baseline_at(tmp_path, monkeypatch, run_cli):
    role_growth = importlib.import_module("veri.role_growth")
    monkeypatch.setattr(role_growth, "main_tree", lambda cwd: str(tmp_path), raising=False)
    home = tmp_path / "home"
    transcript = home / ".claude" / "projects" / "-some-repo" / "sess-42.jsonl"
    transcript.parent.mkdir(parents=True)
    transcript.write_text(
        '{"type":"assistant","message":{"id":"m2","usage":{"input_tokens":100,"cache_read_input_tokens":2000,"cache_creation_input_tokens":300}}}\n'
    )
    state = tmp_path / ".tdd" / "role-coord.state"
    state.parent.mkdir()
    state.write_text("recovered-at=2026-11-13T09:00:00\nbaseline=555\nbaseline-at=2026-11-13T10:00:00\n")

    code, out, _ = run_cli(role_growth, ["coord"], env={"HOME": str(home), "CLAUDE_CODE_SESSION_ID": "sess-42"})

    lines = state.read_text().splitlines()
    baselines = [l for l in lines if l.startswith("baseline")]
    assert (code, out, baselines) == (0, "", ["baseline=555", "baseline-at=2026-11-13T10:00:00"])


def test_a_transcript_with_blank_lines_is_still_read_and_its_usage_line_becomes_the_baseline(tmp_path, monkeypatch, run_cli):
    role_growth = importlib.import_module("veri.role_growth")
    monkeypatch.setattr(role_growth, "main_tree", lambda cwd: str(tmp_path), raising=False)
    home = tmp_path / "home"
    transcript = home / ".claude" / "projects" / "-some-repo" / "sess-42.jsonl"
    transcript.parent.mkdir(parents=True)
    transcript.write_text(
        '\n'
        '{"type":"assistant","message":{"id":"m2","usage":{"input_tokens":100,"cache_read_input_tokens":2000,"cache_creation_input_tokens":300}}}\n'
        '\n'
        '   \n'
    )
    state = tmp_path / ".tdd" / "role-coord.state"
    state.parent.mkdir()
    state.write_text("recovered-at=2026-11-13T10:00:00\n")

    code, out, _ = run_cli(role_growth, ["coord"], env={"HOME": str(home), "CLAUDE_CODE_SESSION_ID": "sess-42"})

    assert (code, out, "baseline=2400" in state.read_text().splitlines()) == (0, "", True)


def test_first_call_with_no_recovered_at_and_no_baseline_at_records_the_last_usage_context_as_baseline_and_now_as_baseline_at(tmp_path, monkeypatch, run_cli):
    role_growth = importlib.import_module("veri.role_growth")
    monkeypatch.setattr(role_growth, "main_tree", lambda cwd: str(tmp_path), raising=False)
    home = tmp_path / "home"
    transcript = home / ".claude" / "projects" / "-some-repo" / "sess-42.jsonl"
    transcript.parent.mkdir(parents=True)
    transcript.write_text(
        '{"type":"assistant","message":{"id":"m1","usage":{"input_tokens":1,"cache_read_input_tokens":2,"cache_creation_input_tokens":3}}}\n'
        '{"type":"assistant","message":{"id":"m2","usage":{"input_tokens":100,"cache_read_input_tokens":2000,"cache_creation_input_tokens":300}}}\n'
    )
    state = tmp_path / ".tdd" / "role-coord.state"
    state.parent.mkdir()
    state.write_text("session=old\n")

    code, out, _ = run_cli(role_growth, ["coord"], env={"HOME": str(home), "CLAUDE_CODE_SESSION_ID": "sess-42"})

    lines = state.read_text().splitlines()
    stamps = [l for l in lines if l.startswith("baseline-at=") and len(l) > len("baseline-at=")]
    assert (code, out, "baseline=2400" in lines, len(stamps)) == (0, "", True, 1)


def test_growth_of_59500_against_the_baseline_prints_one_arm_line_naming_growth_knob_and_the_next_quiet_point(tmp_path, monkeypatch, run_cli):
    role_growth = importlib.import_module("veri.role_growth")
    monkeypatch.setattr(role_growth, "main_tree", lambda cwd: str(tmp_path), raising=False)
    home = tmp_path / "home"
    transcript = home / ".claude" / "projects" / "-some-repo" / "sess-42.jsonl"
    transcript.parent.mkdir(parents=True)
    transcript.write_text(
        '{"type":"assistant","message":{"id":"m2","usage":{"input_tokens":500,"cache_read_input_tokens":50000,"cache_creation_input_tokens":10000}}}\n'
    )
    state = tmp_path / ".tdd" / "role-coord.state"
    state.parent.mkdir()
    state.write_text("recovered-at=2026-11-13T09:00:00\nbaseline=1000\nbaseline-at=2026-11-13T10:00:00\ndecision 1 2026-11-13T09:30:00 use the bus\n")

    code, out, _ = run_cli(role_growth, ["coord"], env={"HOME": str(home), "CLAUDE_CODE_SESSION_ID": "sess-42"})

    line = out.rstrip("\n")
    assert (code, len(out.splitlines()), "59500" in line, "70000" in line, "reset at the next quiet point" in line) == (0, 1, True, True, True)


def test_growth_of_59499_against_the_baseline_with_the_default_knob_prints_nothing_and_exits_0(tmp_path, monkeypatch, run_cli):
    role_growth = importlib.import_module("veri.role_growth")
    monkeypatch.setattr(role_growth, "main_tree", lambda cwd: str(tmp_path), raising=False)
    home = tmp_path / "home"
    transcript = home / ".claude" / "projects" / "-some-repo" / "sess-42.jsonl"
    transcript.parent.mkdir(parents=True)
    transcript.write_text(
        '{"type":"assistant","message":{"id":"m2","usage":{"input_tokens":500,"cache_read_input_tokens":50000,"cache_creation_input_tokens":10000}}}\n'
    )
    state = tmp_path / ".tdd" / "role-coord.state"
    state.parent.mkdir()
    state.write_text("recovered-at=2026-11-13T09:00:00\nbaseline=1001\nbaseline-at=2026-11-13T10:00:00\n")

    code, out, _ = run_cli(role_growth, ["coord"], env={"HOME": str(home), "CLAUDE_CODE_SESSION_ID": "sess-42"})

    assert (code, out) == (0, "")


def test_growth_of_140000_against_the_baseline_with_the_default_knob_prints_one_reset_now_even_mid_task_line_and_exits_0(tmp_path, monkeypatch, run_cli):
    role_growth = importlib.import_module("veri.role_growth")
    monkeypatch.setattr(role_growth, "main_tree", lambda cwd: str(tmp_path), raising=False)
    home = tmp_path / "home"
    transcript = home / ".claude" / "projects" / "-some-repo" / "sess-42.jsonl"
    transcript.parent.mkdir(parents=True)
    transcript.write_text(
        '{"type":"assistant","message":{"id":"m2","usage":{"input_tokens":500,"cache_read_input_tokens":140000,"cache_creation_input_tokens":10000}}}\n'
    )
    state = tmp_path / ".tdd" / "role-coord.state"
    state.parent.mkdir()
    state.write_text("recovered-at=2026-11-13T09:00:00\nbaseline=10500\nbaseline-at=2026-11-13T10:00:00\ndecision 1 2026-11-13T09:30:00 use the bus\n")

    code, out, _ = run_cli(role_growth, ["coord"], env={"HOME": str(home), "CLAUDE_CODE_SESSION_ID": "sess-42"})

    assert (code, len(out.splitlines()), "reset now, even mid-task" in out) == (0, 1, True)


def test_growth_of_139999_against_the_baseline_with_the_default_knob_prints_the_arm_line_not_the_reset_now_line_and_exits_0(tmp_path, monkeypatch, run_cli):
    role_growth = importlib.import_module("veri.role_growth")
    monkeypatch.setattr(role_growth, "main_tree", lambda cwd: str(tmp_path), raising=False)
    home = tmp_path / "home"
    transcript = home / ".claude" / "projects" / "-some-repo" / "sess-42.jsonl"
    transcript.parent.mkdir(parents=True)
    transcript.write_text(
        '{"type":"assistant","message":{"id":"m2","usage":{"input_tokens":500,"cache_read_input_tokens":130499,"cache_creation_input_tokens":10000}}}\n'
    )
    state = tmp_path / ".tdd" / "role-coord.state"
    state.parent.mkdir()
    state.write_text("recovered-at=2026-11-13T09:00:00\nbaseline=1000\nbaseline-at=2026-11-13T10:00:00\ndecision 1 2026-11-13T09:30:00 use the bus\n")

    code, out, _ = run_cli(role_growth, ["coord"], env={"HOME": str(home), "CLAUDE_CODE_SESSION_ID": "sess-42"})

    line = out.rstrip("\n")
    assert (code, len(out.splitlines()), "139999" in line, "reset at the next quiet point" in line, "reset now" in line) == (0, 1, True, True, False)


def test_coord_takes_its_knob_from_veri_reset_growth_coord_and_prints_the_arm_line_at_a_growth_of_850_against_1000(tmp_path, monkeypatch, run_cli):
    role_growth = importlib.import_module("veri.role_growth")
    monkeypatch.setattr(role_growth, "main_tree", lambda cwd: str(tmp_path), raising=False)
    home = tmp_path / "home"
    transcript = home / ".claude" / "projects" / "-some-repo" / "sess-42.jsonl"
    transcript.parent.mkdir(parents=True)
    transcript.write_text(
        '{"type":"assistant","message":{"id":"m2","usage":{"input_tokens":500,"cache_read_input_tokens":1350,"cache_creation_input_tokens":0}}}\n'
    )
    state = tmp_path / ".tdd" / "role-coord.state"
    state.parent.mkdir()
    state.write_text("recovered-at=2026-11-13T09:00:00\nbaseline=1000\nbaseline-at=2026-11-13T10:00:00\ndecision 1 2026-11-13T09:30:00 use the bus\n")

    code, out, _ = run_cli(role_growth, ["coord"], env={"HOME": str(home), "CLAUDE_CODE_SESSION_ID": "sess-42", "VERI_RESET_GROWTH_COORD": "1000"})

    line = out.rstrip("\n")
    assert (code, len(out.splitlines()), "850" in line, "1000" in line, "reset at the next quiet point" in line) == (0, 1, True, True, True)


def test_dev_takes_its_knob_from_veri_reset_growth_dev_and_prints_the_arm_line_at_a_growth_of_850_against_1000(tmp_path, monkeypatch, run_cli):
    role_growth = importlib.import_module("veri.role_growth")
    monkeypatch.setattr(role_growth, "main_tree", lambda cwd: str(tmp_path), raising=False)
    home = tmp_path / "home"
    transcript = home / ".claude" / "projects" / "-some-repo" / "sess-42.jsonl"
    transcript.parent.mkdir(parents=True)
    transcript.write_text(
        '{"type":"assistant","message":{"id":"m2","usage":{"input_tokens":500,"cache_read_input_tokens":1350,"cache_creation_input_tokens":0}}}\n'
    )
    state = tmp_path / ".tdd" / "role-dev.state"
    state.parent.mkdir()
    state.write_text("recovered-at=2026-11-13T09:00:00\nbaseline=1000\nbaseline-at=2026-11-13T10:00:00\ndecision 1 2026-11-13T09:30:00 use the bus\n")

    code, out, _ = run_cli(role_growth, ["dev"], env={"HOME": str(home), "CLAUDE_CODE_SESSION_ID": "sess-42", "VERI_RESET_GROWTH_DEV": "1000", "VERI_RESET_GROWTH_COORD": "999999"})

    line = out.rstrip("\n")
    assert (code, len(out.splitlines()), "850" in line, "1000" in line, "reset at the next quiet point" in line) == (0, 1, True, True, True)


def test_at_the_arm_point_with_nothing_launched_since_recovery_prints_the_refusal_once_in_place_of_the_growth_line_and_records_refused_at(tmp_path, monkeypatch, run_cli):
    role_growth = importlib.import_module("veri.role_growth")
    monkeypatch.setattr(role_growth, "main_tree", lambda cwd: str(tmp_path), raising=False)
    home = tmp_path / "home"
    transcript = home / ".claude" / "projects" / "-some-repo" / "sess-42.jsonl"
    transcript.parent.mkdir(parents=True)
    transcript.write_text(
        '{"type":"assistant","message":{"id":"m2","usage":{"input_tokens":500,"cache_read_input_tokens":50000,"cache_creation_input_tokens":10000}}}\n'
    )
    state = tmp_path / ".tdd" / "role-coord.state"
    state.parent.mkdir()
    state.write_text("recovered-at=2026-11-13T09:00:00\nbaseline=1000\nbaseline-at=2026-11-13T10:00:00\n")

    code, out, _ = run_cli(role_growth, ["coord"], env={"HOME": str(home), "CLAUDE_CODE_SESSION_ID": "sess-42"})

    refused = [l for l in state.read_text().splitlines() if l.startswith("refused-at=") and len(l) > len("refused-at=")]
    assert (code, len(out.splitlines()), "report it to the operator, do not retry" in out, "context grew" in out, len(refused)) == (0, 1, True, False, 1)


def test_a_later_call_at_the_arm_point_with_refused_at_recorded_and_the_guard_still_refusing_prints_nothing_and_exits_0(tmp_path, monkeypatch, run_cli):
    role_growth = importlib.import_module("veri.role_growth")
    monkeypatch.setattr(role_growth, "main_tree", lambda cwd: str(tmp_path), raising=False)
    home = tmp_path / "home"
    transcript = home / ".claude" / "projects" / "-some-repo" / "sess-42.jsonl"
    transcript.parent.mkdir(parents=True)
    transcript.write_text(
        '{"type":"assistant","message":{"id":"m2","usage":{"input_tokens":500,"cache_read_input_tokens":50000,"cache_creation_input_tokens":10000}}}\n'
    )
    state = tmp_path / ".tdd" / "role-coord.state"
    state.parent.mkdir()
    state.write_text("recovered-at=2026-11-13T09:00:00\nbaseline=1000\nbaseline-at=2026-11-13T10:00:00\nrefused-at=2026-11-13T10:30:00\n")

    code, out, _ = run_cli(role_growth, ["coord"], env={"HOME": str(home), "CLAUDE_CODE_SESSION_ID": "sess-42"})

    assert (code, out) == (0, "")


def test_a_call_at_the_arm_point_with_refused_at_recorded_and_a_launch_since_recovery_prints_the_growth_line_again_and_exits_0(tmp_path, monkeypatch, run_cli):
    role_growth = importlib.import_module("veri.role_growth")
    monkeypatch.setattr(role_growth, "main_tree", lambda cwd: str(tmp_path), raising=False)
    home = tmp_path / "home"
    transcript = home / ".claude" / "projects" / "-some-repo" / "sess-42.jsonl"
    transcript.parent.mkdir(parents=True)
    transcript.write_text(
        '{"type":"assistant","message":{"id":"m2","usage":{"input_tokens":500,"cache_read_input_tokens":50000,"cache_creation_input_tokens":10000}}}\n'
    )
    state = tmp_path / ".tdd" / "role-coord.state"
    state.parent.mkdir()
    state.write_text("recovered-at=2026-11-13T09:00:00\nbaseline=1000\nbaseline-at=2026-11-13T10:00:00\nrefused-at=2026-11-13T10:30:00\n")
    (state.parent / "events.jsonl").write_text('{"ts": 4102444800, "event": "conductor-start", "issue": "7"}\n')

    code, out, _ = run_cli(role_growth, ["coord"], env={"HOME": str(home), "CLAUDE_CODE_SESSION_ID": "sess-42"})

    assert (code, len(out.splitlines()), "context grew" in out, "reset at the next quiet point" in out) == (0, 1, True, True)
