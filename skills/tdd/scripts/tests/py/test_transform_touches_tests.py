"""In-process cases for veri/transform_touches_tests.py, the module transform-touches-tests.sh is a shim over."""
import importlib
import pathlib
import subprocess
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

USAGE = "usage: transform-touches-tests.sh <base-sha>\n"


@pytest.fixture
def transform_touches_tests():
    return importlib.import_module("veri.transform_touches_tests")


def test_main_refuses_a_missing_or_unresolvable_base_sha_with_exit_2_and_the_usage_line(
        monkeypatch, capsys, transform_touches_tests):
    calls = []

    def fake(args, *rest, **kwargs):
        calls.append(list(args))
        code = 1 if list(args)[:2] == ["git", "rev-parse"] else 0
        return subprocess.CompletedProcess(args, code, "", "")

    for entry in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, entry, fake)

    for argv in ([], [""]):
        code = transform_touches_tests.main(argv)
        captured = capsys.readouterr()
        assert (argv, code, captured.out, captured.err) == (argv, 2, "", USAGE)
    assert calls == []

    code = transform_touches_tests.main(["nosuch"])
    captured = capsys.readouterr()
    assert code in range(0, 4)
    assert (code, captured.out, captured.err) == (
        2, "",
        "transform-touches-tests.sh: base-sha does not resolve to a commit: nosuch\n" + USAGE)
