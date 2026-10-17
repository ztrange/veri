"""skill-drift.sh's block, driven through the CLI of veri/skill_drift.py."""
import importlib
import subprocess

import pytest

REF = "refs/remotes/origin/main"
ABSENT = "0123456789abcdef0123456789abcdef01234567"
GIT_BOUNDARY = "a real git repository, its clone and a fetch from the clone's origin"


@pytest.fixture
def skill_drift():
    return importlib.import_module("veri.skill_drift")


def git(repo, *args):
    done = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True)
    return done.stdout.strip()


def new_repo(path):
    path.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=path, check=True)
    git(path, "config", "user.name", "Test")
    git(path, "config", "user.email", "test@example.com")


def touch_commit(repo, path, subject):
    target = repo / path
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "a") as handle:
        handle.write(subject + "\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", subject)


def upstream_and_clone(tmp_path, *commits):
    """An upstream whose first commit is the pin, then <commits> after it, and a clone of it."""
    upstream, clone = tmp_path / "upstream", tmp_path / "clone"
    new_repo(upstream)
    touch_commit(upstream, "skills/tdd/scripts/run-leaf.sh", "feat: the pinned skill (#9)")
    pinned = git(upstream, "rev-parse", "HEAD")
    for path, subject in commits:
        touch_commit(upstream, path, subject)
    subprocess.run(["git", "clone", "-q", str(upstream), str(clone)], cwd=tmp_path, check=True)
    return upstream, clone, pinned


def env_for(pinned, clone, ref=REF):
    return {"VERI_SKILL_COMMIT": pinned, "VERI_SKILL_CLONE": str(clone), "VERI_SKILL_REF": ref}


@pytest.mark.process(GIT_BOUNDARY)
def test_two_12_commits_and_one_later_15_commit_after_the_pin_list_15_before_12_with_their_counts_then_the_resume_line(tmp_path, run_cli, skill_drift):
    upstream, clone, pinned = upstream_and_clone(
        tmp_path,
        ("skills/tdd/scripts/supervise.sh", "fix: the supervisor's first window (#12)"),
        ("skills/tdd/scripts/supervise.sh", "fix: the supervisor's second window (#12)"),
        ("skills/tdd/scripts/run-leaf.sh", "feat: a leaf names its model (#15)"))

    code, out, err = run_cli(skill_drift, [], env=env_for(pinned, clone))

    assert (code, err) == (0, "")
    assert out.splitlines() == [
        "#### Skill drift since the pinned commit",
        "Pinned skill commit: %s." % git(upstream, "rev-parse", "--short", pinned),
        "Conductor-path changes on %s since then:" % REF,
        "- #15 — feat: a leaf names its model (#15) (1 commits)",
        "- #12 — fix: the supervisor's second window (#12) (2 commits)",
        "Resume with VERI_NEW_SKILL=1 to run on these."]


@pytest.mark.process(GIT_BOUNDARY)
def test_commits_after_the_pin_touching_only_tests_docs_or_makefile_are_not_listed_the_block_says_none(tmp_path, run_cli, skill_drift):
    upstream, clone, pinned = upstream_and_clone(
        tmp_path,
        ("skills/tdd/scripts/tests/run-leaf.test.sh", "test: a leaf's case (#20)"),
        ("docs/notes.md", "docs: a note (#21)"),
        ("Makefile", "build: a recipe (#22)"))

    code, out, err = run_cli(skill_drift, [], env=env_for(pinned, clone))

    assert (code, err) == (0, "")
    assert out.splitlines() == [
        "#### Skill drift since the pinned commit",
        "Pinned skill commit: %s." % git(upstream, "rev-parse", "--short", pinned),
        "Conductor-path changes on %s since then: none." % REF]


@pytest.mark.process(GIT_BOUNDARY)
def test_a_commit_after_the_pin_with_no_trailing_number_is_listed_by_short_sha(tmp_path, run_cli, skill_drift):
    upstream, clone, pinned = upstream_and_clone(
        tmp_path, ("skills/tdd/scripts/supervise.sh", "fix: a hand-pushed supervisor fix"))
    short = git(upstream, "rev-parse", "--short", "HEAD")

    code, out, err = run_cli(skill_drift, [], env=env_for(pinned, clone))

    assert (code, err) == (0, "")
    assert "- %s fix: a hand-pushed supervisor fix\n" % short in out.splitlines(keepends=True)


