"""take, release and holder of veri/merge_lock.py under an --owner token."""
import os
import types

from veri import merge_lock


def test_3134_release_by_the_owner_token_that_took_the_lock_frees_it(tmp_path, monkeypatch):
    monkeypatch.setattr(merge_lock, "_start_time", lambda pid: "t")
    me = str(os.getpid())
    lock = str(tmp_path / ".tdd" / "merge.lock")
    record = os.path.join(lock, "holder")
    taken = merge_lock._take(lock, record, ["--pid", me, "--owner", "token-a"])
    released = merge_lock._release(lock, record, ["--pid", me, "--owner", "token-a"])
    assert (taken, released, merge_lock._holder(lock, record, [])) == (0, 0, 3)


def test_3134_release_by_another_owner_token_on_the_same_pid_is_refused(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(merge_lock, "_start_time", lambda pid: "t")
    me = str(os.getpid())
    lock = str(tmp_path / ".tdd" / "merge.lock")
    record = os.path.join(lock, "holder")
    merge_lock._take(lock, record, ["--pid", me, "--owner", "token-a"])
    refused = merge_lock._release(lock, record, ["--pid", me, "--owner", "token-b"])
    held = merge_lock._holder(lock, record, [])
    named = capsys.readouterr().out.split()[:1]
    assert (refused, os.path.isdir(lock), held, named) == (1, True, 0, [me])


def test_3134_release_without_an_owner_of_a_lock_taken_under_one_is_refused(tmp_path, monkeypatch):
    monkeypatch.setattr(merge_lock, "_start_time", lambda pid: "t")
    me = str(os.getpid())
    lock = str(tmp_path / ".tdd" / "merge.lock")
    record = os.path.join(lock, "holder")
    merge_lock._take(lock, record, ["--pid", me, "--owner", "token-a"])
    refused = merge_lock._release(lock, record, ["--pid", me])
    assert (refused, os.path.isdir(lock)) == (1, True)


def test_3134_failed_gate_under_another_owner_token_of_the_same_pid_leaves_the_lock_held(tmp_path, monkeypatch):
    monkeypatch.setattr(merge_lock, "_start_time", lambda pid: "t")
    monkeypatch.setattr(merge_lock.subprocess, "run", lambda cmd, **kw: types.SimpleNamespace(returncode=1))
    me = str(os.getpid())
    lock = str(tmp_path / ".tdd" / "merge.lock")
    record = os.path.join(lock, "holder")
    merge_lock._take(lock, record, ["--pid", me, "--owner", "token-a"])
    code = merge_lock._gate(lock, record, ["--pid", me, "--owner", "token-b", "--", "false"])
    assert (code, os.path.isdir(lock), merge_lock._holder(lock, record, [])) == (1, True, 0)


def test_3134_take_under_another_owner_token_of_the_same_pid_keeps_waiting_with_the_lock_held(tmp_path, monkeypatch):
    monkeypatch.setattr(merge_lock, "_start_time", lambda pid: "t")
    polls = []

    def poll():
        polls.append(1)
        if len(polls) > 3:
            raise RuntimeError("still waiting")

    monkeypatch.setattr(merge_lock, "_poll_wait", poll)
    me = str(os.getpid())
    lock = str(tmp_path / ".tdd" / "merge.lock")
    record = os.path.join(lock, "holder")
    merge_lock._take(lock, record, ["--pid", me, "--owner", "token-a"])
    try:
        code = merge_lock._take(lock, record, ["--pid", me, "--owner", "token-b"])
    except RuntimeError:
        code = "waiting"
    held = merge_lock._holder(lock, record, [])
    assert (code, held, open(record).read().split()[3:]) == ("waiting", 0, ["token-a"])


def test_3134_failed_gate_under_the_owner_token_that_took_the_lock_releases_it(tmp_path, monkeypatch):
    monkeypatch.setattr(merge_lock, "_start_time", lambda pid: "t")
    monkeypatch.setattr(merge_lock.subprocess, "run", lambda cmd, **kw: types.SimpleNamespace(returncode=1))
    me = str(os.getpid())
    lock = str(tmp_path / ".tdd" / "merge.lock")
    record = os.path.join(lock, "holder")
    merge_lock._take(lock, record, ["--pid", me, "--owner", "token-a"])
    code = merge_lock._gate(lock, record, ["--pid", me, "--owner", "token-a", "--", "false"])
    assert (code, os.path.isdir(lock)) == (1, False)


def test_3134_forced_release_frees_a_lock_taken_with_an_owner_by_a_dead_pid(tmp_path, monkeypatch):
    monkeypatch.setattr(merge_lock, "_start_time", lambda pid: "t")
    me = str(os.getpid())
    lock = str(tmp_path / ".tdd" / "merge.lock")
    record = os.path.join(lock, "holder")
    merge_lock._take(lock, record, ["--pid", me, "--owner", "token-a"])
    monkeypatch.setattr(merge_lock, "_alive", lambda pid: False)
    stale = merge_lock._holder(lock, record, [])
    released = merge_lock._release(lock, record, ["--force"])
    assert (stale, released, os.path.isdir(lock), merge_lock._holder(lock, record, [])) == (1, 0, False, 3)


def test_3134_an_owner_flag_without_a_token_is_a_usage_error_that_changes_nothing(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(merge_lock, "_start_time", lambda pid: "t")
    me = str(os.getpid())
    lock = str(tmp_path / ".tdd" / "merge.lock")
    record = os.path.join(lock, "holder")
    merge_lock._take(lock, record, ["--pid", me, "--owner", "token-a"])
    capsys.readouterr()
    outcomes = {}
    for verb, args in (("release", ["--pid", me, "--owner"]), ("take", ["--pid", me, "--owner"]),
                       ("gate", ["--pid", me, "--owner", "--", "true"])):
        code = merge_lock._HANDLERS[verb](lock, record, args)
        outcomes[verb] = (code, "usage: merge-lock.sh" in capsys.readouterr().err)
    assert outcomes == {v: (2, True) for v in ("release", "take", "gate")}
    assert open(record).read().split()[3:] == ["token-a"]



ORDERS = {"pid-first": lambda me: ["--pid", me, "--owner", "token-a"],
          "owner-first": lambda me: ["--owner", "token-a", "--pid", me]}


def test_3134_take_and_release_use_the_given_pid_and_owner_in_either_option_order(tmp_path, monkeypatch):
    monkeypatch.setattr(merge_lock, "_start_time", lambda pid: "t")
    me = str(os.getpid())
    outcomes = {}
    for name, order in ORDERS.items():
        lock = str(tmp_path / name / ".tdd" / "merge.lock")
        record = os.path.join(lock, "holder")
        taken = merge_lock._take(lock, record, order(me))
        recorded = open(record).read().split()
        released = merge_lock._release(lock, record, order(me))
        outcomes[name] = (taken, recorded[0], recorded[3:], released, os.path.isdir(lock))
    assert outcomes == {n: (0, me, ["token-a"], 0, False) for n in ORDERS}


def test_3134_gate_uses_the_given_pid_and_owner_in_either_option_order(tmp_path, monkeypatch):
    monkeypatch.setattr(merge_lock, "_start_time", lambda pid: "t")
    monkeypatch.setattr(merge_lock.subprocess, "run", lambda cmd, **kw: types.SimpleNamespace(returncode=1))
    me = str(os.getpid())
    outcomes = {}
    for name, order in ORDERS.items():
        lock = str(tmp_path / name / ".tdd" / "merge.lock")
        record = os.path.join(lock, "holder")
        merge_lock._take(lock, record, ["--pid", me, "--owner", "token-a"])
        code = merge_lock._gate(lock, record, order(me) + ["--", "false"])
        outcomes[name] = (code, os.path.isdir(lock))
    assert outcomes == {n: (1, False) for n in ORDERS}


def test_3134_a_pid_flag_without_a_value_is_a_usage_error(tmp_path, capsys):
    lock = str(tmp_path / ".tdd" / "merge.lock")
    outcomes = {}
    for verb in ("take", "release"):
        code = merge_lock._HANDLERS[verb](lock, os.path.join(lock, "holder"), ["--pid"])
        outcomes[verb] = (code, "usage: merge-lock.sh" in capsys.readouterr().err)
    assert outcomes == {"take": (2, True), "release": (2, True)}


def test_3134_holder_reads_the_start_time_not_the_owner_of_an_owner_bearing_record(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(merge_lock, "_start_time", lambda pid: "t")
    me = str(os.getpid())
    lock = str(tmp_path / ".tdd" / "merge.lock")
    record = os.path.join(lock, "holder")
    merge_lock._take(lock, record, ["--pid", me, "--owner", "token-a"])
    capsys.readouterr()
    live = merge_lock._holder(lock, record, [])
    monkeypatch.setattr(merge_lock, "_start_time", lambda pid: "other")
    reused = merge_lock._holder(lock, record, [])
    monkeypatch.setattr(merge_lock, "_start_time", lambda pid: "t")
    monkeypatch.setattr(merge_lock, "_alive", lambda pid: False)
    dead = merge_lock._holder(lock, record, [])
    assert (live, reused, dead) == (0, 1, 1)


def test_3579_release_by_the_owner_removes_the_token_file_holding_its_token(tmp_path, monkeypatch):
    monkeypatch.setattr(merge_lock, "_start_time", lambda pid: "t")
    me = str(os.getpid())
    lock = str(tmp_path / ".tdd" / "merge.lock")
    record = os.path.join(lock, "holder")
    token_file = tmp_path / ".git" / "veri-merge-42.token"
    token_file.parent.mkdir()
    token_file.write_text("token-a\n")
    merge_lock._take(lock, record, ["--pid", me, "--owner", "token-a"])
    released = merge_lock._release(lock, record, ["--pid", me, "--owner", "token-a"])
    assert (released, token_file.exists()) == (0, False)


def test_3579_forced_release_removes_the_token_file_holding_the_token_the_freed_record_named(tmp_path, monkeypatch):
    monkeypatch.setattr(merge_lock, "_start_time", lambda pid: "t")
    me = str(os.getpid())
    lock = str(tmp_path / ".tdd" / "merge.lock")
    record = os.path.join(lock, "holder")
    mine = tmp_path / ".git" / "veri-merge-42.token"
    theirs = tmp_path / ".git" / "veri-merge-43.token"
    mine.parent.mkdir()
    mine.write_text("token-a\n")
    merge_lock._take(lock, record, ["--pid", me, "--owner", "token-a"])
    theirs.write_text("token-b\n")
    monkeypatch.setattr(merge_lock, "_alive", lambda pid: False)
    released = merge_lock._release(lock, record, ["--force"])
    assert (released, os.path.isdir(lock), mine.exists(), theirs.exists()) == (0, False, False, True)


def test_3579_failed_gate_removes_the_token_file_holding_its_owner_token(tmp_path, monkeypatch):
    monkeypatch.setattr(merge_lock, "_start_time", lambda pid: "t")
    monkeypatch.setattr(merge_lock.subprocess, "run", lambda cmd, **kw: types.SimpleNamespace(returncode=1))
    me = str(os.getpid())
    lock = str(tmp_path / ".tdd" / "merge.lock")
    record = os.path.join(lock, "holder")
    token_file = tmp_path / ".git" / "veri-merge-42.token"
    token_file.parent.mkdir()
    token_file.write_text("token-a\n")
    merge_lock._take(lock, record, ["--pid", me, "--owner", "token-a"])
    code = merge_lock._gate(lock, record, ["--pid", me, "--owner", "token-a", "--", "false"])
    assert (code, os.path.isdir(lock), token_file.exists()) == (1, False, False)


def test_3579_release_by_a_different_owner_token_leaves_the_holders_token_file_untouched(tmp_path, monkeypatch):
    monkeypatch.setattr(merge_lock, "_start_time", lambda pid: "t")
    me = str(os.getpid())
    lock = str(tmp_path / ".tdd" / "merge.lock")
    record = os.path.join(lock, "holder")
    token_file = tmp_path / ".git" / "veri-merge-42.token"
    token_file.parent.mkdir()
    token_file.write_text("token-a\n")
    merge_lock._take(lock, record, ["--pid", me, "--owner", "token-a"])
    refused = merge_lock._release(lock, record, ["--pid", me, "--owner", "token-b"])
    assert (refused, os.path.isdir(lock), token_file.read_text()) == (1, True, "token-a\n")


def test_3579_take_removes_a_leftover_token_file_whose_token_the_new_holder_record_does_not_name(tmp_path, monkeypatch):
    monkeypatch.setattr(merge_lock, "_start_time", lambda pid: "t")
    me = str(os.getpid())
    lock = str(tmp_path / ".tdd" / "merge.lock")
    record = os.path.join(lock, "holder")
    mine = tmp_path / ".git" / "veri-merge-42.token"
    leftover = tmp_path / ".git" / "veri-merge-43.token"
    mine.parent.mkdir()
    mine.write_text("token-a\n")
    leftover.write_text("token-b\n")
    taken = merge_lock._take(lock, record, ["--pid", me, "--owner", "token-a"])
    assert (taken, mine.exists(), leftover.exists()) == (0, True, False)


def test_3579_take_keeps_an_old_token_file_the_live_holder_names_and_removes_a_fresh_one_naming_another_owner(tmp_path, monkeypatch):
    monkeypatch.setattr(merge_lock, "_start_time", lambda pid: "t")
    me = str(os.getpid())
    lock = str(tmp_path / ".tdd" / "merge.lock")
    record = os.path.join(lock, "holder")
    old_live = tmp_path / ".git" / "veri-merge-42.token"
    fresh_other = tmp_path / ".git" / "veri-merge-43.token"
    old_live.parent.mkdir()
    old_live.write_text("token-a\n")
    fresh_other.write_text("token-b\n")
    os.utime(old_live, (1, 1))
    taken = merge_lock._take(lock, record, ["--pid", me, "--owner", "token-a"])
    assert (taken, old_live.exists(), fresh_other.exists()) == (0, True, False)


def test_3793_release_with_no_other_holder_removes_every_token_of_its_owner_and_frees_the_lock(tmp_path, monkeypatch):
    monkeypatch.setattr(merge_lock, "_start_time", lambda pid: "t")
    me = str(os.getpid())
    lock = str(tmp_path / ".tdd" / "merge.lock")
    record = os.path.join(lock, "holder")
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    merge_lock._take(lock, record, ["--pid", me, "--owner", "A"])
    (git_dir / "veri-merge-1.token").write_text("A\n")
    (git_dir / "veri-merge-0.token").write_text("A\n")
    released = merge_lock._release(lock, record, ["--pid", me, "--owner", "A"])
    left = sorted(p.name for p in git_dir.glob("veri-merge-*.token"))
    assert (released, os.path.isdir(lock), left) == (0, False, [])
