"""merge-lock.sh gate's usage guard in veri/merge_lock.py."""
import subprocess

from veri import merge_lock

USAGE = "usage: merge-lock.sh gate [--keep] --pid <pid> -- <cmd>"


def test_2414_gate_refuses_a_pid_that_is_not_a_positive_integer_without_running_the_command(
        tmp_path, monkeypatch, capsys):
    ran = []
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: ran.append(a) or subprocess.CompletedProcess(a, 0))
    outcomes = {}
    for args in (["--pid", "--", "true"], ["--pid", "abc", "--", "true"], ["--keep", "--pid", "0", "--", "true"]):
        lock = tmp_path / ".tdd" / "merge.lock"
        code = merge_lock._gate(str(lock), str(lock / "holder"), args)
        err = capsys.readouterr().err
        outcomes[tuple(args)] = (code, USAGE in err)
    assert outcomes == {a: (2, True) for a in outcomes}
    assert ran == []
    assert not (tmp_path / ".tdd" / "merge.lock").exists()
