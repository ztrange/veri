"""In-process cases for veri/affected_suites.py outside veri's own tree: a working tree with no
skills/tdd/scripts/tests/py directory selects by the repo's own test files (#4105)."""
import importlib
import subprocess

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
