"""In-process cases for veri/near_duplicates.py, the module near-duplicates.sh is a shim over."""
import importlib

import pytest

from repo_builder import commit_all, new_repo

TOTAL = """def total(items):
    sum_ = 0
    for item in items:
        sum_ += item.price
    return sum_
"""

WEIGHT = """
class Parcels:
    def weight(self):
        acc = 0
        for parcel in self:
            acc += parcel.mass
        return acc
"""


@pytest.fixture
def near_duplicates():
    return importlib.import_module("veri.near_duplicates")


@pytest.mark.process("git over a scratch repository whose commit added a renamed, reindented copy of an older function")
def test_an_added_function_repeating_an_older_one_in_the_same_file_prints_the_pair_added_block_first(
        tmp_path, near_duplicates, run_cli):
    repo = new_repo(tmp_path / "same-file")
    commit_all(repo, "feat: total", **{"src__calc.py": TOTAL})
    added = commit_all(repo, "feat: weight", **{"src__calc.py": TOTAL + WEIGHT})
    assert run_cli(near_duplicates, [added], cwd=repo) == (0, "src/calc.py:8-12 src/calc.py:1-5\n", "")


@pytest.mark.process("git over a scratch repository whose commit added a copy, in one file, of a function in another file it touched")
def test_an_added_function_repeating_one_in_another_touched_file_prints_the_pair_across_the_files(
        tmp_path, near_duplicates, run_cli):
    repo = new_repo(tmp_path / "two-files")
    commit_all(repo, "feat: total", **{"src__calc.py": TOTAL})
    added = commit_all(repo, "feat: weight", **{"src__calc.py": TOTAL + "\nTAX = 2\n", "src__parcels.py": WEIGHT.lstrip()})
    assert run_cli(near_duplicates, [added], cwd=repo) == (0, "src/parcels.py:2-6 src/calc.py:1-5\n", "")
