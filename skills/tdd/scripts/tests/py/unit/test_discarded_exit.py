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


def test_each_added_bare_call_discarding_an_exit_code_is_printed_as_file_and_new_line_and_exits_1(
        tmp_path, run_cli, discarded_exit, monkeypatch):
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "mod.py").write_text(
        "import os\n"
        "import subprocess\n"
        "import fused\n"
        "x = 1\n"
        "y = 2\n"
        "z = 3\n"
        "subprocess.run([\"a\"])\n"
        "subprocess.call([\"b\"])\n"
        "os.system(\"c\")\n"
        "fused.call(\"git\", \"status\")\n")
    diff = ("diff --git a/pkg/mod.py b/pkg/mod.py\n"
            "index 1111111..2222222 100644\n"
            "--- a/pkg/mod.py\n"
            "+++ b/pkg/mod.py\n"
            "@@ -5,2 +5,6 @@\n"
            " y = 2\n"
            " z = 3\n"
            "+subprocess.run([\"a\"])\n"
            "+subprocess.call([\"b\"])\n"
            "+os.system(\"c\")\n"
            "+fused.call(\"git\", \"status\")\n")
    monkeypatch.setattr(discarded_exit, "_git", lambda *args: (0, diff))

    assert run_cli(discarded_exit, [], cwd=tmp_path) == (
        1, "pkg/mod.py:7\npkg/mod.py:8\npkg/mod.py:9\npkg/mod.py:10\n", "")


def test_an_added_bare_call_to_any_other_function_prints_nothing_and_exits_0(
        tmp_path, run_cli, discarded_exit, monkeypatch):
    (tmp_path / "mod.py").write_text("import os\nprint(\"x\")\nos.getcwd()\n")
    diff = ("diff --git a/mod.py b/mod.py\n"
            "index 1111111..2222222 100644\n"
            "--- a/mod.py\n"
            "+++ b/mod.py\n"
            "@@ -1 +1,3 @@\n"
            " import os\n"
            "+print(\"x\")\n"
            "+os.getcwd()\n")
    monkeypatch.setattr(discarded_exit, "_git", lambda *args: (0, diff))

    assert run_cli(discarded_exit, [], cwd=tmp_path) == (0, "", "")


def test_an_added_fused_call_unpacking_its_exit_code_into_underscore_is_printed_and_exits_1(
        tmp_path, run_cli, discarded_exit, monkeypatch):
    (tmp_path / "mod.py").write_text("import fused\n_, body, _ = fused.call(\"gh\", \"api\", \"x\")\n")
    diff = ("diff --git a/mod.py b/mod.py\n"
            "index 1111111..2222222 100644\n"
            "--- a/mod.py\n"
            "+++ b/mod.py\n"
            "@@ -1 +1,2 @@\n"
            " import fused\n"
            "+_, body, _ = fused.call(\"gh\", \"api\", \"x\")\n")
    monkeypatch.setattr(discarded_exit, "_git", lambda *args: (0, diff))

    assert run_cli(discarded_exit, [], cwd=tmp_path) == (1, "mod.py:2\n", "")


def test_an_added_exit_code_assigned_whole_to_underscore_is_printed_and_exits_1(
        tmp_path, run_cli, discarded_exit, monkeypatch):
    (tmp_path / "mod.py").write_text(
        "import os\nimport subprocess\n_ = subprocess.call([\"x\"])\n_ = os.system(\"x\")\n")
    diff = ("diff --git a/mod.py b/mod.py\n"
            "index 1111111..2222222 100644\n"
            "--- a/mod.py\n"
            "+++ b/mod.py\n"
            "@@ -1,2 +1,4 @@\n"
            " import os\n"
            " import subprocess\n"
            "+_ = subprocess.call([\"x\"])\n"
            "+_ = os.system(\"x\")\n")
    monkeypatch.setattr(discarded_exit, "_git", lambda *args: (0, diff))

    assert run_cli(discarded_exit, [], cwd=tmp_path) == (1, "mod.py:3\nmod.py:4\n", "")


def test_an_added_exit_code_bound_to_a_name_the_function_never_reads_is_printed_and_exits_1(
        tmp_path, run_cli, discarded_exit, monkeypatch):
    (tmp_path / "mod.py").write_text(
        "import os\n"
        "import fused\n"
        "\n"
        "def status():\n"
        "    code, out, err = fused.call(\"git\", \"status\")\n"
        "    return out\n"
        "\n"
        "def run():\n"
        "    rc = os.system(\"x\")\n"
        "    return 0\n")
    diff = ("diff --git a/mod.py b/mod.py\n"
            "index 1111111..2222222 100644\n"
            "--- a/mod.py\n"
            "+++ b/mod.py\n"
            "@@ -1,2 +1,10 @@\n"
            " import os\n"
            " import fused\n"
            "+\n"
            "+def status():\n"
            "+    code, out, err = fused.call(\"git\", \"status\")\n"
            "+    return out\n"
            "+\n"
            "+def run():\n"
            "+    rc = os.system(\"x\")\n"
            "+    return 0\n")
    monkeypatch.setattr(discarded_exit, "_git", lambda *args: (0, diff))

    assert run_cli(discarded_exit, [], cwd=tmp_path) == (1, "mod.py:5\nmod.py:9\n", "")
