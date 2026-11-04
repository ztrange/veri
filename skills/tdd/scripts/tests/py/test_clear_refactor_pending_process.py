"""Cases for clear-refactor-pending.sh that start the real entry point."""
import importlib
import subprocess

import pytest

from conftest import SCRIPTS

LEDGER = "# Plan for #42\n\n- [x] a ⟂ refactor pending\n- [x] collapse to single hyphen ⟂ refactor pending\n- [ ] b\n"


@pytest.mark.process("clear-refactor-pending.sh run through a symlink to the skill directory from another working directory")
def test_cli_run_through_a_symlink_to_the_skill_directory_from_another_cwd_clears_a_relative_ledger_as_in_place(
        tmp_path, run_cli, leave_receipt):
    clear_refactor_pending = importlib.import_module("veri.clear_refactor_pending")
    for step in (["init", "-q"], ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "base"]):
        subprocess.run(["git", *step], cwd=tmp_path, check=True, capture_output=True)
    (tmp_path / "skill-link").symlink_to(SCRIPTS.parent, target_is_directory=True)
    (tmp_path / "caller").mkdir()
    (tmp_path / "inplace").mkdir()
    (tmp_path / "caller" / "issue-42.md").write_text(LEDGER)
    (tmp_path / "inplace" / "issue-42.md").write_text(LEDGER)
    for name in ("caller", "inplace"):
        leave_receipt(tmp_path / name / "issue-42.md", repo=tmp_path)

    in_place = run_cli(clear_refactor_pending, [str(tmp_path / "inplace" / "issue-42.md"), "collapse to single hyphen"])
    ran = subprocess.run([str(tmp_path / "skill-link" / "scripts" / "clear-refactor-pending.sh"),
                          "issue-42.md", "collapse to single hyphen"],
                         cwd=tmp_path / "caller", capture_output=True, text=True)

    assert in_place == (0, "", "")
    assert (ran.returncode, ran.stdout, ran.stderr) == in_place
    want = LEDGER.replace("collapse to single hyphen ⟂ refactor pending", "collapse to single hyphen")
    assert (tmp_path / "caller" / "issue-42.md").read_text() == want
    assert (tmp_path / "inplace" / "issue-42.md").read_text() == want


@pytest.mark.process("a real git repository under tmp_path whose only change after the receipt's sha is a .tdd/ file")
def test_2972_a_change_under_tdd_alone_since_the_receipt_still_clears_the_step(tmp_path, run_cli, leave_receipt):
    clear_refactor_pending = importlib.import_module("veri.clear_refactor_pending")
    (tmp_path / ".tdd").mkdir()
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.write_text(LEDGER)
    for step in (["init", "-q"], ["add", "-A"],
                 ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "base"]):
        subprocess.run(["git", *step], cwd=tmp_path, check=True, capture_output=True)
    leave_receipt(ledger, repo=tmp_path)
    (tmp_path / ".tdd" / "issue-42-notes.md").write_text("later\n")
    for step in (["add", "-A"], ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "tdd only"]):
        subprocess.run(["git", *step], cwd=tmp_path, check=True, capture_output=True)

    code = run_cli(clear_refactor_pending, [str(ledger), "collapse to single hyphen"], cwd=tmp_path)[0]

    assert (code, "- [x] collapse to single hyphen\n" in ledger.read_text()) == (0, True)
