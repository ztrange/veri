"""run_conductor.main's skill snapshot on disk: read-only while the run executes it, removed at exit (#3963)."""
import importlib
import os

import pinned_scripts
from test_run_conductor_process import fake_pin, fake_snapshot, past_the_guards, scratch_tmpdir

COMMIT = "1" * 40
SKILL = {"SKILL.md": "# skill\n", "scripts/status.sh": "#!/bin/sh\n"}


def launched(tmp_path, monkeypatch, capfdbinary, probe, issue="4242", files=SKILL):
    """run_conductor.main(<issue>) with git and tar faked, the launch replaced by <probe>(snapshot); answers
    (exit code, names left in the scratch TMPDIR)."""
    past_the_guards(monkeypatch)
    for name in ("VERI_NEW_SKILL", "VERI_SKILL_COMMIT", "VERI_SKILL_CLONE", "VERI_SKILL_REF", "VERI_SKILL_UNPINNED"):
        monkeypatch.delenv(name, raising=False)
    scratch = tmp_path / "tmp" if (tmp_path / "tmp").is_dir() else scratch_tmpdir(tmp_path, monkeypatch)
    monkeypatch.chdir(tmp_path)
    calls = fake_pin(monkeypatch, COMMIT, {COMMIT + "^{commit}"})
    fake_snapshot(monkeypatch, calls, 0, 0, files=files)
    run_conductor = importlib.import_module("veri.run_conductor")
    monkeypatch.setattr(run_conductor, "launch", lambda snapshot, *_, **__: probe(snapshot) or 0)
    code = run_conductor.main([issue])
    capfdbinary.readouterr()
    return code, sorted(os.listdir(scratch))


def test_main_removes_a_snapshot_whose_files_and_directories_are_read_only_at_exit_leaving_nothing_of_it_3963(
        tmp_path, monkeypatch, capfdbinary):
    assert launched(tmp_path, monkeypatch, capfdbinary, pinned_scripts.make_read_only) == (0, [])


def test_main_replaces_a_read_only_pinned_scripts_copy_the_last_launch_left_on_the_next_launch_3963(
        tmp_path, monkeypatch, capfdbinary):
    run_conductor = importlib.import_module("veri.run_conductor")
    monkeypatch.setattr(run_conductor, "is_registered_worktree", lambda issue: True)
    kept = tmp_path / ".tdd" / "wt" / "4242" / ".tdd" / "pinned-scripts"
    first = launched(tmp_path, monkeypatch, capfdbinary, lambda snapshot: None)
    pinned_scripts.make_read_only(str(kept))

    second = launched(tmp_path, monkeypatch, capfdbinary, lambda snapshot: None,
                      files={"SKILL.md": "# skill\n", "scripts/status.sh": "#!/bin/sh\necho second\n"})

    assert (first, second, (kept / "status.sh").read_text(), (kept / ".gitignore").read_text()) == (
        (0, []), (0, []), "#!/bin/sh\necho second\n", "*\n")
