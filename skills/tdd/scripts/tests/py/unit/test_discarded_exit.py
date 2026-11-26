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
    monkeypatch.setattr(discarded_exit, "_head_diff", lambda *args: (0, diff))

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
    monkeypatch.setattr(discarded_exit, "_head_diff", lambda *args: (0, diff))

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
    monkeypatch.setattr(discarded_exit, "_head_diff", lambda *args: (0, diff))

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
    monkeypatch.setattr(discarded_exit, "_head_diff", lambda *args: (0, diff))

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
    monkeypatch.setattr(discarded_exit, "_head_diff", lambda *args: (0, diff))

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
    monkeypatch.setattr(discarded_exit, "_head_diff", lambda *args: (0, diff))

    assert run_cli(discarded_exit, [], cwd=tmp_path) == (1, "mod.py:5\nmod.py:9\n", "")


def test_an_added_fused_call_whose_exit_code_the_function_reads_prints_nothing_and_exits_0(
        tmp_path, run_cli, discarded_exit, monkeypatch):
    (tmp_path / "mod.py").write_text(
        "import fused\n"
        "\n"
        "def fetch():\n"
        "    read, body, _ = fused.call(\"gh\", \"api\", \"x\")\n"
        "    if read:\n"
        "        return None\n"
        "    return body\n")
    diff = ("diff --git a/mod.py b/mod.py\n"
            "index 1111111..2222222 100644\n"
            "--- a/mod.py\n"
            "+++ b/mod.py\n"
            "@@ -1 +1,7 @@\n"
            " import fused\n"
            "+\n"
            "+def fetch():\n"
            "+    read, body, _ = fused.call(\"gh\", \"api\", \"x\")\n"
            "+    if read:\n"
            "+        return None\n"
            "+    return body\n")
    monkeypatch.setattr(discarded_exit, "_head_diff", lambda *args: (0, diff))

    assert run_cli(discarded_exit, [], cwd=tmp_path) == (0, "", "")


def test_an_added_subprocess_run_bound_whole_whose_returncode_is_never_read_is_printed_and_exits_1(
        tmp_path, run_cli, discarded_exit, monkeypatch):
    (tmp_path / "mod.py").write_text(
        "import subprocess\n"
        "\n"
        "def output():\n"
        "    proc = subprocess.run([\"x\"], capture_output=True, text=True)\n"
        "    return proc.stdout\n")
    diff = ("diff --git a/mod.py b/mod.py\n"
            "index 1111111..2222222 100644\n"
            "--- a/mod.py\n"
            "+++ b/mod.py\n"
            "@@ -1 +1,5 @@\n"
            " import subprocess\n"
            "+\n"
            "+def output():\n"
            "+    proc = subprocess.run([\"x\"], capture_output=True, text=True)\n"
            "+    return proc.stdout\n")
    monkeypatch.setattr(discarded_exit, "_head_diff", lambda *args: (0, diff))

    assert run_cli(discarded_exit, [], cwd=tmp_path) == (1, "mod.py:4\n", "")


def test_an_added_subprocess_run_with_check_true_whose_returncode_is_never_read_prints_nothing_and_exits_0(
        tmp_path, run_cli, discarded_exit, monkeypatch):
    (tmp_path / "mod.py").write_text(
        "import subprocess\n"
        "\n"
        "def output():\n"
        "    proc = subprocess.run([\"x\"], check=True)\n"
        "    return proc.stdout\n")
    diff = ("diff --git a/mod.py b/mod.py\n"
            "index 1111111..2222222 100644\n"
            "--- a/mod.py\n"
            "+++ b/mod.py\n"
            "@@ -1 +1,5 @@\n"
            " import subprocess\n"
            "+\n"
            "+def output():\n"
            "+    proc = subprocess.run([\"x\"], check=True)\n"
            "+    return proc.stdout\n")
    monkeypatch.setattr(discarded_exit, "_head_diff", lambda *args: (0, diff))

    assert run_cli(discarded_exit, [], cwd=tmp_path) == (0, "", "")


def test_an_added_subprocess_run_whose_returncode_the_function_reads_prints_nothing_and_exits_0(
        tmp_path, run_cli, discarded_exit, monkeypatch):
    (tmp_path / "mod.py").write_text(
        "import subprocess\n"
        "\n"
        "def output():\n"
        "    proc = subprocess.run([\"x\"])\n"
        "    if proc.returncode:\n"
        "        return None\n"
        "    return proc.stdout\n")
    diff = ("diff --git a/mod.py b/mod.py\n"
            "index 1111111..2222222 100644\n"
            "--- a/mod.py\n"
            "+++ b/mod.py\n"
            "@@ -1 +1,7 @@\n"
            " import subprocess\n"
            "+\n"
            "+def output():\n"
            "+    proc = subprocess.run([\"x\"])\n"
            "+    if proc.returncode:\n"
            "+        return None\n"
            "+    return proc.stdout\n")
    monkeypatch.setattr(discarded_exit, "_head_diff", lambda *args: (0, diff))

    assert run_cli(discarded_exit, [], cwd=tmp_path) == (0, "", "")


