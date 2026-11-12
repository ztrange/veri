"""In-process cases for veri/drop_ledger_step.py, the module drop-ledger-step.sh is a shim over."""
import importlib
import os
import subprocess

import pytest

SEED = (
    "# Plan for #42\n\n"
    "- [x] lowercase the slug ⟦criterion 1⟧\n"
    "- [ ] collapse to single hyphen ⟦criterion 2⟧\n"
)


@pytest.mark.process("git init and commit in a scratch repository, then git read back")
def test_issue_3692_drop_ledger_step_refuses_while_the_conductor_is_live_naming_its_pid_and_changes_nothing(
        tmp_path, monkeypatch, run_cli):
    from conftest import live_conductor
    drop_ledger_step = importlib.import_module("veri.drop_ledger_step")
    git = ["git", "-c", "user.name=t", "-c", "user.email=t@example.com"]

    def out(*args):
        return subprocess.run([*git, *args], cwd=tmp_path, check=True, capture_output=True, text=True).stdout

    out("init", "-q")
    (tmp_path / ".tdd").mkdir()
    ledger = tmp_path / ".tdd" / "issue-42-plan.md"
    ledger.write_text(SEED)
    out("add", "-f", ".tdd/issue-42-plan.md")
    out("commit", "-q", "-m", "plan")
    before = out("rev-parse", "HEAD")
    live_conductor(monkeypatch, tmp_path / ".tdd", 42)

    code, _, err = run_cli(drop_ledger_step, [str(ledger), "collapse to single hyphen"], cwd=tmp_path)

    assert code == 1
    assert str(os.getpid()) in err
    assert ledger.read_text() == SEED
    assert out("rev-parse", "HEAD") == before
