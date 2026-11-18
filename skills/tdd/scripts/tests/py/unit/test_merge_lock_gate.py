"""merge-lock.sh gate's usage guard in veri/merge_lock.py."""
import os

from veri import merge_lock

USAGE = "usage: merge-lock.sh gate [--keep] --pid <pid> [--owner <token>] -- <cmd>"


def test_2414_gate_refuses_a_pid_that_is_not_a_positive_integer_without_running_the_command(
        tmp_path, capsys, fake_processes):
    fake = fake_processes.answers({})
    outcomes = {}
    for args in (["--pid", "--", "true"], ["--pid", "abc", "--", "true"], ["--keep", "--pid", "0", "--", "true"]):
        lock = tmp_path / ".tdd" / "merge.lock"
        code = merge_lock._gate(str(lock), str(lock / "holder"), args)
        err = capsys.readouterr().err
        outcomes[tuple(args)] = (code, USAGE in err)
    assert outcomes == {a: (2, True) for a in outcomes}
    assert fake.calls == []
    assert not (tmp_path / ".tdd").exists()


def test_4373_gate_with_no_lock_exits_2_without_running_the_command(tmp_path, capsys, fake_processes):
    fake = fake_processes.answers({"true": (0, "", "")})
    lock = tmp_path / ".tdd" / "merge.lock"
    code = merge_lock._gate(str(lock), str(lock / "holder"), ["--keep", "--pid", "4242", "--owner", "tok", "--", "true"])
    err = capsys.readouterr().err
    assert (code, fake.calls, "not run" in err, lock.exists()) == (2, [], True, False)


def test_4373_gate_with_a_lock_held_by_another_pid_or_owner_exits_2_without_running_the_command_naming_the_holder(
        tmp_path, capsys, monkeypatch, fake_processes):
    monkeypatch.setattr(merge_lock, "_start_time", lambda pid: "t")
    fake = fake_processes.answers({"true": (0, "", "")})
    me = str(os.getpid())
    lock = str(tmp_path / ".tdd" / "merge.lock")
    record = os.path.join(lock, "holder")
    merge_lock._take(lock, record, ["--pid", me, "--owner", "token-a"])
    capsys.readouterr()
    outcomes = {}
    for name, caller in (("other pid", ["--pid", str(int(me) + 1), "--owner", "token-a"]),
                         ("other owner", ["--pid", me, "--owner", "token-b"]),
                         ("no owner", ["--pid", me])):
        code = merge_lock._gate(lock, record, ["--keep", *caller, "--", "true"])
        err = capsys.readouterr().err
        outcomes[name] = (code, f"{me} " in err and "token-a" in err, os.path.isdir(lock))
    assert outcomes == {n: (2, True, True) for n in outcomes}
    assert fake.calls == []
