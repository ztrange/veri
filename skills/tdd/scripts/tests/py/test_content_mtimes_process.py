"""Cases for veri/content_mtimes.py that run real git over scratch repositories."""
import importlib
import os
import subprocess

import pytest

FILES = {"a.py": "x = 1\n", "pkg/b.py": "y = 2\n", "notes.txt": "plain\n"}


@pytest.fixture
def content_mtimes():
    return importlib.import_module("veri.content_mtimes")


def repository(root, files, mtime):
    """A git working tree at <root> tracking <files>, every one's mtime set to <mtime>."""
    for name, text in files.items():
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text(text)
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    for name in files:
        os.utime(root / name, (mtime, mtime))


def mtimes(root, files):
    return {name: os.stat(root / name).st_mtime for name in files}


@pytest.mark.process("git init and git add run for real in two scratch repositories, then content_mtimes in each")
def test_two_working_trees_holding_the_same_content_get_equal_mtimes_per_file_and_a_file_changed_in_one_a_different_one_3922(
        content_mtimes, run_cli, tmp_path):
    one, other = tmp_path / "one", tmp_path / "other"
    repository(one, FILES, 1600000000)
    repository(other, dict(FILES, **{"pkg/b.py": "y = 3\n"}), 1700000000)

    answers = [run_cli(content_mtimes, [], cwd=root) for root in (one, other)]
    stamped = (mtimes(one, FILES), mtimes(other, FILES))

    assert (answers, [name for name in FILES if stamped[0][name] == stamped[1][name]],
            stamped[0]["pkg/b.py"] != stamped[1]["pkg/b.py"]) == ([(0, "", "")] * 2, ["a.py", "notes.txt"], True)
