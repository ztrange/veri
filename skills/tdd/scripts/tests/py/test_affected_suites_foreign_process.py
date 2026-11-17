"""affected-suites.sh run as a process in a scratch git repo that is not veri's own tree (#4105, PRD 031.4 LG30)."""
import subprocess

import pytest

from conftest import SCRIPTS
from repo_builder import commit_all, git, new_repo

CLAUDE_MD = ("veri: fast tests: `python3 -m pytest -q tests`\n"
             "veri: all tests: `python3 -m pytest -q tests`\n"
             "veri: one test file: `python3 -m pytest -q \"$1\"`\n")


def write(root, files):
    for name, text in files.items():
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text(text)


@pytest.mark.process("the affected-suites.sh shim over real git, which quotes a non-ASCII path")
def test_in_a_foreign_repo_a_changed_non_ascii_source_and_test_are_read_unquoted(tmp_path):
    repo = new_repo(tmp_path / "repo")
    write(repo, {"CLAUDE.md": CLAUDE_MD, "src/naïve.py": "x = 1\n", "tests/test_café.py": "import naïve\n",
                 "tests/test_other.py": ""})
    commit_all(repo, "base")
    write(repo, {"src/naïve.py": "x = 2\n", "tests/test_café.py": "import naïve\n# edited\n"})
    done = subprocess.run(["/bin/sh", str(SCRIPTS / "affected-suites.sh"), "HEAD"], cwd=repo,
                          capture_output=True, stdin=subprocess.DEVNULL)
    assert (done.returncode, done.stdout.decode(), done.stderr.decode()) == (0, "tests/test_café.py\n", "")


@pytest.mark.process("the affected-suites.sh shim over real git in a scratch foreign repo")
def test_in_a_foreign_repo_a_test_selects_itself_a_source_selects_the_tests_naming_it_and_an_unnamed_one_widens(
        tmp_path):
    repo = new_repo(tmp_path / "repo")
    write(repo, {"CLAUDE.md": CLAUDE_MD, "src/foo.py": "def foo():\n    return 1\n",
                 "src/bar.py": "def bar():\n    return 2\n",
                 "tests/test_foo.py": "from src.foo import foo\n\n\ndef test_foo():\n    assert foo() == 1\n",
                 "tests/test_other.py": "def test_other():\n    assert True\n"})
    commit_all(repo, "base")

    def affected(edits):
        write(repo, edits)
        done = subprocess.run(["/bin/sh", str(SCRIPTS / "affected-suites.sh"), "HEAD"], cwd=repo,
                              capture_output=True, text=True, stdin=subprocess.DEVNULL)
        git(repo, "checkout", "--", ".")
        return done.returncode, done.stdout, done.stderr

    assert [affected({"tests/test_foo.py": "def test_foo():\n    assert 1\n"}),
            affected({"src/foo.py": "def foo():\n    return 3\n"}),
            affected({"src/bar.py": "def bar():\n    return 4\n"})] == [
        (0, "tests/test_foo.py\n", ""),
        (0, "tests/test_foo.py\n", ""),
        (0, "tests/test_foo.py\ntests/test_other.py\n",
         "affected-suites: no test names src/bar.py; widening to every test file\n")]
