"""parked-issues.sh's entry point: the shim runs veri/parked_issues.py and passes its exit code and output through.
The module's logic is tested in-process, in tests/py/unit/test_parked_issues.py."""
import importlib
import subprocess

import pytest

from conftest import SCRIPTS

ONE_PARKED_GH_STUB = """#!/bin/sh
for a in "$@"; do
  case "$a" in
    *page=[2-9]*) echo '[]'; exit 0 ;;
    */issues/7/comments*)
      echo '[{"author_association":"OWNER","user":{"login":"veri-operator"},"body":"### ⏸ Parked\\nCause: a bail\\nUnblock: a human reads the diff"}]'
      exit 0 ;;
    */issues*)
      echo '[{"number":7,"title":"Teach the verifier to refuse","labels":[{"name":"parked"}]}]'
      exit 0 ;;
  esac
done
echo '[]'
"""


def run(tmp_path, *argv, gh="#!/bin/sh\necho '[]'\n"):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    (bin_dir / "gh").write_text(gh)
    (bin_dir / "gh").chmod(0o755)
    ran = subprocess.run([str(SCRIPTS / "parked-issues.sh"), *argv], cwd=tmp_path, capture_output=True, text=True,
                         stdin=subprocess.DEVNULL,
                         env={"PATH": "%s:/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin" % bin_dir,
                              "PYTHONDONTWRITEBYTECODE": "1"})
    return ran.returncode, ran.stdout, ran.stderr


def usage():
    return importlib.import_module("veri.parked_issues").USAGE + "\n"


@pytest.mark.process("parked-issues.sh run against a gh stub serving one parked issue and its comments")
def test_the_shim_passes_exit_0_and_the_modules_stdout_through(tmp_path):
    assert run(tmp_path, gh=ONE_PARKED_GH_STUB) == (
        0, "7\tTeach the verifier to refuse\ta bail\ta human reads the diff\t-\t-\n", "")


@pytest.mark.process("parked-issues.sh run against a gh stub serving no issue at all")
def test_the_shim_passes_exit_3_through_when_none_is_parked(tmp_path):
    assert run(tmp_path) == (3, "", "")


@pytest.mark.process("parked-issues.sh run with an argument")
def test_the_shim_passes_exit_2_and_the_modules_stderr_through_for_an_argument(tmp_path):
    assert run(tmp_path, "--all") == (2, "", usage())


@pytest.mark.process("parked-issues.sh run as a script")
def test_help_prints_the_modules_usage_on_stdout_and_exits_0(tmp_path):
    assert run(tmp_path, "--help") == (0, usage(), "")
