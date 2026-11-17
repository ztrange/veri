"""In-process cases for veri/git.py, the git runner and symref parser veri's modules share."""
import importlib

import pytest

SHA = "1111111111111111111111111111111111111111"


@pytest.fixture
def git():
    return importlib.import_module("veri.git")


def test_symref_default_names_the_branch_a_symref_line_points_at(git):
    assert git.symref_default(f"ref: refs/heads/trunk\tHEAD\n{SHA}\tHEAD\n") == "trunk"


def test_symref_default_is_none_for_a_sha_line_alone(git):
    assert git.symref_default(f"{SHA}\tHEAD\n") is None


def test_symref_default_is_none_for_an_empty_answer(git):
    assert git.symref_default("") is None


def test_symref_default_is_none_for_an_empty_name(git):
    assert git.symref_default(f"ref: refs/heads/\tHEAD\n{SHA}\tHEAD\n") is None


def test_symref_default_is_none_without_whitespace_before_head(git):
    assert git.symref_default(f"ref: refs/heads/trunkHEAD\n{SHA}\tHEAD\n") is None


def test_symref_default_takes_the_first_of_two_symref_lines(git):
    answer = f"ref: refs/heads/trunk\tHEAD\nref: refs/heads/dev\tHEAD\n{SHA}\tHEAD\n"
    assert git.symref_default(answer) == "trunk"


def test_symref_default_is_none_when_head_is_on_the_next_line(git):
    assert git.symref_default(f"ref: refs/heads/trunk\nHEAD\n{SHA}\tHEAD\n") is None


@pytest.fixture
def runs(fake_processes):
    """install(answers) -> fake: answers maps the argv after "git" to (code, out, err) or an exception to raise;
    any other git command fails with code 1. fake.seen holds (argv, kwargs) per call."""
    def install(answers):
        table = {" ".join(("git",) + key): answer for key, answer in answers.items()}
        return fake_processes.answers(table, default=(1, "", "fatal: nope\n"), exact=True)
    return install


def test_out_returns_stdout_without_its_trailing_newline(git, runs, tmp_path):
    runs({("rev-parse", "HEAD"): (0, f"{SHA}\n", "")})
    assert git.out("rev-parse", "HEAD", cwd=tmp_path) == SHA


def test_out_runs_in_the_given_directory(git, runs, tmp_path):
    fake = runs({("rev-parse", "HEAD"): (0, "x\n", "")})
    git.out("rev-parse", "HEAD", cwd=tmp_path / "elsewhere")
    assert fake.seen[0][1]["cwd"] == tmp_path / "elsewhere"


def test_out_raises_git_failed_carrying_args_code_and_stderr(git, runs, tmp_path):
    runs({("rev-parse", "nope"): (128, "", "fatal: bad revision\n")})
    with pytest.raises(git.GitFailed) as caught:
        git.out("rev-parse", "nope", cwd=tmp_path)
    assert (caught.value.args_, caught.value.returncode, caught.value.stderr) == (
        ("rev-parse", "nope"), 128, "fatal: bad revision\n")


def test_out_raises_git_failed_without_a_return_code_when_git_is_missing(git, runs, tmp_path):
    runs({("status",): FileNotFoundError("git")})
    with pytest.raises(git.GitFailed) as caught:
        git.out("status", cwd=tmp_path)
    assert caught.value.returncode is None


def test_git_failed_message_names_the_command(git):
    assert str(git.GitFailed(("fetch", "-q"), 1, "")) == "git fetch -q failed (exit 1)"


def test_ok_is_true_on_exit_zero(git, runs, tmp_path):
    runs({("rev-parse", "-q", "--verify", "HEAD"): (0, "", "")})
    assert git.ok("rev-parse", "-q", "--verify", "HEAD", cwd=tmp_path) is True


def test_ok_is_false_on_a_non_zero_exit(git, runs, tmp_path):
    runs({})
    assert git.ok("rev-parse", "--verify", "nope", cwd=tmp_path) is False


def test_ok_is_false_when_git_is_missing(git, runs, tmp_path):
    runs({("status",): FileNotFoundError("git")})
    assert git.ok("status", cwd=tmp_path) is False


LOCAL = ("symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD")
REMOTE = ("ls-remote", "--symref", "origin", "HEAD")


def test_default_branch_reads_the_local_origin_head_first(git, runs, tmp_path):
    fake = runs({LOCAL: (0, "origin/trunk\n", "")})
    assert git.default_branch(cwd=tmp_path) == "trunk"
    assert [tuple(c[0][1:]) for c in fake.seen] == [LOCAL]


def test_default_branch_keeps_a_slash_in_the_branch_name(git, runs, tmp_path):
    runs({LOCAL: (0, "origin/release/1.x\n", "")})
    assert git.default_branch(cwd=tmp_path) == "release/1.x"


def test_default_branch_asks_the_remote_when_origin_head_is_unset(git, runs, tmp_path):
    runs({REMOTE: (0, f"ref: refs/heads/dev\tHEAD\n{SHA}\tHEAD\n", "")})
    assert git.default_branch(cwd=tmp_path) == "dev"


def test_default_branch_believes_the_remote_symref_whatever_ls_remote_s_exit_code(git, runs, tmp_path):
    runs({REMOTE: (2, f"ref: refs/heads/trunk\tHEAD\n{SHA}\tHEAD\n", "")})
    assert git.default_branch(cwd=tmp_path) == "trunk"


def test_default_branch_is_none_when_the_remote_names_none(git, runs, tmp_path):
    runs({REMOTE: (0, f"{SHA}\tHEAD\n", "")})
    assert git.default_branch(cwd=tmp_path) is None


def test_default_branch_is_none_when_the_remote_fails(git, runs, tmp_path):
    runs({})
    assert git.default_branch(cwd=tmp_path) is None


def test_default_branch_is_none_when_git_is_missing(git, runs, tmp_path):
    runs({LOCAL: FileNotFoundError("git"), REMOTE: FileNotFoundError("git")})
    assert git.default_branch(cwd=tmp_path) is None


def test_default_branch_is_none_when_the_remote_never_answers_within_the_network_bound(git, runs, tmp_path, monkeypatch):
    import process_fakes
    monkeypatch.setenv("VERI_GIT_NETWORK_TIMEOUT", "1")
    fake = runs({REMOTE: process_fakes.HANGS})
    monkeypatch.setattr(git.os, "killpg", lambda pid, sig: fake.popens[-1].send_signal(sig))

    assert git.default_branch(cwd=tmp_path) is None


def test_default_branch_local_only_never_asks_the_remote(git, runs, tmp_path):
    fake = runs({REMOTE: (0, "ref: refs/heads/dev\tHEAD\n", "")})
    assert git.default_branch(cwd=tmp_path, remote=False) is None
    assert [tuple(c[0][1:]) for c in fake.seen] == [LOCAL]


def test_default_branch_runs_both_questions_in_the_given_directory(git, runs, tmp_path):
    fake = runs({})
    git.default_branch(cwd=tmp_path / "clone")
    assert [c[1]["cwd"] for c in fake.seen] == [tmp_path / "clone"] * 2
