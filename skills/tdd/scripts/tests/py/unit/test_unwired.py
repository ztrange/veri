"""In-process cases for veri/unwired.py, the module unwired.sh is a shim over (#4121, PRD 032.6)."""
import importlib
import os

import pytest


@pytest.fixture
def unwired():
    return importlib.import_module("veri.unwired")


def range_git(fake_processes, added, tracked=()):
    """Answers the git calls of a run: the tree is a work tree, the base resolves, `diff --diff-filter=A` names
    <added>, and `ls-files` lists <tracked> as the files git does not ignore."""
    def answer(line, **kwargs):
        args = list(fake.argvs[-1])
        if args[:3] == ["git", "rev-parse", "--show-toplevel"]:
            return 0, os.getcwd() + "\n", ""
        if args[:2] == ["git", "rev-parse"]:
            return 0, "true\n", ""
        if args[:2] == ["git", "diff"]:
            return 0, "".join(f + "\0" for f in added), ""
        if args[:2] == ["git", "ls-files"]:
            return 0, "".join(f + "\0" for f in tracked), ""
        raise AssertionError("unexpected command: %r" % (args,))

    fake = fake_processes.answers({"git": answer})
    return fake


def write(root, files):
    for name, text in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)


def test_an_added_non_test_file_no_other_non_test_file_names_is_printed_and_exits_1(
        tmp_path, monkeypatch, capsys, unwired, fake_processes):
    tree = {"src/orphan.py": "x = 1\n", "src/used-one.py": "y = 2\n", "src/main.py": "import used_one\n",
            "tests/test_orphan.py": "import orphan\n", ".tdd/issue-7.md": ""}
    write(tmp_path, tree)
    range_git(fake_processes, ["src/orphan.py", "src/used-one.py", "tests/test_orphan.py", ".tdd/issue-7.md"],
              list(tree))
    monkeypatch.chdir(tmp_path)
    assert (unwired.main(["base"]),) + tuple(capsys.readouterr()) == (1, "src/orphan.py\n", "")


def test_every_added_file_named_exits_0_printing_nothing_and_a_range_adding_none_exits_3(
        tmp_path, monkeypatch, capsys, unwired, fake_processes):
    tree = {"src/used.py": "y = 2\n", "src/main.py": "from used import y\n", "tests/test_new.py": "",
            ".tdd/issue-7.md": ""}
    write(tmp_path, tree)
    monkeypatch.chdir(tmp_path)
    results = []
    for added in (["src/used.py", "tests/test_new.py"], ["tests/test_new.py", ".tdd/issue-7.md"]):
        range_git(fake_processes, added, list(tree))
        results.append((unwired.main(["base"]),) + tuple(capsys.readouterr()))
    assert results == [(0, "", ""), (3, "", "")]


def test_added_prose_config_and_data_files_and_github_paths_nothing_names_are_skipped_and_exit_3(
        tmp_path, monkeypatch, capsys, unwired, fake_processes):
    tree = {"README.md": "# scratch\n", ".github/workflows/lint.yml": "on: push\n", "conf.json": "{}\n",
            "src/main.py": "x = 1\n"}
    write(tmp_path, tree)
    range_git(fake_processes, ["README.md", ".github/workflows/lint.yml", "conf.json"], list(tree))
    monkeypatch.chdir(tmp_path)
    assert (unwired.main(["base"]),) + tuple(capsys.readouterr()) == (3, "", "")


def test_an_added_code_file_under_github_nothing_names_is_skipped_and_exits_3(
        tmp_path, monkeypatch, capsys, unwired, fake_processes):
    tree = {".github/scripts/x.py": "y = 1\n", "src/main.py": "z = 1\n"}
    write(tmp_path, tree)
    range_git(fake_processes, [".github/scripts/x.py"], list(tree))
    monkeypatch.chdir(tmp_path)
    assert (unwired.main(["base"]),) + tuple(capsys.readouterr()) == (3, "", "")


def test_accepted_files_are_not_printed_so_a_range_whose_every_unnamed_file_is_accepted_exits_0(
        tmp_path, monkeypatch, capsys, unwired, fake_processes):
    tree = {"pkg/a.go": "package pkg\n", "pkg/b.go": "package pkg\n", "db/0001_init.py": "x = 1\n",
            ".tdd/issue-7-unwired-accepted": "pkg/a.go\ndb/0001_init.py\n"}
    write(tmp_path, tree)
    monkeypatch.chdir(tmp_path)
    accepted = ".tdd/issue-7-unwired-accepted"
    results = []
    for added in (["pkg/a.go", "db/0001_init.py"], ["pkg/a.go", "pkg/b.go", "db/0001_init.py"]):
        range_git(fake_processes, added, list(tree))
        results.append((unwired.main(["--accepted", accepted, "base"]),) + tuple(capsys.readouterr()))
    range_git(fake_processes, ["pkg/a.go"], list(tree))
    results.append((unwired.main(["--accepted", ".tdd/none", "base"]),) + tuple(capsys.readouterr()))
    assert results == [(0, "", ""), (1, "pkg/b.go\n", ""), (1, "pkg/a.go\n", "")]


def test_the_stem_inside_the_added_file_itself_is_no_caller(tmp_path, monkeypatch, capsys, unwired, fake_processes):
    tree = {"src/orphan.py": "def orphan():\n    return orphan\n", "src/main.py": "x = 1\n"}
    write(tmp_path, tree)
    range_git(fake_processes, ["src/orphan.py"], list(tree))
    monkeypatch.chdir(tmp_path)
    assert (unwired.main(["base"]),) + tuple(capsys.readouterr()) == (1, "src/orphan.py\n", "")


def test_a_base_that_does_not_resolve_or_a_directory_that_is_no_work_tree_exits_2_with_one_stderr_line(
        tmp_path, monkeypatch, capsys, unwired, fake_processes):
    monkeypatch.chdir(tmp_path)
    results = []
    for failing in ("--is-inside-work-tree", "--verify"):
        def answer(line, failing=failing, **kwargs):
            if failing in line or not line.startswith("git rev-parse"):
                return 128, "", "fatal: no\n"
            return 0, (str(tmp_path) if "--show-toplevel" in line else "true") + "\n", ""

        fake_processes.answers({"git": answer})
        results.append((unwired.main(["nope"]),) + tuple(capsys.readouterr()))
    assert results == [(2, "", "unwired: not a git work tree\n"), (2, "", "unwired: cannot resolve 'nope'\n")]


def test_a_directory_where_git_answers_false_for_inside_work_tree_exits_2_with_one_stderr_line(
        tmp_path, monkeypatch, capsys, unwired, fake_processes):
    def answer(line, **kwargs):
        if line.startswith("git rev-parse --is-inside-work-tree"):
            return 0, "false\n", ""
        if line.startswith("git rev-parse"):
            return 0, "abc\n", ""
        return 128, "", "fatal: this operation must be run in a work tree\n"

    fake_processes.answers({"git": answer})
    monkeypatch.chdir(tmp_path)
    assert (unwired.main(["base"]),) + tuple(capsys.readouterr()) == (2, "", "unwired: not a git work tree\n")
