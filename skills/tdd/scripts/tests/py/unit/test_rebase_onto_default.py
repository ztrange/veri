"""In-process cases for veri/rebase_onto_default.py, the module rebase-onto-default.sh is a shim over."""
import importlib
import os
import subprocess
import sys
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
def cli(run_cli):
    return Cli(run_cli)


def git_fake(fake_processes, hooks=None, raw=None, **overrides):
    """git faked as a process, answering each git call from a branch behind origin/main;
    <overrides> maps a command line to (exit code, stdout). <hooks> maps a command line to a function
    (kwargs, exit code) run as that command is answered (what git does to the tree or the streams);
    <raw> maps a command prefix to any fake_processes answer. Returns the fake."""
    answers = {
        "git symbolic-ref --quiet --short refs/remotes/origin/HEAD": (0, "origin/main\n"),
        "git fetch -q origin": (0, ""),
        "git ls-remote origin refs/heads/main": (0, f"{ONTO}\trefs/heads/main\n"),
        "git rev-parse origin/main": (0, f"{ONTO}\n"),
        f"git merge-base --is-ancestor {ONTO} HEAD": (1, ""),
        "git rev-parse HEAD": (0, f"{PRE}\n"),
        f"git rebase -q {ONTO}": (0, ""),
    }
    answers.update(overrides)
    hooks = hooks or {}

    def answer(line, code, out):
        if line not in hooks:
            return code, out, ""

        def hooked(_line, **kwargs):
            hooks[line](kwargs, code)
            return code, out, ""
        return hooked

    table = {line: answer(line, code, out) for line, (code, out) in answers.items()}
    table.update(raw or {})
    return fake_processes.answers(table, default=(0, "", ""))


def git_answers(fake_processes, **overrides):
    """git_fake's command lines run."""
    return git_fake(fake_processes, **overrides).calls


def stderr_asked(fake, line):
    """What the last call of <line> asked for stderr (or capture_output)."""
    asked = [kwargs.get("stderr") or kwargs.get("capture_output") for argv, kwargs in fake.seen
             if " ".join([os.path.basename(str(argv[0]))] + [str(a) for a in argv[1:]]) == line]
    return asked[-1]


def test_main_exits_2_on_a_failed_fetch_3_when_up_to_date_0_when_rebased_and_ignores_arguments(
        monkeypatch, cli, fake_processes):
    def run(argv, **overrides):
        calls = git_answers(fake_processes, **overrides)
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
        monkeypatch, cli, fake_processes):
    symref = "git ls-remote --symref origin HEAD"
    local = "git symbolic-ref --quiet --short refs/remotes/origin/HEAD"

    def run(answer, **overrides):
        fake = git_fake(fake_processes, **{local: (1, ""), symref: answer}, **overrides)
        code = cli.main([])
        return code, cli.readouterr().out, fake.calls, fake

    calls = git_answers(fake_processes)
    cli.main([])
    cli.readouterr()
    assert symref not in calls

    code, out, calls, fake = run((2, f"ref: refs/heads/trunk\tHEAD\n{ONTO}\tHEAD\n"),
                                    **{"git ls-remote origin refs/heads/trunk":
                                       (0, f"{ONTO}\trefs/heads/trunk\n"),
                                       "git rev-parse origin/trunk": (0, f"{ONTO}\n")})
    assert symref in calls
    assert stderr_asked(fake, symref) in (True, subprocess.PIPE)
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
        monkeypatch, cli, fake_processes):
    refusal = ("rebase-onto-default: refs/remotes/origin/HEAD is not set — "
               "no default branch to rebase onto\n")
    symref = "git ls-remote --symref origin HEAD"
    calls = git_answers(fake_processes, **{
        "git symbolic-ref --quiet --short refs/remotes/origin/HEAD": (1, ""),
        symref: (0, f"{ONTO}\tHEAD\n")})
    code = cli.main([])
    captured = cli.readouterr()
    assert (code, captured.out, captured.err) == (2, "", refusal)
    assert calls[calls.index(symref) + 1:] == []

    fake_processes.answers({"git": FileNotFoundError(2, "No such file or directory", "git")})
    code = cli.main([])
    captured = cli.readouterr()
    assert (code, captured.out) == (2, "")
    assert captured.err.endswith(refusal)


