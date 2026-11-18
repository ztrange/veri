"""The run line the prompt builders render for the affected suites and for one suite: the repo's own
`veri: one test file:` command outside veri's own tree, today's `make test TESTS=` text inside it (#4105)."""
import importlib
import re

import pytest

from conftest import SCRIPTS

TIMED = str(SCRIPTS / "timed-test-run.sh")
TEST_CMD, TEST_PATH = "npm test", "tests/test_x.py"  # prompt arguments only: no suite runs
LOOP = "sh -c 'for f; do set -- \"$f\"; npx jest \"$1\" || s=$?; done; exit ${s:-0}' sh <those paths>"


@pytest.fixture
def builders():
    return importlib.import_module("veri.build_develop_prompt"), importlib.import_module("veri.build_verify_prompt")


def foreign_tree(tmp_path, claude_md):
    (tmp_path / "CLAUDE.md").write_text(claude_md)
    (tmp_path / "spec.md").write_text("## Acceptance criteria\n\n- [ ] it works\n")
    return tmp_path


def lines_with(text, needle):
    return [line.strip() for line in text.split("\n") if needle in line]


def rendered(run_cli, builders, cwd):
    develop, verify = builders
    spec = str(cwd / "spec.md")
    red = run_cli(develop, ["red", spec, "a step", TEST_CMD], cwd=cwd)
    verify_red = run_cli(verify, ["red", spec, TEST_PATH], cwd=cwd)
    return [(code, err) for code, _, err in (red, verify_red)], [
        (lines_with(out, "timed-test-run.sh changed"), re.findall(r"(`[^`]*`) — the repo's runner for one test file", out))
        for _, out, _ in (red, verify_red)]


def test_outside_veri_both_builders_render_the_repos_one_test_file_command_once_per_path_and_for_one_suite(
        tmp_path, run_cli, builders):
    cwd = foreign_tree(tmp_path, 'veri: fast tests: `npm test`\nveri: all tests: `npm test`\n'
                                 'veri: one test file: `npx jest "$1"`\n')
    ends, lines = rendered(run_cli, builders, cwd)
    affected = [TIMED + " changed '<the test files you ran>' " + LOOP]
    assert (ends, lines) == (
        [(0, ""), (0, "")],
        [(affected, ["`sh -c 'npx jest \"$1\"' sh \"<test file>\"`"])] * 2)


def test_outside_veri_with_no_one_test_file_line_both_builders_render_the_all_tier_command_once(
        tmp_path, run_cli, builders):
    cwd = foreign_tree(tmp_path, 'veri: fast tests: `npm run unit`\nveri: all tests: `npm test`\n')
    ends, lines = rendered(run_cli, builders, cwd)
    assert (ends, lines) == (
        [(0, ""), (0, "")],
        [([TIMED + " changed '<the test files you ran>' npm test"], ["`npm test`"])] * 2)


def test_the_run_line_reaches_the_prompt_from_claude_md_alone_and_no_tdd_file_does(tmp_path, run_cli, builders):
    cwd = foreign_tree(tmp_path, 'veri: one test file: `npx jest "$1"`\n')
    (cwd / ".tdd").mkdir()
    (cwd / ".tdd/notes.md").write_text("veri: one test file: `zq7_marker_4105 \"$1\"`\nzq7_marker_4105\n")
    develop, verify = builders
    spec = str(cwd / "spec.md")
    outs = [run_cli(develop, ["red", spec, "a step", TEST_CMD], cwd=cwd),
            run_cli(verify, ["red", spec, TEST_PATH], cwd=cwd)]
    assert [(code, "npx jest" in out, "zq7_marker_4105" in out) for code, out, _ in outs] == [(0, True, False)] * 2
