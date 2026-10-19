"""Cases for veri/handoff_state.py that start a real process."""
import importlib
import subprocess

import pytest


@pytest.mark.process("git")
def test_main_in_a_repository_with_no_tags_prints_main_sha_and_none_and_exits_0_without_a_traceback_1819(
        tmp_path, monkeypatch, run_cli):
    handoff_state = importlib.import_module("veri.handoff_state")
    status = importlib.import_module("veri.status")
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo, check=True)
    subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.com",
                    "commit", "-q", "--allow-empty", "-m", "base"], check=True)
    sha = subprocess.run(["git", "-C", str(repo), "rev-parse", "main"], check=True,
                         stdout=subprocess.PIPE, text=True).stdout.strip()
    monkeypatch.setattr(handoff_state, "open_prs", lambda fields, *extra: [])
    monkeypatch.setattr(status, "json_document", lambda scope=None: (0, '{"runs": []}'))
    code, out, err = run_cli(handoff_state, [], cwd=repo)
    assert (code, out.splitlines()[0] if out else "", "Traceback" in err) == (0, "main %s (none)" % sha, False)