def test_main_exits_2_when_ls_remote_fails_after_the_fetch_or_an_unchecked_rev_parse_echo_differs_from_its_first_field(
        monkeypatch, cli, fake_processes):
    ls_remote = "git ls-remote origin refs/heads/main"
    rev_parse = "git rev-parse origin/main"

    def run(**overrides):
        fake = git_fake(fake_processes, **overrides)
        code = cli.main([])
        return code, cli.readouterr().out, fake.calls, fake

    code, out, calls, fake = run(**{ls_remote: (2, f"{ONTO}\trefs/heads/main\n")})
    assert (code, out) == (2, "")
    assert "git fetch -q origin" in calls
    assert stderr_asked(fake, ls_remote) == subprocess.DEVNULL
    assert [c for c in calls if c.startswith(("git merge-base", "git rebase"))] == []

    code, out, calls, _ = run(**{rev_parse: (128, "origin/main\n")})
    assert (code, out) == (2, "")
    assert [c for c in calls if c.startswith("git merge-base")] == []

    code, out, calls, _ = run(**{ls_remote: (0, "origin/main\trefs/heads/main\n"),
                                 rev_parse: (128, "origin/main\n")})
    assert "git merge-base --is-ancestor origin/main HEAD" in calls
    assert (code, out) == (3, "")


def test_main_drops_the_fetch_s_stdout_and_stderr_and_the_rebase_s_stdout_and_passes_the_rebase_s_stderr_through(
        monkeypatch, cli, fake_processes):
    fetch = "git fetch -q origin"
    rebase = f"git rebase -q {ONTO}"
    speech = {fetch: ("fetch out\n", "fetch err\n"), rebase: ("rebase out\n", "rebase err\n")}

    def speaks(line):
        def speak(kwargs, code):
            out, err = speech[line]
            if kwargs.get("stdout") is None:
                sys.stdout.write(out)
            if kwargs.get("stderr") is None:
                sys.stderr.write(err)
        return speak

    git_fake(fake_processes, hooks={fetch: speaks(fetch), rebase: speaks(rebase)})
    code = cli.main([])
    captured = cli.readouterr()
    assert (code, captured.out) == (0, f"{PRE}\n{ONTO}\n")
    assert captured.err == "rebase err\n"


def test_main_aborts_a_conflicting_rebase_under_either_backend_and_returns_1_printing_the_abort_s_stdout_then_the_unmerged_files(
        monkeypatch, tmp_path, cli, fake_processes):
    rebase = f"git rebase -q {ONTO}"
    diff = "git diff --name-only --diff-filter=U"
    abort = "git rebase --abort"
    merge, apply = tmp_path / "rebase-merge", tmp_path / "rebase-apply"

    def run(present):
        def leave_the_directory(kwargs, code):
            present.mkdir()

        def say_abort_out(kwargs, code):
            if kwargs.get("stdout") is None:
                sys.stdout.write("abort out\n")

        calls = git_answers(fake_processes, hooks={rebase: leave_the_directory, abort: say_abort_out}, **{
            rebase: (1, ""),
            "git rev-parse --git-path rebase-merge --git-path rebase-apply": (0, f"{merge}\n{apply}\n"),
            "git rev-parse --git-path rebase-merge": (0, f"{merge}\n"),
            "git rev-parse --git-path rebase-apply": (0, f"{apply}\n"),
            diff: (0, "a.txt\nsub/b.txt\n\n\n"),
            abort: (1, "")})
        code = cli.main([])
        present.rmdir()
        return code, cli.readouterr().out, calls

    for present in (merge, apply):
        code, out, calls = run(present)
        assert (code, out) == (1, "abort out\na.txt\nsub/b.txt\n")
        assert calls.index(diff) < calls.index(abort)