def test_an_added_subprocess_run_never_bound_whole_is_printed_and_exits_1(
        tmp_path, run_cli, discarded_exit, monkeypatch):
    (tmp_path / "mod.py").write_text(
        "import subprocess\n"
        "\n"
        "def output():\n"
        "    out = subprocess.run([\"x\"]).stdout\n"
        "    return out\n")
    diff = ("diff --git a/mod.py b/mod.py\n"
            "index 1111111..2222222 100644\n"
            "--- a/mod.py\n"
            "+++ b/mod.py\n"
            "@@ -1 +1,5 @@\n"
            " import subprocess\n"
            "+\n"
            "+def output():\n"
            "+    out = subprocess.run([\"x\"]).stdout\n"
            "+    return out\n")
    monkeypatch.setattr(discarded_exit, "_head_diff", lambda *args: (0, diff))

    assert run_cli(discarded_exit, [], cwd=tmp_path) == (1, "mod.py:4\n", "")


def test_an_added_subprocess_run_with_check_true_bare_or_assigned_to_underscore_prints_nothing_and_exits_0(
        tmp_path, run_cli, discarded_exit, monkeypatch):
    (tmp_path / "mod.py").write_text(
        "import subprocess\n"
        "\n"
        "def build():\n"
        "    subprocess.run([\"x\"], check=True)\n"
        "    _ = subprocess.run([\"x\"], check=True)\n")
    diff = ("diff --git a/mod.py b/mod.py\n"
            "index 1111111..2222222 100644\n"
            "--- a/mod.py\n"
            "+++ b/mod.py\n"
            "@@ -1 +1,5 @@\n"
            " import subprocess\n"
            "+\n"
            "+def build():\n"
            "+    subprocess.run([\"x\"], check=True)\n"
            "+    _ = subprocess.run([\"x\"], check=True)\n")
    monkeypatch.setattr(discarded_exit, "_head_diff", lambda *args: (0, diff))

    assert run_cli(discarded_exit, [], cwd=tmp_path) == (0, "", "")


def test_a_discarded_call_on_a_context_or_removed_line_is_not_printed_while_an_added_one_is(
        tmp_path, run_cli, discarded_exit, monkeypatch):
    (tmp_path / "mod.py").write_text(
        "import subprocess\n"
        "subprocess.call([\"context\"])\n"
        "subprocess.call([\"added\"])\n")
    diff = ("diff --git a/mod.py b/mod.py\n"
            "index 1111111..2222222 100644\n"
            "--- a/mod.py\n"
            "+++ b/mod.py\n"
            "@@ -1,3 +1,3 @@\n"
            " import subprocess\n"
            " subprocess.call([\"context\"])\n"
            "-subprocess.call([\"removed\"])\n"
            "+subprocess.call([\"added\"])\n")
    monkeypatch.setattr(discarded_exit, "_head_diff", lambda *args: (0, diff))

    assert run_cli(discarded_exit, [], cwd=tmp_path) == (1, "mod.py:3\n", "")


def test_an_added_exit_code_assigned_to_underscore_is_printed_even_when_the_function_reads_underscore(
        tmp_path, run_cli, discarded_exit, monkeypatch):
    (tmp_path / "mod.py").write_text(
        "import subprocess\n"
        "\n"
        "def call():\n"
        "    _ = subprocess.call([\"x\"])\n"
        "    print(_)\n")
    diff = ("diff --git a/mod.py b/mod.py\n"
            "index 1111111..2222222 100644\n"
            "--- a/mod.py\n"
            "+++ b/mod.py\n"
            "@@ -1 +1,5 @@\n"
            " import subprocess\n"
            "+\n"
            "+def call():\n"
            "+    _ = subprocess.call([\"x\"])\n"
            "+    print(_)\n")
    monkeypatch.setattr(discarded_exit, "_head_diff", lambda *args: (0, diff))

    assert run_cli(discarded_exit, [], cwd=tmp_path) == (1, "mod.py:4\n", "")


