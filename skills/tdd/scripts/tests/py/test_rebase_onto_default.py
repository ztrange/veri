"""In-process cases for veri/rebase_onto_default.py, the module rebase-onto-default.sh is a shim over."""
import importlib
import os
import pathlib
import subprocess
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

PRE = "1111111111111111111111111111111111111111"
ONTO = "2222222222222222222222222222222222222222"


@pytest.fixture
def rebase_onto_default():
    return importlib.import_module("veri.rebase_onto_default")


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
        monkeypatch, capsys, rebase_onto_default):
    def run(argv, **overrides):
        calls = fake_git(monkeypatch, **overrides)
        code = rebase_onto_default.main(argv)
        captured = capsys.readouterr()
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
        monkeypatch, capsys, rebase_onto_default):
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
        code = rebase_onto_default.main([])
        return code, capsys.readouterr().out, calls, stderrs

    calls = fake_git(monkeypatch)
    rebase_onto_default.main([])
    capsys.readouterr()
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
        monkeypatch, capsys, rebase_onto_default):
    refusal = ("rebase-onto-default: refs/remotes/origin/HEAD is not set — "
               "no default branch to rebase onto\n")
    symref = "git ls-remote --symref origin HEAD"
    calls = fake_git(monkeypatch, **{
        "git rev-parse -q --verify --abbrev-ref refs/remotes/origin/HEAD": (1, ""),
        symref: (0, f"{ONTO}\tHEAD\n")})
    code = rebase_onto_default.main([])
    captured = capsys.readouterr()
    assert (code, captured.out, captured.err) == (2, "", refusal)
    assert calls[calls.index(symref) + 1:] == []

    def no_git(args, **kwargs):
        raise FileNotFoundError(2, "No such file or directory", "git")

    monkeypatch.setattr(subprocess, "run", no_git)
    code = rebase_onto_default.main([])
    captured = capsys.readouterr()
    assert (code, captured.out) == (2, "")
    assert captured.err.endswith(refusal)


def test_main_exits_2_when_ls_remote_fails_after_the_fetch_or_an_unchecked_rev_parse_echo_differs_from_its_first_field(
        monkeypatch, capsys, rebase_onto_default):
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
        code = rebase_onto_default.main([])
        return code, capsys.readouterr().out, calls, stderrs

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
        monkeypatch, capsys, rebase_onto_default):
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
    code = rebase_onto_default.main([])
    captured = capsys.readouterr()
    assert (code, captured.out) == (0, f"{PRE}\n{ONTO}\n")
    assert captured.err == "rebase err\n"


def test_main_aborts_a_conflicting_rebase_under_either_backend_and_returns_1_printing_the_abort_s_stdout_then_the_unmerged_files(
        monkeypatch, capsys, tmp_path, rebase_onto_default):
    rebase = f"git rebase -q {ONTO}"
    diff = "git diff --name-only --diff-filter=U"
    abort = "git rebase --abort"
    merge, apply = tmp_path / "rebase-merge", tmp_path / "rebase-apply"

    def run(present):
        present.mkdir()
        calls = fake_git(monkeypatch, **{
            rebase: (1, ""),
            "git rev-parse --git-path rebase-merge": (0, f"{merge}\n"),
            "git rev-parse --git-path rebase-apply": (0, f"{apply}\n"),
            diff: (0, "a.txt\nsub/b.txt\n\n\n"),
            abort: (1, "")})
        fake_run = subprocess.run

        def speaking_run(args, **kwargs):
            line = " ".join([os.path.basename(str(args[0]))] + [str(a) for a in args[1:]])
            if line == abort and kwargs.get("stdout") is None:
                sys.stdout.write("abort out\n")
            return fake_run(args, **kwargs)

        monkeypatch.setattr(subprocess, "run", speaking_run)
        code = rebase_onto_default.main([])
        present.rmdir()
        return code, capsys.readouterr().out, calls

    for present in (merge, apply):
        code, out, calls = run(present)
        assert (code, out) == (1, "abort out\na.txt\nsub/b.txt\n")
        assert calls.index(diff) < calls.index(abort)


def test_main_returns_2_without_the_conflict_path_when_a_failed_rebase_leaves_neither_rebase_directory(
        monkeypatch, capsys, tmp_path, rebase_onto_default):
    calls = fake_git(monkeypatch, **{
        f"git rebase -q {ONTO}": (1, ""),
        "git rev-parse --git-path rebase-merge": (0, f"{tmp_path / 'rebase-merge'}\n"),
        "git rev-parse --git-path rebase-apply": (0, f"{tmp_path / 'rebase-apply'}\n")})
    code = rebase_onto_default.main([])
    assert (code, capsys.readouterr().out) == (2, "")
    assert [c for c in calls if c.startswith(("git diff", "git rebase --abort"))] == []


