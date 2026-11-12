"""Cases for drop-ledger-step.sh that start the real entry point."""
import subprocess

import pytest

from conftest import ROOT, SCRIPTS

SEED = (
    "# Plan for #42\n\n"
    "- [x] lowercase the slug ⟦criterion 1⟧\n"
    "- [ ] collapse to single hyphen ⟦criterion 2⟧\n"
    "- [ ] strip edge hyphens ⟦criterion 3⟧\n"
)


@pytest.mark.process("drop-ledger-step.sh run on a ledger committed in a scratch git repository")
def test_issue_3692_drop_ledger_step_removes_the_named_unchecked_step_and_keeps_every_other_line(tmp_path):
    git = ["git", "-c", "user.name=t", "-c", "user.email=t@example.com"]
    subprocess.run([*git, "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / "l.md").write_text(SEED)
    subprocess.run([*git, "add", "l.md"], cwd=tmp_path, check=True)
    subprocess.run([*git, "commit", "-q", "-m", "plan"], cwd=tmp_path, check=True)

    ran = subprocess.run([str(SCRIPTS / "drop-ledger-step.sh"), "l.md", "collapse to single hyphen"],
                         cwd=tmp_path, stdin=subprocess.DEVNULL, capture_output=True, text=True)

    assert ran.returncode == 0
    assert (tmp_path / "l.md").read_text() == SEED.replace("- [ ] collapse to single hyphen ⟦criterion 2⟧\n", "")


@pytest.mark.process("drop-ledger-step.sh refusals and the make drop-ledger-step target, on a scratch ledger")
def test_issue_3692_drop_ledger_step_refuses_bad_calls_and_the_make_target_drops_the_step(tmp_path):
    ledger = tmp_path / "l.md"
    ledger.write_text(SEED)
    script = str(SCRIPTS / "drop-ledger-step.sh")

    def run(argv):
        return subprocess.run(argv, cwd=tmp_path, stdin=subprocess.DEVNULL, capture_output=True, text=True)

    bare = run([script])
    none = run([script, "l.md", "no such step"])
    many = run([script, "l.md", "hyphen"])
    unchanged = ledger.read_text()
    made = run(["make", "-C", str(ROOT), "drop-ledger-step", f"LEDGER={ledger}", "STEP=strip edge hyphens"])

    assert (bare.returncode, "usage" in bare.stderr.lower()) == (2, True)
    assert (none.returncode, many.returncode, unchanged) == (1, 1, SEED)
    assert made.returncode == 0
    assert ledger.read_text() == SEED.replace("- [ ] strip edge hyphens ⟦criterion 3⟧\n", "")