def test_an_added_subprocess_run_with_check_true_never_bound_whole_prints_nothing_and_exits_0(
        tmp_path, run_cli, discarded_exit, monkeypatch):
    (tmp_path / "mod.py").write_text(
        "import subprocess\n"
        "\n"
        "def output():\n"
        "    out = subprocess.run([\"x\"], check=True).stdout\n"
        "    return out\n")
    diff = ("diff --git a/mod.py b/mod.py\n"
            "index 1111111..2222222 100644\n"
            "--- a/mod.py\n"
            "+++ b/mod.py\n"
            "@@ -1 +1,5 @@\n"
            " import subprocess\n"
            "+\n"
            "+def output():\n"
            "+    out = subprocess.run([\"x\"], check=True).stdout\n"
            "+    return out\n")
    monkeypatch.setattr(discarded_exit, "_head_diff", lambda *args: (0, diff))

    assert run_cli(discarded_exit, [], cwd=tmp_path) == (0, "", "")


def _whole_file_added(path, source):
    """A diff adding every line of source as the new file path."""
    lines = source.splitlines()
    return (f"diff --git a/{path} b/{path}\n"
            "new file mode 100644\n"
            "index 0000000..2222222\n"
            "--- /dev/null\n"
            f"+++ b/{path}\n"
            f"@@ -0,0 +1,{len(lines)} @@\n"
            + "".join(f"+{line}\n" for line in lines))


def test_a_name_read_only_before_the_exit_code_is_bound_to_it_is_printed_and_exits_1(
        tmp_path, run_cli, discarded_exit, monkeypatch):
    source = ("import subprocess\n"
              "\n"
              "def run(rc):\n"
              "    print(rc)\n"
              "    rc = subprocess.call([\"x\"])\n"
              "    return 0\n")
    (tmp_path / "mod.py").write_text(source)
    monkeypatch.setattr(discarded_exit, "_head_diff", lambda *args: (0, _whole_file_added("mod.py", source)))

    assert run_cli(discarded_exit, [], cwd=tmp_path) == (1, "mod.py:5\n", "")


def test_a_name_read_earlier_in_a_loop_body_that_binds_the_exit_code_is_not_printed_and_exits_0(
        tmp_path, run_cli, discarded_exit, monkeypatch):
    source = ("import subprocess\n"
              "\n"
              "def run():\n"
              "    rc = 0\n"
              "    while rc == 0:\n"
              "        rc = subprocess.call([\"x\"])\n"
              "    return 0\n")
    (tmp_path / "mod.py").write_text(source)
    monkeypatch.setattr(discarded_exit, "_head_diff", lambda *args: (0, _whole_file_added("mod.py", source)))

    assert run_cli(discarded_exit, [], cwd=tmp_path) == (0, "", "")


def test_an_annotated_binding_of_an_exit_code_never_read_is_printed_and_one_read_afterwards_is_not(
        tmp_path, run_cli, discarded_exit, monkeypatch):
    source = ("import subprocess\n"
              "\n"
              "def lost():\n"
              "    rc: int = subprocess.call([\"x\"])\n"
              "    return 0\n"
              "\n"
              "def kept():\n"
              "    rc: int = subprocess.call([\"x\"])\n"
              "    return rc\n")
    (tmp_path / "mod.py").write_text(source)
    monkeypatch.setattr(discarded_exit, "_head_diff", lambda *args: (0, _whole_file_added("mod.py", source)))

    assert run_cli(discarded_exit, [], cwd=tmp_path) == (1, "mod.py:4\n", "")


def test_an_attribute_taken_off_a_run_call_nested_in_an_expression_is_printed_and_exits_1(
        tmp_path, run_cli, discarded_exit, monkeypatch):
    source = ("import subprocess\n"
              "print(subprocess.run([\"x\"], capture_output=True).stdout)\n"
              "print(subprocess.run([\"x\"], check=True).stdout)\n"
              "print(subprocess.run([\"x\"]).returncode)\n")
    (tmp_path / "mod.py").write_text(source)
    monkeypatch.setattr(discarded_exit, "_head_diff", lambda *args: (0, _whole_file_added("mod.py", source)))

    assert run_cli(discarded_exit, [], cwd=tmp_path) == (1, "mod.py:2\n", "")


def test_a_diff_only_deleting_a_py_file_touches_it_so_prints_nothing_and_exits_0(
        tmp_path, run_cli, discarded_exit, monkeypatch):
    diff = ("diff --git a/gone.py b/gone.py\n"
            "deleted file mode 100644\n"
            "index 1111111..0000000\n"
            "--- a/gone.py\n"
            "+++ /dev/null\n"
            "@@ -1 +0,0 @@\n"
            "-import subprocess\n")
    monkeypatch.setattr(discarded_exit, "_head_diff", lambda *args: (0, diff))

    assert run_cli(discarded_exit, [], cwd=tmp_path) == (0, "", "")
