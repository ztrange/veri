"""In-process cases for veri/stack_branch.py, the module stack-branch.sh is a shim over; git is faked at the process boundary."""
import importlib

import pytest


@pytest.fixture
def stack_branch():
    return importlib.import_module("veri.stack_branch")


def git_world(fake_processes, default="main", refused=()):
    """git faked: origin/HEAD names <default>; `check-ref-format --branch` refuses each name in <refused>."""
    def check(line, **_):
        name = line.rsplit(" ", 1)[-1]
        return (128, "", "fatal: '%s' is not a valid branch name\n" % name) if name in refused else (0, name + "\n", "")
    return fake_processes.answers({
        "git symbolic-ref --quiet --short refs/remotes/origin/HEAD": (0, "origin/%s\n" % default, ""),
        "git check-ref-format --branch": check,
    })


def test_prints_the_named_branch_from_the_given_root_or_the_current_directory_and_exits_3_with_no_line_or_no_claude_md(
        tmp_path, monkeypatch, run_cli, fake_processes, stack_branch):
    git_world(fake_processes)
    named = tmp_path / "named"
    named.mkdir()
    (named / "CLAUDE.md").write_text("# notes\n\nveri: all tests: `make test`\nveri: stack branch: `stack`\n")
    silent = tmp_path / "silent"
    silent.mkdir()
    (silent / "CLAUDE.md").write_text("# notes\n\nThe `veri: stack branch:` line names one.\nveri: all tests: make test\n")
    bare = tmp_path / "bare"
    bare.mkdir()
    monkeypatch.chdir(named)

    got = [run_cli(stack_branch, [str(named)]), run_cli(stack_branch, []),
           run_cli(stack_branch, [str(silent)]), run_cli(stack_branch, [str(bare)])]

    assert got == [(0, "stack\n", ""), (0, "stack\n", ""), (3, "", ""), (3, "", "")]


def refusal_of(tmp_path, run_cli, stack_branch, line):
    (tmp_path / "CLAUDE.md").write_text("# notes\n\n%s\n" % line)
    code, out, err = run_cli(stack_branch, [str(tmp_path)])
    return code, out, line in err


def test_exits_2_naming_the_line_when_the_named_branch_is_empty(tmp_path, run_cli, fake_processes, stack_branch):
    git_world(fake_processes)

    got = [refusal_of(tmp_path, run_cli, stack_branch, line) for line in ("veri: stack branch:", "veri: stack branch: ``")]

    assert got == [(2, "", True)] * 2


def test_exits_2_naming_the_line_when_the_named_branch_is_the_default_branch(tmp_path, run_cli, fake_processes, stack_branch):
    git_world(fake_processes, default="trunk")

    assert refusal_of(tmp_path, run_cli, stack_branch, "veri: stack branch: trunk") == (2, "", True)


def test_exits_2_naming_the_line_when_git_check_ref_format_refuses_the_name(tmp_path, run_cli, fake_processes, stack_branch):
    git_world(fake_processes, refused=("bad..name",))

    assert refusal_of(tmp_path, run_cli, stack_branch, "veri: stack branch: bad..name") == (2, "", True)
