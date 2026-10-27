"""Case for the retired-filers guard's sweep, run over a real git repository."""
import importlib.util
import subprocess
from pathlib import Path

import pytest

GUARD = Path(__file__).resolve().parent / "unit" / "test_retired_filers_gone.py"


def load_guard():
    spec = importlib.util.spec_from_file_location("retired_filers_guard", GUARD)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.process("a real git repository under tmp_path holding an untracked nested checkout under .claude/worktrees")
def test_the_retired_filers_sweep_reports_no_file_of_an_untracked_nested_checkout_2520(monkeypatch, tmp_path):
    guard = load_guard()
    (tmp_path / "README.md").write_text("nothing retired here\n")
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "add", "README.md"], cwd=tmp_path, check=True, capture_output=True)
    nested = tmp_path / ".claude" / "worktrees" / "agent-1"
    nested.mkdir(parents=True)
    (nested / "README.md").write_text("run skills/" + guard.RETIRED[0] + "/SKILL.md\n")
    monkeypatch.setattr(guard, "REPO", tmp_path)

    assert guard.namers() == []


@pytest.mark.process("a real git repository under tmp_path holding a tracked file that names a retired filer")
def test_the_retired_filers_sweep_reports_a_tracked_file_that_names_a_retired_filer_2520(monkeypatch, tmp_path):
    guard = load_guard()
    (tmp_path / "README.md").write_text("run skills/" + guard.RETIRED[1] + "/SKILL.md\n")
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "add", "README.md"], cwd=tmp_path, check=True, capture_output=True)
    monkeypatch.setattr(guard, "REPO", tmp_path)

    assert guard.namers() == ["README.md"]