def test_main_returns_2_without_the_conflict_path_when_a_failed_rebase_leaves_neither_rebase_directory(
        monkeypatch, tmp_path, cli, fake_processes):
    calls = git_answers(fake_processes, **{
        f"git rebase -q {ONTO}": (1, ""),
        "git rev-parse --git-path rebase-merge --git-path rebase-apply":
            (0, f"{tmp_path / 'rebase-merge'}\n{tmp_path / 'rebase-apply'}\n"),
        "git rev-parse --git-path rebase-merge": (0, f"{tmp_path / 'rebase-merge'}\n"),
        "git rev-parse --git-path rebase-apply": (0, f"{tmp_path / 'rebase-apply'}\n")})
    code = cli.main([])
    assert (code, cli.readouterr().out) == (2, "")
    assert [c for c in calls if c.startswith(("git diff", "git rebase --abort"))] == []


def test_main_returns_2_with_no_rebase_directory_prints_one_empty_line_for_no_unmerged_files_and_leaves_a_rebase_already_in_progress_alone(
        monkeypatch, tmp_path, cli, fake_processes):
    rebase = f"git rebase -q {ONTO}"
    diff = "git diff --name-only --diff-filter=U"
    abort = "git rebase --abort"
    merge, apply = tmp_path / "rebase-merge", tmp_path / "rebase-apply"
    refusal = ("fatal: It seems that there is already a rebase-merge directory, and\n"
               "I wonder if you are in the middle of another rebase.\n")

    def run(diff_answer, refuse=False, created=None):
        def refusing_rebase(kwargs, code):
            if created is not None:
                created.mkdir()
            if refuse and kwargs.get("stderr") is None:
                sys.stderr.write(refusal)

        calls = git_answers(fake_processes, hooks={rebase: refusing_rebase}, **{
            rebase: (1, ""),
            "git rev-parse --git-path rebase-merge --git-path rebase-apply": (0, f"{merge}\n{apply}\n"),
            "git rev-parse --git-path rebase-merge": (0, f"{merge}\n"),
            "git rev-parse --git-path rebase-apply": (0, f"{apply}\n"),
            diff: diff_answer})
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
        monkeypatch, tmp_path, cli, fake_processes):
    rebase = f"git rebase -q {ONTO}"
    diff = "git diff --name-only --diff-filter=U"
    abort = "git rebase --abort"
    merge, apply = tmp_path / "rebase-merge", tmp_path / "rebase-apply"
    refusal = ("fatal: It seems that there is already a rebase-merge directory, and\n"
               "I wonder if you are in the middle of another rebase.\n")
    merge.mkdir()
    def refusing_rebase(kwargs, code):
        if kwargs.get("stderr") is None:
            sys.stderr.write(refusal)

    calls = git_answers(fake_processes, hooks={rebase: refusing_rebase}, **{
        rebase: (1, ""),
        "git rev-parse --git-path rebase-merge --git-path rebase-apply": (0, f"{merge}\n{apply}\n"),
        "git rev-parse --git-path rebase-merge": (0, f"{merge}\n"),
        "git rev-parse --git-path rebase-apply": (0, f"{apply}\n"),
        diff: (0, "earlier.txt\n")})
    code = cli.main([])
    captured = cli.readouterr()
    assert (code, captured.out) == (2, "")
    assert refusal in captured.err
    assert [c for c in calls if c in (diff, abort)] == []


