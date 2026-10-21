"""In-process cases for veri/rebase_onto_default.py, the module rebase-onto-default.sh is a shim over."""
import importlib
import os
import pathlib
import re
import shutil
import subprocess
import sys
import textwrap
import types

import pytest

PRE = "1111111111111111111111111111111111111111"
ONTO = "2222222222222222222222222222222222222222"


class Cli:
    """veri.rebase_onto_default driven through run_cli; readouterr() returns what the runs since the last call wrote."""

    def __init__(self, run_cli):
        self.module = importlib.import_module("veri.rebase_onto_default")
        self.run_cli = run_cli
        self.out = self.err = ""

    def main(self, argv):
        code, out, err = self.run_cli(self.module, argv)
        self.out, self.err = self.out + out, self.err + err
        return code

    def readouterr(self):
        seen, self.out, self.err = (self.out, self.err), "", ""
        return types.SimpleNamespace(out=seen[0], err=seen[1])


@pytest.fixture
def rebase_onto_default():
    return importlib.import_module("veri.rebase_onto_default")


@pytest.fixture
def cli(run_cli):
    return Cli(run_cli)


def fake_git(monkeypatch, **overrides):
    """subprocess.run recording each command as one line, its program by basename, and
    answering each git call from a branch behind origin/main, its stdout only when piped;
    <overrides> maps a line to (exit code, stdout)."""
    answers = {
        "git rev-parse -q --verify --abbrev-ref refs/remotes/origin/HEAD": (0, "origin/main\n"),
        "git fetch -q origin": (0, ""),
        "git ls-remote origin refs/heads/main": (0, f"{ONTO}\trefs/heads/main\n"),
        "git rev-parse origin/main": (0, f"{ONTO}\n"),
        f"git merge-base --is-ancestor {ONTO} HEAD": (1, ""),
        "git rev-parse HEAD": (0, f"{PRE}\n"),
        f"git rebase -q {ONTO}": (0, ""),
    }
    answers.update(overrides)
    calls = []

    def fake_run(args, **kwargs):
        line = " ".join([os.path.basename(str(args[0]))] + [str(a) for a in args[1:]])
        calls.append(line)
        code, out = answers.get(line, (0, ""))
        return subprocess.CompletedProcess(
            args, code, out if kwargs.get("stdout") == subprocess.PIPE else None, "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    return calls


def test_main_exits_2_on_a_failed_fetch_3_when_up_to_date_0_when_rebased_and_ignores_arguments(
        monkeypatch, cli):
    def run(argv, **overrides):
        calls = fake_git(monkeypatch, **overrides)
        code = cli.main(argv)
        captured = cli.readouterr()
        assert code in range(0, 4)
        return code, captured.out, calls

    code, out, calls = run([], **{"git fetch -q origin": (1, "")})
    assert (code, out) == (2, "")
    assert [c for c in calls if c.startswith(("git ls-remote origin refs/heads/main",
                                              "git merge-base", "git rebase"))] == []

    up_to_date = {f"git merge-base --is-ancestor {ONTO} HEAD": (0, "")}
    code, out, calls = run([], **up_to_date)
    assert (code, out) == (3, "")
    assert [c for c in calls if c.startswith("git rebase")] == []

    code, out, calls = run([])
    assert (code, out) == (0, f"{PRE}\n{ONTO}\n")
    assert f"git rebase -q {ONTO}" in calls

    assert run(["--bogus"], **up_to_date)[:2] == run([], **up_to_date)[:2] == (3, "")


def test_main_falls_back_to_the_remote_symref_only_when_the_local_read_fails_and_keeps_its_refs_heads_name_whole(
        monkeypatch, cli):
    symref = "git ls-remote --symref origin HEAD"
    local = "git rev-parse -q --verify --abbrev-ref refs/remotes/origin/HEAD"

    def run(answer, **overrides):
        calls = fake_git(monkeypatch, **{local: (1, ""), symref: answer}, **overrides)
        fake_run = subprocess.run
        stderrs = {}

        def recording_run(args, **kwargs):
            line = " ".join([os.path.basename(str(args[0]))] + [str(a) for a in args[1:]])
            stderrs[line] = kwargs.get("stderr")
            return fake_run(args, **kwargs)

        monkeypatch.setattr(subprocess, "run", recording_run)
        code = cli.main([])
        return code, cli.readouterr().out, calls, stderrs

    calls = fake_git(monkeypatch)
    cli.main([])
    cli.readouterr()
    assert symref not in calls

    code, out, calls, stderrs = run((2, f"ref: refs/heads/trunk\tHEAD\n{ONTO}\tHEAD\n"),
                                    **{"git ls-remote origin refs/heads/trunk":
                                       (0, f"{ONTO}\trefs/heads/trunk\n"),
                                       "git rev-parse origin/trunk": (0, f"{ONTO}\n")})
    assert symref in calls
    assert stderrs[symref] == subprocess.DEVNULL
    after = calls[calls.index(symref) + 1:]
    assert after[:3] == ["git fetch -q origin", "git ls-remote origin refs/heads/trunk",
                         "git rev-parse origin/trunk"]
    assert (code, out) == (0, f"{PRE}\n{ONTO}\n")

    def names_a_default(calls):
        return [c for c in calls
                if c.startswith(("git ls-remote origin refs/heads/", "git rev-parse origin/"))
                and c not in ("git ls-remote origin refs/heads/", "git rev-parse origin/")]

    for answer in [(0, f"{ONTO}\tHEAD\n"), (0, f"ref: refs/tags/v1\tHEAD\n{ONTO}\tHEAD\n")]:
        code, out, calls, _ = run(answer)
        assert symref in calls
        assert names_a_default(calls) == []
        assert code in range(0, 4)

    code, out, calls, _ = run((0, f"ref: refs/heads/origin/x\tHEAD\n{ONTO}\tHEAD\n"))
    assert names_a_default(calls) == ["git ls-remote origin refs/heads/origin/x",
                                      "git rev-parse origin/origin/x"]


def test_main_refuses_with_2_and_the_not_set_line_before_any_fetch_when_no_default_branch_resolves_or_git_cannot_start(
        monkeypatch, cli):
    refusal = ("rebase-onto-default: refs/remotes/origin/HEAD is not set — "
               "no default branch to rebase onto\n")
    symref = "git ls-remote --symref origin HEAD"
    calls = fake_git(monkeypatch, **{
        "git rev-parse -q --verify --abbrev-ref refs/remotes/origin/HEAD": (1, ""),
        symref: (0, f"{ONTO}\tHEAD\n")})
    code = cli.main([])
    captured = cli.readouterr()
    assert (code, captured.out, captured.err) == (2, "", refusal)
    assert calls[calls.index(symref) + 1:] == []

    def no_git(args, **kwargs):
        raise FileNotFoundError(2, "No such file or directory", "git")

    monkeypatch.setattr(subprocess, "run", no_git)
    code = cli.main([])
    captured = cli.readouterr()
    assert (code, captured.out) == (2, "")
    assert captured.err.endswith(refusal)


def test_main_exits_2_when_ls_remote_fails_after_the_fetch_or_an_unchecked_rev_parse_echo_differs_from_its_first_field(
        monkeypatch, cli):
    ls_remote = "git ls-remote origin refs/heads/main"
    rev_parse = "git rev-parse origin/main"

    def run(**overrides):
        calls = fake_git(monkeypatch, **overrides)
        fake_run = subprocess.run
        stderrs = {}

        def recording_run(args, **kwargs):
            line = " ".join([os.path.basename(str(args[0]))] + [str(a) for a in args[1:]])
            stderrs[line] = kwargs.get("stderr")
            return fake_run(args, **kwargs)

        monkeypatch.setattr(subprocess, "run", recording_run)
        code = cli.main([])
        return code, cli.readouterr().out, calls, stderrs

    code, out, calls, stderrs = run(**{ls_remote: (2, f"{ONTO}\trefs/heads/main\n")})
    assert (code, out) == (2, "")
    assert "git fetch -q origin" in calls
    assert stderrs[ls_remote] == subprocess.DEVNULL
    assert [c for c in calls if c.startswith(("git merge-base", "git rebase"))] == []

    code, out, calls, _ = run(**{rev_parse: (128, "origin/main\n")})
    assert (code, out) == (2, "")
    assert [c for c in calls if c.startswith("git merge-base")] == []

    code, out, calls, _ = run(**{ls_remote: (0, "origin/main\trefs/heads/main\n"),
                                 rev_parse: (128, "origin/main\n")})
    assert "git merge-base --is-ancestor origin/main HEAD" in calls
    assert (code, out) == (3, "")


def test_main_drops_the_fetch_s_stdout_and_stderr_and_the_rebase_s_stdout_and_passes_the_rebase_s_stderr_through(
        monkeypatch, cli):
    fetch = "git fetch -q origin"
    rebase = f"git rebase -q {ONTO}"
    fake_git(monkeypatch)
    fake_run = subprocess.run
    speech = {fetch: ("fetch out\n", "fetch err\n"), rebase: ("rebase out\n", "rebase err\n")}

    def speaking_run(args, **kwargs):
        line = " ".join([os.path.basename(str(args[0]))] + [str(a) for a in args[1:]])
        out, err = speech.get(line, ("", ""))
        if kwargs.get("stdout") is None:
            sys.stdout.write(out)
        if kwargs.get("stderr") is None:
            sys.stderr.write(err)
        return fake_run(args, **kwargs)

    monkeypatch.setattr(subprocess, "run", speaking_run)
    code = cli.main([])
    captured = cli.readouterr()
    assert (code, captured.out) == (0, f"{PRE}\n{ONTO}\n")
    assert captured.err == "rebase err\n"


def test_main_aborts_a_conflicting_rebase_under_either_backend_and_returns_1_printing_the_abort_s_stdout_then_the_unmerged_files(
        monkeypatch, tmp_path, cli):
    rebase = f"git rebase -q {ONTO}"
    diff = "git diff --name-only --diff-filter=U"
    abort = "git rebase --abort"
    merge, apply = tmp_path / "rebase-merge", tmp_path / "rebase-apply"

    def run(present):
        calls = fake_git(monkeypatch, **{
            rebase: (1, ""),
            "git rev-parse --git-path rebase-merge --git-path rebase-apply": (0, f"{merge}\n{apply}\n"),
            "git rev-parse --git-path rebase-merge": (0, f"{merge}\n"),
            "git rev-parse --git-path rebase-apply": (0, f"{apply}\n"),
            diff: (0, "a.txt\nsub/b.txt\n\n\n"),
            abort: (1, "")})
        fake_run = subprocess.run

        def speaking_run(args, **kwargs):
            line = " ".join([os.path.basename(str(args[0]))] + [str(a) for a in args[1:]])
            if line == rebase:
                present.mkdir()
            if line == abort and kwargs.get("stdout") is None:
                sys.stdout.write("abort out\n")
            return fake_run(args, **kwargs)

        monkeypatch.setattr(subprocess, "run", speaking_run)
        code = cli.main([])
        present.rmdir()
        return code, cli.readouterr().out, calls

    for present in (merge, apply):
        code, out, calls = run(present)
        assert (code, out) == (1, "abort out\na.txt\nsub/b.txt\n")
        assert calls.index(diff) < calls.index(abort)


def test_main_returns_2_without_the_conflict_path_when_a_failed_rebase_leaves_neither_rebase_directory(
        monkeypatch, tmp_path, cli):
    calls = fake_git(monkeypatch, **{
        f"git rebase -q {ONTO}": (1, ""),
        "git rev-parse --git-path rebase-merge --git-path rebase-apply":
            (0, f"{tmp_path / 'rebase-merge'}\n{tmp_path / 'rebase-apply'}\n"),
        "git rev-parse --git-path rebase-merge": (0, f"{tmp_path / 'rebase-merge'}\n"),
        "git rev-parse --git-path rebase-apply": (0, f"{tmp_path / 'rebase-apply'}\n")})
    code = cli.main([])
    assert (code, cli.readouterr().out) == (2, "")
    assert [c for c in calls if c.startswith(("git diff", "git rebase --abort"))] == []


def test_main_returns_2_with_no_rebase_directory_prints_one_empty_line_for_no_unmerged_files_and_leaves_a_rebase_already_in_progress_alone(
        monkeypatch, tmp_path, cli):
    rebase = f"git rebase -q {ONTO}"
    diff = "git diff --name-only --diff-filter=U"
    abort = "git rebase --abort"
    merge, apply = tmp_path / "rebase-merge", tmp_path / "rebase-apply"
    refusal = ("fatal: It seems that there is already a rebase-merge directory, and\n"
               "I wonder if you are in the middle of another rebase.\n")

    def run(diff_answer, refuse=False, created=None):
        calls = fake_git(monkeypatch, **{
            rebase: (1, ""),
            "git rev-parse --git-path rebase-merge --git-path rebase-apply": (0, f"{merge}\n{apply}\n"),
            "git rev-parse --git-path rebase-merge": (0, f"{merge}\n"),
            "git rev-parse --git-path rebase-apply": (0, f"{apply}\n"),
            diff: diff_answer})
        fake_run = subprocess.run

        def refusing_run(args, **kwargs):
            line = " ".join([os.path.basename(str(args[0]))] + [str(a) for a in args[1:]])
            if created is not None and line == rebase:
                created.mkdir()
            if refuse and line == rebase and kwargs.get("stderr") is None:
                sys.stderr.write(refusal)
            return fake_run(args, **kwargs)

        monkeypatch.setattr(subprocess, "run", refusing_run)
        code = cli.main([])
        return code, cli.readouterr(), calls

    code, captured, calls = run((0, "a.txt\n"))
    assert (code, captured.out) == (2, "")
    assert [c for c in calls if c.startswith(("git diff", abort))] == []

    code, captured, calls = run((0, ""), created=merge)
    assert (code, captured.out) == (1, "\n")
    assert calls.index(diff) < calls.index(abort)

    code, captured, calls = run((0, "earlier.txt\n"), refuse=True)
    assert (code, captured.out) == (2, "")
    assert refusal in captured.err
    assert [c for c in calls if c in (diff, abort)] == []


def test_main_exits_2_on_git_s_refusal_when_a_rebase_directory_exists_before_it_runs_without_diffing_or_aborting(
        monkeypatch, tmp_path, cli):
    rebase = f"git rebase -q {ONTO}"
    diff = "git diff --name-only --diff-filter=U"
    abort = "git rebase --abort"
    merge, apply = tmp_path / "rebase-merge", tmp_path / "rebase-apply"
    refusal = ("fatal: It seems that there is already a rebase-merge directory, and\n"
               "I wonder if you are in the middle of another rebase.\n")
    merge.mkdir()
    calls = fake_git(monkeypatch, **{
        rebase: (1, ""),
        "git rev-parse --git-path rebase-merge --git-path rebase-apply": (0, f"{merge}\n{apply}\n"),
        "git rev-parse --git-path rebase-merge": (0, f"{merge}\n"),
        "git rev-parse --git-path rebase-apply": (0, f"{apply}\n"),
        diff: (0, "earlier.txt\n")})
    fake_run = subprocess.run

    def refusing_run(args, **kwargs):
        line = " ".join([os.path.basename(str(args[0]))] + [str(a) for a in args[1:]])
        if line == rebase and kwargs.get("stderr") is None:
            sys.stderr.write(refusal)
        return fake_run(args, **kwargs)

    monkeypatch.setattr(subprocess, "run", refusing_run)
    code = cli.main([])
    captured = cli.readouterr()
    assert (code, captured.out) == (2, "")
    assert refusal in captured.err
    assert [c for c in calls if c in (diff, abort)] == []


def test_main_returns_1_with_the_conflict_output_when_its_own_rebase_leaves_the_directory_the_two_name_git_path_call_did_not_see(
        monkeypatch, tmp_path, cli):
    rebase = f"git rebase -q {ONTO}"
    two_names = "git rev-parse --git-path rebase-merge --git-path rebase-apply"
    diff = "git diff --name-only --diff-filter=U"
    abort = "git rebase --abort"
    merge, apply = tmp_path / "rebase-merge", tmp_path / "rebase-apply"

    def run(present, diff_answer):
        calls = fake_git(monkeypatch, **{
            rebase: (1, ""),
            two_names: (0, f"{merge}\n{apply}\n"),
            "git rev-parse --git-path rebase-merge": (0, f"{merge}\n"),
            "git rev-parse --git-path rebase-apply": (0, f"{apply}\n"),
            diff: diff_answer,
            abort: (1, "")})
        fake_run = subprocess.run

        def conflicting_run(args, **kwargs):
            line = " ".join([os.path.basename(str(args[0]))] + [str(a) for a in args[1:]])
            if line == rebase:
                present.mkdir()
            if line == abort and kwargs.get("stdout") is None:
                sys.stdout.write("abort out\n")
            return fake_run(args, **kwargs)

        monkeypatch.setattr(subprocess, "run", conflicting_run)
        code = cli.main([])
        present.rmdir()
        return code, cli.readouterr().out, calls

    code, out, calls = run(merge, (0, ""))
    assert (code, out) == (1, "abort out\n\n")
    assert calls.index(two_names) < calls.index(rebase) < calls.index(diff) < calls.index(abort)

    for present in (merge, apply):
        code, out, calls = run(present, (0, "a.txt\nsub/b.txt\n\n\n"))
        assert (code, out) == (1, "abort out\na.txt\nsub/b.txt\n")
        assert calls.index(two_names) < calls.index(rebase) < calls.index(diff) < calls.index(abort)


def test_main_answers_the_cut_contract_cases_a_dirty_tree_refusal_an_unfetchable_origin_a_fallback_rebase_and_an_unreachable_fallback(
        monkeypatch, tmp_path, cli):
    local = "git rev-parse -q --verify --abbrev-ref refs/remotes/origin/HEAD"
    symref = "git ls-remote --symref origin HEAD"
    rebase = f"git rebase -q {ONTO}"
    refused = ("error: Your local changes to the following files would be overwritten by checkout:\n"
               "\tfile.txt\nerror: could not detach HEAD\n")

    def run(**overrides):
        calls = fake_git(monkeypatch, **{
            "git rev-parse --git-path rebase-merge --git-path rebase-apply":
                (0, f"{tmp_path / 'rebase-merge'}\n{tmp_path / 'rebase-apply'}\n"),
            "git rev-parse --git-path rebase-merge": (0, f"{tmp_path / 'rebase-merge'}\n"),
            "git rev-parse --git-path rebase-apply": (0, f"{tmp_path / 'rebase-apply'}\n")},
            **overrides)
        fake_run = subprocess.run

        def refusing_run(args, **kwargs):
            line = " ".join([os.path.basename(str(args[0]))] + [str(a) for a in args[1:]])
            result = fake_run(args, **kwargs)
            if line == rebase and result.returncode != 0 and kwargs.get("stderr") is None:
                sys.stderr.write(refused)
            return result

        monkeypatch.setattr(subprocess, "run", refusing_run)
        code = cli.main([])
        return code, cli.readouterr(), calls

    code, captured, calls = run(**{rebase: (1, "")})
    assert (code, captured.out) == (2, "")
    assert refused in captured.err
    assert [c for c in calls if c.startswith(("git diff", "git rebase --abort"))] == []

    code, captured, calls = run(**{"git fetch -q origin": (128, "")})
    assert (code, captured.out) == (2, "")
    assert [c for c in calls if c.startswith(("git merge-base", "git rebase"))] == []

    code, captured, calls = run(**{local: (1, ""),
                                   symref: (0, f"ref: refs/heads/main\tHEAD\n{ONTO}\tHEAD\n")})
    assert (code, captured.out) == (0, f"{PRE}\n{ONTO}\n")
    assert rebase in calls

    code, captured, calls = run(**{local: (1, ""), symref: (128, ""),
                                   "git fetch -q origin": (128, "")})
    assert (code, captured.out) == (2, "")
    assert "refs/remotes/origin/HEAD" in captured.err
    assert [c for c in calls if c.startswith(("git fetch", "git merge-base", "git rebase"))] == []


def test_main_leaves_a_rebase_already_in_progress_alone_and_exits_2_however_it_asks_for_the_rebase_directories_819(
        monkeypatch, tmp_path, cli):
    rebase = f"git rebase -q {ONTO}"
    merge = tmp_path / "rebase-merge"
    merge.mkdir()
    (merge / "head-name").write_text("refs/heads/caller\n")
    calls = fake_git(monkeypatch, **{rebase: (1, "")})
    fake_run = subprocess.run

    def git_path_run(args, **kwargs):
        if list(args[:3]) == ["git", "rev-parse", "--git-path"]:
            fake_run(args, **kwargs)
            names = [a for a in args[2:] if a != "--git-path"]
            out = "".join(f"{tmp_path / name}\n" for name in names)
            return subprocess.CompletedProcess(
                args, 0, out if kwargs.get("stdout") == subprocess.PIPE else None, "")
        return fake_run(args, **kwargs)

    monkeypatch.setattr(subprocess, "run", git_path_run)
    code = cli.main([])
    assert (code, cli.readouterr().out) == (2, "")
    assert [c for c in calls if c.startswith("git rebase") and c != rebase] == []
    assert sorted(p.name for p in merge.iterdir()) == ["head-name"]


def test_main_answers_each_ls_remote_shape_with_its_stdout_stderr_and_exit_code_when_origin_head_is_absent(
        monkeypatch, cli):
    refusal = ("rebase-onto-default: refs/remotes/origin/HEAD is not set — "
               "no default branch to rebase onto\n")
    local = "git rev-parse -q --verify --abbrev-ref refs/remotes/origin/HEAD"
    symref = "git ls-remote --symref origin HEAD"

    def run(answer, **overrides):
        fake_git(monkeypatch, **{local: (1, ""), symref: answer}, **overrides)
        code = cli.main([])
        captured = cli.readouterr()
        return code, captured.out, captured.err

    trunk = {"git ls-remote origin refs/heads/trunk": (0, f"{ONTO}\trefs/heads/trunk\n"),
             "git rev-parse origin/trunk": (0, f"{ONTO}\n")}
    assert run((0, f"ref: refs/heads/trunk\tHEAD\n{ONTO}\tHEAD\n"), **trunk) == (
        0, f"{PRE}\n{ONTO}\n", "")
    assert run((0, f"{ONTO}\tHEAD\n")) == (2, "", refusal)
    assert run((128, "")) == (2, "", refusal)


@pytest.mark.process("git: a real clone rebased onto an origin that moved")
def test_main_rebases_a_real_branch_behind_origin_main_exits_0_prints_the_pre_rebase_and_onto_shas_and_keeps_its_commit_on_top(
        monkeypatch, tmp_path, rebase_onto_default, run_cli):
    for who in ("AUTHOR", "COMMITTER"):
        monkeypatch.setenv(f"GIT_{who}_NAME", "veri")
        monkeypatch.setenv(f"GIT_{who}_EMAIL", "veri@example.test")

    def git(repo, *args):
        return subprocess.run(["git", "-C", str(repo), *args], check=True, text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.strip()

    def commit(repo, name, body, message):
        (repo / name).write_text(body)
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", message)

    origin, seed, clone = tmp_path / "origin.git", tmp_path / "seed", tmp_path / "clone"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], check=True)
    subprocess.run(["git", "init", "-q", "-b", "main", str(seed)], check=True)
    commit(seed, "file.txt", "base\n", "initial")
    git(seed, "push", "-q", str(origin), "main")
    subprocess.run(["git", "clone", "-q", str(origin), str(clone)], check=True, stderr=subprocess.DEVNULL)
    git(clone, "checkout", "-q", "-b", "tdd/1-a-run")
    commit(clone, "work.txt", "the run's work\n", "feat: a step's green commit (#1)")
    commit(seed, "other.txt", "another run's work\n", "feat: another run merged (#2)")
    git(seed, "push", "-q", str(origin), "main")
    pre = git(clone, "rev-parse", "HEAD")
    onto = git(seed, "rev-parse", "HEAD")

    code, out, err = run_cli(rebase_onto_default, [], cwd=clone)

    assert (code, out, err) == (0, f"{pre}\n{onto}\n", "")
    assert git(clone, "rev-parse", "HEAD~1") == onto
    assert git(clone, "log", "-1", "--format=%s") == "feat: a step's green commit (#1)"
    assert git(clone, "status", "--porcelain=v1", "--untracked-files=all") == ""


