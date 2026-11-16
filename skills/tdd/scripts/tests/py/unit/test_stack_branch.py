"""In-process cases for veri/stack_branch.py, the module stack-branch.sh is a shim over; git is faked at the process boundary."""
import importlib

import pytest


@pytest.fixture
def stack_branch():
    return importlib.import_module("veri.stack_branch")


def git_world(fake_processes, default="main", refused=(), local=True, remote=True):
    """git faked: origin/HEAD names <default> (unset when not <local>), and so does origin itself when asked (no answer
    when not <remote>); `check-ref-format --branch` refuses each name in <refused>."""
    def check(line, **_):
        name = line.rsplit(" ", 1)[-1]
        return (128, "", "fatal: '%s' is not a valid branch name\n" % name) if name in refused else (0, name + "\n", "")
    return fake_processes.answers({
        "git symbolic-ref --quiet --short refs/remotes/origin/HEAD":
            (0, "origin/%s\n" % default, "") if local else (1, "", ""),
        "git ls-remote --symref origin HEAD":
            (0, "ref: refs/heads/%s\tHEAD\n1111111\tHEAD\n" % default, "") if remote else (128, "", "fatal: unreachable\n"),
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


def test_run_base_answers_the_named_stack_the_default_branch_with_none_named_and_raises_the_refusal_of_a_bad_name_4170(
        tmp_path, fake_processes, stack_branch):
    git_world(fake_processes, default="trunk")
    stacked, plain, refused = tmp_path / "stacked", tmp_path / "plain", tmp_path / "refused"
    for root in (stacked, plain, refused):
        root.mkdir()
    (stacked / "CLAUDE.md").write_text("veri: stack branch: stack\n")
    (refused / "CLAUDE.md").write_text("veri: stack branch: trunk\n")
    for root, recorded in ((stacked, "stack"), (refused, "trunk")):
        (root / ".tdd").mkdir()
        (root / ".tdd" / "issue-7-base").write_text(recorded + "\n")

    with pytest.raises(stack_branch.Refused) as refusal:
        stack_branch.run_base(str(refused))

    assert (stack_branch.run_base(str(stacked)), stack_branch.run_base(str(plain)),
            "veri: stack branch: trunk" in str(refusal.value)) == (("stack", True), ("trunk", False), True)


def test_with_no_local_origin_head_the_default_branch_as_origin_states_it_is_refused_4171(
        tmp_path, run_cli, fake_processes, stack_branch):
    git_world(fake_processes, default="main", local=False)

    assert refusal_of(tmp_path, run_cli, stack_branch, "veri: stack branch: main") == (2, "", True)


def test_a_default_branch_that_cannot_be_told_locally_or_from_origin_is_exit_2_never_0_4171(
        tmp_path, run_cli, fake_processes, stack_branch):
    git_world(fake_processes, local=False, remote=False)

    assert refusal_of(tmp_path, run_cli, stack_branch, "veri: stack branch: stack") == (2, "", True)


@pytest.mark.parametrize("record, answer", [
    (None, ("trunk", False)),
    ("stack\n", ("stack", True)),
])
def test_run_base_is_the_stack_only_for_a_branch_whose_cut_recorded_it_and_the_default_branch_otherwise_4171(
        tmp_path, fake_processes, stack_branch, record, answer):
    git_world(fake_processes, default="trunk")
    (tmp_path / "CLAUDE.md").write_text("veri: stack branch: stack\n")
    if record is not None:
        (tmp_path / ".tdd").mkdir()
        (tmp_path / ".tdd" / "issue-7-base").write_text(record)

    assert stack_branch.run_base(str(tmp_path)) == answer


@pytest.mark.parametrize("records", [{"issue-7-base": "other\n"}, {"issue-7-base": ""}, {"issue-7-base": "stack\nmore\n"},
                                     {"issue-7-base": "stack\n", "issue-8-base": "stack\n"}])
def test_run_base_refuses_a_recorded_base_that_is_garbled_or_no_longer_the_named_stack_naming_both_4171(
        tmp_path, fake_processes, stack_branch, records):
    git_world(fake_processes, default="trunk")
    (tmp_path / "CLAUDE.md").write_text("veri: stack branch: stack\n")
    (tmp_path / ".tdd").mkdir()
    for name, text in records.items():
        (tmp_path / ".tdd" / name).write_text(text)

    with pytest.raises(stack_branch.Refused) as refusal:
        stack_branch.run_base(str(tmp_path))

    assert "issue-7-base" in str(refusal.value) and "stack" in str(refusal.value)
