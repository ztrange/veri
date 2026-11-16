"""In-process cases for veri/solvable_issues.py in a repository whose CLAUDE.md names a stack branch (PRD 034.1c, KJ9)."""
import importlib
import json

import pytest


@pytest.fixture(autouse=True)
def no_ambient_tunables(monkeypatch):
    for name in ("VERI_GH_JSON", "VERI_LABEL", "VERI_PRIORITY_LABEL"):
        monkeypatch.delenv(name, raising=False)


@pytest.fixture(autouse=True)
def case_works_in_its_scratch_tree(tmp_path, monkeypatch):
    """solvable_issues.py runs git with no cwd; from the case's own tmp_path the git guard sees every call."""
    monkeypatch.chdir(tmp_path)


@pytest.fixture
def solvable_issues():
    return importlib.import_module("veri.solvable_issues")


def opted_in(number):
    return {"number": number, "title": "issue %d" % number, "state": "OPEN",
            "labels": [{"name": "ready-for-agent"}], "body": "## Blocked by\n\nNone.\n"}


def world(tmp_path, fake_processes, monkeypatch, stack_line, joined, origin_url="https://github.com/Me/Repo.git\n"):
    """A main clone at <tmp_path>/repo whose CLAUDE.md holds <stack_line>, issues 5 and 6 open and opted in, no open
    pull request, and <joined> the closed pull requests into the stack GitHub lists."""
    main_tree = tmp_path / "repo"
    main_tree.mkdir()
    (main_tree / "CLAUDE.md").write_text(stack_line)
    fixtures = tmp_path / "gh"
    fixtures.mkdir()
    (fixtures / "issues.json").write_text(json.dumps([opted_in(5), opted_in(6)]))
    (fixtures / "prs.json").write_text("[]")
    (fixtures / "stack-prs.json").write_text(json.dumps(joined))
    monkeypatch.setenv("VERI_GH_JSON", str(fixtures))
    return fake_processes.answers({
        "git worktree list --porcelain": (0, "worktree %s\nHEAD 0000000\nbranch refs/heads/trunk\n" % main_tree, ""),
        "git check-ref-format --branch": lambda line, **_: (0, line.rsplit(" ", 1)[-1] + "\n", ""),
        "git symbolic-ref --quiet --short refs/remotes/origin/HEAD": (0, "origin/trunk\n", ""),
        "git ls-remote --symref origin HEAD": (0, "ref: refs/heads/trunk\tHEAD\n", ""),
        "git remote get-url origin": (0, origin_url, "") if origin_url else (2, "", "error: No such remote 'origin'\n"),
    })


JOINED = [{"body": "Closes #5", "state": "MERGED"},
          {"body": "Closes #6", "state": "closed", "merged_at": None}]


def test_an_open_issue_a_pull_request_merged_into_the_stack_closes_is_not_listed(
        tmp_path, fake_processes, monkeypatch, run_cli, solvable_issues):
    world(tmp_path, fake_processes, monkeypatch, "veri: stack branch: stack\n", JOINED)

    assert run_cli(solvable_issues, []) == (0, "6\n", "")


@pytest.mark.parametrize("repo, listed", [("me/repo", "6\n"), ("someone/else", "5\n6\n")])
def test_with_repo_the_stack_claim_applies_only_to_the_repository_the_local_claude_md_belongs_to(
        tmp_path, fake_processes, monkeypatch, run_cli, solvable_issues, repo, listed):
    world(tmp_path, fake_processes, monkeypatch, "veri: stack branch: stack\n", JOINED)

    assert run_cli(solvable_issues, ["--repo", repo])[:2] == (0, listed)


@pytest.mark.parametrize("url", ["/srv/origin.git\n", None])
def test_with_repo_and_a_stack_named_an_origin_that_names_no_github_repository_is_exit_2(
        tmp_path, fake_processes, monkeypatch, run_cli, solvable_issues, url):
    world(tmp_path, fake_processes, monkeypatch, "veri: stack branch: stack\n", JOINED, origin_url=url)

    code, out, err = run_cli(solvable_issues, ["--repo", "me/repo"])

    assert (code, out, "origin" in err) == (2, "", True)
