"""In-process cases for veri/seam_settle.py, the module seam-settle.sh is a shim over (PRD 038.1 SC6, #4342)."""
import hashlib
import importlib
import os

import pytest

STEP = "one thing works ⟦criterion 1⟧"
LEDGER = "# Plan for #12\n\n- [x] %s ⟂ refactor pending\n- [ ] two ⟦criterion 2⟧\n" % STEP
GREEN_SHA = "d" * 40


@pytest.fixture
def settle(monkeypatch, run_cli, tmp_path):
    """settle(*argv, ledger=LEDGER) runs seam-settle for issue 12 from the main tree, the run's worktree at
    .tdd/wt/12, git answering GREEN_SHA; returns (code, stdout, stderr, the record's text or None)."""
    fused = importlib.import_module("veri.fused")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    calls = []

    def fake(name, *args, cwd=None, **kw):
        calls.append((os.path.basename(name), args))
        return (0, GREEN_SHA + "\n", "") if args[:2] == ("log", "-1") else (2, "", "unexpected call")

    monkeypatch.setattr(fused, "run_script", fake)

    def go(*argv, ledger=LEDGER):
        (wt / ".tdd" / "issue-12.md").write_text(ledger)
        code, out, err = run_cli(importlib.import_module("veri.seam_settle"), ["12", *argv], cwd=str(tmp_path))
        record = wt / ".tdd" / ("issue-12-" + argv[0]) if argv else None
        return code, out, err, record.read_text() if record is not None and record.exists() else None

    go.wt, go.calls = wt, calls
    return go


def test_it_writes_green_halfs_and_refactor_halfs_records_the_step_from_the_ledger_and_green_sha_from_git_4342(settle):
    (settle.wt / ".tdd" / "verify-refactor.log").write_text("VERDICT: PASS\n")
    green = settle("green-half", "test_path=tests/test_h.py")
    refactor = settle("refactor-half")

    verdict = hashlib.sha256(b"VERDICT: PASS\n").hexdigest()
    assert green == (0, green[1], "", "step=%s\ngreen_sha=%s\ntest_path=tests/test_h.py\n" % (STEP, GREEN_SHA))
    assert refactor == (0, refactor[1], "", "step=%s\ngreen_sha=%s\nverdict_log=%s\n" % (STEP, GREEN_SHA, verdict))
    assert ("git", ("log", "-1", "--format=%H", "--", ".tdd/issue-12.md")) in settle.calls
