"""The verifier's run lines read from CLAUDE.md as it stood at the `--branch-base` commit, over a real git repository
(#4263): a developer leaf's edit to the working tree's line never reaches them."""
import importlib
import re

import pytest

from conftest import SCRIPTS
from repo_builder import commit_all, git, new_repo

TIMED = str(SCRIPTS / "timed-test-run.sh")
BASE_MD = 'veri: all tests: pytest\nveri: one test file: pytest "$1"\n'
EDITED_MD = 'veri: all tests: pytest\nveri: one test file: true # $1\n'
BASE_LINES = (
    [TIMED + " affected '<the suites you ran>' "
     "sh -c 'for f; do set -- \"$f\"; pytest \"$1\" || s=$?; done; exit ${s:-0}' sh <those paths>"],
    ["`sh -c 'pytest \"$1\"' sh \"<test file>\"`"])


def run_lines_of(out):
    return ([line.strip() for line in out.split("\n") if "timed-test-run.sh affected" in line],
            re.findall(r"(`[^`]*`) — the repo's runner for one test file", out))


@pytest.mark.process("git init, commit and checkout run for real in a scratch repository, then build-verify-prompt in it")
def test_outside_veri_branch_base_renders_the_base_commits_one_test_file_run_lines_after_an_uncommitted_and_a_committed_edit_4263(
        tmp_path, run_cli):
    verify = importlib.import_module("veri.build_verify_prompt")
    repo = new_repo(tmp_path / "repo")
    spec = tmp_path / "spec.md"
    spec.write_text("## Acceptance criteria\n\n- [ ] it works\n")
    base = commit_all(repo, "base", **{"CLAUDE.md": BASE_MD})
    argv = ["--branch-base", base, "red", str(spec), "tests/test_x.py"]

    (repo / "CLAUDE.md").write_text(EDITED_MD)
    uncommitted = run_cli(verify, argv, cwd=repo)
    git(repo, "checkout", "-q", "-b", "feature")
    commit_all(repo, "edit the run line")
    committed = run_cli(verify, argv, cwd=repo)

    assert [(code, run_lines_of(out), err) for code, out, err in (uncommitted, committed)] == [(0, BASE_LINES, "")] * 2


@pytest.mark.process("git init, commit and checkout run for real in a scratch repository, then build-verify-prompt in it")
def test_outside_veri_branch_base_with_no_one_test_file_line_renders_the_base_commits_all_tier_fallback_after_an_uncommitted_and_a_committed_edit_4263(
        tmp_path, run_cli):
    verify = importlib.import_module("veri.build_verify_prompt")
    repo = new_repo(tmp_path / "repo")
    spec = tmp_path / "spec.md"
    spec.write_text("## Acceptance criteria\n\n- [ ] it works\n")
    base = commit_all(repo, "base", **{"CLAUDE.md": "veri: all tests: pytest\n"})
    argv = ["--branch-base", base, "red", str(spec), "tests/test_x.py"]

    (repo / "CLAUDE.md").write_text("veri: all tests: true\nveri: one test file: true # $1\n")
    uncommitted = run_cli(verify, argv, cwd=repo)
    git(repo, "checkout", "-q", "-b", "feature")
    commit_all(repo, "add a one test file line")
    committed = run_cli(verify, argv, cwd=repo)

    fallback = ([TIMED + " affected '<the suites you ran>' pytest"], ["`pytest`"])
    assert [(code, run_lines_of(out), err) for code, out, err in (uncommitted, committed)] == [(0, fallback, "")] * 2


@pytest.mark.process("git init and commit run for real in a scratch repository, then build-verify-prompt in it")
def test_outside_veri_a_branch_base_naming_no_commit_is_refused_with_exit_2_and_one_stderr_line_4263(tmp_path, run_cli):
    verify = importlib.import_module("veri.build_verify_prompt")
    repo = new_repo(tmp_path / "repo")
    spec = tmp_path / "spec.md"
    spec.write_text("## Acceptance criteria\n\n- [ ] it works\n")
    commit_all(repo, "base", **{"CLAUDE.md": BASE_MD})

    code, out, err = run_cli(verify, ["--branch-base", "0000000", "red", str(spec), "tests/test_x.py"], cwd=repo)

    assert (code, out, err) == (2, "", "build-verify-prompt: --branch-base '0000000' names no commit git can resolve\n")


@pytest.mark.process("git init, commit, update-ref and symbolic-ref run for real in a scratch repository, then verify.sh's"
                     " module in it, launching a real supervise.sh around a stub claude")
def test_outside_veri_verify_red_reads_its_run_lines_at_the_merge_base_with_origin_head_and_exits_2_naming_a_missing_one_4263(
        tmp_path, run_cli):
    verify = importlib.import_module("veri.verify")
    repo = new_repo(tmp_path / "repo")
    spec = tmp_path / "spec.md"
    spec.write_text("## Acceptance criteria\n\n- [ ] it works\n")
    claude = tmp_path / "claude-pass"
    claude.write_text("#!/bin/sh\nprintf 'VERDICT: PASS\\nREASON: fine.'\n")
    claude.chmod(0o755)
    env = {"CLAUDE_BIN": str(claude), "VERI_POLL": "0.02", "VERI_KILL_POLL": "0.01"}
    base = commit_all(repo, "base", **{"CLAUDE.md": BASE_MD, ".gitignore": ".tdd/\n"})
    git(repo, "remote", "add", "origin", str(tmp_path / "origin.git"))
    git(repo, "update-ref", "refs/remotes/origin/main", base)
    git(repo, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/main")
    git(repo, "checkout", "-q", "-b", "feature")
    commit_all(repo, "edit the run line", **{"CLAUDE.md": EDITED_MD})
    argv = ["red", str(spec), "tests/test_x.py", "test_x"]

    run_cli(verify, argv, env=env, cwd=repo)
    prompt = (repo / ".tdd" / "verify-red.prompt").read_text()
    git(repo, "symbolic-ref", "--delete", "refs/remotes/origin/HEAD")
    refused = run_cli(verify, argv, env=env, cwd=repo)

    assert (run_lines_of(prompt), refused) == (BASE_LINES, (
        2, "", "verify: no merge-base of HEAD and origin/HEAD; the red verifier reads its run lines from CLAUDE.md there\n"))
