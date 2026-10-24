"""Cases for the gate supervise.sh puts on verify-red and verify-green, run against a real git repository."""
import importlib
import subprocess

import pytest

from pass_marker import write_pass_marker


def git(repo, *argv):
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *argv], cwd=repo, check=True,
                   capture_output=True)


@pytest.mark.process("a real git repository under tmp_path, hashed by check-earlier and read back by supervise")
def test_supervise_refuses_verify_green_when_the_work_tree_changed_after_check_earlier_and_launches_when_it_did_not_2230(
        monkeypatch, tmp_path, run_cli):
    tests_frozen = importlib.import_module("veri.tests_frozen")
    supervise = importlib.import_module("veri.supervise")
    step = "first step"
    (tmp_path / ".tdd").mkdir()
    ledger = tmp_path / ".tdd" / "issue-2230.md"
    ledger.write_text(f"# Plan for #2230\n\n- [ ] {step}\n")
    (tmp_path / "lib.py").write_text("one\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "lib.py")
    git(tmp_path, "commit", "-q", "-m", "base")
    started = []

    def attempt_once(*_):
        started.append(True)
        return "success", "", "0", 0

    monkeypatch.setattr(supervise, "attempt_once", attempt_once)
    monkeypatch.setattr(supervise, "HERE", str(tmp_path))
    env = {"VERI_ISSUE": "2230", "VERI_STEP": "1"}
    stub = str(tmp_path / "claude")

    def launch():
        started.clear()
        code, _, _ = run_cli(supervise, ["verify-green", stub], cwd=tmp_path, env=env)
        return code, bool(started)

    run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", step], cwd=tmp_path)
    (tmp_path / "lib.py").write_text("one, edited after the check\n")
    stale = launch()
    run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", step], cwd=tmp_path)
    current = launch()

    assert (stale, current) == ((2, False), (0, True))


@pytest.mark.process("a real git repository under tmp_path holding a nested repository made by git init")
def test_supervise_refuses_verify_red_naming_the_work_tree_hash_when_it_cannot_be_computed_even_with_an_empty_tree_marker_2230(
        monkeypatch, tmp_path, run_cli):
    supervise = importlib.import_module("veri.supervise")
    step = "first step"
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-2230.md").write_text(f"# Plan for #2230\n\n- [ ] {step}\n")
    (tmp_path / "lib.py").write_text("one\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "lib.py")
    git(tmp_path, "commit", "-q", "-m", "base")
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                          text=True).stdout.strip()
    write_pass_marker(tmp_path, step, head, "")
    (tmp_path / "nested").mkdir()
    git(tmp_path / "nested", "init", "-q")
    started = []

    def attempt_once(*_):
        started.append(True)
        return "success", "", "0", 0

    monkeypatch.setattr(supervise, "attempt_once", attempt_once)
    monkeypatch.setattr(supervise, "HERE", str(tmp_path))

    code, _, err = run_cli(supervise, ["verify-red", str(tmp_path / "claude")], cwd=tmp_path,
                           env={"VERI_ISSUE": "2230", "VERI_STEP": "1"})

    assert (code, "work-tree hash" in err, started) == (2, True, [])
