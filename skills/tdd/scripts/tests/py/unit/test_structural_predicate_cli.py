"""run_cli cases for veri/structural_predicate.py, the module structural-predicate.sh is a shim over."""
import importlib
import io
import subprocess
import sys
import types

import pytest

USAGE = "usage: structural-predicate.sh <record>\n"


@pytest.fixture
def structural_predicate():
    module = importlib.import_module("veri.structural_predicate")

    def main(argv):
        sys.stdin = io.TextIOWrapper(io.BytesIO(sys.stdin.getvalue().encode("utf-8")))
        return module.main(argv)

    return types.SimpleNamespace(main=main)


def fake_bash(monkeypatch, status):
    ran = []

    def run(args, *rest, **kwargs):
        ran.append(args)
        return types.SimpleNamespace(returncode=status)

    monkeypatch.setattr(subprocess, "run", run)
    return ran


def test_cli_writes_a_predicate_that_fails_on_the_current_tree_to_the_record_and_exits_0(
    monkeypatch, tmp_path, run_cli, structural_predicate
):
    ran = fake_bash(monkeypatch, 1)
    predicate = "test -e lib/shared-opening.md"

    code, out, err = run_cli(
        structural_predicate,
        [str(tmp_path / "predicate")],
        stdin="Read the candidate and the files it names.\nPREDICATE: %s\n" % predicate,
        cwd=tmp_path,
    )

    assert (code, out, err, ran) == (0, "", "", [["bash", "-c", predicate]])
    assert (tmp_path / "predicate").read_text() == predicate + "\n"


def test_cli_exits_1_and_writes_no_record_for_a_predicate_that_already_succeeds(
    monkeypatch, tmp_path, run_cli, structural_predicate
):
    ran = fake_bash(monkeypatch, 0)

    code, out, err = run_cli(
        structural_predicate,
        [str(tmp_path / "predicate")],
        stdin="Read the candidate and the files it names.\nPREDICATE: test -e shared-opening.md\n",
        cwd=tmp_path,
    )

    assert (code, out, err, ran) == (1, "", "", [["bash", "-c", "test -e shared-opening.md"]])
    assert list(tmp_path.iterdir()) == []


def test_cli_exits_3_for_none_and_2_for_a_report_without_a_predicate_line_writing_no_record(
    monkeypatch, tmp_path, run_cli, structural_predicate
):
    ran = fake_bash(monkeypatch, 1)
    record = str(tmp_path / "predicate")

    none = run_cli(
        structural_predicate,
        [record],
        stdin="No command can tell this candidate's transform apart from the tree as it is.\nPREDICATE: NONE\n",
        cwd=tmp_path,
    )
    assert none == (3, "", "")
    assert list(tmp_path.iterdir()) == []

    missing = run_cli(
        structural_predicate,
        [record],
        stdin="Read the candidate and the files it names.\n",
        cwd=tmp_path,
    )
    assert missing[0] == 2
    assert missing[1] == ""
    assert missing[2].count("\n") == 1 and "PREDICATE" in missing[2]
    assert list(tmp_path.iterdir()) == []
    assert ran == []


def test_cli_exits_3_for_none_followed_by_a_why_and_writes_no_record(
    monkeypatch, tmp_path, run_cli, structural_predicate
):
    ran = fake_bash(monkeypatch, 1)

    result = run_cli(
        structural_predicate,
        [str(tmp_path / "predicate")],
        stdin=(
            "Read the candidate and the files it names.\n"
            "PREDICATE: NONE — the transform only renames prose, and no command can tell it apart\n"
        ),
        cwd=tmp_path,
    )

    assert result == (3, "", "")
    assert list(tmp_path.iterdir()) == []
    assert ran == []


def test_cli_with_no_argument_exits_2_with_only_its_usage_line_on_stderr_and_writes_nothing(
    monkeypatch, tmp_path, run_cli, structural_predicate
):
    ran = fake_bash(monkeypatch, 1)

    result = run_cli(structural_predicate, [], stdin="", cwd=tmp_path)

    assert result == (2, "", USAGE)
    assert list(tmp_path.iterdir()) == []
    assert ran == []
