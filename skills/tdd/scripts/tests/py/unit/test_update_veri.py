"""In-process cases for veri/update_veri.py, the module update-veri.sh is a shim over."""
import importlib
import subprocess

import pytest

USAGE = "usage: update-veri.sh [--consent yes|no]\n"


@pytest.fixture
def update_veri():
    return importlib.import_module("veri.update_veri")


def test_main_exits_2_with_the_usage_line_and_writes_no_record_for_a_consent_value_other_than_yes_or_no_a_missing_value_or_any_other_argument(
        tmp_path, run_cli, update_veri):
    record = tmp_path / "self-update"
    results = {}
    for argv in (["--consent", "maybe"], ["--consent"], ["--consent", ""], ["--bogus"], ["yes"],
                 ["--consent", "yes", "extra"]):
        results[tuple(argv)] = run_cli(update_veri, argv, env={"VERI_SELF_UPDATE_FILE": str(record)})

    assert results == {argv: (2, "", USAGE) for argv in results}
    assert not record.exists()


def test_main_fast_forwards_a_clean_clone_on_its_default_branch_behind_its_upstream_and_names_the_old_and_new_sha_on_stdout(
        tmp_path, run_cli, update_veri, monkeypatch):
    old, new = "a" * 40, "b" * 40
    clone = {"head": old}

    def fake_git(*args, **_):
        def answer(out="", code=0):
            return subprocess.CompletedProcess(args, code, out + "\n" if out else "", "")

        if "merge" in args or "pull" in args:
            clone["head"] = new
            return answer()
        if "status" in args:
            return answer()
        if "--is-ancestor" in args:
            return answer(code=0 if clone["head"] == old else 1)
        if "--abbrev-ref" in args:
            return answer("origin/main" if args[-1].startswith("origin") else "main")
        if "symbolic-ref" in args:
            return answer("refs/remotes/origin/main" if "refs/remotes/origin/HEAD" in args else "refs/heads/main")
        if "rev-parse" in args:
            return answer(clone["head"] if args[-1] == "HEAD" else new)
        return answer()

    monkeypatch.setattr(update_veri, "git", fake_git, raising=False)

    code, out, err = run_cli(update_veri, [], env={"VERI_SELF_UPDATE_FILE": str(tmp_path / "self-update")})

    assert (code, clone["head"]) == (0, new)
    assert old[:7] in out and new[:7] in out


def test_main_exits_1_with_one_stderr_line_naming_the_reason_and_leaves_the_clone_untouched_when_the_self_update_record_says_no(
        tmp_path, run_cli, update_veri, monkeypatch):
    record = tmp_path / "self-update"
    record.write_text("no\n")
    calls = []

    def fake_git(*args, **_):
        calls.append(args)
        return subprocess.CompletedProcess(args, 0, "main\n", "")

    monkeypatch.setattr(update_veri, "git", fake_git, raising=False)

    code, out, err = run_cli(update_veri, [], env={"VERI_SELF_UPDATE_FILE": str(record)})

    moved = [a for a in calls if {"fetch", "merge", "pull", "reset", "checkout", "stash"} & set(a)]
    assert (code, moved) == (1, [])
    assert out == "" and err.count("\n") == 1 and "no" in err.lower()


def test_main_exits_1_with_one_stderr_line_naming_the_reason_and_leaves_the_clone_untouched_when_veri_self_update_is_0(
        tmp_path, run_cli, update_veri, monkeypatch):
    calls = []

    def fake_git(*args, **_):
        calls.append(args)
        return subprocess.CompletedProcess(args, 0, "main\n", "")

    monkeypatch.setattr(update_veri, "git", fake_git, raising=False)

    code, out, err = run_cli(update_veri, [], env={"VERI_SELF_UPDATE": "0",
                                                   "VERI_SELF_UPDATE_FILE": str(tmp_path / "self-update")})

    moved = [a for a in calls if {"fetch", "merge", "pull", "reset", "checkout", "stash"} & set(a)]
    assert (code, moved) == (1, [])
    assert out == "" and err.count("\n") == 1 and "VERI_SELF_UPDATE" in err


