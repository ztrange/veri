"""build-develop-prompt.sh test-quality renders the develop-test-quality prompt over the run's test files (#4119)."""
import importlib

import pytest

from conftest import SCRIPTS

SMELLS = SCRIPTS.parent / "SMELLS.md"


@pytest.fixture
def bdp():
    return importlib.import_module("veri.build_develop_prompt")


@pytest.fixture
def spec(tmp_path):
    path = tmp_path / "spec.md"
    path.write_bytes(b"# spec\nthe issue body\nTest command: make test\n")
    return str(path)


def test_cli_renders_the_smells_test_code_rules_and_each_given_test_file(run_cli, bdp, spec):
    rules = SMELLS.read_text().split("#### Rules for test code", 1)[1].strip()

    code, out, err = run_cli(bdp,
                    ["test-quality", spec, "make test", "test_alpha.py", "beta.test.js"])

    assert (code, err, rules in out, "- test_alpha.py" in out, "- beta.test.js" in out, "{{" in out) == (
        0, "", True, True, True, False)


def test_test_quality_takes_the_spec_the_test_command_and_at_least_one_test_file(bdp, spec):
    refusal = bdp.arguments(["test-quality", spec, "make test"])

    assert (refusal.message, refusal.code) == ("build-develop-prompt: test-quality needs 4 arguments, got 3", 2)
