"""In-process cases for veri/git.py, the git runner and symref parser veri's modules share."""
import importlib

import pytest

SHA = "1111111111111111111111111111111111111111"


@pytest.fixture
def git():
    return importlib.import_module("veri.git")


def test_symref_default_names_the_branch_a_symref_line_points_at(git):
    assert git.symref_default(f"ref: refs/heads/trunk\tHEAD\n{SHA}\tHEAD\n") == "trunk"


def test_symref_default_is_none_for_a_sha_line_alone(git):
    assert git.symref_default(f"{SHA}\tHEAD\n") is None


def test_symref_default_is_none_for_an_empty_answer(git):
    assert git.symref_default("") is None


def test_symref_default_is_none_for_an_empty_name(git):
    assert git.symref_default(f"ref: refs/heads/\tHEAD\n{SHA}\tHEAD\n") is None


def test_symref_default_is_none_without_whitespace_before_head(git):
    assert git.symref_default(f"ref: refs/heads/trunkHEAD\n{SHA}\tHEAD\n") is None


def test_symref_default_takes_the_first_of_two_symref_lines(git):
    answer = f"ref: refs/heads/trunk\tHEAD\nref: refs/heads/dev\tHEAD\n{SHA}\tHEAD\n"
    assert git.symref_default(answer) == "trunk"


def test_symref_default_is_none_when_head_is_on_the_next_line(git):
    assert git.symref_default(f"ref: refs/heads/trunk\nHEAD\n{SHA}\tHEAD\n") is None
