"""wrong-test-route.sh's entry point: the shim runs veri/wrong_test_route.py and passes its exit code and output through.
The module's logic is tested in-process, in tests/py/unit/test_wrong_test_route.py."""
import importlib
import subprocess

import pytest

from conftest import SCRIPTS

STEP = "a wheel turns ⟦criterion 1⟧"
OWN_ID = "tests/test_wheel.py::test_a_wheel_turns"


def run(tmp_path, *argv, **env):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests" / "test_cog.py").write_text("def test_a_cog_never_moves():\n    assert True\n")
    (tmp_path / "tests" / "test_wheel.py").write_text("def test_a_wheel_turns():\n    assert True\n")
    ran = subprocess.run([str(SCRIPTS / "wrong-test-route.sh"), *argv], cwd=tmp_path, capture_output=True, text=True,
                         stdin=subprocess.DEVNULL,
                         env={"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "PYTHONDONTWRITEBYTECODE": "1",
                              "VERI_STEP": STEP, **env})
    return ran.returncode, ran.stdout, ran.stderr


def route(tmp_path, report, **env):
    (tmp_path / "green.out").write_text(report)
    return run(tmp_path, "--spec", ".tdd/issue-0-spec.md", "green.out", OWN_ID, **env)


def usage():
    return importlib.import_module("veri.wrong_test_route").USAGE + "\n"


@pytest.mark.process("wrong-test-route.sh run as the Green step runs it")
def test_the_shim_passes_exit_0_and_the_modules_route_through(tmp_path):
    assert route(tmp_path, "SUPERSEDED: tests/test_cog.py::test_a_cog_never_moves the cog now moves\n") == (
        0, "red tests/test_cog.py::test_a_cog_never_moves\n", "")


@pytest.mark.process("wrong-test-route.sh run as the Green step runs it, the missing reroute budget spent")
def test_the_shim_passes_exit_1_and_missing_exhausted_through(tmp_path):
    code, out, err = route(tmp_path, "MISSING_TEST: a cog never moves alone\n", VERI_MISSING_REROUTE_BUDGET="0")

    assert (code, out, err) == (1, "missing-exhausted a cog never moves alone\n", "")


@pytest.mark.process("wrong-test-route.sh run without --spec")
def test_the_shim_passes_exit_2_and_the_modules_stderr_through_for_bad_arguments(tmp_path):
    assert run(tmp_path, "green.out", OWN_ID) == (2, "", usage())


@pytest.mark.process("wrong-test-route.sh run as the Green step runs it")
def test_the_shim_passes_exit_3_and_revise_through(tmp_path):
    assert route(tmp_path, "SUITE: make test\nVERDICT: REJECT\n") == (3, "revise\n", "")


@pytest.mark.process("wrong-test-route.sh run as a script")
def test_help_prints_the_modules_usage_on_stdout_and_exits_0(tmp_path):
    assert run(tmp_path, "--help") == (0, usage(), "")