def test_an_unpinned_run_or_an_unset_or_empty_skill_commit_answers_not_pinned(tmp_path, run_cli, skill_drift):
    want = "Skill drift: unavailable — run was not pinned to a skill commit\n"
    base = {"VERI_SKILL_CLONE": str(tmp_path), "VERI_SKILL_REF": REF}
    variants = {
        "unpinned": {**base, "VERI_SKILL_UNPINNED": "1", "VERI_SKILL_COMMIT": ABSENT},
        "unset": base,
        "empty": {**base, "VERI_SKILL_COMMIT": ""},
    }
    got = {name: run_cli(skill_drift, [], env=env) for name, env in variants.items()}

    assert got == {name: (0, want, "") for name in variants}


@pytest.mark.process(GIT_BOUNDARY)
def test_an_unset_skill_clone_or_one_that_is_not_a_git_work_tree_answers_clone_not_known(tmp_path, run_cli, skill_drift):
    (tmp_path / "not-a-clone").mkdir()
    want = "Skill drift: unavailable — skill clone not known\n"
    variants = {
        "unset": {"VERI_SKILL_COMMIT": ABSENT, "VERI_SKILL_REF": REF},
        "not-a-work-tree": env_for(ABSENT, tmp_path / "not-a-clone"),
    }
    got = {name: run_cli(skill_drift, [], env=env) for name, env in variants.items()}

    assert got == {name: (0, want, "") for name in variants}


@pytest.mark.process(GIT_BOUNDARY)
def test_a_pinned_commit_the_clone_does_not_have_answers_it_is_not_in_the_clone(tmp_path, run_cli, skill_drift):
    _, clone, _ = upstream_and_clone(tmp_path)

    code, out, err = run_cli(skill_drift, [], env=env_for(ABSENT, clone))

    assert (code, out, err) == (
        0, "Skill drift: unavailable — pinned commit %s is not in %s\n" % (ABSENT, clone), "")


@pytest.mark.process(GIT_BOUNDARY)
def test_a_ref_that_does_not_resolve_in_the_clone_answers_it_does_not_resolve(tmp_path, run_cli, skill_drift):
    _, clone, pinned = upstream_and_clone(tmp_path)

    code, out, err = run_cli(skill_drift, [], env=env_for(pinned, clone, "refs/remotes/origin/absent"))

    assert (code, out, err) == (
        0, "Skill drift: unavailable — refs/remotes/origin/absent does not resolve in %s\n" % clone, "")


@pytest.mark.process(GIT_BOUNDARY)
def test_a_clone_whose_origin_cannot_be_fetched_still_lists_then_says_so(tmp_path, run_cli, skill_drift):
    upstream, clone, pinned = upstream_and_clone(
        tmp_path, ("skills/tdd/scripts/supervise.sh", "fix: the supervisor's window (#12)"))
    git(clone, "remote", "set-url", "origin", str(tmp_path / "gone"))

    code, out, err = run_cli(skill_drift, [], env=env_for(pinned, clone))

    assert (code, err) == (0, "")
    assert out.splitlines() == [
        "#### Skill drift since the pinned commit",
        "Pinned skill commit: %s." % git(upstream, "rev-parse", "--short", pinned),
        "Conductor-path changes on %s since then:" % REF,
        "- #12 — fix: the supervisor's window (#12) (1 commits)",
        "Resume with VERI_NEW_SKILL=1 to run on these.",
        "origin could not be fetched — list is as of the last fetch of %s" % REF]


@pytest.mark.process(GIT_BOUNDARY)
def test_the_skills_tdd_directory_as_the_clone_still_lists_conductor_path_commits_and_leaves_out_tests_only_ones(tmp_path, run_cli, skill_drift):
    _, clone, pinned = upstream_and_clone(
        tmp_path,
        ("skills/tdd/scripts/supervise.sh", "fix: the supervisor's window (#12)"),
        ("skills/tdd/scripts/tests/run-leaf.test.sh", "test: a leaf's case (#20)"))

    code, out, err = run_cli(skill_drift, [], env=env_for(pinned, clone / "skills" / "tdd"))

    assert (code, err) == (0, "")
    lines = out.splitlines()
    assert "- #12 — fix: the supervisor's window (#12) (1 commits)" in lines
    assert [line for line in lines if line.startswith("- #20 ")] == []


@pytest.mark.process(GIT_BOUNDARY)
def test_an_unset_or_empty_skill_ref_on_a_pinned_run_with_a_known_clone_answers_one_unavailable_line(tmp_path, run_cli, skill_drift):
    _, clone, pinned = upstream_and_clone(tmp_path)
    base = {"VERI_SKILL_COMMIT": pinned, "VERI_SKILL_CLONE": str(clone)}
    got = {name: run_cli(skill_drift, [], env=env) for name, env in
           {"unset": base, "empty": {**base, "VERI_SKILL_REF": ""}}.items()}

    for name, (code, out, err) in got.items():
        assert code == 0, name
        assert out.startswith("Skill drift: unavailable — ") and out.count("\n") == 1, name
        assert "Traceback" not in err, name
