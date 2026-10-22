"""Cases for veri/resume_clean.py that start a real process."""
import importlib
import subprocess

import pytest


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.com", *args],
                          check=True, stdout=subprocess.PIPE, text=True).stdout


@pytest.mark.process("git")
def test_main_discards_an_untracked_file_and_a_modified_tracked_file_listing_each_and_leaves_tdd_untouched_1967(
        tmp_path, run_cli):
    resume_clean = importlib.import_module("veri.resume_clean")
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    (repo / ".gitignore").write_text(".tdd/*.log\n")
    (repo / "file.txt").write_text("one\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "base")
    (repo / "file.txt").write_text("two\n")
    (repo / "other.txt").write_text("stray\n")
    (repo / ".tdd").mkdir()
    (repo / ".tdd" / "leaf.log").write_text("log\n")
    (repo / ".tdd" / "issue-1-refactor-owed.md").write_text("owed\n")

    code, out, err = run_cli(resume_clean, [], cwd=repo)

    assert (code, sorted(out.splitlines()), err) == (0, ["?? other.txt", " M file.txt"][::-1], "")
    assert git(repo, "status", "--porcelain", "--", ":!.tdd").strip() == ""
    assert (repo / "file.txt").read_text() == "one\n"
    assert not (repo / "other.txt").exists()
    assert (repo / ".tdd" / "leaf.log").read_text() == "log\n"
    assert (repo / ".tdd" / "issue-1-refactor-owed.md").read_text() == "owed\n"


@pytest.mark.process("git")
def test_main_reapplies_uncommitted_tdd_appends_byte_for_byte_while_still_discarding_the_tracked_change_outside_tdd_1967(
        tmp_path, run_cli):
    resume_clean = importlib.import_module("veri.resume_clean")
    repo = tmp_path / "repo"
    (repo / ".tdd").mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    (repo / "file.txt").write_text("one\n")
    (repo / ".tdd" / "issue-7.md").write_text("- [ ] step\n")
    (repo / ".tdd" / "events.log").write_text("start\n")
    git(repo, "add", "-f", ".")
    git(repo, "commit", "-q", "-m", "base")
    (repo / "file.txt").write_text("two\n")
    with open(repo / ".tdd" / "issue-7.md", "a") as f:
        f.write("appended line\n")
    with open(repo / ".tdd" / "events.log", "a") as f:
        f.write("event two\n")

    code, out, err = run_cli(resume_clean, [], cwd=repo)

    assert code == 0
    assert (repo / ".tdd" / "issue-7.md").read_bytes() == b"- [ ] step\nappended line\n"
    assert (repo / ".tdd" / "events.log").read_bytes() == b"start\nevent two\n"
    assert (repo / "file.txt").read_text() == "one\n"


@pytest.mark.process("git")
def test_main_unticks_working_ticks_the_committed_ledger_does_not_hold_counted_and_touches_nothing_else_1967(
        tmp_path, run_cli):
    resume_clean = importlib.import_module("veri.resume_clean")
    repo = tmp_path / "repo"
    (repo / ".tdd").mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    (repo / ".tdd" / "issue-7.md").write_text("# plan\n- [x] one\n- [ ] two\n- [ ] three\n")
    (repo / ".tdd" / "issue-8.md").write_text("- [x] kept ⟂ refactor pending\n- [ ] next\n")
    (repo / ".tdd" / "notes.md").write_text("- [ ] zzz\n")
    git(repo, "add", "-f", ".")
    git(repo, "commit", "-q", "-m", "base")
    (repo / ".tdd" / "issue-7.md").write_text(
        "# plan\n- [x] one ⟂ refactor pending\n- [x] two ⟂ refactor pending\n- [x] one\nfree text\n- [ ] three\n")
    (repo / ".tdd" / "notes.md").write_text("- [x] zzz\n")

    code, out, err = run_cli(resume_clean, [], cwd=repo)

    assert code == 0
    assert (repo / ".tdd" / "issue-7.md").read_bytes() == (
        "# plan\n- [x] one ⟂ refactor pending\n- [ ] two\n- [ ] one\nfree text\n- [ ] three\n").encode()
    assert (repo / ".tdd" / "issue-8.md").read_bytes() == "- [x] kept ⟂ refactor pending\n- [ ] next\n".encode()
    assert (repo / ".tdd" / "notes.md").read_bytes() == b"- [x] zzz\n"


@pytest.mark.process("git")
def test_main_keeps_appends_it_cannot_reapply_in_the_git_dir_and_exits_2_with_one_stderr_line_naming_file_and_place_1967(
        tmp_path, run_cli):
    resume_clean = importlib.import_module("veri.resume_clean")
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    (repo / "file.txt").write_text("one\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "base")
    (repo / ".tdd").mkdir()
    (repo / ".tdd" / "fresh.md").write_text("start\n")
    git(repo, "add", "-f", ".tdd/fresh.md")
    git(repo, "commit", "-q", "-m", "ledger")
    git(repo, "config", "apply.whitespace", "error")
    with open(repo / ".tdd" / "fresh.md", "a") as f:
        f.write("trailing space \n")

    code, out, err = run_cli(resume_clean, [], cwd=repo)

    kept = repo / git(repo, "rev-parse", "--git-path", "kept-tdd-appends.diff").strip()
    assert code == 2
    assert kept.is_file() and ".tdd/fresh.md" in kept.read_text()
    assert len(err.splitlines()) == 1
    assert ".tdd/fresh.md" in err and "kept-tdd-appends.diff" in err


@pytest.mark.process("git")
def test_main_keeps_appends_at_a_suffixed_name_when_kept_file_exists_leaving_it_unchanged_and_naming_both_1967(
        tmp_path, run_cli):
    resume_clean = importlib.import_module("veri.resume_clean")
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    (repo / "file.txt").write_text("one\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "base")
    (repo / ".tdd").mkdir()
    (repo / ".tdd" / "fresh.md").write_text("start\n")
    git(repo, "add", "-f", ".tdd/fresh.md")
    git(repo, "commit", "-q", "-m", "ledger")
    git(repo, "config", "apply.whitespace", "error")
    kept = repo / git(repo, "rev-parse", "--git-path", "kept-tdd-appends.diff").strip()
    kept.write_text("earlier kept appends\n")
    with open(repo / ".tdd" / "fresh.md", "a") as f:
        f.write("trailing space \n")

    code, out, err = run_cli(resume_clean, [], cwd=repo)

    others = sorted(kept.parent.glob("kept-tdd-appends.diff.*"))
    assert kept.read_text() == "earlier kept appends\n"
    assert code == 2
    assert len(others) == 1 and ".tdd/fresh.md" in others[0].read_text()
    assert len(err.splitlines()) == 1
    assert str(kept) in err and str(others[0]) in err


@pytest.mark.process("git")
def test_main_exits_2_with_one_stderr_line_naming_the_failed_git_command_and_runs_nothing_after_it_1967(
        tmp_path, run_cli):
    resume_clean = importlib.import_module("veri.resume_clean")
    repo = tmp_path / "repo"
    (repo / ".tdd").mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    (repo / ".tdd" / "issue-7.md").write_text("- [ ] one\n")
    git(repo, "add", "-f", ".")
    git(repo, "commit", "-q", "-m", "base")
    (repo / ".tdd" / "issue-7.md").write_text("- [x] one\n")
    (repo / "stray.txt").write_text("stray\n")
    (repo / ".git" / "index.lock").write_text("")

    code, out, err = run_cli(resume_clean, [], cwd=repo)

    assert code == 2
    assert len(err.splitlines()) == 1 and "git reset --hard HEAD" in err
    assert (repo / "stray.txt").read_text() == "stray\n"
    assert (repo / ".tdd" / "issue-7.md").read_bytes() == b"- [x] one\n"
    assert out == ""
