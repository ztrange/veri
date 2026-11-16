"""Cases for park-issue.sh that start a real process: the entry point, and the cases whose PR argument has the module
read a real git origin. The module's other logic is tested in-process, in tests/py/unit/test_park_issue.py."""
import os
import subprocess

import pytest

from conftest import SCRIPTS

GH_STUB = """#!/bin/sh
{
  echo "ARGS: $*"
  for a in "$@"; do [ -f "$a" ] && cat "$a"; done
  [ -t 0 ] || cat
} >> "$GH_LOG" 2>/dev/null
echo '{}'
"""


URL_REFUSING_GH_STUB = """#!/bin/sh
echo "ARGS: $*" >> "$GH_LOG"
for a in "$@"; do
  case "$a" in
    */issues/http*) echo "gh: Not Found (HTTP 404)" >&2; exit 1 ;;
  esac
done
echo '{}'
"""


@pytest.mark.process("park-issue.sh run against a gh stub that refuses a label write aimed at a URL, from a scratch git repo whose origin names the PR's repository")
def test_park_issue_labels_the_pr_parked_through_the_number_path_when_given_a_pr_url_2429(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    gh = bin_dir / "gh"
    gh.write_text(URL_REFUSING_GH_STUB)
    gh.chmod(0o755)
    log = tmp_path / "gh.log"
    log.write_text("")
    repo = tmp_path / "repo"
    repo.mkdir()
    for git_args in (["init", "-q"], ["remote", "add", "origin", "https://github.com/ztrange/veri.git"]):
        subprocess.run(["git", *git_args], cwd=repo, check=True, capture_output=True)

    ran = subprocess.run([str(SCRIPTS / "park-issue.sh"), "7", "held for review", "a human merges",
                          "https://github.com/ztrange/veri/pull/12"],
                         cwd=repo, capture_output=True, text=True, stdin=subprocess.DEVNULL,
                         env={"PATH": "%s:/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin" % bin_dir,
                              "GH_LOG": str(log), "PYTHONDONTWRITEBYTECODE": "1"})

    recorded = log.read_text()
    assert "repos/{owner}/{repo}/issues/12/labels" in recorded, recorded
    assert ran.returncode == 0, ran.stderr


@pytest.mark.process("park-issue.sh run against a gh stub that records every call, from a scratch git repo whose origin names another repository")
def test_park_issue_with_a_pr_url_for_another_repository_exits_2_with_usage_and_calls_no_gh_2457(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    gh = bin_dir / "gh"
    gh.write_text(GH_STUB)
    gh.chmod(0o755)
    log = tmp_path / "gh.log"
    log.write_text("")
    repo = tmp_path / "repo"
    repo.mkdir()
    for git_args in (["init", "-q"], ["remote", "add", "origin", "https://github.com/ztrange/veri.git"]):
        subprocess.run(["git", *git_args], cwd=repo, check=True, capture_output=True)
    env = {"PATH": "%s:/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin" % bin_dir,
           "GH_LOG": str(log), "PYTHONDONTWRITEBYTECODE": "1"}

    for url in ("https://github.com/some-other-org/veri/pull/12", "https://github.com/ztrange/some-other-repo/pull/12"):
        ran = subprocess.run([str(SCRIPTS / "park-issue.sh"), "7", "held for review", "a human merges", url],
                             cwd=repo, capture_output=True, text=True, stdin=subprocess.DEVNULL, env=env)

        usage = [line for line in ran.stderr.splitlines() if line.startswith("usage:")]
        assert ran.returncode == 2, (url, ran.returncode, ran.stderr, log.read_text())
        assert usage, (url, ran.stderr)
        assert log.read_text() == "", (url, log.read_text())


@pytest.mark.process("park-issue.sh run against a gh stub that records every call, from a directory with no git origin")
def test_park_issue_with_a_pr_url_where_no_origin_can_be_read_exits_2_with_usage_and_calls_no_gh_2457(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    gh = bin_dir / "gh"
    gh.write_text(GH_STUB)
    gh.chmod(0o755)
    log = tmp_path / "gh.log"
    log.write_text("")
    bare = tmp_path / "no-repo"
    bare.mkdir()
    env = {"PATH": "%s:/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin" % bin_dir,
           "GH_LOG": str(log), "PYTHONDONTWRITEBYTECODE": "1", "GIT_CEILING_DIRECTORIES": str(tmp_path)}

    ran = subprocess.run([str(SCRIPTS / "park-issue.sh"), "7", "held for review", "a human merges",
                          "https://github.com/some-other-org/veri/pull/12"],
                         cwd=bare, capture_output=True, text=True, stdin=subprocess.DEVNULL, env=env)

    usage = [line for line in ran.stderr.splitlines() if line.startswith("usage:")]
    assert ran.returncode == 2, (ran.returncode, ran.stderr, log.read_text())
    assert usage, ran.stderr
    assert log.read_text() == "", log.read_text()


@pytest.mark.process("park-issue.sh run against a gh stub that records every call, from scratch git repos whose origin names the PR's repository in another form")
def test_park_issue_labels_the_pr_parked_when_the_origin_names_the_same_repository_as_an_https_dot_git_or_scp_url_2457(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    gh = bin_dir / "gh"
    gh.write_text(GH_STUB)
    gh.chmod(0o755)
    log = tmp_path / "gh.log"
    env = {"PATH": "%s:/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin" % bin_dir,
           "GH_LOG": str(log), "PYTHONDONTWRITEBYTECODE": "1"}

    for n, origin in enumerate(("https://github.com/ztrange/veri.git", "git@github.com:ztrange/veri.git")):
        repo = tmp_path / ("repo%d" % n)
        repo.mkdir()
        for git_args in (["init", "-q"], ["remote", "add", "origin", origin]):
            subprocess.run(["git", *git_args], cwd=repo, check=True, capture_output=True)
        log.write_text("")

        ran = subprocess.run([str(SCRIPTS / "park-issue.sh"), "7", "held for review", "a human merges",
                              "https://github.com/ztrange/veri/pull/12"],
                             cwd=repo, capture_output=True, text=True, stdin=subprocess.DEVNULL, env=env)

        recorded = log.read_text()
        assert ran.returncode == 0, (origin, ran.returncode, ran.stderr, recorded)
        assert "issues/12/labels" in recorded, (origin, recorded)


@pytest.mark.process("park-issue.sh run against a gh stub that records every call, from a scratch git repo whose origin names the PR's repository")
def test_park_issue_with_a_pr_of_0_or_with_leading_zeros_exits_2_with_usage_and_calls_no_gh_2457(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    gh = bin_dir / "gh"
    gh.write_text(GH_STUB)
    gh.chmod(0o755)
    log = tmp_path / "gh.log"
    log.write_text("")
    repo = tmp_path / "repo"
    repo.mkdir()
    for git_args in (["init", "-q"], ["remote", "add", "origin", "https://github.com/ztrange/veri.git"]):
        subprocess.run(["git", *git_args], cwd=repo, check=True, capture_output=True)
    env = {"PATH": "%s:/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin" % bin_dir,
           "GH_LOG": str(log), "PYTHONDONTWRITEBYTECODE": "1"}

    for pr in ("0", "007", "https://github.com/ztrange/veri/pull/0", "https://github.com/ztrange/veri/pull/007"):
        ran = subprocess.run([str(SCRIPTS / "park-issue.sh"), "7", "held for review", "a human merges", pr],
                             cwd=repo, capture_output=True, text=True, stdin=subprocess.DEVNULL, env=env)

        usage = [line for line in ran.stderr.splitlines() if line.startswith("usage:")]
        assert ran.returncode == 2, (pr, ran.returncode, ran.stderr, log.read_text())
        assert usage, (pr, ran.stderr)
        assert log.read_text() == "", (pr, log.read_text())


@pytest.mark.process("park-issue.sh run against a gh stub that records every call, from a scratch git repo whose origin names the PR's repository")
def test_park_issue_labels_the_pr_parked_and_records_its_url_when_given_a_pr_url_of_this_repository_or_a_bare_number_2457(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    gh = bin_dir / "gh"
    gh.write_text(GH_STUB)
    gh.chmod(0o755)
    log = tmp_path / "gh.log"
    repo = tmp_path / "repo"
    repo.mkdir()
    for git_args in (["init", "-q"], ["remote", "add", "origin", "https://github.com/ztrange/veri.git"]):
        subprocess.run(["git", *git_args], cwd=repo, check=True, capture_output=True)
    env = {"PATH": "%s:/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin" % bin_dir,
           "GH_LOG": str(log), "PYTHONDONTWRITEBYTECODE": "1"}

    for pr in ("https://github.com/ztrange/veri/pull/12", "12"):
        log.write_text("")
        ran = subprocess.run([str(SCRIPTS / "park-issue.sh"), "7", "held for review", "a human merges", pr],
                             cwd=repo, capture_output=True, text=True, stdin=subprocess.DEVNULL, env=env)

        recorded = log.read_text()
        assert ran.returncode == 0, (pr, ran.returncode, ran.stderr, recorded)
        assert "issues/7/labels" in recorded, (pr, recorded)
        assert "issues/12/labels" in recorded, (pr, recorded)
        assert "\nPR: %s\n" % pr in recorded, (pr, recorded)