@pytest.mark.process("git: real clones left untouched by an up-to-date run and by an aborted conflicting rebase")
def test_main_leaves_head_the_tree_and_the_rebase_state_untouched_when_up_to_date_with_3_and_when_a_rebase_conflicts_with_1_under_either_backend(
        monkeypatch, tmp_path, rebase_onto_default, run_cli):
    for who in ("AUTHOR", "COMMITTER"):
        monkeypatch.setenv(f"GIT_{who}_NAME", "veri")
        monkeypatch.setenv(f"GIT_{who}_EMAIL", "veri@example.test")

    def git(repo, *args):
        return subprocess.run(["git", "-C", str(repo), *args], check=True, text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.strip()

    def commit(repo, files, message, *flags):
        for name, body in files.items():
            (repo / name).write_text(body)
        git(repo, "add", "-A")
        git(repo, "commit", "-q", *flags, "-m", message)

    def fixture(name, backend=None):
        root = tmp_path / name
        origin, seed, clone = root / "origin.git", root / "seed", root / "clone"
        root.mkdir()
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], check=True)
        subprocess.run(["git", "init", "-q", "-b", "main", str(seed)], check=True)
        commit(seed, {"file.txt": "base\n"}, "initial")
        git(seed, "push", "-q", str(origin), "main")
        subprocess.run(["git", "clone", "-q", str(origin), str(clone)], check=True,
                       stderr=subprocess.DEVNULL)
        if backend:
            git(clone, "config", "rebase.backend", backend)
        git(clone, "checkout", "-q", "-b", "tdd/1-a-run")
        return seed, origin, clone

    def untouched(clone, pre, code, out, err, want_code, want_out):
        assert code == want_code
        assert (err == "") == (want_code == 3)
        assert sorted(out.split()) == want_out
        assert git(clone, "rev-parse", "HEAD") == pre
        assert git(clone, "status", "--porcelain=v1", "--untracked-files=all") == ""
        for d in ("rebase-merge", "rebase-apply"):
            assert not os.path.exists(git(clone, "rev-parse", "--path-format=absolute", "--git-path", d))

    seed, origin, clone = fixture("up-to-date")
    commit(clone, {"work.txt": "the run's work\n"}, "feat: a step's green commit (#1)")
    git(clone, "fetch", "-q", "origin")
    pre = git(clone, "rev-parse", "HEAD")
    untouched(clone, pre, *run_cli(rebase_onto_default, [], cwd=clone), 3, [])

    for backend in (None, "apply"):
        seed, origin, clone = fixture(f"conflict-{backend}", backend)
        commit(clone, {"work.txt": "the run's work\n", "file.txt": "the run's edit\n"},
               "feat: a step's green commit (#1)")
        commit(seed, {"file.txt": "another run's edit\n", "work.txt": "another run's work\n"},
               "feat: another run merged (#2)")
        git(seed, "push", "-q", str(origin), "main")
        pre = git(clone, "rev-parse", "HEAD")
        untouched(clone, pre, *run_cli(rebase_onto_default, [], cwd=clone), 1, ["file.txt", "work.txt"])