def test_main_returns_2_with_no_rebase_directory_prints_one_empty_line_for_no_unmerged_files_and_takes_a_rebase_already_in_progress_for_its_own_conflict(
        monkeypatch, capsys, tmp_path, rebase_onto_default):
    rebase = f"git rebase -q {ONTO}"
    diff = "git diff --name-only --diff-filter=U"
    abort = "git rebase --abort"
    merge, apply = tmp_path / "rebase-merge", tmp_path / "rebase-apply"
    refusal = ("fatal: It seems that there is already a rebase-merge directory, and\n"
               "I wonder if you are in the middle of another rebase.\n")

    def run(diff_answer, refuse=False):
        calls = fake_git(monkeypatch, **{
            rebase: (1, ""),
            "git rev-parse --git-path rebase-merge": (0, f"{merge}\n"),
            "git rev-parse --git-path rebase-apply": (0, f"{apply}\n"),
            diff: diff_answer})
        fake_run = subprocess.run

        def refusing_run(args, **kwargs):
            line = " ".join([os.path.basename(str(args[0]))] + [str(a) for a in args[1:]])
            if refuse and line == rebase and kwargs.get("stderr") is None:
                sys.stderr.write(refusal)
            return fake_run(args, **kwargs)

        monkeypatch.setattr(subprocess, "run", refusing_run)
        code = rebase_onto_default.main([])
        return code, capsys.readouterr(), calls

    code, captured, calls = run((0, "a.txt\n"))
    assert (code, captured.out) == (2, "")
    assert [c for c in calls if c.startswith(("git diff", abort))] == []

    merge.mkdir()
    code, captured, calls = run((0, ""))
    assert (code, captured.out) == (1, "\n")
    assert calls.index(diff) < calls.index(abort)

    code, captured, calls = run((0, "earlier.txt\n"), refuse=True)
    assert (code, captured.out) == (1, "earlier.txt\n")
    assert refusal in captured.err
    assert calls.index(diff) < calls.index(abort)


def test_main_answers_the_cut_contract_cases_a_dirty_tree_refusal_an_unfetchable_origin_a_fallback_rebase_and_an_unreachable_fallback(
        monkeypatch, capsys, tmp_path, rebase_onto_default):
    local = "git rev-parse -q --verify --abbrev-ref refs/remotes/origin/HEAD"
    symref = "git ls-remote --symref origin HEAD"
    rebase = f"git rebase -q {ONTO}"
    refused = ("error: Your local changes to the following files would be overwritten by checkout:\n"
               "\tfile.txt\nerror: could not detach HEAD\n")

    def run(**overrides):
        calls = fake_git(monkeypatch, **{
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
        code = rebase_onto_default.main([])
        return code, capsys.readouterr(), calls

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
        monkeypatch, capsys, tmp_path, rebase_onto_default):
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
    code = rebase_onto_default.main([])
    assert (code, capsys.readouterr().out) == (2, "")
    assert [c for c in calls if c.startswith("git rebase") and c != rebase] == []
    assert sorted(p.name for p in merge.iterdir()) == ["head-name"]


def test_main_answers_each_ls_remote_shape_with_its_stdout_stderr_and_exit_code_when_origin_head_is_absent(
        monkeypatch, capsys, rebase_onto_default):
    refusal = ("rebase-onto-default: refs/remotes/origin/HEAD is not set — "
               "no default branch to rebase onto\n")
    local = "git rev-parse -q --verify --abbrev-ref refs/remotes/origin/HEAD"
    symref = "git ls-remote --symref origin HEAD"

    def run(answer, **overrides):
        fake_git(monkeypatch, **{local: (1, ""), symref: answer}, **overrides)
        code = rebase_onto_default.main([])
        captured = capsys.readouterr()
        return code, captured.out, captured.err

    trunk = {"git ls-remote origin refs/heads/trunk": (0, f"{ONTO}\trefs/heads/trunk\n"),
             "git rev-parse origin/trunk": (0, f"{ONTO}\n")}
    assert run((0, f"ref: refs/heads/trunk\tHEAD\n{ONTO}\tHEAD\n"), **trunk) == (
        0, f"{PRE}\n{ONTO}\n", "")
    assert run((0, f"{ONTO}\tHEAD\n")) == (2, "", refusal)
    assert run((128, "")) == (2, "", refusal)
