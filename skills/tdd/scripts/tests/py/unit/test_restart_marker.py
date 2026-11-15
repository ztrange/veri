"""In-process cases for veri/restart_marker.py, the owner of a run's restart-pending marker."""
import importlib
import os

import pytest

DEAD_PID = "2147483646"


def marker():
    return importlib.import_module("veri.restart_marker")


def write(tmp_path, content):
    (tmp_path / ".tdd").mkdir(exist_ok=True)
    (tmp_path / ".tdd" / "restart-pending").write_bytes(content)


def test_path_is_the_restart_pending_file_of_the_runs_tdd_directory(tmp_path):
    assert marker().path(str(tmp_path)) == str(tmp_path / ".tdd" / "restart-pending")


def test_claim_creates_the_tdd_directory_and_writes_the_pid_and_a_newline(tmp_path):
    marker().claim(str(tmp_path), 4321)

    assert (tmp_path / ".tdd" / "restart-pending").read_bytes() == b"4321\n"


def test_clear_removes_the_marker_and_raises_when_there_is_none(tmp_path):
    write(tmp_path, b"1\n")
    marker().clear(str(tmp_path))

    assert not (tmp_path / ".tdd" / "restart-pending").exists()
    with pytest.raises(FileNotFoundError):
        marker().clear(str(tmp_path))


# The truth table: marker content -> in_flight(run, unreadable=...)
#   marker missing                            False   False
#   empty / whitespace only                   the unreadable policy
#   non-digit text                            the unreadable policy
#   digits of a dead pid                      False   False
#   digits of a live pid                      True    True
#   pid probe raises PermissionError          the unreadable policy
#   marker open raises OSError (not missing)  the unreadable policy
@pytest.mark.parametrize("unreadable", [True, False])
@pytest.mark.parametrize("content,expect", [
    (None, "no"),
    (b"", "policy"),
    (b"  \n", "policy"),
    (b"abc\n", "policy"),
    (b"\xff\xfe", "policy"),
    (DEAD_PID.encode() + b"\n", "no"),
    (b"99999999999999999999\n", "no"),
    (b"9" * 5000 + b"\n", "policy"),
    ("live", "yes"),
])
def test_in_flight_follows_the_truth_table(tmp_path, unreadable, content, expect):
    if content == "live":
        content = b"%d\n" % os.getpid()
    if content is not None:
        write(tmp_path, content)

    answer = marker().in_flight(str(tmp_path), unreadable=unreadable)

    assert answer == {"no": False, "yes": True, "policy": unreadable}[expect]


@pytest.mark.parametrize("unreadable", [True, False])
def test_in_flight_applies_the_policy_when_the_pid_probe_is_denied(tmp_path, monkeypatch, unreadable):
    write(tmp_path, b"1234\n")

    def denied(pid, sig):
        raise PermissionError

    monkeypatch.setattr(os, "kill", denied)

    assert marker().in_flight(str(tmp_path), unreadable=unreadable) is unreadable


@pytest.mark.parametrize("unreadable", [True, False])
def test_in_flight_applies_the_policy_when_the_marker_cannot_be_opened(tmp_path, monkeypatch, unreadable):
    write(tmp_path, b"1234\n")
    module = marker()

    def denied(*args, **kwargs):
        raise PermissionError

    monkeypatch.setattr(module, "open", denied, raising=False)

    assert module.in_flight(str(tmp_path), unreadable=unreadable) is unreadable


def test_in_flight_requires_the_policy_to_be_named(tmp_path):
    with pytest.raises(TypeError):
        marker().in_flight(str(tmp_path))
