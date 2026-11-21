"""coupling.sh run as a process in a scratch git repo that is not veri's own tree (#4124, PRD 032.8 CU5)."""
import subprocess

import pytest

from conftest import SCRIPTS
from repo_builder import commit_all, new_repo


@pytest.mark.process("the coupling.sh shim over real git in a scratch foreign repo")
def test_in_a_foreign_repo_only_the_pair_importing_each_other_is_printed(tmp_path):
    repo = new_repo(tmp_path / "repo")
    (repo / "README.md").write_text("scratch\n")
    base = commit_all(repo, "base")
    for name, text in {"a.py": "import b\n", "b.py": "import a\n", "c.py": "import a\n"}.items():
        (repo / name).write_text(text)
    commit_all(repo, "three files")
    done = subprocess.run(["/bin/sh", str(SCRIPTS / "coupling.sh"), base], cwd=repo,
                          capture_output=True, text=True, stdin=subprocess.DEVNULL)
    assert (done.returncode, done.stdout, done.stderr) == (0, "mutual: a.py b.py\n", "")


@pytest.mark.process("the coupling.sh shim over real git, run from a subdirectory of a scratch repo")
def test_run_from_a_subdirectory_it_prints_repo_root_paths(tmp_path):
    repo = new_repo(tmp_path / "repo")
    (repo / "src").mkdir()
    (repo / "README.md").write_text("scratch\n")
    base = commit_all(repo, "base")
    for name, text in {"src/a.py": "import b\n", "src/b.py": "import a\n"}.items():
        (repo / name).write_text(text)
    commit_all(repo, "two files")
    done = subprocess.run(["/bin/sh", str(SCRIPTS / "coupling.sh"), base], cwd=repo / "src",
                          capture_output=True, text=True, stdin=subprocess.DEVNULL)
    assert (done.returncode, done.stdout, done.stderr) == (0, "mutual: src/a.py src/b.py\n", "")
