"""Cases for ready-check.sh that start the real entry point."""
import os
import re
import subprocess

import pytest

from conftest import SCRIPTS


@pytest.mark.process("ready-check.sh, a /bin/sh shim over veri/ready_check.py, run as a subprocess outside a git repository")
def test_issue_3055_ready_check_outside_a_git_repository_exits_2_with_a_usage_line_and_make_declares_its_caller(tmp_path):
    elsewhere = tmp_path / "not-a-repo"
    elsewhere.mkdir()
    env = {**os.environ, "GIT_CEILING_DIRECTORIES": str(tmp_path)}
    ran = subprocess.run([str(SCRIPTS / "ready-check.sh")], cwd=elsewhere, capture_output=True, text=True, env=env)
    makefile = (SCRIPTS.parent.parent.parent / "Makefile").read_text()

    assert ran.returncode == 2, (ran.returncode, ran.stdout, ran.stderr)
    assert "ready-check" in ran.stderr and "usage" in ran.stderr.lower()
    assert re.search(r"^ready-check:", makefile, re.M)


@pytest.mark.process("ready-check.sh, a /bin/sh shim over veri/ready_check.py, run as a subprocess inside a git repository")
def test_issue_3055_ready_check_with_two_positionals_or_an_unknown_option_exits_2_with_its_usage_line_and_no_stdout(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True, capture_output=True)
    for argv in (["one", "two"], ["--no-such-option"]):
        ran = subprocess.run([str(SCRIPTS / "ready-check.sh"), *argv], cwd=repo, capture_output=True, text=True)

        assert ran.returncode == 2, (argv, ran.returncode, ran.stdout, ran.stderr)
        assert "usage: ready-check.sh [repo-root]" in ran.stderr, (argv, ran.stderr)
        assert ran.stdout == "", (argv, ran.stdout)


def _git(repo, *argv):
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *argv], cwd=repo, check=True, capture_output=True)


def build_ready_repo(tmp_path):
    """A repo where every ready-check row holds, and an env whose PATH leads to a permissive gh stub."""
    repo = tmp_path / "ready-repo"
    (repo / ".github" / "workflows").mkdir(parents=True)
    (repo / "tests").mkdir()
    (repo / "CLAUDE.md").write_text("veri: fast tests: `make unit`\nveri: all tests: `make test`\n")
    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / ".github" / "workflows" / "ci.yml").write_text(
        "name: ci\non:\n  pull_request:\n  push:\n    branches: [main]\njobs:\n  t:\n    runs-on: ubuntu-latest\n    steps:\n      - run: make test\n")
    (repo / "tests" / "test_one.py").write_text("def test_one():\n    assert True\n")
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo, check=True, capture_output=True)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "init")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    gh = bin_dir / "gh"
    gh.write_text('#!/bin/sh\ncase "$*" in\n  "auth status"*) exit 0 ;;\n  *label*) echo \'[{"name":"veri"}]\' ;;\n  *) echo \'{"permissions":{"push":true,"admin":true}}\' ;;\nesac\n')
    gh.chmod(0o755)
    env = {**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}", "VERI_LABEL": "veri"}
    return repo, env


@pytest.mark.process("ready-check.sh, a /bin/sh shim over veri/ready_check.py, run as a subprocess inside a repository where every row holds")
def test_issue_3055_ready_check_exits_0_with_ready_as_its_last_line_where_every_row_holds(tmp_path):
    repo, env = build_ready_repo(tmp_path)
    ran = subprocess.run([str(SCRIPTS / "ready-check.sh")], cwd=repo, capture_output=True, text=True, env=env)
    lines = ran.stdout.splitlines()

    assert ran.returncode == 0, (ran.returncode, ran.stdout, ran.stderr)
    assert lines and lines[-1] == "ready", (ran.stdout, ran.stderr)


