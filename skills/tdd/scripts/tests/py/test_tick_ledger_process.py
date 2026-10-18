"""Cases for tick-ledger.sh that start the real entry point."""
import importlib
import subprocess

import pytest

from conftest import SCRIPTS


@pytest.mark.process("tick-ledger.sh run through a symlink to the skill directory from another working directory")
def test_cli_run_through_a_symlink_to_the_skill_directory_from_another_cwd_ticks_the_relative_ledger_as_it_does_in_place(
        tmp_path, run_cli):
    tick_ledger = importlib.import_module("veri.tick_ledger")
    seed = "# Plan for #42\n\n- [ ] add lowercasing\n- [ ] collapse to single hyphen\n"
    (tmp_path / "linked-skill").symlink_to(SCRIPTS.parent, target_is_directory=True)
    for name in ("in-place", "caller"):
        (tmp_path / name).mkdir()
        (tmp_path / name / "issue-42.md").write_text(seed)

    code, out, err = run_cli(tick_ledger, ["--refactor-pending", "issue-42.md", "collapse to single hyphen"],
                             cwd=tmp_path / "in-place")
    ran = subprocess.run([str(tmp_path / "linked-skill" / "scripts" / "tick-ledger.sh"), "--refactor-pending",
                          "issue-42.md", "collapse to single hyphen"],
                         cwd=tmp_path / "caller", stdin=subprocess.DEVNULL, capture_output=True, text=True)

    assert (ran.returncode, ran.stdout, ran.stderr) == (code, out, err) == (0, "", "")
    assert (tmp_path / "caller" / "issue-42.md").read_bytes() == (tmp_path / "in-place" / "issue-42.md").read_bytes()
    assert "- [x] collapse to single hyphen ⟂ refactor pending\n" in (tmp_path / "caller" / "issue-42.md").read_text()
