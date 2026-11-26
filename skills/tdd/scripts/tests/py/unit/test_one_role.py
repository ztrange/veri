"""PRD 026.8: the role scripts take one role, `dev`; the retired `coord` role is refused (CR1, CR2, CR4)."""
import importlib
import json

import pytest

DEV_ONLY = {
    "role_state": "usage: role-state.sh dev ",
}


@pytest.mark.parametrize("module,argv", [
    ("role_state", ["coord", "show"]),
    ("role_state", ["coord", "--lane", "mu", "set", "n", "2"]),
])
def test_issue_4103_a_role_script_given_coord_exits_2_writing_nothing_with_a_usage_line_naming_dev_alone(
        module, argv, tmp_path, monkeypatch, run_cli):
    mod = importlib.import_module("veri." + module)
    monkeypatch.setattr(mod.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path), raising=False)
    monkeypatch.chdir(tmp_path)

    code, out, err = run_cli(mod, argv, env={"HOME": str(tmp_path / "home"), "CLAUDE_CODE_SESSION_ID": "sess-1"})

    usage = [line for line in err.splitlines() if line.startswith("usage:")]
    assert (code, out, list(tmp_path.iterdir()), len(usage), usage[0].startswith(DEV_ONLY[module]) if usage else None,
            "coord" in err) == (2, "", [], 1, True, False), err


def test_issue_4103_status_recover_coord_exits_2_writing_nothing_with_a_usage_line_naming_dev_alone(
        tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status.run_dir, "main_tree", lambda **_: str(tmp_path))
    monkeypatch.chdir(tmp_path)

    code, out, err = run_cli(status, ["--recover", "coord"])

    assert (code, out, list(tmp_path.iterdir()), err) == (
        2, "", [], "usage: status.sh --recover dev [--lane <lane>]\n")


@pytest.mark.parametrize("argv", [["dev", "set", "coordinator", "sess-1"], ["dev", "drop", "coordinator"]])
def test_issue_4103_role_state_dev_set_or_drop_coordinator_exits_2_and_leaves_the_state_file_as_it_was(
        argv, tmp_path, monkeypatch, run_cli):
    role_state = importlib.import_module("veri.role_state")
    monkeypatch.setattr(role_state.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))
    (tmp_path / ".tdd").mkdir()
    state = tmp_path / ".tdd" / "role-dev.state"
    state.write_text("n=2\ncoordinator=sess-old\n")

    code, out, err = run_cli(role_state, argv)

    assert (code, out, state.read_text(), err.startswith("usage: role-state.sh dev ")) == (
        2, "", "n=2\ncoordinator=sess-old\n", True)


def test_issue_4103_recover_dev_lists_no_coordinator_line_under_state_when_the_state_file_holds_one(
        tmp_path, monkeypatch, run_cli, fake_processes):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status.run_dir, "main_tree", lambda **_: str(tmp_path))
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "role-dev.state").write_text("n=2\ncoordinator=sess-old\nlane=mu\n")
    fake = fake_processes.answers({}, default=lambda line, **k: (0, "[]" if fake.argvs[-1][:1] == ["gh"] else "", ""))

    code, out, _ = run_cli(status, ["--recover", "dev"])

    lines = [line.strip() for line in out.splitlines() if line.strip()]
    state = lines[lines.index("State") + 1:lines.index("Pending decisions")]
    assert (code, state) == (0, ["n 2", "lane mu"]), state


def test_issue_4103_a_transcript_whose_first_prompt_invokes_vcoord_adds_no_operator_session_row(
        tmp_path, monkeypatch, capsys):
    metrics = importlib.import_module("veri.metrics")
    monkeypatch.setattr(importlib.import_module("veri.run_records"), "read", lambda issue, name, cwd: None)
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "events.jsonl").write_text(
        json.dumps({"event": "step-start", "step": "1", "ts": 100}) + "\n"
        + json.dumps({"event": "step-done", "step": "1", "ts": 160}) + "\n")
    transcripts = tmp_path / "transcripts"
    transcripts.mkdir()
    rows = [{"type": "user", "message": {"role": "user", "content": "/vcoord 3154"}},
            {"type": "assistant", "message": {"id": "msg_1", "model": "claude-opus-4", "usage": {
                "input_tokens": 1, "cache_read_input_tokens": 50000, "cache_creation_input_tokens": 0,
                "output_tokens": 1}}}]
    (transcripts / "coord.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VERI_SESSION_TRANSCRIPTS", str(transcripts))

    code = metrics.main(["108"])
    out = capsys.readouterr().out

    assert (code, "Coordinator" in out, " session: " in out) == (0, False, False), out
