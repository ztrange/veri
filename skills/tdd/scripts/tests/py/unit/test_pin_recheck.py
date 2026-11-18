"""Cases for pin_recheck's command line, driven in-process."""
import pytest

from veri import pin_recheck

SHA = "1234567" * 5 + "89abc"
REFUSAL = ("pin-recheck.sh: --branch-base must name the run's branch base, a sha matching ^[0-9a-f]{7,40}$\n"
           "usage: pin-recheck.sh --branch-base <sha> <base-sha> [--ledger <file>]\n")


@pytest.mark.parametrize("argv", [
    [SHA],
    [SHA, "--ledger", ".tdd/issue-1-mutations.md"],
    ["--branch-base"],
    ["--branch-base", "HEAD", SHA],
    ["--branch-base", "abc123", SHA],
    ["--branch-base", "a" * 41, SHA],
    ["--branch-base", SHA.upper(), SHA],
    ["--branch-base", SHA + "\n", SHA],
    [SHA, "--branch-base", SHA],
    [SHA, SHA],
    ["--branch-bas", SHA, SHA],
])
def test_4376_a_branch_base_flag_missing_or_not_a_hex_sha_exits_2_naming_the_flag_and_writes_no_receipt(
        tmp_path, run_cli, argv):
    (tmp_path / ".tdd").mkdir()

    code, out, err = run_cli(pin_recheck, argv, cwd=tmp_path)

    assert (code, out, err, (tmp_path / ".tdd" / "pin-recheck-ok").exists()) == (2, "", REFUSAL, False)