def test_main_exits_1_with_one_stderr_line_naming_the_reason_and_leaves_the_clone_untouched_when_the_clone_is_not_on_its_upstream_default_branch(
        tmp_path, run_cli, update_veri, monkeypatch):
    calls = []

    def fake_git(*args, **_):
        calls.append(args)
        out = ""
        if "symbolic-ref" in args:
            out = "refs/remotes/origin/main" if "refs/remotes/origin/HEAD" in args else "refs/heads/feature"
        elif "--abbrev-ref" in args:
            out = "origin/main" if args[-1].startswith("origin") else "feature"
        elif "rev-parse" in args:
            out = "c" * 40
        return subprocess.CompletedProcess(args, 0, out + "\n" if out else "", "")

    monkeypatch.setattr(update_veri, "git", fake_git, raising=False)

    code, out, err = run_cli(update_veri, [], env={"VERI_SELF_UPDATE_FILE": str(tmp_path / "self-update")})

    moved = [a for a in calls if {"merge", "pull", "reset", "checkout", "stash"} & set(a)]
    assert (code, moved) == (1, [])
    assert out == "" and err.count("\n") == 1 and "branch" in err.lower()


def test_main_exits_1_with_one_stderr_line_naming_the_reason_and_leaves_the_clone_untouched_when_the_working_tree_is_dirty(
        tmp_path, run_cli, update_veri, monkeypatch):
    calls = []

    def fake_git(*args, **_):
        calls.append(args)
        out = ""
        if "status" in args:
            out = " M skills/tdd/SKILL.md"
        elif "symbolic-ref" in args:
            out = "refs/remotes/origin/main" if "refs/remotes/origin/HEAD" in args else "refs/heads/main"
        elif "--abbrev-ref" in args:
            out = "origin/main" if args[-1].startswith("origin") else "main"
        elif "rev-parse" in args:
            out = "c" * 40
        return subprocess.CompletedProcess(args, 0, out + "\n" if out else "", "")

    monkeypatch.setattr(update_veri, "git", fake_git, raising=False)

    code, out, err = run_cli(update_veri, [], env={"VERI_SELF_UPDATE_FILE": str(tmp_path / "self-update")})

    moved = [a for a in calls if {"merge", "pull", "reset", "checkout", "stash"} & set(a)]
    assert (code, moved) == (1, [])
    assert out == "" and err.count("\n") == 1 and "dirty" in err.lower()


def test_main_exits_1_with_one_stderr_line_naming_the_reason_and_leaves_the_clone_untouched_when_the_upstream_is_not_a_fast_forward_of_head(
        tmp_path, run_cli, update_veri, monkeypatch):
    calls = []

    def fake_git(*args, **_):
        calls.append(args)
        out, code = "", 0
        if "--is-ancestor" in args:
            code = 1
        elif "merge" in args:
            code = 128
        elif "symbolic-ref" in args:
            out = "refs/remotes/origin/main" if "refs/remotes/origin/HEAD" in args else "refs/heads/main"
        elif "--abbrev-ref" in args:
            out = "origin/main" if args[-1].startswith("origin") else "main"
        elif "rev-parse" in args:
            out = ("d" if args[-1] == "HEAD" else "e") * 40
        return subprocess.CompletedProcess(args, code, out + "\n" if out else "", "")

    monkeypatch.setattr(update_veri, "git", fake_git, raising=False)

    code, out, err = run_cli(update_veri, [], env={"VERI_SELF_UPDATE_FILE": str(tmp_path / "self-update")})

    moved = [a for a in calls if {"merge", "pull", "reset", "checkout", "stash"} & set(a)]
    assert (code, moved) == (1, [])
    assert out == "" and err.count("\n") == 1 and "fast-forward" in err.lower()


def test_main_exits_2_with_one_stderr_line_naming_the_fetch_and_leaves_the_clone_untouched_when_the_fetch_of_the_upstream_fails(
        tmp_path, run_cli, update_veri, monkeypatch):
    calls = []

    def fake_git(*args, **_):
        calls.append(args)
        out, code = "", 0
        if "fetch" in args:
            code = 128
        elif "symbolic-ref" in args:
            out = "refs/remotes/origin/main" if "refs/remotes/origin/HEAD" in args else "refs/heads/main"
        elif "--abbrev-ref" in args:
            out = "origin/main" if args[-1].startswith("origin") else "main"
        elif "rev-parse" in args:
            out = ("a" if args[-1] == "HEAD" else "b") * 40
        return subprocess.CompletedProcess(args, code, out + "\n" if out else "", "fatal: unable to access\n" if code else "")

    monkeypatch.setattr(update_veri, "git", fake_git, raising=False)

    code, out, err = run_cli(update_veri, [], env={"VERI_SELF_UPDATE_FILE": str(tmp_path / "self-update")})

    moved = [a for a in calls if {"merge", "pull", "reset", "checkout", "stash"} & set(a)]
    assert (code, moved) == (2, [])
    assert out == "" and err.count("\n") == 1 and "fetch" in err.lower()


