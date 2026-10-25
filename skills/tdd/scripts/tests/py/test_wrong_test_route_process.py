"""Conductor-level cases for wrong-test-route.sh: the real script, called as the Green step and REVISE.md call it."""
import os
import subprocess

import pytest

from conftest import SCRIPTS

STEP = "a wheel turns ⟦criterion 1⟧"
OWN_ID = "tests/test_wheel.py::test_a_wheel_turns"
OLDER = "test_a_cog_never_moves"


def a_repo_with_an_older_frozen_case(tmp_path):
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / ".tdd").mkdir()
    (repo / "tests" / "test_cog.py").write_text("def %s():\n    assert True\n" % OLDER)
    (repo / "tests" / "test_wheel.py").write_text("def test_a_wheel_turns():\n    assert True\n")
    return repo


def route(repo, report):
    env = {k: v for k, v in os.environ.items() if not k.startswith("VERI_")}
    env["VERI_STEP"] = STEP
    ran = subprocess.run([str(SCRIPTS / "wrong-test-route.sh"), report, OWN_ID], cwd=repo, env=env,
                         stdin=subprocess.DEVNULL, capture_output=True, text=True)
    return ran.returncode, ran.stdout, ran.stderr


@pytest.mark.process("wrong-test-route.sh run as the Green step runs it")
def test_2254_criterion_1_a_develop_green_report_naming_one_older_case_on_superseded_alone_reroutes_red_over_it(tmp_path):
    repo = a_repo_with_an_older_frozen_case(tmp_path)
    (repo / ".tdd" / "develop-green.out").write_text(
        "The wheel now turns, so the cog moves with it.\n"
        "SUPERSEDED: tests/test_cog.py::%s asserts the cog never moves, which this step's change supersedes\n"
        "SUITE: make test\n" % OLDER)

    code, out, err = route(repo, ".tdd/develop-green.out")

    assert (code, out) == (0, "red %s\n" % OLDER), err


@pytest.mark.process("wrong-test-route.sh run as REVISE.md runs it")
def test_2254_criterion_3_a_revise_green_report_naming_one_older_case_on_superseded_alone_is_never_answered_revise(tmp_path):
    repo = a_repo_with_an_older_frozen_case(tmp_path)
    (repo / ".tdd" / "revise-green-1.out").write_text(
        "Revised: the wheel turns and drives the cog.\n"
        "SUPERSEDED: `tests/test_cog.py::%s` — the cog now moves with the wheel\n" % OLDER)

    code, out, err = route(repo, ".tdd/revise-green-1.out")

    assert out != "revise\n" and code != 3, err
    assert (code, out) == (0, "red %s\n" % OLDER), err
