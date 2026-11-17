"""unwired.sh run as a process in a scratch git repo that is not veri's own tree (#4121, PRD 032.6 WN6)."""
import importlib
import subprocess

import pytest

from conftest import SCRIPTS
from repo_builder import commit_all, new_repo


def write(root, files):
    for name, text in files.items():
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text(text)


@pytest.mark.process("the unwired.sh shim over real git in a scratch foreign repo")
def test_in_a_foreign_repo_only_the_added_file_nothing_names_is_printed_and_exits_1(tmp_path):
    repo = new_repo(tmp_path / "repo")
    write(repo, {"src/main.py": "def main():\n    return 0\n"})
    base = commit_all(repo, "base")
    write(repo, {"src/orphan.py": "def orphan():\n    return orphan\n", "src/used.py": "def used():\n    return 2\n",
                 "src/main.py": "from used import used\n\n\ndef main():\n    return used()\n"})
    commit_all(repo, "add two files")
    done = subprocess.run(["/bin/sh", str(SCRIPTS / "unwired.sh"), base], cwd=repo,
                          capture_output=True, text=True, stdin=subprocess.DEVNULL)
    assert (done.returncode, done.stdout, done.stderr) == (1, "src/orphan.py\n", "")


@pytest.mark.process("the unwired.sh shim over real git: a bail's pending record, a resume before and after the release")
def test_an_unreleased_resume_bails_again_and_a_released_one_goes_on_until_a_file_not_recorded_is_added(tmp_path):
    repo = new_repo(tmp_path / "repo")
    write(repo, {"pkg/main.go": "package pkg\n"})
    base = commit_all(repo, "base")
    write(repo, {"pkg/helper.go": "package pkg\n"})
    commit_all(repo, "a file found by package discovery")
    (repo / ".tdd").mkdir()
    pending = repo / ".tdd" / "issue-7-unwired-pending"
    accepted = repo / ".tdd" / "issue-7-unwired-accepted"

    def unwired():
        done = subprocess.run(["/bin/sh", str(SCRIPTS / "unwired.sh"), "--accepted", str(accepted), base], cwd=repo,
                              capture_output=True, text=True, stdin=subprocess.DEVNULL)
        return done.returncode, done.stdout, done.stderr

    def bail(printed):
        with open(pending, "a") as kept:
            kept.write(printed)

    bailed = unwired()
    bail(bailed[1])
    unreleased = unwired()
    importlib.import_module("veri.release_issue").accept_unwired(str(repo), "7")
    released = unwired()
    write(repo, {"pkg/other.go": "package pkg\n"})
    commit_all(repo, "another")
    assert [bailed, unreleased, released, unwired()] == [
        (1, "pkg/helper.go\n", ""), (1, "pkg/helper.go\n", ""), (0, "", ""), (1, "pkg/other.go\n", "")]



@pytest.mark.process("the unwired.sh shim over real git, run from a subdirectory of a scratch repo")
def test_run_from_a_subdirectory_it_reads_repo_root_paths_and_prints_the_same_answer(tmp_path):
    repo = new_repo(tmp_path / "repo")
    write(repo, {"src/main.py": "def main():\n    return 0\n"})
    base = commit_all(repo, "base")
    write(repo, {"src/orphan.py": "def orphan():\n    return orphan\n", "src/used.py": "def used():\n    return 2\n",
                 "src/main.py": "from used import used\n\n\ndef main():\n    return used()\n"})
    commit_all(repo, "add two files")
    done = subprocess.run(["/bin/sh", str(SCRIPTS / "unwired.sh"), base], cwd=repo / "src",
                          capture_output=True, text=True, stdin=subprocess.DEVNULL)
    assert (done.returncode, done.stdout, done.stderr) == (1, "src/orphan.py\n", "")
