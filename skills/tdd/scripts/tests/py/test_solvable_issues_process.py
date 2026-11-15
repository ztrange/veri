"""Process cases split from test_solvable_issues.py: they start a real process or put a local fake in front of one."""
import importlib
import json
import os
import pathlib
import re
import subprocess
import tempfile
import pytest
from conftest import fake_pid_file_ps
from test_run_conductor import fake_claude_exiting, past_the_guards, scratch_tmpdir
from test_run_conductor import state_label_clearing_answers_removed  # noqa: F401 -- autouse: the launch's label clearing faked


@pytest.fixture(autouse=True)
def no_ambient_tunables(monkeypatch):
    for name in ("VERI_GH_JSON", "VERI_LABEL", "VERI_PRIORITY_LABEL"):
        monkeypatch.delenv(name, raising=False)


def conducting(monkeypatch, *numbers):
    """pid_file's ps answering every pid as a claude under run_conductor.py."""
    fake_pid_file_ps(monkeypatch)


@pytest.fixture
def conductor_process(request):
    """conductor_process(*numbers) starts a real process whose command line names run-conductor.sh <n> for each, returning its pid; killed at the end."""
    started = []

    def start(*numbers):
        claude = pathlib.Path(tempfile.mkdtemp(prefix="exp-claude-")) / "claude"
        claude.symlink_to("/bin/sh")
        parent = subprocess.Popen(["/bin/sh", "-c", 'exec 3<&0; "$1" -c "read x" <&3 3<&- & echo $!; wait', "run_conductor.py", str(claude)],
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        started.append(parent)
        return int(parent.stdout.readline())

    yield start
    for child in started:
        child.stdin.close()
        child.wait()
        child.stdout.close()


@pytest.fixture
def solvable_issues():
    return importlib.import_module("veri.solvable_issues")


def opted_in(number):
    return {"number": number, "title": "issue %d" % number, "state": "OPEN",
            "labels": [{"name": "ready-for-agent"}], "body": "## Blocked by\n\nNone.\n"}


REPO_ROOT = pathlib.Path(__file__).resolve().parents[5]


@pytest.fixture
def plant_claim():
    """plant_claim(main_tree, number, pid) writes .tdd/wt/<number>/.tdd/conductor.pid under main_tree."""
    def plant(main_tree, number, pid):
        lock = main_tree / ".tdd" / "wt" / str(number) / ".tdd" / "conductor.pid"
        lock.parent.mkdir(parents=True)
        lock.write_text("%d\n" % pid)
    return plant


@pytest.mark.process("git: a real repository whose worktree branch is pushed to a bare remote")
def test_cli_lists_an_issue_whose_branch_is_on_the_remote_with_no_open_pr_and_no_live_pid(tmp_path, run_cli, solvable_issues):
    def git(*args):
        return subprocess.run(["git", "-c", "user.name=veri", "-c", "user.email=veri@example.test", *args],
                              check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout

    fixtures, repo, remote = tmp_path / "fixtures", tmp_path / "pushed", tmp_path / "pushed-remote.git"
    fixtures.mkdir()
    (fixtures / "issues.json").write_text(json.dumps([opted_in(191)]))
    (fixtures / "prs.json").write_text("[]")
    git("init", "-q", "-b", "main", str(repo))
    git("-C", str(repo), "commit", "-q", "--allow-empty", "-m", "initial")
    git("init", "-q", "--bare", str(remote))
    git("-C", str(repo), "remote", "add", "origin", str(remote))
    worktree = repo / ".tdd" / "wt" / "191"
    git("-C", str(repo), "worktree", "add", "-q", "-b", "tdd/191-slug", str(worktree), "main")
    git("-C", str(worktree), "push", "-q", "--set-upstream", "origin", "HEAD")

    on_remote = git("-C", str(repo), "ls-remote", "--heads", "origin", "tdd/191-slug")
    answer = run_cli(solvable_issues, [], env={"VERI_GH_JSON": str(fixtures)}, cwd=repo)

    assert (bool(on_remote), answer) == (True, (0, "191\n", ""))


def write_gh_fixtures(directory, issues):
    directory.mkdir()
    (directory / "issues.json").write_text(json.dumps(issues))
    (directory / "prs.json").write_text("[]")


def git_in(*args):
    return subprocess.run(["git", "-c", "user.name=veri", "-c", "user.email=veri@example.test", *args],
                          check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout


@pytest.mark.process("git and solvable-issues.sh: a linked worktree's run through a symlink to the skill directory")
def test_cli_run_through_a_symlink_to_the_skill_directory_from_a_linked_worktree_answers_as_in_place_withholding_the_issue_locked_under_the_main_tree(tmp_path, run_cli, plant_claim, conductor_process, solvable_issues):
    fixtures, repo, linked, link = tmp_path / "fixtures", tmp_path / "repo", tmp_path / "linked", tmp_path / "skill-link"
    write_gh_fixtures(fixtures, [opted_in(5), opted_in(6)])
    git_in("init", "-q", "-b", "main", str(repo))
    git_in("-C", str(repo), "commit", "-q", "--allow-empty", "-m", "initial")
    git_in("-C", str(repo), "worktree", "add", "-q", "-b", "linked", str(linked), "main")
    plant_claim(repo, 5, conductor_process(5))
    link.symlink_to(REPO_ROOT / "skills" / "tdd", target_is_directory=True)

    in_place = run_cli(solvable_issues, [], env={"VERI_GH_JSON": str(fixtures)}, cwd=linked)
    through_link = subprocess.run([str(link / "scripts" / "solvable-issues.sh")], cwd=linked, text=True,
                                  env=dict(os.environ, VERI_GH_JSON=str(fixtures)),
                                  stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    assert (in_place, (through_link.returncode, through_link.stdout, through_link.stderr)) == ((0, "6\n", ""), (0, "6\n", ""))


def numbers_this_files_fixtures_name():
    text = pathlib.Path(__file__).read_text()
    return sorted({int(a or b) for a, b in re.findall(r'(?:opted_in|labelled|blocked_by)\((\d+)|"number": (\d+)', text)})


@pytest.mark.process("git: a surrounding repository whose main tree holds live conductor locks")
def test_cli_answer_is_unchanged_by_live_conductor_locks_under_the_surrounding_repository_for_unrelated_numbers_and_every_number_this_file_names(tmp_path, monkeypatch, run_cli, plant_claim, conductor_process, solvable_issues):
    unrelated, named = [108, 117, 120, 124], numbers_this_files_fixtures_name()
    fixtures, cwd = tmp_path / "fixtures", tmp_path / "no-claims"
    write_gh_fixtures(fixtures, [opted_in(n) for n in sorted(set(unrelated + named))])
    git_in("init", "-q", "-b", "main", str(cwd))
    surroundings = {"surrounding-unrelated": unrelated, "surrounding-every": named}
    conductor = conductor_process(*unrelated, *named)
    for name, numbers in surroundings.items():
        git_in("init", "-q", "-b", "main", str(tmp_path / name))
        for n in numbers:
            plant_claim(tmp_path / name, n, conductor)

    def answers():
        run = run_cli(solvable_issues, [], env={"VERI_GH_JSON": str(fixtures)}, cwd=cwd)
        monkeypatch.delenv("VERI_PRIORITY_LABEL", raising=False)
        label_run = run_cli(solvable_issues, [], env={"VERI_GH_JSON": str(fixtures)}, cwd=cwd)
        return {"run": run, "label_run": label_run}

    no_lock = answers()
    under = {}
    for name in surroundings:
        monkeypatch.chdir(tmp_path / name)
        under[name] = answers()

    assert (bool(named), no_lock["run"][0], bool(no_lock["run"][1]), under) == (
        True, 0, True, {name: no_lock for name in surroundings})


def test_in_flight_reads_a_fresh_run_whose_worktree_did_not_exist_at_launch_as_in_flight_while_its_conductor_runs_issue_2390(
        tmp_path, monkeypatch, run_cli, solvable_issues):
    past_the_guards(monkeypatch)
    monkeypatch.delenv("VERI_NEW_SKILL", raising=False)
    scratch_tmpdir(tmp_path, monkeypatch)
    run_conductor = importlib.import_module("veri.run_conductor")
    import github
    monkeypatch.setattr(github, "gh_issue_view", lambda number, field: "## Problem\n\nA fresh run.\n")
    fake_claude_exiting(monkeypatch, 0, 0)
    conducting(monkeypatch, 4242)
    answer, seen = subprocess.run, []

    def fake_git(base, *args, **kwargs):
        resolved = args == ("rev-parse", "HEAD")
        out = "1111111111111111111111111111111111111111\n" if resolved else ""
        return subprocess.CompletedProcess(args, 0 if resolved else 2, out if kwargs.get("text") else out.encode(), b"")

    monkeypatch.setattr(run_conductor, "git", fake_git)
    cwd = tmp_path / "cwd"
    cwd.mkdir()

    def reading_the_claim_while_running(args, *rest, **kwargs):
        if list(args)[:1] == ["fake-claude"]:
            if kwargs.get("preexec_fn") is not None:
                kwargs["preexec_fn"]()
            seen.append(solvable_issues.in_flight(str(cwd), 4242))
        return answer(args, *rest, **kwargs)

    monkeypatch.setattr(subprocess, "run", reading_the_claim_while_running)
    assert not (cwd / ".tdd" / "wt" / "4242").exists()

    code, _, err = run_cli(run_conductor, ["4242"], cwd=cwd)

    assert (code, seen, err) == (0, [True], "")