@pytest.mark.process("ready-check.sh, a /bin/sh shim over veri/ready_check.py, run as a subprocess inside a repository whose fast tier resolves to nothing")
def test_issue_3055_ready_check_with_no_fast_tier_exits_1_with_a_fail_row_naming_the_claude_md_line_to_add(tmp_path):
    repo, env = build_ready_repo(tmp_path)
    (repo / "CLAUDE.md").write_text("veri: all tests: `make test`\n")
    _git(repo, "mv", "tests/test_one.py", "tests/one_test.py")
    _git(repo, "commit", "-q", "-am", "drop the fast tier line")
    resolved = subprocess.run([str(SCRIPTS / "detect-test-command.sh"), "--tier", "fast"], cwd=repo, capture_output=True, text=True, env=env)
    ran = subprocess.run([str(SCRIPTS / "ready-check.sh")], cwd=repo, capture_output=True, text=True, env=env)
    lines = ran.stdout.splitlines()

    assert resolved.returncode == 3, (resolved.returncode, resolved.stdout, resolved.stderr)
    assert ran.returncode == 1, (ran.returncode, ran.stdout, ran.stderr)
    assert any(l.startswith("fail") and "veri: fast tests:" in l for l in lines), (ran.stdout, ran.stderr)
    assert lines and lines[-1] == "not ready — 1 rows to fix", (ran.stdout, ran.stderr)


@pytest.mark.process("ready-check.sh, a /bin/sh shim over veri/ready_check.py, run as a subprocess inside a repository whose full tier resolves to nothing")
def test_issue_3055_ready_check_with_no_full_tier_exits_1_with_a_fail_row_naming_the_claude_md_line_to_add(tmp_path):
    repo, env = build_ready_repo(tmp_path)
    (repo / "CLAUDE.md").write_text("veri: fast tests: `make unit`\n")
    _git(repo, "mv", "tests/test_one.py", "tests/one_test.py")
    _git(repo, "commit", "-q", "-am", "drop the full tier line")
    resolved = subprocess.run([str(SCRIPTS / "detect-test-command.sh"), "--tier", "all"], cwd=repo, capture_output=True, text=True, env=env)
    ran = subprocess.run([str(SCRIPTS / "ready-check.sh")], cwd=repo, capture_output=True, text=True, env=env)
    lines = ran.stdout.splitlines()

    assert resolved.returncode == 3, (resolved.returncode, resolved.stdout, resolved.stderr)
    assert ran.returncode == 1, (ran.returncode, ran.stdout, ran.stderr)
    assert any(l.startswith("fail") and "veri: all tests:" in l for l in lines), (ran.stdout, ran.stderr)
    assert lines and lines[-1] == "not ready — 1 rows to fix", (ran.stdout, ran.stderr)


@pytest.mark.process("ready-check.sh, a /bin/sh shim over veri/ready_check.py, run as a subprocess inside a repository where no workflow triggers on pull_request")
def test_issue_3055_ready_check_with_no_pull_request_workflow_exits_1_with_a_fail_row_naming_its_fix(tmp_path):
    repo, env = build_ready_repo(tmp_path)
    env.pop("VERI_CI_ON_PR", None)
    (repo / ".github" / "workflows" / "ci.yml").write_text(
        "name: ci\non:\n  push:\n    branches: [main]\njobs:\n  t:\n    runs-on: ubuntu-latest\n    steps:\n      - run: make test\n")
    _git(repo, "commit", "-q", "-am", "ci on push only")
    ran = subprocess.run([str(SCRIPTS / "ready-check.sh")], cwd=repo, capture_output=True, text=True, env=env)
    lines = ran.stdout.splitlines()

    assert ran.returncode == 1, (ran.returncode, ran.stdout, ran.stderr)
    assert any(l.startswith("fail") and "pull_request" in l for l in lines), (ran.stdout, ran.stderr)
    assert lines and lines[-1] == "not ready — 1 rows to fix", (ran.stdout, ran.stderr)