def test_main_returns_1_with_the_conflict_output_when_its_own_rebase_leaves_the_directory_the_two_name_git_path_call_did_not_see(
        monkeypatch, tmp_path, cli, fake_processes):
    rebase = f"git rebase -q {ONTO}"
    two_names = "git rev-parse --git-path rebase-merge --git-path rebase-apply"
    diff = "git diff --name-only --diff-filter=U"
    abort = "git rebase --abort"
    merge, apply = tmp_path / "rebase-merge", tmp_path / "rebase-apply"

    def run(present, diff_answer):
        def leave_the_directory(kwargs, code):
            present.mkdir()

        def say_abort_out(kwargs, code):
            if kwargs.get("stdout") is None:
                sys.stdout.write("abort out\n")

        calls = git_answers(fake_processes, hooks={rebase: leave_the_directory, abort: say_abort_out}, **{
            rebase: (1, ""),
            two_names: (0, f"{merge}\n{apply}\n"),
            "git rev-parse --git-path rebase-merge": (0, f"{merge}\n"),
            "git rev-parse --git-path rebase-apply": (0, f"{apply}\n"),
            diff: diff_answer,
            abort: (1, "")})
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
        monkeypatch, tmp_path, cli, fake_processes):
    local = "git symbolic-ref --quiet --short refs/remotes/origin/HEAD"
    symref = "git ls-remote --symref origin HEAD"
    rebase = f"git rebase -q {ONTO}"
    refused = ("error: Your local changes to the following files would be overwritten by checkout:\n"
               "\tfile.txt\nerror: could not detach HEAD\n")

    def run(**overrides):
        def refusing_rebase(kwargs, code):
            if code != 0 and kwargs.get("stderr") is None:
                sys.stderr.write(refused)

        calls = git_answers(fake_processes, hooks={rebase: refusing_rebase}, **{
            "git rev-parse --git-path rebase-merge --git-path rebase-apply":
                (0, f"{tmp_path / 'rebase-merge'}\n{tmp_path / 'rebase-apply'}\n"),
            "git rev-parse --git-path rebase-merge": (0, f"{tmp_path / 'rebase-merge'}\n"),
            "git rev-parse --git-path rebase-apply": (0, f"{tmp_path / 'rebase-apply'}\n")},
            **overrides)
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
        monkeypatch, tmp_path, cli, fake_processes):
    rebase = f"git rebase -q {ONTO}"
    merge = tmp_path / "rebase-merge"
    merge.mkdir()
    (merge / "head-name").write_text("refs/heads/caller\n")
    holder = []

    def git_path(line, **kwargs):
        names = [a for a in holder[0].argvs[-1][2:] if a != "--git-path"]
        return 0, "".join(f"{tmp_path / name}\n" for name in names), ""

    holder.append(git_fake(fake_processes, raw={"git rev-parse --git-path": git_path}, **{rebase: (1, "")}))
    calls = holder[0].calls
    code = cli.main([])
    assert (code, cli.readouterr().out) == (2, "")
    assert [c for c in calls if c.startswith("git rebase") and c != rebase] == []
    assert sorted(p.name for p in merge.iterdir()) == ["head-name"]


def test_main_answers_each_ls_remote_shape_with_its_stdout_stderr_and_exit_code_when_origin_head_is_absent(
        monkeypatch, cli, fake_processes):
    refusal = ("rebase-onto-default: refs/remotes/origin/HEAD is not set — "
               "no default branch to rebase onto\n")
    local = "git symbolic-ref --quiet --short refs/remotes/origin/HEAD"
    symref = "git ls-remote --symref origin HEAD"

    def run(answer, **overrides):
        git_answers(fake_processes, **{local: (1, ""), symref: answer}, **overrides)
        code = cli.main([])
        captured = cli.readouterr()
        return code, captured.out, captured.err

    trunk = {"git ls-remote origin refs/heads/trunk": (0, f"{ONTO}\trefs/heads/trunk\n"),
             "git rev-parse origin/trunk": (0, f"{ONTO}\n")}
    assert run((0, f"ref: refs/heads/trunk\tHEAD\n{ONTO}\tHEAD\n"), **trunk) == (
        0, f"{PRE}\n{ONTO}\n", "")
    assert run((0, f"{ONTO}\tHEAD\n")) == (2, "", refusal)
    assert run((128, "")) == (2, "", refusal)


