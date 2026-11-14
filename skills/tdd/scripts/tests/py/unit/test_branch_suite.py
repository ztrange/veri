"""In-process cases for veri/branch_suite.py, the module branch-suite.sh is a shim over."""
import importlib

import pytest


@pytest.fixture
def branch_suite():
    return importlib.import_module("veri.branch_suite")


def test_main_prints_an_explicit_ci_or_local_as_given(tmp_path, run_cli, branch_suite):
    ci = run_cli(branch_suite, [], env={"VERI_BRANCH_SUITE": "ci"}, cwd=tmp_path)
    local = run_cli(branch_suite, [], env={"VERI_BRANCH_SUITE": "local"}, cwd=tmp_path)

    assert ci[:2] == (0, "ci\n")
    assert local[:2] == (0, "local\n")


def _tree(root, on):
    (root / ".github" / "workflows").mkdir(parents=True)
    (root / ".github" / "workflows" / "test.yml").write_text(
        "name: test\non:\n  %s:\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n      - run: echo pull_request\n" % on)
    return root


def test_main_with_branch_suite_unset_or_empty_prints_ci_where_a_workflow_triggers_on_pull_request_and_local_otherwise(
        tmp_path, run_cli, branch_suite):
    triggered = _tree(tmp_path / "triggered", "pull_request")
    target = _tree(tmp_path / "target", "pull_request_target")
    push_only = _tree(tmp_path / "push-only", "push")
    bare = tmp_path / "bare"
    bare.mkdir()

    assert run_cli(branch_suite, [], cwd=triggered)[:2] == (0, "ci\n")
    assert run_cli(branch_suite, [], cwd=target)[:2] == (0, "ci\n")
    assert run_cli(branch_suite, [], env={"VERI_BRANCH_SUITE": ""}, cwd=triggered)[:2] == (0, "ci\n")
    assert run_cli(branch_suite, [], cwd=push_only)[:2] == (0, "local\n")
    assert run_cli(branch_suite, [], cwd=bare)[:2] == (0, "local\n")


def test_main_with_branch_suite_unset_prints_ci_for_ci_on_pr_1_and_local_for_0_whatever_the_tree_holds(
        tmp_path, run_cli, branch_suite):
    triggered = _tree(tmp_path / "triggered", "pull_request")
    push_only = _tree(tmp_path / "push-only", "push")
    bare = tmp_path / "bare"
    bare.mkdir()

    assert run_cli(branch_suite, [], env={"VERI_CI_ON_PR": "0"}, cwd=triggered)[:2] == (0, "local\n")
    assert run_cli(branch_suite, [], env={"VERI_CI_ON_PR": "1"}, cwd=push_only)[:2] == (0, "ci\n")
    assert run_cli(branch_suite, [], env={"VERI_CI_ON_PR": "1"}, cwd=bare)[:2] == (0, "ci\n")


def test_main_exits_2_naming_the_variable_and_its_value_on_a_bad_branch_suite_or_a_bad_ci_on_pr_when_the_mode_is_not_explicit(
        tmp_path, run_cli, branch_suite):
    code, out, err = run_cli(branch_suite, [], env={"VERI_BRANCH_SUITE": "remote"}, cwd=tmp_path)
    assert (code, out) == (2, "")
    assert "VERI_BRANCH_SUITE" in err and "remote" in err and len(err.splitlines()) == 1

    code, out, err = run_cli(branch_suite, [], env={"VERI_BRANCH_SUITE": "", "VERI_CI_ON_PR": "yes"}, cwd=tmp_path)
    assert (code, out) == (2, "")
    assert "VERI_CI_ON_PR" in err and "yes" in err and len(err.splitlines()) == 1

    explicit = run_cli(branch_suite, [], env={"VERI_BRANCH_SUITE": "ci", "VERI_CI_ON_PR": "yes"}, cwd=tmp_path)
    assert explicit[:2] == (0, "ci\n")