@pytest.mark.process("ready-check.sh, a /bin/sh shim over veri/ready_check.py, run as a subprocess on a feature branch whose own tree has no pull_request workflow while the default branch's tip has one")
def test_issue_3055_ready_check_reads_the_pull_request_workflow_at_the_default_branch_tip_not_head(tmp_path):
    repo, env = build_ready_repo(tmp_path)
    env.pop("VERI_CI_ON_PR", None)
    _git(repo, "checkout", "-q", "-b", "feature")
    (repo / ".github" / "workflows" / "ci.yml").write_text(
        "name: ci\non:\n  push:\n    branches: [main]\njobs:\n  t:\n    runs-on: ubuntu-latest\n    steps:\n      - run: make test\n")
    _git(repo, "commit", "-q", "-am", "feature drops the pull_request trigger")
    ran = subprocess.run([str(SCRIPTS / "ready-check.sh")], cwd=repo, capture_output=True, text=True, env=env)
    lines = ran.stdout.splitlines()

    assert ran.returncode == 0, (ran.returncode, ran.stdout, ran.stderr)
    assert lines and lines[-1] == "ready", (ran.stdout, ran.stderr)


@pytest.mark.process("ready-check.sh, a /bin/sh shim over veri/ready_check.py, run as a subprocess in a repository whose origin/HEAD names a default branch other than main")
def test_issue_3055_ready_check_reads_the_pull_request_workflow_at_the_branch_origin_head_names(tmp_path):
    repo, env = build_ready_repo(tmp_path)
    env.pop("VERI_CI_ON_PR", None)
    _git(repo, "update-ref", "refs/remotes/origin/trunk", "HEAD")
    _git(repo, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/trunk")
    (repo / ".github" / "workflows" / "ci.yml").write_text(
        "name: ci\non:\n  push:\n    branches: [main]\njobs:\n  t:\n    runs-on: ubuntu-latest\n    steps:\n      - run: make test\n")
    _git(repo, "commit", "-q", "-am", "main drops the pull_request trigger")
    ran = subprocess.run([str(SCRIPTS / "ready-check.sh")], cwd=repo, capture_output=True, text=True, env=env)
    lines = ran.stdout.splitlines()

    assert ran.returncode == 0, (ran.returncode, ran.stdout, ran.stderr)
    assert lines and lines[-1] == "ready", (ran.stdout, ran.stderr)


@pytest.mark.process("ready-check.sh, a /bin/sh shim over veri/ready_check.py, run as a subprocess from a directory outside the repository it is pointed at")
def test_issue_3055_ready_check_given_a_repo_root_from_outside_it_checks_that_repository(tmp_path):
    repo, env = build_ready_repo(tmp_path)
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    env = {**env, "GIT_CEILING_DIRECTORIES": str(tmp_path)}
    ran = subprocess.run([str(SCRIPTS / "ready-check.sh"), str(repo)], cwd=elsewhere, capture_output=True, text=True, env=env)
    lines = ran.stdout.splitlines()

    assert ran.returncode == 0, (ran.returncode, ran.stdout, ran.stderr)
    assert lines and lines[-1] == "ready", (ran.stdout, ran.stderr)



@pytest.mark.process("ready-check.sh, a /bin/sh shim over veri/ready_check.py, run as a subprocess with no argument from a linked worktree whose tree lacks a row the main working tree holds")
def test_issue_3055_ready_check_with_no_argument_from_a_linked_worktree_checks_the_main_working_tree(tmp_path):
    repo, env = build_ready_repo(tmp_path)
    linked = tmp_path / "linked"
    _git(repo, "worktree", "add", "-q", "-b", "feature", str(linked))
    (linked / "CLAUDE.md").write_text("veri: all tests: `make test`\n")
    _git(linked, "mv", "tests/test_one.py", "tests/one_test.py")
    _git(linked, "commit", "-q", "-am", "drop the fast tier line")
    ran = subprocess.run([str(SCRIPTS / "ready-check.sh")], cwd=linked, capture_output=True, text=True, env=env)
    lines = ran.stdout.splitlines()

    assert ran.returncode == 0, (ran.returncode, ran.stdout, ran.stderr)
    assert lines and lines[-1] == "ready", (ran.stdout, ran.stderr)
