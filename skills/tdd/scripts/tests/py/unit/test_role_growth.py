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
