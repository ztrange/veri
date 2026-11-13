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
