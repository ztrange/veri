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
