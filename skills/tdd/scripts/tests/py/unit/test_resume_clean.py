"""In-process cases for veri/resume_clean.py, the module resume-clean.sh is a shim over."""
import importlib

import pytest

APPENDS = "diff --git a/.tdd/issue-7.md b/.tdd/issue-7.md\n+appended line\n"


@pytest.mark.parametrize("appends", ["", APPENDS], ids=["without-appends", "with-appends"])
def test_a_failing_reset_exits_2_with_one_stderr_line_naming_it_and_with_appends_the_kept_file_and_the_stray_paths_4043(
        appends, run_cli, fake_processes, tmp_path):
    resume_clean = importlib.import_module("veri.resume_clean")
    (tmp_path / ".git").mkdir()
    fake_processes.answers({
        "git diff --binary HEAD -- .tdd": (0, appends, ""),
        "git status --porcelain -uall": (0, "?? stray.txt\n M kept.py\n", ""),
        "git reset --hard HEAD": (128, "", "fatal: Unable to create '.git/index.lock': File exists.\n"),
        "git rev-parse --git-path kept-tdd-appends.diff": (0, ".git/kept-tdd-appends.diff\n", ""),
    })

    code, out, err = run_cli(resume_clean, [], cwd=tmp_path)

    kept = (tmp_path / ".git" / "kept-tdd-appends.diff").resolve()
    saved = "; appends saved in %s; stray: stray.txt kept.py" % kept if appends else ""
    assert (code, out, err) == (2, "", "resume-clean: git reset --hard HEAD failed%s\n" % saved)
    assert (kept.read_text() if kept.exists() else None) == (appends or None)