@pytest.mark.process("rebase-onto-default.sh run through a symlink to the skill directory, from the caller's clone")
def test_main_run_through_a_symlink_from_another_directory_rebases_the_callers_clone_and_never_the_skills_repository(
        monkeypatch, tmp_path):
    for who in ("AUTHOR", "COMMITTER"):
        monkeypatch.setenv(f"GIT_{who}_NAME", "veri")
        monkeypatch.setenv(f"GIT_{who}_EMAIL", "veri@example.test")
    skill = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

    def git(repo, *args):
        return subprocess.run(["git", "-C", str(repo), *args], check=True, text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.strip()

    def commit(repo, name, body, message):
        (repo / name).write_text(body)
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", message)

    origin, seed, clone = tmp_path / "origin.git", tmp_path / "seed", tmp_path / "clone"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], check=True)
    subprocess.run(["git", "init", "-q", "-b", "main", str(seed)], check=True)
    commit(seed, "file.txt", "base\n", "initial")
    git(seed, "push", "-q", str(origin), "main")
    subprocess.run(["git", "clone", "-q", str(origin), str(clone)], check=True, stderr=subprocess.DEVNULL)
    git(clone, "checkout", "-q", "-b", "tdd/1-a-run")
    commit(clone, "work.txt", "the run's work\n", "feat: a step's green commit (#1)")
    commit(seed, "other.txt", "another run's work\n", "feat: another run merged (#2)")
    git(seed, "push", "-q", str(origin), "main")
    git(clone, "fetch", "-q", "origin")
    pre = git(clone, "rev-parse", "HEAD")
    onto = git(clone, "rev-parse", "origin/main")
    skill_head = git(skill, "rev-parse", "HEAD")
    (tmp_path / "linked-skill").symlink_to(skill, target_is_directory=True)

    done = subprocess.run([str(tmp_path / "linked-skill" / "scripts" / "rebase-onto-default.sh")],
                          cwd=clone, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    assert (done.returncode, done.stdout, done.stderr) == (0, f"{pre}\n{onto}\n", "")
    assert git(clone, "rev-parse", "HEAD~1") == onto
    assert git(skill, "rev-parse", "HEAD") == skill_head


@pytest.mark.process("git: a real resumed worktree whose tracked ledger carries an uncommitted append, discarded by the resume's own commands, then rebased onto a default branch that moved twice")
def test_main_after_the_resume_discard_rebases_a_ledger_with_an_uncommitted_append_and_keeps_the_append_across_two_resumes_1547(
        monkeypatch, tmp_path, rebase_onto_default, run_cli):
    for who in ("AUTHOR", "COMMITTER"):
        monkeypatch.setenv(f"GIT_{who}_NAME", "veri")
        monkeypatch.setenv(f"GIT_{who}_EMAIL", "veri@example.test")
    skill_md = pathlib.Path(__file__).resolve().parents[3] / "SKILL.md"
    discard = re.search(r"captures and discards whatever a killed leaf left uncommitted.*?```\n(.*?)```",
                        skill_md.read_text(), re.S).group(1)

    def git(repo, *args):
        return subprocess.run(["git", "-C", str(repo), *args], check=True, text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.strip()

    def commit(repo, name, body, message):
        (repo / name).parent.mkdir(exist_ok=True)
        (repo / name).write_text(body)
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", message)

    def resume(clone):
        subprocess.run(["bash", "-c", textwrap.dedent(discard)], cwd=clone, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return run_cli(rebase_onto_default, [], cwd=clone)[0]

    origin, seed, clone = tmp_path / "origin.git", tmp_path / "seed", tmp_path / "clone"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], check=True)
    subprocess.run(["git", "init", "-q", "-b", "main", str(seed)], check=True)
    commit(seed, "file.txt", "base\n", "initial")
    git(seed, "push", "-q", str(origin), "main")
    subprocess.run(["git", "clone", "-q", str(origin), str(clone)], check=True, stderr=subprocess.DEVNULL)
    git(clone, "checkout", "-q", "-b", "tdd/1-a-run")
    commit(clone, ".tdd/issue-1.md", "- [x] step one\n", "plan: scope #1 (#1)")
    commit(clone, "work.txt", "the run's work\n", "feat: a step's green commit (#1)")
    ledger = clone / ".tdd" / "issue-1.md"
    ledger.write_text(ledger.read_text() + "- [ ] step two ⟦added⟧\n")

    commit(seed, "other.txt", "another run's work\n", "feat: another run merged (#2)")
    git(seed, "push", "-q", str(origin), "main")
    assert resume(clone) == 0
    assert "- [ ] step two ⟦added⟧\n" in ledger.read_text()

    commit(seed, "third.txt", "a third run's work\n", "feat: a third run merged (#3)")
    git(seed, "push", "-q", str(origin), "main")
    assert resume(clone) == 0
    assert "- [ ] step two ⟦added⟧\n" in ledger.read_text()


@pytest.mark.process("git and tick-ledger.sh: a real resumed worktree whose ledger tick was written before a green commit that the kill prevented, discarded by the resume's own commands, then rebased")
def test_main_after_the_resume_discard_leaves_a_tick_whose_green_commit_never_landed_unticked_and_keeps_other_appends_1547(
        monkeypatch, tmp_path, rebase_onto_default, run_cli):
    for who in ("AUTHOR", "COMMITTER"):
        monkeypatch.setenv(f"GIT_{who}_NAME", "veri")
        monkeypatch.setenv(f"GIT_{who}_EMAIL", "veri@example.test")
    scripts = pathlib.Path(__file__).resolve().parents[2]
    discard = re.search(r"captures and discards whatever a killed leaf left uncommitted.*?```\n(.*?)```",
                        (scripts.parent / "SKILL.md").read_text(), re.S).group(1)

    def git(repo, *args):
        return subprocess.run(["git", "-C", str(repo), *args], check=True, text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.strip()

    def commit(repo, name, body, message):
        (repo / name).parent.mkdir(exist_ok=True)
        (repo / name).write_text(body)
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", message)

    origin, seed, clone = tmp_path / "origin.git", tmp_path / "seed", tmp_path / "clone"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], check=True)
    subprocess.run(["git", "init", "-q", "-b", "main", str(seed)], check=True)
    commit(seed, "file.txt", "base\n", "initial")
    git(seed, "push", "-q", str(origin), "main")
    subprocess.run(["git", "clone", "-q", str(origin), str(clone)], check=True, stderr=subprocess.DEVNULL)
    git(clone, "checkout", "-q", "-b", "tdd/1-a-run")
    commit(clone, ".tdd/issue-1.md", "- [ ] step one\n- [ ] step two\n", "plan: scope #1 (#1)")
    commit(clone, "work.txt", "before the green\n", "test: a red (#1)")
    ledger = clone / ".tdd" / "issue-1.md"
    subprocess.run([str(scripts / "tick-ledger.sh"), "--refactor-pending", str(ledger), "step one"], check=True)
    ledger.write_text(ledger.read_text() + "- [ ] step three ⟦added⟧\n")
    (clone / "work.txt").write_text("the green code, killed before its commit\n")

    commit(seed, "other.txt", "another run's work\n", "feat: another run merged (#2)")
    git(seed, "push", "-q", str(origin), "main")
    subprocess.run(["bash", "-c", textwrap.dedent(discard)], cwd=clone, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    assert run_cli(rebase_onto_default, [], cwd=clone)[0] == 0

    assert (clone / "work.txt").read_text() == "before the green\n"
    assert ledger.read_text() == "- [ ] step one\n- [ ] step two\n- [ ] step three ⟦added⟧\n"


@pytest.mark.process("git: a real resumed worktree whose uncommitted .tdd/ append no longer applies once the rebase moved the lines around it")
def test_main_stops_with_exit_2_naming_the_file_and_the_kept_appends_when_they_cannot_be_reapplied_after_the_rebase_1547(
        monkeypatch, tmp_path, rebase_onto_default, run_cli):
    for who in ("AUTHOR", "COMMITTER"):
        monkeypatch.setenv(f"GIT_{who}_NAME", "veri")
        monkeypatch.setenv(f"GIT_{who}_EMAIL", "veri@example.test")

    def git(repo, *args):
        return subprocess.run(["git", "-C", str(repo), *args], check=True, text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.strip()

    def commit(repo, name, body, message):
        (repo / name).parent.mkdir(exist_ok=True)
        (repo / name).write_text(body)
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", message)

    origin, seed, clone = tmp_path / "origin.git", tmp_path / "seed", tmp_path / "clone"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], check=True)
    subprocess.run(["git", "init", "-q", "-b", "main", str(seed)], check=True)
    commit(seed, ".tdd/notes.md", "a\nb\nc\n", "initial")
    git(seed, "push", "-q", str(origin), "main")
    subprocess.run(["git", "clone", "-q", str(origin), str(clone)], check=True, stderr=subprocess.DEVNULL)
    git(clone, "checkout", "-q", "-b", "tdd/1-a-run")
    commit(clone, "work.txt", "the run's work\n", "feat: a step's green commit (#1)")
    notes = clone / ".tdd" / "notes.md"
    notes.write_text("a\nb\nc\nd\n")
    commit(seed, ".tdd/notes.md", "a\nb\nchanged\n", "feat: another run merged (#2)")
    git(seed, "push", "-q", str(origin), "main")

    code, _, err = run_cli(rebase_onto_default, [], cwd=clone)

    kept = [pathlib.Path(token) if os.path.isabs(token) else clone / token for token in err.split()]
    kept = [path for path in kept if path.is_file() and path != notes and "+d\n" in path.read_text()]
    assert (code, ".tdd/notes.md" in err, len(kept)) == (2, True, 1)


