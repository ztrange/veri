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