def test_main_exits_2_with_one_stderr_line_naming_the_failed_fetch_of_origin_1605(
        monkeypatch, cli, fake_processes):
    git_answers(fake_processes, **{"git fetch -q origin": (1, "")})
    assert cli.main([]) == 2
    err = cli.readouterr().err
    assert len(err.splitlines()) == 1, err
    assert "fetch" in err and "origin" in err, err
    assert "refs/remotes/origin/HEAD" not in err and "re-apply" not in err, err


def test_main_exits_2_with_one_stderr_line_naming_the_failed_ls_remote_of_the_default_branch_1605(
        monkeypatch, cli, fake_processes):
    git_answers(fake_processes, **{"git ls-remote origin refs/heads/main": (1, "")})
    assert cli.main([]) == 2
    err = cli.readouterr().err
    assert len(err.splitlines()) == 1, err
    assert "ls-remote" in err and "main" in err, err
    assert "fetch" not in err and "refs/remotes/origin/HEAD" not in err and "re-apply" not in err, err


def test_main_exits_2_with_one_stderr_line_naming_the_stale_remote_tracking_ref_1605(
        monkeypatch, cli, fake_processes):
    git_answers(fake_processes, **{"git rev-parse origin/main": (0, f"{PRE}\n")})
    assert cli.main([]) == 2
    err = cli.readouterr().err
    assert len(err.splitlines()) == 1, err
    assert "origin/main" in err, err
    assert "fetch" not in err and "refs/heads/main" not in err, err
    assert "refs/remotes/origin/HEAD" not in err and "re-apply" not in err, err


