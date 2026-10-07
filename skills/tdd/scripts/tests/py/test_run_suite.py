"""In-process cases for veri/run_suite.py, the module run-suite.sh is a shim over."""
import importlib
import pathlib
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


@pytest.fixture
def run_suite():
    return importlib.import_module("veri.run_suite")


def fake_suite(tmp_path, name, body):
    suite = tmp_path / name
    suite.write_text("#!/bin/sh\n" + body)
    suite.chmod(0o755)
    return str(suite)


def test_main_refuses_a_countless_suite_quoting_its_last_line_or_naming_its_empty_output(tmp_path, capfd, run_suite):
    answers = []
    for name, body in (("partial.test.sh", "echo partial\nexit 0\n"), ("silent.test.sh", "exit 0\n")):
        code = run_suite.main([fake_suite(tmp_path, name, body)])
        out, _ = capfd.readouterr()
        answers.append((code, out.splitlines()[-2:]))
    assert answers == [
        (1, ["partial.test.sh: never reached its count line", "partial.test.sh: its last line was: partial"]),
        (1, ["silent.test.sh: never reached its count line", "silent.test.sh: its output was empty"]),
    ]


def test_main_reads_a_suite_output_over_one_mebibyte_to_its_count_line(tmp_path, capfd, run_suite):
    output = tmp_path / "output.txt"
    output.write_text(("y" * 79 + "\n") * 13200 + "13 passed, 0 failed\n")
    assert output.stat().st_size > 1024 * 1024
    code = run_suite.main([fake_suite(tmp_path, "big.test.sh", 'cat "%s"\nexit 0\n' % output)])
    out, _ = capfd.readouterr()
    assert (code, "never reached its count line" in out) == (0, False)