@pytest.mark.process("git, tick-ledger.sh and add-ledger-step.sh: a real resumed worktree whose ledger carries an append right after a step ticked in the same uncommitted change, discarded by the resume's own commands, then rebased")
def test_main_after_the_resume_discard_keeps_an_append_right_after_a_tick_whose_green_commit_never_landed_and_unticks_the_step_1547(
        monkeypatch, tmp_path, rebase_onto_default, run_cli):
    for who in ("AUTHOR", "COMMITTER"):
        monkeypatch.setenv(f"GIT_{who}_NAME", "veri")
        monkeypatch.setenv(f"GIT_{who}_EMAIL", "veri@example.test")
    scripts = pathlib.Path(__file__).resolve().parents[2]
    discard = re.search(r"captures and discards whatever a killed leaf left uncommitted.*?```\n(.*?)```",
                        (scripts.parent / "SKILL.md").read_text(), re.S).group(1)

    def git(repo, *args):
        return subprocess.run(["git", "-C", str(repo), *args], check=True, text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.strip()

    def commit(repo, name, body, message):
        (repo / name).parent.mkdir(exist_ok=True)
        (repo / name).write_text(body)
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", message)

    origin, seed, clone = tmp_path / "origin.git", tmp_path / "seed", tmp_path / "clone"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], check=True)
    subprocess.run(["git", "init", "-q", "-b", "main", str(seed)], check=True)
    commit(seed, "file.txt", "base\n", "initial")
    git(seed, "push", "-q", str(origin), "main")
    subprocess.run(["git", "clone", "-q", str(origin), str(clone)], check=True, stderr=subprocess.DEVNULL)
    git(clone, "checkout", "-q", "-b", "tdd/1-a-run")
    commit(clone, ".tdd/issue-1.md", "- [ ] step one\n- [ ] step two\n", "plan: scope #1 (#1)")
    commit(clone, "work.txt", "before the green\n", "test: a red (#1)")
    ledger = clone / ".tdd" / "issue-1.md"
    subprocess.run([str(scripts / "tick-ledger.sh"), "--refactor-pending", str(ledger), "step one"], check=True)
    subprocess.run([str(scripts / "add-ledger-step.sh"), str(ledger), "after", "step one", "step added"], check=True)
    (clone / "work.txt").write_text("the green code, killed before its commit\n")

    commit(seed, "other.txt", "another run's work\n", "feat: another run merged (#2)")
    git(seed, "push", "-q", str(origin), "main")
    subprocess.run(["bash", "-c", textwrap.dedent(discard)], cwd=clone, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    assert run_cli(rebase_onto_default, [], cwd=clone)[0] == 0

    assert ledger.read_text() == "- [ ] step one\n- [ ] step added ⟦added⟧\n- [ ] step two\n"


@pytest.mark.process("git: a real resumed worktree whose ledger's last committed line has no trailing newline and carries an uncommitted append, discarded by the resume's own commands, then rebased")
def test_main_after_the_resume_discard_keeps_an_append_to_a_ledger_whose_last_committed_line_had_no_trailing_newline_1547(
        monkeypatch, tmp_path, rebase_onto_default, run_cli):
    for who in ("AUTHOR", "COMMITTER"):
        monkeypatch.setenv(f"GIT_{who}_NAME", "veri")
        monkeypatch.setenv(f"GIT_{who}_EMAIL", "veri@example.test")
    scripts = pathlib.Path(__file__).resolve().parents[2]
    discard = re.search(r"captures and discards whatever a killed leaf left uncommitted.*?```\n(.*?)```",
                        (scripts.parent / "SKILL.md").read_text(), re.S).group(1)

    def git(repo, *args):
        return subprocess.run(["git", "-C", str(repo), *args], check=True, text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.strip()

    def commit(repo, name, body, message):
        (repo / name).parent.mkdir(exist_ok=True)
        (repo / name).write_text(body)
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", message)

    origin, seed, clone = tmp_path / "origin.git", tmp_path / "seed", tmp_path / "clone"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], check=True)
    subprocess.run(["git", "init", "-q", "-b", "main", str(seed)], check=True)
    commit(seed, "file.txt", "base\n", "initial")
    git(seed, "push", "-q", str(origin), "main")
    subprocess.run(["git", "clone", "-q", str(origin), str(clone)], check=True, stderr=subprocess.DEVNULL)
    git(clone, "checkout", "-q", "-b", "tdd/1-a-run")
    commit(clone, ".tdd/issue-1.md", "- [ ] step one", "plan: scope #1 (#1)")
    ledger = clone / ".tdd" / "issue-1.md"
    ledger.write_text(ledger.read_text() + "\n- [ ] step added ⟦added⟧\n")

    commit(seed, "other.txt", "another run's work\n", "feat: another run merged (#2)")
    git(seed, "push", "-q", str(origin), "main")
    subprocess.run(["bash", "-c", textwrap.dedent(discard)], cwd=clone, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    assert run_cli(rebase_onto_default, [], cwd=clone)[0] == 0

    assert ledger.read_text() == "- [ ] step one\n- [ ] step added ⟦added⟧\n"


@pytest.mark.process("git: a real resumed worktree whose ledger carries an uncommitted instead-of replacement, discarded by the resume's own commands, then rebased")
def test_main_after_the_resume_discard_keeps_the_line_an_instead_of_replacement_adds_to_a_ledger_1547(
        monkeypatch, tmp_path, rebase_onto_default, run_cli):
    for who in ("AUTHOR", "COMMITTER"):
        monkeypatch.setenv(f"GIT_{who}_NAME", "veri")
        monkeypatch.setenv(f"GIT_{who}_EMAIL", "veri@example.test")
    scripts = pathlib.Path(__file__).resolve().parents[2]
    discard = re.search(r"captures and discards whatever a killed leaf left uncommitted.*?```\n(.*?)```",
                        (scripts.parent / "SKILL.md").read_text(), re.S).group(1)

    def git(repo, *args):
        return subprocess.run(["git", "-C", str(repo), *args], check=True, text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.strip()

    def commit(repo, name, body, message):
        (repo / name).parent.mkdir(exist_ok=True)
        (repo / name).write_text(body)
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", message)

    origin, seed, clone = tmp_path / "origin.git", tmp_path / "seed", tmp_path / "clone"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], check=True)
    subprocess.run(["git", "init", "-q", "-b", "main", str(seed)], check=True)
    commit(seed, "file.txt", "base\n", "initial")
    git(seed, "push", "-q", str(origin), "main")
    subprocess.run(["git", "clone", "-q", str(origin), str(clone)], check=True, stderr=subprocess.DEVNULL)
    git(clone, "checkout", "-q", "-b", "tdd/1-a-run")
    commit(clone, ".tdd/issue-1.md", "- [ ] step one\n- [ ] step two\n", "plan: scope #1 (#1)")
    ledger = clone / ".tdd" / "issue-1.md"
    subprocess.run([str(scripts / "add-ledger-step.sh"), str(ledger), "instead-of", "step two", "step replaced"], check=True)

    commit(seed, "other.txt", "another run's work\n", "feat: another run merged (#2)")
    git(seed, "push", "-q", str(origin), "main")
    subprocess.run(["bash", "-c", textwrap.dedent(discard)], cwd=clone, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    assert run_cli(rebase_onto_default, [], cwd=clone)[0] == 0

    assert ledger.read_text() == "- [ ] step one\n- [ ] step replaced ⟦added⟧\n"


@pytest.mark.process("git, tick-ledger.sh and add-ledger-step.sh: a real resumed worktree whose ledger carries a stale tick next to an uncommitted instead-of replacement, discarded by the resume's own commands, then rebased")
def test_main_after_the_resume_discard_unticks_a_stale_tick_next_to_an_instead_of_replacement_and_keeps_the_replacement_1547(
        monkeypatch, tmp_path, rebase_onto_default, run_cli):
    for who in ("AUTHOR", "COMMITTER"):
        monkeypatch.setenv(f"GIT_{who}_NAME", "veri")
        monkeypatch.setenv(f"GIT_{who}_EMAIL", "veri@example.test")
    scripts = pathlib.Path(__file__).resolve().parents[2]
    discard = re.search(r"captures and discards whatever a killed leaf left uncommitted.*?```\n(.*?)```",
                        (scripts.parent / "SKILL.md").read_text(), re.S).group(1)

    def git(repo, *args):
        return subprocess.run(["git", "-C", str(repo), *args], check=True, text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.strip()

    def commit(repo, name, body, message):
        (repo / name).parent.mkdir(exist_ok=True)
        (repo / name).write_text(body)
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", message)

    origin, seed, clone = tmp_path / "origin.git", tmp_path / "seed", tmp_path / "clone"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], check=True)
    subprocess.run(["git", "init", "-q", "-b", "main", str(seed)], check=True)
    commit(seed, "file.txt", "base\n", "initial")
    git(seed, "push", "-q", str(origin), "main")
    subprocess.run(["git", "clone", "-q", str(origin), str(clone)], check=True, stderr=subprocess.DEVNULL)
    git(clone, "checkout", "-q", "-b", "tdd/1-a-run")
    commit(clone, ".tdd/issue-1.md", "- [ ] step one\n- [ ] step two\n", "plan: scope #1 (#1)")
    ledger = clone / ".tdd" / "issue-1.md"
    subprocess.run([str(scripts / "tick-ledger.sh"), "--refactor-pending", str(ledger), "step one"], check=True)
    subprocess.run([str(scripts / "add-ledger-step.sh"), str(ledger), "instead-of", "step two", "step replaced"], check=True)

    commit(seed, "other.txt", "another run's work\n", "feat: another run merged (#2)")
    git(seed, "push", "-q", str(origin), "main")
    subprocess.run(["bash", "-c", textwrap.dedent(discard)], cwd=clone, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    assert run_cli(rebase_onto_default, [], cwd=clone)[0] == 0

    assert ledger.read_text() == "- [ ] step one\n- [ ] step replaced ⟦added⟧\n"


@pytest.mark.process("git: a real resumed worktree whose uncommitted ledger append the resume's discard cannot re-apply because git apply fails, run through the discard as SKILL.md writes it")
def test_main_stops_the_resume_discard_with_exit_2_naming_the_file_and_the_kept_appends_when_its_git_apply_fails_1547(
        monkeypatch, tmp_path):
    for who in ("AUTHOR", "COMMITTER"):
        monkeypatch.setenv(f"GIT_{who}_NAME", "veri")
        monkeypatch.setenv(f"GIT_{who}_EMAIL", "veri@example.test")
    scripts = pathlib.Path(__file__).resolve().parents[2]
    discard = re.search(r"captures and discards whatever a killed leaf left uncommitted.*?```\n(.*?)```",
                        (scripts.parent / "SKILL.md").read_text(), re.S).group(1)
    real_git = shutil.which("git")

    def git(repo, *args):
        return subprocess.run(["git", "-C", str(repo), *args], check=True, text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.strip()

    clone = tmp_path / "clone"
    subprocess.run(["git", "init", "-q", "-b", "tdd/1-a-run", str(clone)], check=True)
    (clone / ".tdd").mkdir()
    ledger = clone / ".tdd" / "issue-1.md"
    ledger.write_text("- [ ] step one\n")
    git(clone, "add", "-A")
    git(clone, "commit", "-q", "-m", "plan: scope #1 (#1)")
    ledger.write_text(ledger.read_text() + "- [ ] step added ⟦added⟧\n")

    shim = tmp_path / "bin"
    shim.mkdir()
    (shim / "git").write_text(f'#!/bin/sh\n[ "$1" = apply ] && exit 1\nexec {real_git} "$@"\n')
    (shim / "git").chmod(0o755)
    env = {**os.environ, "PATH": f"{shim}:{os.environ['PATH']}"}

    done = subprocess.run(["bash", "-c", textwrap.dedent(discard) + "\nexit $?"], cwd=clone, env=env, text=True,
                          stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

    kept = [pathlib.Path(token) if os.path.isabs(token) else clone / token for token in done.stderr.split()]
    kept = [path for path in kept if path.is_file() and path != ledger and "+- [ ] step added ⟦added⟧\n" in path.read_text()]
    assert (done.returncode, ".tdd/issue-1.md" in done.stderr, len(kept)) == (2, True, 1)


@pytest.mark.process("git: a real resumed worktree whose rebase conflicts and is aborted, with an uncommitted ledger append that git apply then fails to restore")
def test_main_exits_2_naming_the_file_and_the_kept_appends_when_they_cannot_be_reapplied_after_a_conflict_abort_1547(
        monkeypatch, tmp_path, rebase_onto_default, run_cli):
    for who in ("AUTHOR", "COMMITTER"):
        monkeypatch.setenv(f"GIT_{who}_NAME", "veri")
        monkeypatch.setenv(f"GIT_{who}_EMAIL", "veri@example.test")
    real_git = shutil.which("git")

    def git(repo, *args):
        return subprocess.run(["git", "-C", str(repo), *args], check=True, text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.strip()

    def commit(repo, files, message):
        for name, body in files.items():
            (repo / name).parent.mkdir(exist_ok=True)
            (repo / name).write_text(body)
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", message)

    origin, seed, clone = tmp_path / "origin.git", tmp_path / "seed", tmp_path / "clone"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], check=True)
    subprocess.run(["git", "init", "-q", "-b", "main", str(seed)], check=True)
    commit(seed, {"file.txt": "base\n", ".tdd/issue-1.md": "- [ ] step one\n"}, "initial")
    git(seed, "push", "-q", str(origin), "main")
    subprocess.run(["git", "clone", "-q", str(origin), str(clone)], check=True, stderr=subprocess.DEVNULL)
    git(clone, "checkout", "-q", "-b", "tdd/1-a-run")
    commit(clone, {"file.txt": "the run's edit\n"}, "feat: a step's green commit (#1)")
    ledger = clone / ".tdd" / "issue-1.md"
    ledger.write_text(ledger.read_text() + "- [ ] step added ⟦added⟧\n")
    commit(seed, {"file.txt": "another run's edit\n"}, "feat: another run merged (#2)")
    git(seed, "push", "-q", str(origin), "main")

    shim = tmp_path / "bin"
    shim.mkdir()
    (shim / "git").write_text(f'#!/bin/sh\n[ "$1" = apply ] && exit 1\nexec {real_git} "$@"\n')
    (shim / "git").chmod(0o755)
    monkeypatch.setenv("PATH", f"{shim}:{os.environ['PATH']}")

    code, _, err = run_cli(rebase_onto_default, [], cwd=clone)

    kept = [pathlib.Path(token) if os.path.isabs(token) else clone / token for token in err.split()]
    kept = [path for path in kept if path.is_file() and path != ledger and "+- [ ] step added ⟦added⟧\n" in path.read_text()]
    assert (code, ".tdd/issue-1.md" in err, len(kept)) == (2, True, 1)


@pytest.mark.process("git: a real resumed worktree whose rebase is refused without a conflict to abort, with an uncommitted ledger append that git apply then fails to restore")
def test_main_exits_2_naming_the_file_and_the_kept_appends_when_they_cannot_be_reapplied_after_a_rebase_refused_without_a_conflict_1547(
        monkeypatch, tmp_path, rebase_onto_default, run_cli):
    for who in ("AUTHOR", "COMMITTER"):
        monkeypatch.setenv(f"GIT_{who}_NAME", "veri")
        monkeypatch.setenv(f"GIT_{who}_EMAIL", "veri@example.test")
    real_git = shutil.which("git")

    def git(repo, *args):
        return subprocess.run(["git", "-C", str(repo), *args], check=True, text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.strip()

    def commit(repo, files, message):
        for name, body in files.items():
            (repo / name).parent.mkdir(exist_ok=True)
            (repo / name).write_text(body)
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", message)

    origin, seed, clone = tmp_path / "origin.git", tmp_path / "seed", tmp_path / "clone"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], check=True)
    subprocess.run(["git", "init", "-q", "-b", "main", str(seed)], check=True)
    commit(seed, {"file.txt": "base\n", ".tdd/issue-1.md": "- [ ] step one\n"}, "initial")
    git(seed, "push", "-q", str(origin), "main")
    subprocess.run(["git", "clone", "-q", str(origin), str(clone)], check=True, stderr=subprocess.DEVNULL)
    git(clone, "checkout", "-q", "-b", "tdd/1-a-run")
    commit(clone, {"file.txt": "the run's edit\n"}, "feat: a step's green commit (#1)")
    ledger = clone / ".tdd" / "issue-1.md"
    ledger.write_text(ledger.read_text() + "- [ ] step added ⟦added⟧\n")
    commit(seed, {"file.txt": "another run's edit\n"}, "feat: another run merged (#2)")
    git(seed, "push", "-q", str(origin), "main")

    shim = tmp_path / "bin"
    shim.mkdir()
    (shim / "git").write_text(f'#!/bin/sh\ncase "$1" in apply|rebase) exit 1;; esac\nexec {real_git} "$@"\n')
    (shim / "git").chmod(0o755)
    monkeypatch.setenv("PATH", f"{shim}:{os.environ['PATH']}")

    code, _, err = run_cli(rebase_onto_default, [], cwd=clone)

    kept = [pathlib.Path(token) if os.path.isabs(token) else clone / token for token in err.split()]
    kept = [path for path in kept if path.is_file() and path != ledger and "+- [ ] step added ⟦added⟧\n" in path.read_text()]
    assert (code, ".tdd/issue-1.md" in err, len(kept)) == (2, True, 1)


@pytest.mark.process("git and add-ledger-step.sh: a real resumed worktree whose ledger carries an uncommitted line inserted right before a committed ticked step, discarded by the resume's own commands, then rebased")
def test_main_after_the_resume_discard_keeps_a_line_inserted_right_before_a_ticked_step_and_does_not_duplicate_the_step_1547(
        monkeypatch, tmp_path, rebase_onto_default, run_cli):
    for who in ("AUTHOR", "COMMITTER"):
        monkeypatch.setenv(f"GIT_{who}_NAME", "veri")
        monkeypatch.setenv(f"GIT_{who}_EMAIL", "veri@example.test")
    scripts = pathlib.Path(__file__).resolve().parents[2]
    discard = re.search(r"captures and discards whatever a killed leaf left uncommitted.*?```\n(.*?)```",
                        (scripts.parent / "SKILL.md").read_text(), re.S).group(1)

    def git(repo, *args):
        return subprocess.run(["git", "-C", str(repo), *args], check=True, text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.strip()

    def commit(repo, name, body, message):
        (repo / name).parent.mkdir(exist_ok=True)
        (repo / name).write_text(body)
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", message)

    origin, seed, clone = tmp_path / "origin.git", tmp_path / "seed", tmp_path / "clone"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], check=True)
    subprocess.run(["git", "init", "-q", "-b", "main", str(seed)], check=True)
    commit(seed, "file.txt", "base\n", "initial")
    git(seed, "push", "-q", str(origin), "main")
    subprocess.run(["git", "clone", "-q", str(origin), str(clone)], check=True, stderr=subprocess.DEVNULL)
    git(clone, "checkout", "-q", "-b", "tdd/1-a-run")
    commit(clone, ".tdd/issue-1.md", "- [x] step one\n- [ ] step two\n", "plan: scope #1 (#1)")
    ledger = clone / ".tdd" / "issue-1.md"
    subprocess.run([str(scripts / "add-ledger-step.sh"), str(ledger), "before", "step one", "step inserted"], check=True)

    commit(seed, "other.txt", "another run's work\n", "feat: another run merged (#2)")
    git(seed, "push", "-q", str(origin), "main")
    subprocess.run(["bash", "-c", textwrap.dedent(discard)], cwd=clone, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    assert run_cli(rebase_onto_default, [], cwd=clone)[0] == 0

    assert ledger.read_text() == "- [ ] step inserted ⟦added⟧\n- [x] step one\n- [ ] step two\n"


@pytest.mark.process("git and add-ledger-step.sh: a real resumed worktree whose ledger carries an uncommitted instead-of replacement whose new text starts with the replaced step's text, discarded by the resume's own commands, then rebased")
def test_main_after_the_resume_discard_keeps_an_instead_of_replacement_whose_new_text_starts_with_the_old_text_1547(
        monkeypatch, tmp_path, rebase_onto_default, run_cli):
    for who in ("AUTHOR", "COMMITTER"):
        monkeypatch.setenv(f"GIT_{who}_NAME", "veri")
        monkeypatch.setenv(f"GIT_{who}_EMAIL", "veri@example.test")
    scripts = pathlib.Path(__file__).resolve().parents[2]
    discard = re.search(r"captures and discards whatever a killed leaf left uncommitted.*?```\n(.*?)```",
                        (scripts.parent / "SKILL.md").read_text(), re.S).group(1)

    def git(repo, *args):
        return subprocess.run(["git", "-C", str(repo), *args], check=True, text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.strip()

    def commit(repo, name, body, message):
        (repo / name).parent.mkdir(exist_ok=True)
        (repo / name).write_text(body)
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", message)

    origin, seed, clone = tmp_path / "origin.git", tmp_path / "seed", tmp_path / "clone"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], check=True)
    subprocess.run(["git", "init", "-q", "-b", "main", str(seed)], check=True)
    commit(seed, "file.txt", "base\n", "initial")
    git(seed, "push", "-q", str(origin), "main")
    subprocess.run(["git", "clone", "-q", str(origin), str(clone)], check=True, stderr=subprocess.DEVNULL)
    git(clone, "checkout", "-q", "-b", "tdd/1-a-run")
    commit(clone, ".tdd/issue-1.md", "- [ ] step one\n- [ ] step two\n", "plan: scope #1 (#1)")
    ledger = clone / ".tdd" / "issue-1.md"
    subprocess.run([str(scripts / "add-ledger-step.sh"), str(ledger), "instead-of", "step two", "step two extended"], check=True)

    commit(seed, "other.txt", "another run's work\n", "feat: another run merged (#2)")
    git(seed, "push", "-q", str(origin), "main")
    subprocess.run(["bash", "-c", textwrap.dedent(discard)], cwd=clone, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    assert run_cli(rebase_onto_default, [], cwd=clone)[0] == 0

    assert ledger.read_text() == "- [ ] step one\n- [ ] step two extended ⟦added⟧\n"


@pytest.mark.process("git: a real resumed worktree whose tracked metrics file carries an uncommitted rewritten row, discarded by the resume's own commands, then rebased")
def test_main_after_the_resume_discard_keeps_a_rewritten_row_of_a_tracked_metrics_file_unchanged_1547(
        monkeypatch, tmp_path, rebase_onto_default, run_cli):
    for who in ("AUTHOR", "COMMITTER"):
        monkeypatch.setenv(f"GIT_{who}_NAME", "veri")
        monkeypatch.setenv(f"GIT_{who}_EMAIL", "veri@example.test")
    scripts = pathlib.Path(__file__).resolve().parents[2]
    discard = re.search(r"captures and discards whatever a killed leaf left uncommitted.*?```\n(.*?)```",
                        (scripts.parent / "SKILL.md").read_text(), re.S).group(1)

    def git(repo, *args):
        return subprocess.run(["git", "-C", str(repo), *args], check=True, text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.strip()

    def commit(repo, name, body, message):
        (repo / name).parent.mkdir(exist_ok=True)
        (repo / name).write_text(body)
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", message)

    origin, seed, clone = tmp_path / "origin.git", tmp_path / "seed", tmp_path / "clone"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], check=True)
    subprocess.run(["git", "init", "-q", "-b", "main", str(seed)], check=True)
    commit(seed, "file.txt", "base\n", "initial")
    git(seed, "push", "-q", str(origin), "main")
    subprocess.run(["git", "clone", "-q", str(origin), str(clone)], check=True, stderr=subprocess.DEVNULL)
    git(clone, "checkout", "-q", "-b", "tdd/1-a-run")
    commit(clone, ".tdd/issue-1.md", "- [ ] step one\n", "plan: scope #1 (#1)")
    commit(clone, ".tdd/issue-1-metrics.md", "| step | cost |\n| one | 0.10 |\n| two | 0.20 |\n", "metrics (#1)")
    metrics = clone / ".tdd" / "issue-1-metrics.md"
    rewritten = "| step | cost |\n| one | 0.10 |\n| two | 0.35 |\n"
    metrics.write_text(rewritten)

    commit(seed, "other.txt", "another run's work\n", "feat: another run merged (#2)")
    git(seed, "push", "-q", str(origin), "main")
    subprocess.run(["bash", "-c", textwrap.dedent(discard)], cwd=clone, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    assert run_cli(rebase_onto_default, [], cwd=clone)[0] == 0

    assert metrics.read_text() == rewritten


@pytest.mark.process("git: a real resumed worktree whose rebase-onto-default.sh is killed by SIGKILL inside git rebase, after it set the uncommitted ledger append aside, then resumed through the discard as SKILL.md writes it")
def test_main_after_a_kill_mid_rebase_the_next_resume_reapplies_the_set_aside_appends_or_exits_2_naming_where_they_are_1611(
        monkeypatch, tmp_path, rebase_onto_default, run_cli):
    for who in ("AUTHOR", "COMMITTER"):
        monkeypatch.setenv(f"GIT_{who}_NAME", "veri")
        monkeypatch.setenv(f"GIT_{who}_EMAIL", "veri@example.test")
    scripts = pathlib.Path(__file__).resolve().parents[2]
    discard = re.search(r"captures and discards whatever a killed leaf left uncommitted.*?```\n(.*?)```",
                        (scripts.parent / "SKILL.md").read_text(), re.S).group(1)
    real_git = shutil.which("git")
    append = "- [ ] step two ⟦added⟧\n"

    def git(repo, *args):
        return subprocess.run(["git", "-C", str(repo), *args], check=True, text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.strip()

    def commit(repo, name, body, message):
        (repo / name).parent.mkdir(exist_ok=True)
        (repo / name).write_text(body)
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", message)

    origin, seed, clone = tmp_path / "origin.git", tmp_path / "seed", tmp_path / "clone"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], check=True)
    subprocess.run(["git", "init", "-q", "-b", "main", str(seed)], check=True)
    commit(seed, "file.txt", "base\n", "initial")
    git(seed, "push", "-q", str(origin), "main")
    subprocess.run(["git", "clone", "-q", str(origin), str(clone)], check=True, stderr=subprocess.DEVNULL)
    git(clone, "checkout", "-q", "-b", "tdd/1-a-run")
    commit(clone, ".tdd/issue-1.md", "- [x] step one\n", "plan: scope #1 (#1)")
    commit(clone, "work.txt", "the run's work\n", "feat: a step's green commit (#1)")
    ledger = clone / ".tdd" / "issue-1.md"
    ledger.write_text(ledger.read_text() + append)
    commit(seed, "other.txt", "another run's work\n", "feat: another run merged (#2)")
    git(seed, "push", "-q", str(origin), "main")

    shim = tmp_path / "bin"
    shim.mkdir()
    (shim / "git").write_text(
        f'#!/bin/sh\n[ "$1" = rebase ] && {{ kill -KILL $PPID; sleep 5; exit 1; }}\nexec {real_git} "$@"\n')
    (shim / "git").chmod(0o755)
    killed = subprocess.run([str(scripts / "rebase-onto-default.sh")], cwd=clone, stdin=subprocess.DEVNULL,
                            env={**os.environ, "PATH": f"{shim}:{os.environ['PATH']}"},
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    assert killed.returncode < 0
    assert append not in ledger.read_text()

    subprocess.run(["bash", "-c", textwrap.dedent(discard) + "\nexit 0"], cwd=clone, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    code, _, err = run_cli(rebase_onto_default, [], cwd=clone)

    named = [pathlib.Path(token) if os.path.isabs(token) else clone / token for token in err.split()]
    named = [path for path in named if path.is_file() and path != ledger and append in path.read_text()]
    assert (code, append in ledger.read_text() or len(named) == 1) == (code, True) and code in (0, 2)


def _failing_apply_env_1611(tmp_path):
    shim = tmp_path / "bin"
    shim.mkdir()
    (shim / "git").write_text(f'#!/bin/sh\n[ "$1" = apply ] && exit 1\nexec {shutil.which("git")} "$@"\n')
    (shim / "git").chmod(0o755)
    return {**os.environ, "PATH": f"{shim}:{os.environ['PATH']}"}


def _resumed_clone_1611(monkeypatch, tmp_path, ledger_text, message):
    for who in ("AUTHOR", "COMMITTER"):
        monkeypatch.setenv(f"GIT_{who}_NAME", "veri")
        monkeypatch.setenv(f"GIT_{who}_EMAIL", "veri@example.test")
    scripts = pathlib.Path(__file__).resolve().parents[2]
    discard = re.search(r"captures and discards whatever a killed leaf left uncommitted.*?```\n(.*?)```",
                        (scripts.parent / "SKILL.md").read_text(), re.S).group(1)

    def git(repo, *args):
        return subprocess.run(["git", "-C", str(repo), *args], check=True, text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.strip()

    clone = tmp_path / "clone"
    subprocess.run(["git", "init", "-q", "-b", "tdd/1-a-run", str(clone)], check=True)
    (clone / ".tdd").mkdir()
    ledger = clone / ".tdd" / "issue-1.md"
    ledger.write_text(ledger_text)
    git(clone, "add", "-A")
    git(clone, "commit", "-q", "-m", message)
    return scripts, clone, ledger, git, discard


@pytest.mark.process("git: a real resumed worktree whose resume discard cannot re-apply the uncommitted ledger appends twice in a row, run through the discard as SKILL.md writes it")
def test_main_keeps_both_sets_of_appends_recoverable_and_named_when_two_resume_discards_fail_to_reapply_in_a_row_1611(
        monkeypatch, tmp_path):
    scripts, clone, ledger, git, discard = _resumed_clone_1611(
        monkeypatch, tmp_path, "- [ ] step one\n", "plan: scope #1 (#1)")
    first, second = "- [ ] first failure's step ⟦added⟧\n", "- [ ] second failure's step ⟦added⟧\n"

    env = _failing_apply_env_1611(tmp_path)

    def resume_discard():
        return subprocess.run(["bash", "-c", textwrap.dedent(discard) + "\nexit $?"], cwd=clone, env=env, text=True,
                              stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

    ledger.write_text(ledger.read_text() + first)
    one = resume_discard()
    ledger.write_text(ledger.read_text() + second)
    two = resume_discard()

    named = [pathlib.Path(token) if os.path.isabs(token) else clone / token
             for token in (one.stderr + two.stderr).split()]
    kept = "".join(path.read_text() for path in dict.fromkeys(named) if path.is_file() and path != ledger)
    assert (one.returncode, two.returncode, f"+{first}" in kept, f"+{second}" in kept) == (2, 2, True, True)


@pytest.mark.process("git: a real resumed worktree holding a set-aside-tdd-appends.diff and kept-tdd-appends.diff* files, whose resume discard cannot re-apply the uncommitted appends, run as SKILL.md writes it")
def test_resume_discard_stop_names_the_set_aside_file_and_every_kept_file_when_its_reapply_fails_1638(
        monkeypatch, tmp_path):
    scripts, clone, ledger, git, discard = _resumed_clone_1611(
        monkeypatch, tmp_path, "- [ ] step one\n", "plan: scope #1 (#1)")
    gitdir = pathlib.Path(git(clone, "rev-parse", "--absolute-git-dir"))
    saved = [gitdir / "set-aside-tdd-appends.diff", gitdir / "kept-tdd-appends.diff",
             gitdir / "kept-tdd-appends.diff.1700000000.42"]
    for path in saved:
        path.write_text("earlier appends\n")
    ledger.write_text(ledger.read_text() + "- [ ] new step ⟦added⟧\n")

    run = subprocess.run(["bash", "-c", textwrap.dedent(discard) + "\nexit $?"], cwd=clone,
                         env=_failing_apply_env_1611(tmp_path), text=True,
                         stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

    assert (run.returncode, [p.name in run.stderr for p in saved]) == (2, [True, True, True])


@pytest.mark.process("git and tick-ledger.sh: a real resumed worktree whose ledger carries a step ticked by a green commit on the branch and then reworded in the uncommitted copy, discarded by the resume's own commands")
def test_main_after_the_resume_discard_unticks_a_reworded_step_even_though_its_green_commit_is_on_the_branch_1611(
        monkeypatch, tmp_path):
    scripts, clone, ledger, git, discard = _resumed_clone_1611(
        monkeypatch, tmp_path, "- [ ] step one\n- [ ] step two\n", "plan: scope #1 (#1)")
    subprocess.run([str(scripts / "tick-ledger.sh"), str(ledger), "step one"], check=True)
    git(clone, "add", "-A")
    git(clone, "commit", "-q", "-m", "fix: step one (#1)")
    ledger.write_text(ledger.read_text().replace("step one", "step one reworded"))

    subprocess.run(["bash", "-c", textwrap.dedent(discard)], cwd=clone, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    assert ledger.read_text() == "- [ ] step one reworded\n- [ ] step two\n"


@pytest.mark.process("git: a real resumed worktree whose ledger carries two steps of identical text, one ticked by a green commit on the branch and one ticked only in the uncommitted copy, discarded by the resume's own commands")
def test_main_after_the_resume_discard_judges_each_tick_of_two_steps_with_identical_text_on_its_own_1611(
        monkeypatch, tmp_path):
    scripts, clone, ledger, git, discard = _resumed_clone_1611(
        monkeypatch, tmp_path, "- [ ] same step\n- [x] same step\n", "fix: the second same step (#1)")
    ledger.write_text("- [x] same step\n- [x] same step\n")

    subprocess.run(["bash", "-c", textwrap.dedent(discard)], cwd=clone, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    assert ledger.read_text() == "- [ ] same step\n- [x] same step\n"


@pytest.mark.process("git and tick-ledger.sh: a real resumed worktree whose ledger carries an uncommitted line inserted above a step ticked by a green commit on the branch, discarded by the resume's own commands")
def test_main_after_the_resume_discard_keeps_the_tick_of_a_committed_step_when_a_line_is_inserted_above_it_1611(
        monkeypatch, tmp_path):
    scripts, clone, ledger, git, discard = _resumed_clone_1611(
        monkeypatch, tmp_path, "- [ ] step one\n- [ ] step two\n", "plan: scope #1 (#1)")
    subprocess.run([str(scripts / "tick-ledger.sh"), str(ledger), "step two"], check=True)
    git(clone, "add", "-A")
    git(clone, "commit", "-q", "-m", "fix: step two (#1)")
    ticked = ledger.read_text()
    ledger.write_text("- [ ] inserted step ⟦added⟧\n" + ticked)

    subprocess.run(["bash", "-c", textwrap.dedent(discard)], cwd=clone, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    assert ledger.read_text() == "- [ ] inserted step ⟦added⟧\n" + ticked


@pytest.mark.process("git: a real resumed worktree whose ledger carries a stale tick on a step whose text matches no committed tick, at the line position of a committed tick, discarded by the resume's own commands")
def test_main_after_the_resume_discard_unticks_a_stale_tick_at_the_line_position_of_a_committed_tick_1611(
        monkeypatch, tmp_path):
    scripts, clone, ledger, git, discard = _resumed_clone_1611(
        monkeypatch, tmp_path, "- [ ] step one\n- [x] step two\n", "fix: step two (#1)")
    ledger.write_text("- [ ] step one\n- [x] step three\n")

    subprocess.run(["bash", "-c", textwrap.dedent(discard)], cwd=clone, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    assert ledger.read_text() == "- [ ] step one\n- [ ] step three\n"


@pytest.mark.process("git: a real resumed worktree whose ledger carries two ticked steps of identical text in the uncommitted copy and one committed tick of that text, discarded by the resume's own commands")
def test_main_after_the_resume_discard_keeps_exactly_one_tick_of_two_working_ticks_with_one_committed_tick_of_that_text_1611(
        monkeypatch, tmp_path):
    scripts, clone, ledger, git, discard = _resumed_clone_1611(
        monkeypatch, tmp_path, "- [x] twin step\n- [ ] other step\n- [ ] twin step\n", "fix: a twin step (#1)")
    ledger.write_text("- [x] twin step\n- [ ] other step\n- [x] twin step\n")

    subprocess.run(["bash", "-c", textwrap.dedent(discard)], cwd=clone, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    lines = ledger.read_text().splitlines()
    assert (len(lines), lines.count("- [x] twin step"), lines.count("- [ ] twin step"), "- [ ] other step" in lines) == (3, 1, 1, True)


@pytest.mark.process("git: a real resumed worktree whose resume discard fails to re-apply appends A, then re-applies appends B, then whose rebase-onto-default.sh fails to re-apply B, run through the discard as SKILL.md writes it")
def test_main_keeps_the_appends_an_earlier_failed_reapply_saved_when_a_later_reapply_fails_after_the_rebase_and_names_every_saved_file_1611(
        monkeypatch, tmp_path, rebase_onto_default, run_cli):
    for who in ("AUTHOR", "COMMITTER"):
        monkeypatch.setenv(f"GIT_{who}_NAME", "veri")
        monkeypatch.setenv(f"GIT_{who}_EMAIL", "veri@example.test")
    scripts = pathlib.Path(__file__).resolve().parents[2]
    discard = re.search(r"captures and discards whatever a killed leaf left uncommitted.*?```\n(.*?)```",
                        (scripts.parent / "SKILL.md").read_text(), re.S).group(1)
    first, second = "- [ ] first failure's step ⟦added⟧\n", "- [ ] second failure's step ⟦added⟧\n"

    def git(repo, *args):
        return subprocess.run(["git", "-C", str(repo), *args], check=True, text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.strip()

    def commit(repo, name, body, message):
        (repo / name).parent.mkdir(exist_ok=True)
        (repo / name).write_text(body)
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", message)

    origin, seed, clone = tmp_path / "origin.git", tmp_path / "seed", tmp_path / "clone"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], check=True)
    subprocess.run(["git", "init", "-q", "-b", "main", str(seed)], check=True)
    commit(seed, ".tdd/issue-1.md", "- [ ] step one\n", "initial")
    git(seed, "push", "-q", str(origin), "main")
    subprocess.run(["git", "clone", "-q", str(origin), str(clone)], check=True, stderr=subprocess.DEVNULL)
    git(clone, "checkout", "-q", "-b", "tdd/1-a-run")
    commit(clone, "work.txt", "the run's work\n", "feat: a step's green commit (#1)")
    commit(seed, "other.txt", "another run's work\n", "feat: another run merged (#2)")
    git(seed, "push", "-q", str(origin), "main")
    ledger = clone / ".tdd" / "issue-1.md"

    failing = _failing_apply_env_1611(tmp_path)

    def resume_discard(env):
        return subprocess.run(["bash", "-c", textwrap.dedent(discard) + "\nexit $?"], cwd=clone, env=env, text=True,
                              stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

    ledger.write_text(ledger.read_text() + first)
    one = resume_discard(failing)
    ledger.write_text(ledger.read_text() + second)
    two = resume_discard(os.environ)
    rebased = subprocess.run([str(scripts / "rebase-onto-default.sh")], cwd=clone, env=failing, text=True,
                             stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

    def saved(stderr):
        tokens = [pathlib.Path(t) if os.path.isabs(t) else clone / t for t in stderr.split()]
        return [p for p in dict.fromkeys(tokens) if p.is_file() and p != ledger and "+++ b/.tdd/issue-1.md" in p.read_text()]

    on_disk = "".join(p.read_text() for p in saved(one.stderr))
    named = "".join(p.read_text() for p in saved(rebased.stderr))
    assert (one.returncode, two.returncode, rebased.returncode) == (2, 0, 2)
    assert (f"+{first}" in on_disk, f"+{first}" in named, f"+{second}" in named) == (True, True, True)


@pytest.mark.process("git: a real resumed worktree whose resume discard fails to re-apply the uncommitted ledger appends while a file saved by an earlier failure is on disk, run through the discard as SKILL.md writes it")
def test_main_stops_the_second_failing_resume_discard_naming_the_earlier_saved_file_and_its_own_1611(
        monkeypatch, tmp_path):
    scripts, clone, ledger, git, discard = _resumed_clone_1611(
        monkeypatch, tmp_path, "- [ ] step one\n", "plan: scope #1 (#1)")
    first, second = "- [ ] first failure's step ⟦added⟧\n", "- [ ] second failure's step ⟦added⟧\n"

    env = _failing_apply_env_1611(tmp_path)

    def resume_discard():
        return subprocess.run(["bash", "-c", textwrap.dedent(discard) + "\nexit $?"], cwd=clone, env=env, text=True,
                              stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

    def saved(stderr):
        tokens = [pathlib.Path(t) if os.path.isabs(t) else clone / t for t in stderr.split()]
        return [p for p in dict.fromkeys(tokens) if p.is_file() and p != ledger and "+++ b/.tdd/issue-1.md" in p.read_text()]

    ledger.write_text(ledger.read_text() + first)
    resume_discard()
    ledger.write_text(ledger.read_text() + second)
    two = resume_discard()

    named = "".join(p.read_text() for p in saved(two.stderr))
    assert (two.returncode, f"+{first}" in named, f"+{second}" in named) == (2, True, True)


@pytest.mark.process("git: a real clone holding a set-aside-tdd-appends.diff left by a killed run whose re-apply git apply fails")
def test_main_exits_2_naming_the_set_aside_file_and_keeps_it_when_its_reapply_fails_1611(
        monkeypatch, tmp_path, rebase_onto_default, run_cli):
    for who in ("AUTHOR", "COMMITTER"):
        monkeypatch.setenv(f"GIT_{who}_NAME", "veri")
        monkeypatch.setenv(f"GIT_{who}_EMAIL", "veri@example.test")

    def git(repo, *args):
        return subprocess.run(["git", "-C", str(repo), *args], check=True, text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.strip()

    origin, seed, clone = tmp_path / "origin.git", tmp_path / "seed", tmp_path / "clone"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], check=True)
    subprocess.run(["git", "init", "-q", "-b", "main", str(seed)], check=True)
    (seed / ".tdd").mkdir()
    (seed / ".tdd" / "issue-1.md").write_text("- [ ] step one\n")
    git(seed, "add", "-A")
    git(seed, "commit", "-q", "-m", "initial")
    git(seed, "push", "-q", str(origin), "main")
    subprocess.run(["git", "clone", "-q", str(origin), str(clone)], check=True, stderr=subprocess.DEVNULL)
    saved = pathlib.Path(git(clone, "rev-parse", "--absolute-git-dir")) / "set-aside-tdd-appends.diff"
    saved.write_text("--- a/.tdd/issue-1.md\n+++ b/.tdd/issue-1.md\n@@ -1 +1,2 @@\n - [ ] step one\n+- [ ] step two\n")
    before = saved.read_text()
    monkeypatch.setenv("PATH", _failing_apply_env_1611(tmp_path)["PATH"])

    code, _, err = run_cli(rebase_onto_default, [], cwd=clone)

    assert (code, str(saved) in err, saved.is_file() and saved.read_text() == before) == (2, True, True)


@pytest.mark.process("git: a real clone holding a set-aside-tdd-appends.diff and kept-tdd-appends.diff* files from earlier failures, whose re-apply git apply fails")
def test_main_exits_2_naming_the_set_aside_file_and_every_kept_file_when_its_reapply_fails_1638(
        monkeypatch, tmp_path, rebase_onto_default, run_cli):
    for who in ("AUTHOR", "COMMITTER"):
        monkeypatch.setenv(f"GIT_{who}_NAME", "veri")
        monkeypatch.setenv(f"GIT_{who}_EMAIL", "veri@example.test")

    def git(repo, *args):
        return subprocess.run(["git", "-C", str(repo), *args], check=True, text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.strip()

    origin, seed, clone = tmp_path / "origin.git", tmp_path / "seed", tmp_path / "clone"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], check=True)
    subprocess.run(["git", "init", "-q", "-b", "main", str(seed)], check=True)
    (seed / ".tdd").mkdir()
    (seed / ".tdd" / "issue-1.md").write_text("- [ ] step one\n")
    git(seed, "add", "-A")
    git(seed, "commit", "-q", "-m", "initial")
    git(seed, "push", "-q", str(origin), "main")
    subprocess.run(["git", "clone", "-q", str(origin), str(clone)], check=True, stderr=subprocess.DEVNULL)
    gitdir = pathlib.Path(git(clone, "rev-parse", "--absolute-git-dir"))
    saved = gitdir / "set-aside-tdd-appends.diff"
    saved.write_text("--- a/.tdd/issue-1.md\n+++ b/.tdd/issue-1.md\n@@ -1 +1,2 @@\n - [ ] step one\n+- [ ] step two\n")
    kept = [gitdir / "kept-tdd-appends.diff", gitdir / "kept-tdd-appends.diff.1700000000.42"]
    for path in kept:
        path.write_text("earlier appends\n")
    monkeypatch.setenv("PATH", _failing_apply_env_1611(tmp_path)["PATH"])

    code, _, err = run_cli(rebase_onto_default, [], cwd=clone)

    assert (code, [str(p) in err for p in [saved, *kept]]) == (2, [True, True, True])


@pytest.mark.process("git: a real clone behind origin with uncommitted ledger appends and a kept-tdd-appends.diff from an earlier failure, whose re-apply after the rebase git apply fails")
def test_main_exits_2_naming_the_set_aside_file_it_left_and_every_kept_file_when_the_reapply_after_the_rebase_fails_1638(
        monkeypatch, tmp_path, rebase_onto_default, run_cli):
    for who in ("AUTHOR", "COMMITTER"):
        monkeypatch.setenv(f"GIT_{who}_NAME", "veri")
        monkeypatch.setenv(f"GIT_{who}_EMAIL", "veri@example.test")

    def git(repo, *args):
        return subprocess.run(["git", "-C", str(repo), *args], check=True, text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.strip()

    origin, seed, clone = tmp_path / "origin.git", tmp_path / "seed", tmp_path / "clone"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], check=True)
    subprocess.run(["git", "init", "-q", "-b", "main", str(seed)], check=True)
    (seed / ".tdd").mkdir()
    (seed / ".tdd" / "issue-1.md").write_text("- [ ] step one\n")
    git(seed, "add", "-A")
    git(seed, "commit", "-q", "-m", "initial")
    git(seed, "push", "-q", str(origin), "main")
    subprocess.run(["git", "clone", "-q", str(origin), str(clone)], check=True, stderr=subprocess.DEVNULL)
    (seed / "other.txt").write_text("another run's work\n")
    git(seed, "add", "-A")
    git(seed, "commit", "-q", "-m", "feat: another run merged (#2)")
    git(seed, "push", "-q", str(origin), "main")
    (clone / ".tdd" / "issue-1.md").write_text("- [ ] step one\n- [ ] step two\n")
    gitdir = pathlib.Path(git(clone, "rev-parse", "--absolute-git-dir"))
    (gitdir / "kept-tdd-appends.diff").write_text("earlier appends\n")
    real_path = os.environ["PATH"]
    monkeypatch.setenv("PATH", _failing_apply_env_1611(tmp_path)["PATH"])

    code, _, err = run_cli(rebase_onto_default, [], cwd=clone)
    monkeypatch.setenv("PATH", real_path)
    run_cli(rebase_onto_default, [], cwd=clone)
    git(clone, "reset", "--hard", "-q")

    holders = [p for p in gitdir.glob("*-tdd-appends.diff*") if "step two" in p.read_text()]
    assert (code, [p.name.startswith("kept-tdd-appends.diff") for p in holders],
            (gitdir / "set-aside-tdd-appends.diff").exists(), [str(p) in err for p in holders]) == (
        2, [True], False, [True])


@pytest.mark.process("git: a real resumed worktree whose committed ledger ticks a step that still carries ⟂ refactor pending while the uncommitted copy has the mark taken off, discarded by the resume's own commands")
def test_main_after_the_resume_discard_keeps_a_tick_whose_committed_step_carries_refactor_pending_and_whose_working_copy_does_not_1611(
        monkeypatch, tmp_path):
    scripts, clone, ledger, git, discard = _resumed_clone_1611(
        monkeypatch, tmp_path, "- [x] step one ⟂ refactor pending\n- [ ] step two\n", "fix: step one (#1)")
    ledger.write_text("- [x] step one\n- [ ] step two\n")

    subprocess.run(["bash", "-c", textwrap.dedent(discard)], cwd=clone, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    assert ledger.read_text() == "- [x] step one\n- [ ] step two\n"


@pytest.mark.process("git: a real clone already holding origin/main, with a set-aside-tdd-appends.diff left by a killed rebase, run through rebase-onto-default twice")
def test_main_removes_the_set_aside_appends_once_it_reapplies_them_so_the_next_resume_exits_3_again_1611(
        monkeypatch, tmp_path, rebase_onto_default, run_cli):
    for who in ("AUTHOR", "COMMITTER"):
        monkeypatch.setenv(f"GIT_{who}_NAME", "veri")
        monkeypatch.setenv(f"GIT_{who}_EMAIL", "veri@example.test")

    def git(repo, *args):
        return subprocess.run(["git", "-C", str(repo), *args], check=True, text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.strip()

    origin, clone = tmp_path / "origin.git", tmp_path / "clone"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], check=True)
    subprocess.run(["git", "clone", "-q", str(origin), str(clone)], check=True, stderr=subprocess.DEVNULL)
    git(clone, "checkout", "-q", "-b", "main")
    ledger = clone / ".tdd" / "issue-1.md"
    ledger.parent.mkdir()
    ledger.write_text("- [x] step one\n")
    git(clone, "add", "-A")
    git(clone, "commit", "-q", "-m", "plan: scope #1 (#1)")
    git(clone, "push", "-q", "origin", "main")
    git(clone, "checkout", "-q", "-b", "tdd/1-a-run")
    append = "- [ ] step two ⟦added⟧\n"
    ledger.write_text(ledger.read_text() + append)
    saved = pathlib.Path(git(clone, "rev-parse", "--git-path", "set-aside-tdd-appends.diff"))
    saved = saved if saved.is_absolute() else clone / saved
    saved.write_text(git(clone, "diff") + "\n")
    git(clone, "checkout", "--", ".tdd/issue-1.md")

    first = run_cli(rebase_onto_default, [], cwd=clone)[0]
    left = saved.is_file()
    second = run_cli(rebase_onto_default, [], cwd=clone)[0]

    assert (first, left, second, ledger.read_text()) == (3, False, 3, "- [x] step one\n" + append)


def test_main_exits_2_with_one_stderr_line_naming_the_failed_fetch_of_origin_1605(
        monkeypatch, cli):
    fake_git(monkeypatch, **{"git fetch -q origin": (1, "")})
    assert cli.main([]) == 2
    err = cli.readouterr().err
    assert len(err.splitlines()) == 1, err
    assert "fetch" in err and "origin" in err, err
    assert "refs/remotes/origin/HEAD" not in err and "re-apply" not in err, err


def test_main_exits_2_with_one_stderr_line_naming_the_failed_ls_remote_of_the_default_branch_1605(
        monkeypatch, cli):
    fake_git(monkeypatch, **{"git ls-remote origin refs/heads/main": (1, "")})
    assert cli.main([]) == 2
    err = cli.readouterr().err
    assert len(err.splitlines()) == 1, err
    assert "ls-remote" in err and "main" in err, err
    assert "fetch" not in err and "refs/remotes/origin/HEAD" not in err and "re-apply" not in err, err


def test_main_exits_2_with_one_stderr_line_naming_the_stale_remote_tracking_ref_1605(
        monkeypatch, cli):
    fake_git(monkeypatch, **{"git rev-parse origin/main": (0, f"{PRE}\n")})
    assert cli.main([]) == 2
    err = cli.readouterr().err
    assert len(err.splitlines()) == 1, err
    assert "origin/main" in err, err
    assert "fetch" not in err and "refs/heads/main" not in err, err
    assert "refs/remotes/origin/HEAD" not in err and "re-apply" not in err, err


def test_main_exits_2_with_one_stderr_line_naming_the_rebase_already_in_progress_1605(
        monkeypatch, tmp_path, cli):
    merge, apply = tmp_path / "rebase-merge", tmp_path / "rebase-apply"
    merge.mkdir()
    fake_git(monkeypatch, **{
        f"git rebase -q {ONTO}": (1, ""),
        "git rev-parse --git-path rebase-merge --git-path rebase-apply": (0, f"{merge}\n{apply}\n"),
        "git rev-parse --git-path rebase-merge": (0, f"{merge}\n"),
        "git rev-parse --git-path rebase-apply": (0, f"{apply}\n")})
    assert cli.main([]) == 2
    err = cli.readouterr().err
    assert len(err.splitlines()) == 1, err
    assert "rebase" in err and "in progress" in err, err
    assert "fetch" not in err and "ls-remote" not in err and "stale" not in err, err
    assert "refs/remotes/origin/HEAD" not in err and "re-apply" not in err, err


def test_main_exits_2_with_one_stderr_line_naming_the_rebase_refused_without_a_conflict_1605(
        monkeypatch, tmp_path, cli):
    merge, apply = tmp_path / "rebase-merge", tmp_path / "rebase-apply"
    fake_git(monkeypatch, **{
        f"git rebase -q {ONTO}": (1, ""),
        "git rev-parse --git-path rebase-merge --git-path rebase-apply": (0, f"{merge}\n{apply}\n"),
        "git rev-parse --git-path rebase-merge": (0, f"{merge}\n"),
        "git rev-parse --git-path rebase-apply": (0, f"{apply}\n")})
    assert cli.main([]) == 2
    err = cli.readouterr().err
    assert len(err.splitlines()) == 1, err
    assert "rebase" in err and "without a conflict" in err, err
    assert "in progress" not in err and "fetch" not in err and "ls-remote" not in err, err
    assert "stale" not in err and "refs/remotes/origin/HEAD" not in err and "re-apply" not in err, err


def _failed_reapply_after_the_rebase_1638(monkeypatch, tmp_path, rebase_onto_default, run_cli, kept_text):
    for who in ("AUTHOR", "COMMITTER"):
        monkeypatch.setenv(f"GIT_{who}_NAME", "veri")
        monkeypatch.setenv(f"GIT_{who}_EMAIL", "veri@example.test")

    def git(repo, *args):
        return subprocess.run(["git", "-C", str(repo), *args], check=True, text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.strip()

    origin, seed, clone = tmp_path / "origin.git", tmp_path / "seed", tmp_path / "clone"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], check=True)
    subprocess.run(["git", "init", "-q", "-b", "main", str(seed)], check=True)
    (seed / ".tdd").mkdir()
    (seed / ".tdd" / "issue-1.md").write_text("- [ ] step one\n")
    git(seed, "add", "-A")
    git(seed, "commit", "-q", "-m", "initial")
    git(seed, "push", "-q", str(origin), "main")
    subprocess.run(["git", "clone", "-q", str(origin), str(clone)], check=True, stderr=subprocess.DEVNULL)
    (seed / "other.txt").write_text("another run's work\n")
    git(seed, "add", "-A")
    git(seed, "commit", "-q", "-m", "feat: another run merged (#2)")
    git(seed, "push", "-q", str(origin), "main")
    (clone / ".tdd" / "issue-1.md").write_text("- [ ] step one\n- [ ] step two\n")
    gitdir = pathlib.Path(git(clone, "rev-parse", "--absolute-git-dir"))
    (gitdir / "kept-tdd-appends.diff.1").write_text(kept_text)
    monkeypatch.setenv("PATH", _failing_apply_env_1611(tmp_path)["PATH"])

    code, _, err = run_cli(rebase_onto_default, [], cwd=clone)
    return code, err, gitdir


@pytest.mark.process("git: a real clone behind origin with uncommitted ledger appends, whose re-apply after the rebase git apply fails")
def test_main_removes_the_set_aside_appends_as_soon_as_their_reapply_after_the_rebase_fails_1638(
        monkeypatch, tmp_path, rebase_onto_default, run_cli):
    code, _, gitdir = _failed_reapply_after_the_rebase_1638(
        monkeypatch, tmp_path, rebase_onto_default, run_cli, "earlier appends\n")

    holders = [p.name for p in gitdir.glob("*-tdd-appends.diff*") if "step two" in p.read_text()]
    assert (code, (gitdir / "set-aside-tdd-appends.diff").exists(), len(holders)) == (2, False, 1)


@pytest.mark.process("git: a real clone behind origin with uncommitted ledger appends and a kept-tdd-appends.diff.1 from an earlier failure, whose re-apply after the rebase git apply fails")
def test_main_leaves_an_earlier_kept_appends_file_unchanged_when_the_reapply_after_the_rebase_fails_1638(
        monkeypatch, tmp_path, rebase_onto_default, run_cli):
    code, err, gitdir = _failed_reapply_after_the_rebase_1638(
        monkeypatch, tmp_path, rebase_onto_default, run_cli, "earlier appends\n")

    earlier = gitdir / "kept-tdd-appends.diff.1"
    assert (code, earlier.read_text(), str(earlier) in err) == (2, "earlier appends\n", True)
