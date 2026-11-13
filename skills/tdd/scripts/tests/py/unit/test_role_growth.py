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
