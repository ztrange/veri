"""run_conductor.pin_mode and skill_snapshot: which skill snapshot a launch executes, one case per row of the decision table."""
import importlib

import pytest


@pytest.fixture
def rc():
    return importlib.import_module("veri.run_conductor")


def test_an_unreadable_record_is_a_first_pin_even_with_the_env_and_a_released_marker(rc, tmp_path, monkeypatch):
    released = tmp_path / "released"
    released.write_text("")
    monkeypatch.setenv("VERI_NEW_SKILL", "1")

    assert rc.pin_mode(str(tmp_path / "missing"), str(released)) == "first"


def test_a_readable_record_with_veri_new_skill_1_re_pins_for_the_env(rc, tmp_path, monkeypatch):
    record = tmp_path / "record"
    record.write_text("abc\n")
    released = tmp_path / "released"
    released.write_text("")
    monkeypatch.setenv("VERI_NEW_SKILL", "1")

    assert rc.pin_mode(str(record), str(released)) == "env"


def test_a_readable_record_with_a_released_marker_re_pins_for_the_marker(rc, tmp_path, monkeypatch):
    record = tmp_path / "record"
    record.write_text("abc\n")
    released = tmp_path / "released"
    released.write_text("")
    monkeypatch.delenv("VERI_NEW_SKILL", raising=False)

    assert rc.pin_mode(str(record), str(released)) == "released"


def test_a_readable_record_with_neither_resumes(rc, tmp_path, monkeypatch):
    record = tmp_path / "record"
    record.write_text("abc\n")
    monkeypatch.setenv("VERI_NEW_SKILL", "0")

    assert rc.pin_mode(str(record), str(tmp_path / "released")) == "resume"


def test_a_head_that_does_not_resolve_is_unpinned_whatever_the_mode(rc, fake_processes):
    fake_processes.answers({"git -C /b rev-parse HEAD": (1, "", "")})

    assert rc.skill_snapshot("/b", "HEAD", "/nope", "resume") == ("unpinned", None, "", "", 0)


def test_a_resumed_run_whose_recorded_commit_resolves_keeps_it(rc, tmp_path, fake_processes):
    record = tmp_path / "record"
    record.write_text("oldsha\n")
    fake = fake_processes.answers({"git -C /b rev-parse HEAD": (0, "newsha\n", ""),
                                   "git -C /b cat-file -e oldsha^{commit}": (0, "", "")})

    snap = rc.skill_snapshot("/b", "HEAD", str(record), "resume")

    assert (snap, fake.calls) == (("kept", "oldsha", "", "", 0),
                                  ["git -C /b rev-parse HEAD", "git -C /b cat-file -e oldsha^{commit}"])


def test_a_resumed_run_whose_recorded_commit_does_not_resolve_is_refused_with_code_2(rc, tmp_path, fake_processes):
    record = tmp_path / "record"
    record.write_text("oldsha\n")
    fake_processes.answers({"git -C /b rev-parse HEAD": (0, "newsha\n", ""),
                            "git -C /b cat-file -e oldsha^{commit}": (128, "", "")})

    snap = rc.skill_snapshot("/b", "HEAD", str(record), "resume")

    assert snap == ("refused", None, "", "run-conductor: recorded skill commit 'oldsha' is not in '/b' — refusing to re-pin; "
                    "set VERI_NEW_SKILL=1 to take the new skill\n", 2)


def test_an_unreadable_record_on_resume_is_refused_naming_an_empty_commit(rc, tmp_path, fake_processes):
    fake_processes.answers({"git -C /b rev-parse HEAD": (0, "newsha\n", ""),
                            "git -C /b cat-file -e ^{commit}": (128, "", "")})

    snap = rc.skill_snapshot("/b", "HEAD", str(tmp_path / "missing"), "resume")

    assert (snap.kind, snap.message.startswith("run-conductor: recorded skill commit '' is not in '/b'")) == ("refused", True)


def test_a_first_launch_pins_the_resolved_head_without_looking_up_a_record(rc, tmp_path, fake_processes):
    fake = fake_processes.answers({"git -C /b rev-parse refs/remotes/origin/HEAD": (0, "headsha\n", "")})

    snap = rc.skill_snapshot("/b", "refs/remotes/origin/HEAD", str(tmp_path / "missing"), "first")

    assert (snap, len(fake.calls)) == (("first", "headsha", "first", "", 0), 1)


@pytest.mark.parametrize("mode", ["env", "released"])
def test_a_re_pin_takes_the_resolved_head_and_names_its_reason(rc, tmp_path, fake_processes, mode):
    fake = fake_processes.answers({"git -C /b rev-parse HEAD": (0, "headsha\n", "")})

    snap = rc.skill_snapshot("/b", "HEAD", str(tmp_path / "record"), mode)

    assert (snap, len(fake.calls)) == (("repin", "headsha", mode, "", 0), 1)
