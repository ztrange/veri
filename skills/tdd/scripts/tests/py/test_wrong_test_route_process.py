"""Conductor-level cases for wrong-test-route.sh: the real script, called as the Green step and REVISE.md call it."""
import hashlib
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
    ran = subprocess.run([str(SCRIPTS / "wrong-test-route.sh"), "--spec", ".tdd/issue-0-spec.md", report, OWN_ID], cwd=repo, env=env,
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

    assert (code, out) == (0, "red tests/test_cog.py::%s\n" % OLDER), err


@pytest.mark.process("wrong-test-route.sh run as REVISE.md runs it")
def test_2254_criterion_3_a_revise_green_report_naming_one_older_case_on_superseded_alone_is_never_answered_revise(tmp_path):
    repo = a_repo_with_an_older_frozen_case(tmp_path)
    (repo / ".tdd" / "revise-green-1.out").write_text(
        "Revised: the wheel turns and drives the cog.\n"
        "SUPERSEDED: `tests/test_cog.py::%s` — the cog now moves with the wheel\n" % OLDER)

    code, out, err = route(repo, ".tdd/revise-green-1.out")

    assert out != "revise\n" and code != 3, err
    assert (code, out) == (0, "red tests/test_cog.py::%s\n" % OLDER), err


@pytest.mark.process("wrong-test-route.sh run as the Green step runs it")
def test_2868_two_superseded_cases_with_the_own_red_case_recorded_and_unnamed_route_supersede_diff(tmp_path):
    repo = a_repo_with_an_older_frozen_case(tmp_path)
    (repo / "tests" / "test_gear.py").write_text("def test_a_gear_never_slips():\n    assert True\n")
    key = hashlib.sha256(os.fsencode(STEP)).hexdigest()[:16]
    (repo / ".tdd" / ("tests-frozen-%s.record" % key)).write_text("case: test_a_wheel_turns\n")
    (repo / ".tdd" / "develop-green.out").write_text(
        "The wheel now turns, so the cog and the gear move with it.\n"
        "SUPERSEDED: tests/test_cog.py::%s asserts the cog never moves\n"
        "SUPERSEDED: tests/test_gear.py::test_a_gear_never_slips asserts the gear never slips\n"
        "WRONG_TEST: none\n" % OLDER)

    code, out, err = route(repo, ".tdd/develop-green.out")

    assert (code, out) == (0, "supersede-diff %s test_a_gear_never_slips\n" % OLDER), err


@pytest.mark.process("wrong-test-route.sh run as the Green step runs it")
def test_2916_criterion_2_a_missing_report_with_a_later_step_that_is_unchecked_in_the_ledger_routes_later(tmp_path):
    repo = a_repo_with_an_older_frozen_case(tmp_path)
    later = "a cog never moves alone ⟦criterion 3⟧"
    (repo / ".tdd" / "issue-77.md").write_text(
        "# Plan for #77\n\n- [ ] %s\n- [ ] a gear never slips ⟦criterion 2⟧\n- [ ] %s\n" % (STEP, later))
    (repo / ".tdd" / "verify-green.out").write_text(
        "The cog can still move alone.\n"
        "MISSING_TEST: a cog never moves alone\n"
        "LATER_STEP: %s\n"
        "VERDICT: REJECT\n" % later)
    env = {k: v for k, v in os.environ.items() if not k.startswith("VERI_")}
    env["VERI_STEP"] = STEP
    env["VERI_ISSUE"] = "77"

    ran = subprocess.run([str(SCRIPTS / "wrong-test-route.sh"), "--spec", ".tdd/issue-0-spec.md", ".tdd/verify-green.out", OWN_ID], cwd=repo,
                         env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True)

    assert (ran.returncode, ran.stdout) == (0, "later %s\n" % later), ran.stderr


@pytest.mark.process("wrong-test-route.sh run as the Green step runs it")
def test_2916_criterion_2_a_later_step_report_routes_later_even_when_the_missing_reroute_budget_is_spent(tmp_path):
    repo = a_repo_with_an_older_frozen_case(tmp_path)
    later = "a cog never moves alone ⟦criterion 3⟧"
    (repo / ".tdd" / "issue-77.md").write_text(
        "# Plan for #77\n\n- [ ] %s\n- [ ] %s\n" % (STEP, later))
    (repo / ".tdd" / "events.jsonl").write_text(
        '{"event": "reroute", "step": "%s", "kind": "missing"}\n' % STEP)
    (repo / ".tdd" / "verify-green.out").write_text(
        "MISSING_TEST: a cog never moves alone\nLATER_STEP: %s\nVERDICT: REJECT\n" % later)
    env = {k: v for k, v in os.environ.items() if not k.startswith("VERI_")}
    env.update(VERI_STEP=STEP, VERI_ISSUE="77", VERI_MISSING_REROUTE_BUDGET="1")

    ran = subprocess.run([str(SCRIPTS / "wrong-test-route.sh"), "--spec", ".tdd/issue-0-spec.md", ".tdd/verify-green.out", OWN_ID], cwd=repo,
                         env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True)

    assert (ran.returncode, ran.stdout) == (0, "later %s\n" % later), ran.stderr


@pytest.mark.process("wrong-test-route.sh run as the Green step runs it")
def test_2916_criterion_4_a_later_step_report_naming_a_step_already_checked_falls_through_to_missing(tmp_path):
    repo = a_repo_with_an_older_frozen_case(tmp_path)
    done = "a cog never moves alone ⟦criterion 3⟧"
    (repo / ".tdd" / "issue-77.md").write_text(
        "# Plan for #77\n\n- [ ] %s\n- [x] %s\n" % (STEP, done))
    (repo / ".tdd" / "verify-green.out").write_text(
        "MISSING_TEST: a cog never moves alone\nLATER_STEP: %s\nVERDICT: REJECT\n" % done)
    env = {k: v for k, v in os.environ.items() if not k.startswith("VERI_")}
    env.update(VERI_STEP=STEP, VERI_ISSUE="77")

    ran = subprocess.run([str(SCRIPTS / "wrong-test-route.sh"), "--spec", ".tdd/issue-0-spec.md", ".tdd/verify-green.out", OWN_ID], cwd=repo,
                         env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True)

    assert (ran.returncode, ran.stdout) == (0, "missing a cog never moves alone\n"), ran.stderr


@pytest.mark.process("wrong-test-route.sh run as the Green step runs it")
def test_2916_criterion_4_a_later_step_report_naming_no_step_of_the_ledger_falls_through_to_missing(tmp_path):
    repo = a_repo_with_an_older_frozen_case(tmp_path)
    (repo / ".tdd" / "issue-77.md").write_text(
        "# Plan for #77\n\n- [ ] %s\n- [ ] a gear never slips ⟦criterion 2⟧\n" % STEP)
    (repo / ".tdd" / "verify-green.out").write_text(
        "MISSING_TEST: a cog never moves alone\nLATER_STEP: a step nobody planned ⟦criterion 9⟧\nVERDICT: REJECT\n")
    env = {k: v for k, v in os.environ.items() if not k.startswith("VERI_")}
    env.update(VERI_STEP=STEP, VERI_ISSUE="77")

    ran = subprocess.run([str(SCRIPTS / "wrong-test-route.sh"), "--spec", ".tdd/issue-0-spec.md", ".tdd/verify-green.out", OWN_ID], cwd=repo,
                         env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True)

    assert (ran.returncode, ran.stdout) == (0, "missing a cog never moves alone\n"), ran.stderr


@pytest.mark.process("wrong-test-route.sh run as the Green step runs it")
def test_2916_criterion_4_a_later_step_report_naming_the_current_step_falls_through_to_missing(tmp_path):
    repo = a_repo_with_an_older_frozen_case(tmp_path)
    (repo / ".tdd" / "issue-77.md").write_text(
        "# Plan for #77\n\n- [ ] %s\n- [ ] a gear never slips ⟦criterion 2⟧\n" % STEP)
    (repo / ".tdd" / "verify-green.out").write_text(
        "MISSING_TEST: a cog never moves alone\nLATER_STEP: %s\nVERDICT: REJECT\n" % STEP)
    env = {k: v for k, v in os.environ.items() if not k.startswith("VERI_")}
    env.update(VERI_STEP=STEP, VERI_ISSUE="77")

    ran = subprocess.run([str(SCRIPTS / "wrong-test-route.sh"), "--spec", ".tdd/issue-0-spec.md", ".tdd/verify-green.out", OWN_ID], cwd=repo,
                         env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True)

    assert (ran.returncode, ran.stdout) == (0, "missing a cog never moves alone\n"), ran.stderr


@pytest.mark.process("wrong-test-route.sh run as the Green step runs it")
def test_2916_criterion_4_a_later_step_report_naming_an_earlier_unchecked_step_falls_through_to_missing(tmp_path):
    repo = a_repo_with_an_older_frozen_case(tmp_path)
    earlier = "a gear never slips ⟦criterion 0⟧"
    (repo / ".tdd" / "issue-77.md").write_text(
        "# Plan for #77\n\n- [ ] %s\n- [ ] %s\n" % (earlier, STEP))
    (repo / ".tdd" / "verify-green.out").write_text(
        "MISSING_TEST: a cog never moves alone\nLATER_STEP: %s\nVERDICT: REJECT\n" % earlier)
    env = {k: v for k, v in os.environ.items() if not k.startswith("VERI_")}
    env.update(VERI_STEP=STEP, VERI_ISSUE="77")

    ran = subprocess.run([str(SCRIPTS / "wrong-test-route.sh"), "--spec", ".tdd/issue-0-spec.md", ".tdd/verify-green.out", OWN_ID], cwd=repo,
                         env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True)

    assert (ran.returncode, ran.stdout) == (0, "missing a cog never moves alone\n"), ran.stderr


@pytest.mark.process("wrong-test-route.sh run as the Green step runs it")
def test_3037_criterion_1_a_name_defined_only_in_an_untouched_test_file_routes_no_fixture(tmp_path):
    repo = a_repo_with_an_older_frozen_case(tmp_path)
    (repo / "tests" / "test_cog.py").write_text("def ran():\n    return 1\n")
    (repo / ".tdd" / "develop-green.out").write_text(
        "WRONG_TEST: the local variable `ran` in the Red case is never set\n")

    code, out, err = route(repo, ".tdd/develop-green.out")

    assert out == "revise\n", err
