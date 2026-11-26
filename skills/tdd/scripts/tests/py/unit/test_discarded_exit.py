"""discarded-exit.sh prints each added .py line of `git diff HEAD` whose exit code is discarded."""
import importlib

import pytest


@pytest.fixture
def discarded_exit():
    return importlib.import_module("veri.discarded_exit")


def test_any_argument_prints_the_usage_line_on_stderr_and_exits_2(run_cli, discarded_exit):
    code, out, err = run_cli(discarded_exit, ["x"])

    assert (code, out) == (2, "")
    assert err.splitlines()[-1] == "usage: discarded-exit.sh"


def test_a_diff_touching_no_py_file_prints_nothing_and_exits_3(run_cli, discarded_exit, monkeypatch):
    diff = ("diff --git a/README.md b/README.md\n"
            "index 1111111..2222222 100644\n"
            "--- a/README.md\n"
            "+++ b/README.md\n"
            "@@ -1 +1,2 @@\n"
            " # Title\n"
            "+subprocess.call([\"x\"])\n")
    monkeypatch.setattr(discarded_exit, "_git", lambda *args: (0, diff))

    assert run_cli(discarded_exit, []) == (3, "", "")
