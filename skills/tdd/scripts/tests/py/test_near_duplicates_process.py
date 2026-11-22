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


@pytest.mark.process("git over a scratch repository whose commit added a copy of a function in a file it did not touch")
def test_an_older_copy_in_a_file_the_commit_did_not_touch_is_not_reported(tmp_path, near_duplicates, run_cli):
    repo = new_repo(tmp_path / "untouched")
    commit_all(repo, "feat: total", **{"src__calc.py": TOTAL})
    added = commit_all(repo, "feat: weight", **{"src__parcels.py": WEIGHT.lstrip()})
    assert run_cli(near_duplicates, [added], cwd=repo)[1] == ""


@pytest.mark.process("git over a scratch repository whose commit added an unrelated line to a file already holding two copies")
def test_a_pair_neither_side_of_which_holds_an_added_line_is_never_printed(tmp_path, near_duplicates, run_cli):
    repo = new_repo(tmp_path / "old-pair")
    commit_all(repo, "feat: total and weight", **{"src__calc.py": TOTAL + WEIGHT})
    added = commit_all(repo, "feat: tax", **{"src__calc.py": TOTAL + WEIGHT + "\nTAX = 2\n"})
    assert run_cli(near_duplicates, [added], cwd=repo)[1] == ""


@pytest.mark.process("git over a scratch repository whose commit added a copy matching on two counting lines and many brace-only and blank ones")
def test_a_run_of_fewer_than_3_counting_lines_prints_nothing_however_many_brace_only_or_blank_lines_it_spans(
        tmp_path, near_duplicates, run_cli):
    older = "function total(items) {\n  {\n  }\n\n  return items;\n}\n"
    copy = "\nfunction weight(parcels) {\n    {\n    }\n\n    return parcels;\n}\n"
    repo = new_repo(tmp_path / "braces")
    commit_all(repo, "feat: total", **{"src__calc.js": older})
    added = commit_all(repo, "feat: weight", **{"src__calc.js": older + copy})
    assert run_cli(near_duplicates, [added], cwd=repo)[1] == ""


@pytest.mark.process("git over a scratch repository whose commit added a 6-line copy of an older function")
def test_one_maximal_6_line_repeat_prints_one_line_not_one_per_3_line_window(tmp_path, near_duplicates, run_cli):
    older = TOTAL.replace("    return sum_\n", "    sum_ = round(sum_)\n    return sum_\n")
    copy = "\ndef weight(parcels):\n  acc = 0\n  for parcel in parcels:\n    acc += parcel.mass\n  acc = round(acc)\n  return acc\n"
    repo = new_repo(tmp_path / "maximal")
    commit_all(repo, "feat: total", **{"src__calc.py": older})
    added = commit_all(repo, "feat: weight", **{"src__calc.py": older + copy})
    assert run_cli(near_duplicates, [added], cwd=repo) == (0, "src/calc.py:8-13 src/calc.py:1-6\n", "")


@pytest.mark.process("git over a scratch repository whose commit added a copy, in one test file, of a function in another test file")
def test_a_repeat_between_two_test_files_is_never_paired(tmp_path, near_duplicates, run_cli):
    repo = new_repo(tmp_path / "test-files")
    commit_all(repo, "test: total", **{"tests__test_calc.py": TOTAL})
    added = commit_all(repo, "test: weight", **{
        "tests__test_calc.py": TOTAL + "\nTAX = 2\n", "tests__test_parcels.py": WEIGHT.lstrip()})
    assert run_cli(near_duplicates, [added], cwd=repo)[1] == ""


@pytest.mark.process("git over a scratch repository whose commit added a line repeating nothing")
def test_no_pair_exits_3_printing_nothing(tmp_path, near_duplicates, run_cli):
    repo = new_repo(tmp_path / "no-pair")
    commit_all(repo, "feat: total", **{"src__calc.py": TOTAL})
    added = commit_all(repo, "feat: tax", **{"src__calc.py": TOTAL + "\nTAX = 2\n"})
    assert run_cli(near_duplicates, [added], cwd=repo) == (3, "", "")
