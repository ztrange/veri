"""unwired.sh run as a process in a scratch git repo that is not veri's own tree (#4121, PRD 032.6 WN6)."""
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


@pytest.mark.process("the unwired.sh shim over real git: a bail's record, then the resumed run's call")
def test_files_a_bail_recorded_go_on_after_the_resume_and_a_file_not_recorded_bails_again(tmp_path):
    repo = new_repo(tmp_path / "repo")
    write(repo, {"pkg/main.go": "package pkg\n"})
    base = commit_all(repo, "base")
    write(repo, {"pkg/helper.go": "package pkg\n"})
    commit_all(repo, "a file found by package discovery")
    record = repo / ".tdd" / "issue-7-unwired-accepted"
    record.parent.mkdir()

    def unwired():
        done = subprocess.run(["/bin/sh", str(SCRIPTS / "unwired.sh"), "--accepted", str(record), base], cwd=repo,
                              capture_output=True, text=True, stdin=subprocess.DEVNULL)
        return done.returncode, done.stdout, done.stderr

    bailed = unwired()
    with open(record, "a") as kept:
        kept.write(bailed[1])
    resumed = unwired()
    write(repo, {"pkg/other.go": "package pkg\n"})
    commit_all(repo, "another")
    assert [bailed, resumed, unwired()] == [(1, "pkg/helper.go\n", ""), (0, "", ""), (1, "pkg/other.go\n", "")]


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