def test_main_exits_3_and_leaves_the_clone_untouched_when_the_fetched_upstream_default_branch_is_the_commit_the_clone_already_holds(
        tmp_path, run_cli, update_veri, monkeypatch):
    calls = []

    def fake_git(*args, **_):
        calls.append(args)
        out = ""
        if "symbolic-ref" in args:
            out = "refs/remotes/origin/main" if "refs/remotes/origin/HEAD" in args else "refs/heads/main"
        elif "--abbrev-ref" in args:
            out = "origin/main" if args[-1].startswith("origin") else "main"
        elif "rev-parse" in args:
            out = "f" * 40
        return subprocess.CompletedProcess(args, 0, out + "\n" if out else "", "")

    monkeypatch.setattr(update_veri, "git", fake_git, raising=False)

    code, out, err = run_cli(update_veri, [], env={"VERI_SELF_UPDATE_FILE": str(tmp_path / "self-update")})

    moved = [a for a in calls if {"merge", "pull", "reset", "checkout", "stash"} & set(a)]
    assert (code, moved) == (3, [])


def test_main_exits_2_with_one_stderr_line_naming_the_record_and_leaves_the_clone_untouched_when_the_self_update_record_holds_neither_yes_nor_no(
        tmp_path, run_cli, update_veri, monkeypatch):
    record = tmp_path / "self-update"
    record.write_text("maybe\n")
    calls = []

    def fake_git(*args, **_):
        calls.append(args)
        out = ""
        if "symbolic-ref" in args:
            out = "refs/remotes/origin/main" if "refs/remotes/origin/HEAD" in args else "refs/heads/main"
        elif "--abbrev-ref" in args:
            out = "origin/main" if args[-1].startswith("origin") else "main"
        elif "rev-parse" in args:
            out = "f" * 40
        return subprocess.CompletedProcess(args, 0, out + "\n" if out else "", "")

    monkeypatch.setattr(update_veri, "git", fake_git, raising=False)

    code, out, err = run_cli(update_veri, [], env={"VERI_SELF_UPDATE_FILE": str(record)})

    moved = [a for a in calls if {"fetch", "merge", "pull", "reset", "checkout", "stash"} & set(a)]
    assert (code, moved) == (2, [])
    assert out == "" and err.count("\n") == 1 and "record" in err.lower()


def test_main_consent_yes_and_consent_no_each_write_that_answer_as_the_self_update_record_creating_its_directory_and_exit_0_without_touching_git(
        tmp_path, run_cli, update_veri, monkeypatch):
    calls = []

    def fake_git(*args, **_):
        calls.append(args)
        return subprocess.CompletedProcess(args, 0, "", "")

    monkeypatch.setattr(update_veri, "git", fake_git, raising=False)
    results, records = {}, {}
    for answer in ("yes", "no"):
        record = tmp_path / answer / "nested" / "self-update"
        results[answer] = run_cli(update_veri, ["--consent", answer], env={"VERI_SELF_UPDATE_FILE": str(record)})
        records[answer] = record.read_text().strip() if record.exists() else None

    assert results == {"yes": (0, "", ""), "no": (0, "", "")}
    assert records == {"yes": "yes", "no": "no"}
    assert calls == []


def test_main_exits_2_with_the_git_error_on_stderr_and_prints_no_old_and_new_sha_when_the_fast_forward_merge_fails(
        tmp_path, run_cli, update_veri, monkeypatch):
    old, new = "a" * 40, "b" * 40

    def fake_git(*args, **_):
        out, code, err = "", 0, ""
        if "merge" in args and "--ff-only" in args:
            code, err = 128, "error: Your local changes to the following files would be overwritten by merge\n"
        elif "symbolic-ref" in args:
            out = "refs/remotes/origin/main" if "refs/remotes/origin/HEAD" in args else "refs/heads/main"
        elif "--abbrev-ref" in args:
            out = "origin/main" if args[-1].startswith("origin") else "main"
        elif "rev-parse" in args:
            out = old if args[-1] == "HEAD" else new
        return subprocess.CompletedProcess(args, code, out + "\n" if out else "", err)

    monkeypatch.setattr(update_veri, "git", fake_git, raising=False)

    code, out, err = run_cli(update_veri, [], env={"VERI_SELF_UPDATE_FILE": str(tmp_path / "self-update")})

    assert (code, out) == (2, "")
    assert "would be overwritten by merge" in err
