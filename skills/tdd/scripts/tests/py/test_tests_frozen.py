"""In-process cases for veri/tests_frozen.py, the module tests-frozen.sh is a shim over."""
import hashlib
import importlib

import pytest


@pytest.fixture
def tests_frozen():
    return importlib.import_module("veri.tests_frozen")


def test_path_names_a_steps_record_by_the_first_16_hex_digits_of_its_texts_sha256_whatever_its_length_or_slashes_1586(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "a.test.sh").write_text("assert one\n")
    long_step = "port the case / its pair " * 20
    short_step = "port the other case"

    answers = []
    for step in (long_step, short_step):
        code, out, err = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
        recorded = run_cli(tests_frozen, ["record", out.rstrip("\n"), "a.test.sh"], cwd=tmp_path)[0]
        answers.append((code, out, err, recorded))

    assert answers == [(0, ".tdd/tests-frozen-%s.record\n" % hashlib.sha256(step.encode()).hexdigest()[:16], "", 0)
                       for step in (long_step, short_step)]


def test_path_without_a_step_text_or_with_an_empty_one_is_exit_2_naming_the_usage_1586(tmp_path, run_cli, tests_frozen):
    answers = [run_cli(tests_frozen, argv, cwd=tmp_path) for argv in (["path"], ["path", ""])]

    assert [(code, out, "path <step-text>" in err) for code, out, err in answers] == [(2, "", True), (2, "", True)]
