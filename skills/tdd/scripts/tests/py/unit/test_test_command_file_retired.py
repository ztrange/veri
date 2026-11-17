"""PRD 016.3b: `.veri/test-command` is no longer a declaration (TF1), and no tracked file still names it (TF6).

This file holds the cases proving TF1, so it is the one file outside specs/ and .tdd/ the TF6 guard lets name the path.
"""
import importlib

import pytest

RETIRED = ".veri/test-command"


@pytest.fixture
def detect():
    return importlib.import_module("veri.detect_test_command")


def planted(root, **files):
    """<root> holding a `.veri/test-command` and <files> (the name's `__` is a `/`)."""
    (root / ".veri").mkdir(parents=True)
    (root / RETIRED).write_text("bin/run-suite --all --strict\n")
    for name, text in files.items():
        (root / name.replace("__", "/")).write_text(text)
    return str(root)


@pytest.mark.parametrize("tier", ["fast", "all"])
def test_a_repo_declaring_only_the_retired_file_gets_what_inference_finds_or_exit_3_with_nothing(tmp_path, run_cli, detect, tier):
    made = planted(tmp_path / "made", Makefile="test:\n\techo hi\n")
    bare = planted(tmp_path / "bare")

    assert (run_cli(detect, ["--tier", tier, made]), run_cli(detect, ["--tier", tier, bare])) == (
        (0, "make test\n", ""), (3, "", ""))
