"""In-process cases for veri/affected_suites.py outside veri's own tree: a working tree with no
skills/tdd/scripts/tests/py directory selects by the repo's own test files (#4105)."""
import importlib

import pytest


@pytest.fixture
def affected():
    return importlib.import_module("veri.affected_suites")


def foreign_git(fake_processes, touched, tracked=()):
    """Answers the git calls of a foreign-tree run: the range resolves, `diff --name-only` names <touched>, and
    `ls-files` lists <tracked> as the files git does not ignore."""
    def answer(line, **kwargs):
        args = fake.argvs[-1]
        if list(args[:2]) == ["git", "rev-parse"]:
            return 0, "abc\n", ""
        if list(args[:3]) == ["git", "cat-file", "-t"]:
            return 128, b"", b"fatal: not a valid object name\n"
        if list(args[:3]) == ["git", "diff", "--name-only"]:
            return 0, "".join(f + "\n" for f in touched), ""
        if list(args[:2]) == ["git", "ls-files"]:
            return 0, "".join(f + "\0" for f in tracked), ""
        raise AssertionError("unexpected command: %r" % (args,))

    fake = fake_processes.answers({"git": answer})
    return fake


def write(root, files):
    for name, text in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)


def test_a_changed_test_file_that_exists_selects_itself_and_a_deleted_one_selects_nothing(
        tmp_path, monkeypatch, capsys, affected, fake_processes):
    write(tmp_path, {"tests/test_foo.py": "def test_x(): pass\n", "src/app.test.js": "it('x', () => {})\n"})
    foreign_git(fake_processes, ["tests/test_foo.py", "src/app.test.js", "tests/test_gone.py"],
                ["tests/test_foo.py", "src/app.test.js"])
    monkeypatch.chdir(tmp_path)
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0, "src/app.test.js\ntests/test_foo.py\n", "")


def test_a_changed_source_file_selects_the_test_files_git_does_not_ignore_naming_its_stem_as_a_whole_word(
        tmp_path, monkeypatch, capsys, affected, fake_processes):
    named = "import foo_bar\n"
    write(tmp_path, {"src/foo-bar.py": "x = 1\n",
                     "tests/test_uses.py": named,
                     "src/widget.test.js": "require('./foo-bar')\n",
                     "tests/test_longer.py": "import foo_barbaz\n",
                     "tests/test_ignored.py": named,
                     "node_modules/pkg/tests/test_vendored.py": named,
                     ".venv/lib/tests/test_venv.py": named,
                     ".tdd/tests/test_state.py": named})
    foreign_git(fake_processes, ["src/foo-bar.py"],
                ["src/foo-bar.py", "tests/test_uses.py", "src/widget.test.js", "tests/test_longer.py",
                 "node_modules/pkg/tests/test_vendored.py", ".venv/lib/tests/test_venv.py", ".tdd/tests/test_state.py"])
    monkeypatch.chdir(tmp_path)
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0, "src/widget.test.js\ntests/test_uses.py\n", "")


def test_a_test_file_holding_the_changed_files_stem_only_in_a_comment_or_a_string_is_still_selected_4556(
        tmp_path, monkeypatch, capsys, affected, fake_processes):
    write(tmp_path, {"src/revise.py": "x = 1\n",
                     "tests/test_comment.py": "# the revise phase\n",
                     "tests/test_string.py": 'PHASE = "revise"\n'})
    foreign_git(fake_processes, ["src/revise.py"], ["src/revise.py", "tests/test_comment.py", "tests/test_string.py"])
    monkeypatch.chdir(tmp_path)
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0, "tests/test_comment.py\ntests/test_string.py\n", "")


def test_a_range_changing_only_run_state_under_tdd_exits_3_even_when_a_test_names_its_stem(
        tmp_path, monkeypatch, capsys, affected, fake_processes):
    write(tmp_path, {".tdd/issue-7.md": "- [ ] step\n", ".tdd/test_state.py": "",
                     "tests/test_notes.py": "issue_7 = 1\n"})
    foreign_git(fake_processes, [".tdd/issue-7.md", ".tdd/test_state.py"], ["tests/test_notes.py"])
    monkeypatch.chdir(tmp_path)
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (3, "", "")


