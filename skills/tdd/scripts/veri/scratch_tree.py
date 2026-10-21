"""A pytest plugin the launcher loads: one committed git scratch tree prepared per session, and a per-case copy of it."""
import pathlib
import shutil
import subprocess

import pytest

REAL_RUN = subprocess.run
IDENTITY = ["-c", "user.name=scratch", "-c", "user.email=scratch@example.invalid", "-c", "commit.gpgsign=false"]


@pytest.fixture(scope="session")
def scratch_tree(tmp_path_factory):
    tree = tmp_path_factory.mktemp("scratch-tree")
    (tree / "README.md").write_text("scratch\n")
    for args in (["init", "-q"], ["add", "."], [*IDENTITY, "commit", "-q", "-m", "prepared"]):
        REAL_RUN(["git", "-C", str(tree), *args], check=True, capture_output=True)
    return tree


@pytest.fixture
def scratch_copy(scratch_tree, tmp_path_factory):
    def copy():
        return pathlib.Path(shutil.copytree(scratch_tree, tmp_path_factory.mktemp("scratch-copy") / "repo",
                                            copy_function=shutil.copyfile))
    return copy
