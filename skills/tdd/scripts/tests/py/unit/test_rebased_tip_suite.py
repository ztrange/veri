"""In-process cases for veri/rebased_tip_suite.py, the module rebased-tip-suite.sh is a shim over."""
import importlib

import pytest


@pytest.fixture
def rebased_tip_suite():
    return importlib.import_module("veri.rebased_tip_suite")


def test_main_with_rebased_tip_suite_unset_prints_ci_in_a_tree_where_a_workflow_triggers_on_pull_request(
        tmp_path, run_cli, rebased_tip_suite):
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (workflows / "test.yml").write_text("name: test\non:\n  pull_request:\n  push:\n    branches: [main]\njobs:\n  test:\n    runs-on: ubuntu-latest\n")

    code, out, err = run_cli(rebased_tip_suite, [], cwd=tmp_path)

    assert (code, out) == (0, "ci\n")


def test_main_with_rebased_tip_suite_unset_prints_local_where_no_workflow_triggers_on_pull_request_or_ci_on_pr_is_0_and_ci_when_ci_on_pr_is_1(
        tmp_path, run_cli, rebased_tip_suite):
    def tree(name, on):
        root = tmp_path / name
        (root / ".github" / "workflows").mkdir(parents=True)
        (root / ".github" / "workflows" / "test.yml").write_text(
            "name: test\non:\n  %s:\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n      - run: echo pull_request\n" % on)
        return root

    push_only, triggered, target = tree("push-only", "push"), tree("triggered", "pull_request"), tree("target", "pull_request_target")
    bare = tmp_path / "bare"
    bare.mkdir()

    assert run_cli(rebased_tip_suite, [], cwd=push_only)[:2] == (0, "local\n")
    assert run_cli(rebased_tip_suite, [], cwd=bare)[:2] == (0, "local\n")
    assert run_cli(rebased_tip_suite, [], cwd=target)[:2] == (0, "ci\n")
    assert run_cli(rebased_tip_suite, [], env={"VERI_CI_ON_PR": "0"}, cwd=triggered)[:2] == (0, "local\n")
    assert run_cli(rebased_tip_suite, [], env={"VERI_CI_ON_PR": "1"}, cwd=push_only)[:2] == (0, "ci\n")
    assert run_cli(rebased_tip_suite, [], env={"VERI_CI_ON_PR": "1"}, cwd=bare)[:2] == (0, "ci\n")
    code, out, err = run_cli(rebased_tip_suite, [], env={"VERI_CI_ON_PR": "yes"}, cwd=triggered)
    assert (code, out) == (2, "")
    assert "VERI_CI_ON_PR" in err and len(err.splitlines()) == 1


def test_main_prints_an_explicit_local_or_ci_as_given_whatever_the_tree_holds_and_exits_2_naming_the_variable_on_any_other_value(
        tmp_path, run_cli, rebased_tip_suite):
    triggered, bare = tmp_path / "triggered", tmp_path / "bare"
    (triggered / ".github" / "workflows").mkdir(parents=True)
    (triggered / ".github" / "workflows" / "test.yml").write_text("on:\n  pull_request:\n")
    bare.mkdir()

    local = run_cli(rebased_tip_suite, [], env={"VERI_REBASED_TIP_SUITE": "local"}, cwd=triggered)
    ci = run_cli(rebased_tip_suite, [], env={"VERI_REBASED_TIP_SUITE": "ci"}, cwd=bare)
    code, out, err = run_cli(rebased_tip_suite, [], env={"VERI_REBASED_TIP_SUITE": "remote"}, cwd=triggered)

    assert local[:2] == (0, "local\n")
    assert ci[:2] == (0, "ci\n")
    assert (code, out) == (2, "")
    assert "VERI_REBASED_TIP_SUITE" in err and len(err.splitlines()) == 1