def test_main_exits_2_with_one_stderr_line_naming_the_rebase_already_in_progress_1605(
        monkeypatch, tmp_path, cli, fake_processes):
    merge, apply = tmp_path / "rebase-merge", tmp_path / "rebase-apply"
    merge.mkdir()
    git_answers(fake_processes, **{
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
        monkeypatch, tmp_path, cli, fake_processes):
    merge, apply = tmp_path / "rebase-merge", tmp_path / "rebase-apply"
    git_answers(fake_processes, **{
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


STACK = "3333333333333333333333333333333333333333"


def stack_answers(contained=False):
    """git_fake's overrides for a worktree whose CLAUDE.md names the stack branch `stack`, origin holding it at STACK."""
    return {
        "git check-ref-format --branch stack": (0, "stack\n"),
        "git ls-remote origin refs/heads/stack": (0, f"{STACK}\trefs/heads/stack\n"),
        "git rev-parse origin/stack": (0, f"{STACK}\n"),
        f"git merge-base --is-ancestor {STACK} HEAD": ((0 if contained else 1), ""),
        f"git rebase -q {STACK}": (0, ""),
    }


@pytest.mark.parametrize("argv", [[], ["--graded-only"]])
def test_main_rebases_onto_origin_stack_where_a_stack_branch_is_named_and_exits_3_when_the_branch_contains_it_4170(
        monkeypatch, tmp_path, cli, fake_processes, argv):
    (tmp_path / "CLAUDE.md").write_text("veri: stack branch: stack\n")
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-7-base").write_text("stack\n")
    monkeypatch.chdir(tmp_path)

    rebased = git_answers(fake_processes, **stack_answers())
    code, out = cli.main(argv), cli.readouterr().out
    contained = git_answers(fake_processes, **stack_answers(contained=True))
    up_to_date = cli.main(argv), cli.readouterr().out

    assert (code, out, [c for c in rebased if c.startswith("git rebase")], up_to_date,
            [c for c in contained if c.startswith("git rebase")]) == (
        0, f"{PRE}\n{STACK}\n", [f"git rebase -q {STACK}"], (3, ""), [])



def test_main_rebases_a_hand_branch_in_a_stacking_repository_onto_the_default_branch_as_before_4171(
        monkeypatch, tmp_path, cli, fake_processes):
    (tmp_path / "CLAUDE.md").write_text("veri: stack branch: stack\n")
    monkeypatch.chdir(tmp_path)

    calls = git_answers(fake_processes, **stack_answers())
    code, out = cli.main([]), cli.readouterr().out

    assert (code, out, [c for c in calls if c.startswith("git rebase")]) == (0, f"{PRE}\n{ONTO}\n", [f"git rebase -q {ONTO}"])


def test_main_exits_2_naming_both_when_the_recorded_base_is_not_the_named_stack_4171(
        monkeypatch, tmp_path, cli, fake_processes):
    (tmp_path / "CLAUDE.md").write_text("veri: stack branch: stack\n")
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-7-base").write_text("older-stack\n")
    monkeypatch.chdir(tmp_path)

    calls = git_answers(fake_processes, **stack_answers())
    code, captured = cli.main([]), cli.readouterr()

    assert (code, [c for c in calls if c.startswith("git rebase")], "older-stack" in captured.err, "stack" in captured.err) == (
        2, [], True, True)


@pytest.mark.parametrize("fetch, code", [((0, ""), 0), ((1, ""), 2)], ids=["rebased", "unfetchable origin"])
def test_4232_rebase_onto_default_runs_as_stage_rebase_carrying_the_runs_issue_ending_with_its_exit_code(
        monkeypatch, tmp_path, cli, fake_processes, events, fetch, code):
    (tmp_path / ".tdd").mkdir()
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VERI_STATE_LABEL_ISSUE", "12")
    git_answers(fake_processes, **{"git fetch -q origin": fetch})

    returned = cli.main([])

    stages = [(r["event"], r["stage"], r.get("status"), r["issue"]) for r in events.records(tmp_path)]
    assert (returned, stages) == (code, [("stage-start", "rebase", None, "12"), ("stage-end", "rebase", str(code), "12")])


@pytest.mark.parametrize("case", ["rebased", "up to date", "not a run branch", "record unwritable",
                                  "up to date, record unwritable"])
def test_a_rebase_of_a_run_branch_re_records_its_branch_base_as_the_onto_sha_and_nothing_else_does_4374(
        cli, fake_processes, tmp_path, case):
    """The record lands in the main working tree, here <tmp_path> (no `.git` above it). A branch already up to
    date re-records it too, so a rebase whose record write failed leaves no stale base behind a later exit 3."""
    record = tmp_path / ".tdd" / "issue-12-branch-base"
    if case.endswith("record unwritable"):
        record.mkdir(parents=True)
    git_fake(fake_processes, **{
        "git symbolic-ref --quiet --short HEAD": (0, ("main" if case == "not a run branch" else "tdd/12-slug") + "\n"),
        **({f"git merge-base --is-ancestor {ONTO} HEAD": (0, "")} if case.startswith("up to date") else {})})

    code, out, err = cli.run_cli(cli.module, [], cwd=str(tmp_path))

    expected = {"rebased": (0, ONTO + "\n", False), "up to date": (3, ONTO + "\n", False),
                "not a run branch": (0, None, False), "record unwritable": (2, None, True),
                "up to date, record unwritable": (2, None, True)}[case]
    assert (code, record.read_text() if record.is_file() else None, str(record) in err) == expected


@pytest.mark.parametrize("argv, named", [(["--resolved", ONTO], ONTO), (["--resolved", "origin/main"], "origin/main"),
                                         (["--resolved"], "usage: ")], ids=["not in HEAD", "not hex", "missing"])
def test_resolved_exits_2_leaving_the_record_untouched_when_head_lacks_the_onto_sha_or_it_is_no_hex_commit_name_4553(
        cli, fake_processes, tmp_path, argv, named):
    record = tmp_path / ".tdd" / "issue-12-branch-base"
    record.parent.mkdir()
    record.write_text(PRE + "\n")
    calls = git_answers(fake_processes, **{"git symbolic-ref --quiet --short HEAD": (0, "tdd/12-slug\n")})

    code, out, err = cli.run_cli(cli.module, argv, cwd=str(tmp_path))

    asked = [c for c in calls if c.startswith(("git fetch", "git rebase", "git merge-base"))]
    assert (code, named in err, record.read_text(), asked) == (
        2, True, PRE + "\n", [f"git merge-base --is-ancestor {ONTO} HEAD"] if named == ONTO else [])