def test_the_walk_prints_only_files_that_are_themselves_test_files_and_an_unnamed_source_adds_none_of_them(
        tmp_path, monkeypatch, capsys, affected, fake_processes):
    named = "foo = 1\n"
    tree = {"src/foo.py": "", "src/bar.py": "", "tests/test_uses.py": named, "tests/conftest.py": named,
            "tests/fixtures/d.json": '{"foo": 1}\n', "web/__snapshots__/x.test.js.snap": "exports[`foo`] = 1\n",
            "web/x.test.js": named, "pkg/foo_test.go": named}
    write(tmp_path, tree)
    monkeypatch.chdir(tmp_path)
    foreign_git(fake_processes, ["src/foo.py"], list(tree))
    walked = (affected.main(["base..head"]),) + tuple(capsys.readouterr())
    foreign_git(fake_processes, ["src/bar.py"], list(tree))
    unnamed = (affected.main(["base..head"]),) + tuple(capsys.readouterr())
    tests = "pkg/foo_test.go\ntests/test_uses.py\nweb/x.test.js\n"
    assert (walked, unnamed) == (
        (0, tests, ""),
        (3, "", "affected-suites: no test names src/bar.py; no test file covers them, so the full suite at the PR runs them\n"))


def test_a_changed_path_git_quotes_for_its_non_ascii_bytes_is_read_unquoted(
        tmp_path, monkeypatch, capsys, affected, fake_processes):
    tree = {"tests/test_café.py": "", "src/naïve.py": "", "tests/test_uses.py": "import naïve\n",
            "tests/test_other.py": ""}
    write(tmp_path, tree)
    monkeypatch.chdir(tmp_path)
    foreign_git(fake_processes, ['"tests/test_caf\\303\\251.py"', '"src/na\\303\\257ve.py"'], list(tree))
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (
        0, "tests/test_café.py\ntests/test_uses.py\n", "")


def test_a_failed_tree_listing_is_no_answer_exit_2_never_a_selection(tmp_path, run_cli, affected, fake_processes):
    write(tmp_path, {"src/foo.py": "", "tests/test_foo.py": "import foo\n"})

    def answer(line, **kwargs):
        args = fake.argvs[-1]
        if list(args[:2]) == ["git", "rev-parse"]:
            return 0, "abc\n", ""
        if list(args[:3]) == ["git", "diff", "--name-only"]:
            return 0, "src/foo.py\n", ""
        if list(args[:2]) == ["git", "ls-files"]:
            return 128, "", "fatal: index file corrupt\n"
        if list(args[:3]) == ["git", "cat-file", "-t"]:
            return 128, b"", b"fatal: not a valid object name\n"
        raise AssertionError("unexpected command: %r" % (args,))

    fake = fake_processes.answers({"git": answer})
    code, out, err = run_cli(affected, ["base..head"], cwd=tmp_path)
    assert (code, out, "ls-files" in err, err.count("\n")) == (2, "", True, 1)


def test_a_repo_whose_tests_no_file_name_rule_knows_falls_back_to_every_path_under_its_tests_rather_than_to_none(
        tmp_path, monkeypatch, capsys, affected, fake_processes):
    tree = {"lib/foo.rb": "", "tests/foo_spec.rb": "require 'foo'\n", "tests/bar_spec.rb": ""}
    write(tmp_path, tree)
    monkeypatch.chdir(tmp_path)
    foreign_git(fake_processes, ["lib/foo.rb"], list(tree))
    assert (affected.main(["base..head"]),) + tuple(capsys.readouterr()) == (0, "tests/foo_spec.rb\n", "")


def test_a_named_source_plus_unnamed_ones_prints_only_the_named_sources_test_files_and_with_none_exits_3_saying_so_4333(
        tmp_path, monkeypatch, capsys, affected, fake_processes):
    write(tmp_path, {"src/foo.py": "", "src/bar.py": "", "src/baz.py": "", "tests/test_baz.py": "import baz\n",
                     "tests/test_other.py": "", "web/a.spec.ts": "", "tests/test_ignored.py": ""})
    foreign_git(fake_processes, ["src/foo.py", "src/bar.py", "src/baz.py"],
                ["src/foo.py", "src/bar.py", "src/baz.py", "tests/test_baz.py", "tests/test_other.py", "web/a.spec.ts"])
    monkeypatch.chdir(tmp_path)
    named = (affected.main(["base..head"]),) + tuple(capsys.readouterr())
    empty = tmp_path / "empty"
    write(empty, {"src/foo.py": ""})
    foreign_git(fake_processes, ["src/foo.py"], ["src/foo.py"])
    monkeypatch.chdir(empty)
    none = (affected.main(["base..head"]),) + tuple(capsys.readouterr())
    line = "affected-suites: no test names %s; no test file covers them, so the full suite at the PR runs them\n"
    assert (named, none) == (
        (0, "tests/test_baz.py\n", line % "src/foo.py,src/bar.py"),
        (3, "", line % "src/foo.py"))
