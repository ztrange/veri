"""Process-starting cases split from unit/test_preserve_attempt.py, which holds the small cases of the same module."""
import importlib
import importlib.util
import os
import subprocess

import pytest

from repo_builder import commit_all, new_repo


@pytest.fixture
def preserve_attempt():
    return importlib.import_module("veri.preserve_attempt")


REF = "refs/veri/attempts/409/3/develop-green-1"
IDENT = {"GIT_AUTHOR_NAME": "veri", "GIT_AUTHOR_EMAIL": "veri@example.test",
         "GIT_COMMITTER_NAME": "veri", "GIT_COMMITTER_EMAIL": "veri@example.test"}
REJECTED = "rejected work"


def git_in(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True,
                          env={**os.environ, **IDENT})


def committed_repo(root):
    new_repo(root)
    commit_all(root, "initial", **{"stop-run.sh": "committed\n"})
    return root


def dirty_repo(root):
    committed_repo(root)
    (root / "stop-run.sh").write_text(REJECTED + "\n")
    return root


def write_ledger(repo, *steps):
    (repo / ".tdd").mkdir(exist_ok=True)
    lines = ["# Plan for #409", ""]
    lines += [f"- [{'x' if i == 0 else ' '}] {step}" for i, step in enumerate(steps)]
    (repo / ".tdd" / "issue-409.md").write_text("\n".join(lines) + "\n")
    git_in(repo, "add", ".tdd/issue-409.md")
    git_in(repo, "commit", "-q", "-m", "plan: scope #409")


def leaf_output(repo, log_text, out_text=None):
    (repo / ".tdd").mkdir(exist_ok=True)
    (repo / ".tdd" / "develop-green.log").write_text(log_text + "\n")
    if out_text is not None:
        (repo / ".tdd" / "develop-green.out").write_text(out_text + "\n")


def preserve_in(run_cli, preserve_attempt, monkeypatch, repo, *args):
    for name, value in IDENT.items():
        monkeypatch.setenv(name, value)
    return run_cli(preserve_attempt, list(args), cwd=repo)


def ref_resolves(repo, ref=REF):
    return git_in(repo, "rev-parse", "--verify", "--quiet", ref + "^{commit}").returncode == 0


def attempts(repo):
    directory = repo / ".tdd" / "attempts"
    return sorted(os.listdir(directory)) if directory.exists() else []


@pytest.mark.process("real git repository and its side ref")
def test_commits_the_worktree_to_the_ref_and_git_show_reads_it_back(
        tmp_path, monkeypatch, run_cli, preserve_attempt):
    repo = dirty_repo(tmp_path / "repo")
    code, out, err = preserve_in(run_cli, preserve_attempt, monkeypatch, repo, "409", "3", "develop-green", "1")
    shown = git_in(repo, "show", f"{REF}:stop-run.sh").stdout.rstrip("\n")
    assert (code, out, err, ref_resolves(repo), shown) == (0, "", "", True, REJECTED)


@pytest.mark.process("real git repository and its side ref")
def test_leaves_head_the_index_and_git_log_untouched(tmp_path, monkeypatch, run_cli, preserve_attempt):
    repo = dirty_repo(tmp_path / "repo")
    (repo / "staged.txt").write_text("staged\n")
    git_in(repo, "add", "staged.txt")

    def state():
        return (git_in(repo, "rev-parse", "HEAD").stdout, git_in(repo, "ls-files", "-s").stdout,
                git_in(repo, "log", "--oneline").stdout)

    before = state()
    code, out, err = preserve_in(run_cli, preserve_attempt, monkeypatch, repo, "409", "3", "develop-green", "1")
    assert (code, out, err, state()) == (0, "", "", before)


@pytest.mark.process("real git repository and the leaf's files")
def test_copies_the_leafs_log_and_final_output_to_names_carrying_step_phase_attempt_and_mark(
        tmp_path, monkeypatch, run_cli, preserve_attempt):
    repo = committed_repo(tmp_path / "repo")
    leaf_output(repo, "streamed progress", "final result text")
    code, out, err = preserve_in(run_cli, preserve_attempt, monkeypatch, repo,
                                 "409", "3", "develop-green", "1", "reject")
    copies = repo / ".tdd" / "attempts"
    assert (code, out, err) == (0, "", "")
    assert (copies / "3-develop-green-1-reject.log").read_text() == "streamed progress\n"
    assert (copies / "3-develop-green-1-reject.out").read_text() == "final result text\n"
    assert (repo / ".tdd" / "develop-green.log").is_file()
    assert (repo / ".tdd" / "develop-green.out").is_file()


@pytest.mark.process("real git repository and the leaf's files")
def test_preserves_the_log_of_a_leaf_that_wrote_no_final_output_with_exit_0(
        tmp_path, monkeypatch, run_cli, preserve_attempt):
    repo = committed_repo(tmp_path / "repo")
    leaf_output(repo, "streamed progress")
    code, out, err = preserve_in(run_cli, preserve_attempt, monkeypatch, repo,
                                 "409", "3", "develop-green", "1", "stuck")
    assert (code, out, err) == (0, "", "")
    assert (repo / ".tdd" / "attempts" / "3-develop-green-1-stuck.log").read_text() == "streamed progress\n"
    assert attempts(repo) == ["3-develop-green-1-stuck.log"]


@pytest.mark.process("real git repository and its side ref")
def test_preserves_the_tree_and_exits_0_when_the_leaf_wrote_neither_log_nor_output(
        tmp_path, monkeypatch, run_cli, preserve_attempt):
    repo = dirty_repo(tmp_path / "repo")
    code, out, err = preserve_in(run_cli, preserve_attempt, monkeypatch, repo,
                                 "409", "3", "develop-green", "1", "bail")
    assert (code, out, err, ref_resolves(repo), attempts(repo)) == (0, "", "", True, [])


@pytest.mark.process("real git repository and the leaf's files")
def test_copies_nothing_when_no_mark_is_given_log_present(tmp_path, monkeypatch, run_cli, preserve_attempt):
    repo = dirty_repo(tmp_path / "repo")
    leaf_output(repo, "streamed progress", "final result text")
    code, out, err = preserve_in(run_cli, preserve_attempt, monkeypatch, repo, "409", "3", "develop-green", "1")
    assert (code, out, err, ref_resolves(repo)) == (0, "", "", True)
    assert not (repo / ".tdd" / "attempts").exists()
    assert attempts(repo) == []


@pytest.mark.process("real git repository and ancestry of the side ref")
def test_leaves_the_preserved_commit_unreachable_from_head_with_a_message_carrying_no_rationale(
        tmp_path, monkeypatch, run_cli, preserve_attempt):
    repo = dirty_repo(tmp_path / "repo")
    rationale = "I used a helper because the verifier rejected the inline version"
    leaf_output(repo, rationale, rationale)
    code, out, err = preserve_in(run_cli, preserve_attempt, monkeypatch, repo,
                                 "409", "3", "develop-green", "1", "reject")
    reachable = git_in(repo, "merge-base", "--is-ancestor", REF, "HEAD").returncode == 0
    message = git_in(repo, "log", "-1", "--format=%B", REF).stdout.strip()
    assert (code, out, err, reachable, message) == (
        0, "", "", False, "attempt: issue 409 step 3 develop-green attempt 1")


@pytest.mark.process("real git repository and its side ref")
def test_names_the_ref_by_the_steps_ledger_index_not_its_prose(
        tmp_path, monkeypatch, run_cli, preserve_attempt):
    repo = dirty_repo(tmp_path / "repo")
    prose = "A leaf's output is kept under refs/veri, not the branch"
    write_ledger(repo, "The first step, already done", prose, "A third step nobody is on")
    code, out, err = preserve_in(run_cli, preserve_attempt, monkeypatch, repo, "409", prose, "develop-green", "1")
    refs = git_in(repo, "for-each-ref", "--format=%(refname)", "refs/veri/attempts").stdout.split()
    assert (code, out, err, refs) == (0, "", "", ["refs/veri/attempts/409/2/develop-green-1"])


@pytest.mark.process("real git repository and git check-ref-format")
def test_preserves_the_attempt_under_a_ref_git_accepts_when_the_step_title_carries_spaces_an_apostrophe_and_a_slash(
        tmp_path, monkeypatch, run_cli, preserve_attempt):
    repo = dirty_repo(tmp_path / "repo")
    prose = "A leaf's tree is kept under refs/veri, not the branch"
    code, out, err = preserve_in(run_cli, preserve_attempt, monkeypatch, repo, "409", prose, "develop-green", "1")
    found = git_in(repo, "for-each-ref", "--count=1", "--format=%(refname)", "refs/veri/attempts/409").stdout.strip()
    legal = git_in(repo, "check-ref-format", found).returncode == 0
    shown = git_in(repo, "show", f"{found}:stop-run.sh").stdout.rstrip("\n")
    assert (code, out, err, bool(found), legal, shown) == (0, "", "", True, True, REJECTED)


@pytest.mark.process("real git repository and the leaf's files")
def test_names_the_leafs_copies_by_the_steps_ledger_index_so_a_title_carrying_a_slash_writes_no_nested_path(
        tmp_path, monkeypatch, run_cli, preserve_attempt):
    repo = committed_repo(tmp_path / "repo")
    prose = "A leaf's output is kept under refs/veri, not the branch"
    write_ledger(repo, "The first step, already done", prose)
    leaf_output(repo, "streamed progress", "final result text")
    code, out, err = preserve_in(run_cli, preserve_attempt, monkeypatch, repo,
                                 "409", prose, "develop-green", "1", "reject")
    copies = repo / ".tdd" / "attempts"
    assert (code, out, err) == (0, "", "")
    assert (copies / "2-develop-green-1-reject.log").read_text() == "streamed progress\n"
    assert (copies / "2-develop-green-1-reject.out").read_text() == "final result text\n"
    assert attempts(repo) == ["2-develop-green-1-reject.log", "2-develop-green-1-reject.out"]


@pytest.mark.process("real git repository whose ref store refuses the write")
def test_says_on_stderr_that_it_could_not_preserve_the_attempt_when_the_ref_write_fails_for_another_reason(
        tmp_path, monkeypatch, run_cli, preserve_attempt):
    repo = dirty_repo(tmp_path / "repo")
    git_in(repo, "update-ref", "refs/veri/attempts/409/3", "HEAD")
    code, out, err = preserve_in(run_cli, preserve_attempt, monkeypatch, repo, "409", "3", "develop-green", "1")
    assert code != 0
    assert "preserve-attempt.sh" in err and "409" in err and "develop-green" in err


@pytest.mark.process("real git repository whose ref store refuses the write")
def test_exits_exactly_1_with_the_could_not_preserve_line_last_on_stderr_when_an_existing_ref_refuses_the_ref_write(
        tmp_path, monkeypatch, run_cli, preserve_attempt):
    repo = dirty_repo(tmp_path / "repo")
    git_in(repo, "update-ref", "refs/veri/attempts/409/3", "HEAD")
    code, out, err = preserve_in(run_cli, preserve_attempt, monkeypatch, repo, "409", "3", "develop-green", "1")
    expected = f"preserve-attempt.sh: could not preserve issue 409 step 3 develop-green attempt 1 to {REF}"
    assert (code, err.splitlines()[-1:]) == (1, [expected])


@pytest.mark.process("real git repository carrying a copy of the skill, left without a side ref")
def test_refuses_from_the_skills_own_scripts_directory_with_exit_2_one_stderr_line_and_no_ref_or_attempts_entry(
        tmp_path, monkeypatch, run_cli, preserve_attempt):
    decoy = committed_repo(tmp_path / "decoy")
    write_ledger(decoy, "The first step, already done", "A step the decoy is on")
    leaf_output(decoy, "decoy progress", "decoy result")
    ledger_before = (decoy / ".tdd" / "issue-409.md").read_text()
    scripts = decoy / "skills" / "tdd" / "scripts"
    (scripts / "veri").mkdir(parents=True)
    (scripts / "tests").mkdir()
    copy = scripts / "veri" / "preserve_attempt.py"
    with open(preserve_attempt.__file__) as source:
        copy.write_text(source.read())
    spec = importlib.util.spec_from_file_location("preserve_attempt_scratch_copy", copy)
    subject = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(subject)
    expected = ("preserve-attempt.sh: type this from the run's worktree,"
                " not from the skill's own scripts directory\n")
    answers = [preserve_in(run_cli, subject, monkeypatch, where, "409", "3", "develop-green", "1", "reject")
               for where in (scripts, scripts / "tests")]
    refs = git_in(decoy, "for-each-ref", "--format=%(refname)", "refs/veri").stdout
    assert answers == [(2, "", expected), (2, "", expected)]
    assert (refs, attempts(decoy), (decoy / ".tdd" / "issue-409.md").read_text()) == ("", [], ledger_before)


@pytest.mark.process("real git refusing a directory that is not a work tree")
def test_outside_a_work_tree_with_a_mark_exits_2_and_writes_no_attempts_entry_copy_or_ref(
        tmp_path, monkeypatch, run_cli, preserve_attempt):
    outside = tmp_path / "outside"
    outside.mkdir()
    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", str(tmp_path))
    leaf_output(outside, "leaf log", "leaf output")

    def tree():
        return sorted(str(p.relative_to(outside)) for p in outside.rglob("*"))

    before = tree()
    code, out, err = preserve_in(run_cli, preserve_attempt, monkeypatch, outside,
                                 "409", "3", "develop-green", "1", "reject")
    assert (code, out, err) == (2, "", "preserve-attempt.sh: not in a git work tree\n")
    assert attempts(outside) == []
    assert tree() == before
    assert not (outside / ".git").exists()


@pytest.mark.process("real git repository with an unborn HEAD")
def test_exits_2_when_the_repository_has_an_unborn_head(tmp_path, monkeypatch, run_cli, preserve_attempt):
    repo = tmp_path / "unborn"
    repo.mkdir()
    git_in(repo, "init", "-q", "-b", "main")
    (repo / "stop-run.sh").write_text(REJECTED + "\n")
    code, out, err = preserve_in(run_cli, preserve_attempt, monkeypatch, repo, "409", "3", "develop-green", "1")
    assert code == 2


@pytest.mark.process("real symlinked shim run from a subdirectory of another repository")
def test_preserves_the_same_ref_tree_and_exit_code_through_a_symlink_to_the_skill_from_a_subdirectory(
        tmp_path, monkeypatch, run_cli, preserve_attempt):
    skill = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(preserve_attempt.__file__))))
    link = tmp_path / "skill-link"
    link.symlink_to(skill)
    inplace = dirty_repo(tmp_path / "inplace")
    linked = dirty_repo(tmp_path / "linked")
    for repo in (inplace, linked):
        (repo / "sub").mkdir()
        (repo / "sub" / "nested.txt").write_text("nested\n")
    code_inplace, _, _ = preserve_in(run_cli, preserve_attempt, monkeypatch, inplace,
                                     "409", "3", "develop-green", "1")
    ran = subprocess.run([str(link / "scripts" / "preserve-attempt.sh"), "409", "3", "develop-green", "1"],
                         cwd=linked / "sub", capture_output=True, text=True, env={**os.environ, **IDENT})
    tree_inplace = git_in(inplace, "rev-parse", "--verify", "--quiet", REF + "^{tree}").stdout.strip()
    tree_linked = git_in(linked, "rev-parse", "--verify", "--quiet", REF + "^{tree}").stdout.strip()
    assert (ran.returncode, code_inplace) == (0, 0)
    assert tree_inplace and tree_linked == tree_inplace


@pytest.mark.process("real git repository and git check-ref-format")
def test_makes_one_ref_git_accepts_for_a_step_holding_multi_byte_characters_a_slash_an_apostrophe_and_spaces(
        tmp_path, monkeypatch, run_cli, preserve_attempt):
    repo = dirty_repo(tmp_path / "repo")
    code, out, err = preserve_in(run_cli, preserve_attempt, monkeypatch, repo,
                                 "409", "a—b ⟦x⟧/c'd e", "develop-green", "1")
    made = git_in(repo, "for-each-ref", "--format=%(refname)", "refs/veri/attempts/409/").stdout.split("\n")[:-1]
    legal = [git_in(repo, "check-ref-format", ref).returncode == 0 for ref in made]
    assert (code, len(made), legal) == (0, 1, [True])


def tracked_ignored_repo(root):
    committed_repo(root)
    (root / "t.txt").write_text("committed\n")
    (root / "gone.txt").write_text("committed\n")
    git_in(root, "add", "t.txt", "gone.txt")
    git_in(root, "commit", "-q", "-m", "track t.txt and gone.txt")
    return root


@pytest.mark.process("real git repository and its side ref")
def test_keeps_a_file_tracked_in_head_and_matched_by_gitignore_in_the_preserved_tree_with_its_worktree_content(
        tmp_path, monkeypatch, run_cli, preserve_attempt):
    repo = tracked_ignored_repo(tmp_path / "repo")
    (repo / ".gitignore").write_text("t.txt\n")
    (repo / "t.txt").write_text("edited by the leaf\n")
    code, out, err = preserve_in(run_cli, preserve_attempt, monkeypatch, repo, "409", "3", "develop-green", "1")
    shown = git_in(repo, "show", f"{REF}:t.txt").stdout.rstrip("\n")
    assert (code, shown) == (0, "edited by the leaf")


@pytest.mark.process("real git repository and its side ref")
def test_beside_a_tracked_ignored_file_leaves_an_untracked_ignored_and_a_deleted_tracked_file_out_and_keeps_an_untracked_one(
        tmp_path, monkeypatch, run_cli, preserve_attempt):
    repo = tracked_ignored_repo(tmp_path / "repo")
    (repo / ".gitignore").write_text("t.txt\nscratch.log\n")
    (repo / "scratch.log").write_text("ignored\n")
    (repo / "fresh.txt").write_text("new\n")
    (repo / "gone.txt").unlink()
    code, out, err = preserve_in(run_cli, preserve_attempt, monkeypatch, repo, "409", "3", "develop-green", "1")
    listed = git_in(repo, "ls-tree", "--name-only", REF).stdout.split()
    assert (code, listed) == (0, [".gitignore", "fresh.txt", "stop-run.sh", "t.txt"])


@pytest.mark.process("real git repository and its index")
def test_leaves_the_callers_index_head_and_branch_untouched_when_the_worktree_holds_a_tracked_ignored_file(
        tmp_path, monkeypatch, run_cli, preserve_attempt):
    repo = tracked_ignored_repo(tmp_path / "repo")
    (repo / ".gitignore").write_text("t.txt\n")
    (repo / "t.txt").write_text("edited by the leaf\n")
    (repo / "staged.txt").write_text("staged\n")
    git_in(repo, "add", "staged.txt")

    def state():
        return (git_in(repo, "rev-parse", "HEAD").stdout, git_in(repo, "symbolic-ref", "HEAD").stdout,
                git_in(repo, "ls-files", "-s").stdout)

    before = state()
    code, out, err = preserve_in(run_cli, preserve_attempt, monkeypatch, repo, "409", "3", "develop-green", "1")
    assert (code, state()) == (0, before)


def no_identity(monkeypatch, tmp_path):
    for name in (*IDENT, "EMAIL"):
        monkeypatch.delenv(name, raising=False)
    config = tmp_path / "noidentity.gitconfig"
    config.write_text("[user]\n\tuseConfigOnly = true\n")
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(config))
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")


@pytest.mark.process("real git repository with no identity in any git config")
def test_writes_the_ref_and_exits_0_with_no_user_name_or_email_in_any_git_config(
        tmp_path, monkeypatch, run_cli, preserve_attempt):
    repo = dirty_repo(tmp_path / "repo")
    no_identity(monkeypatch, tmp_path)
    code, out, err = run_cli(preserve_attempt, ["409", "3", "develop-green", "1"], cwd=repo)
    assert (code, ref_resolves(repo)) == (0, True)


@pytest.mark.process("real git repository with no identity in any git config")
def test_copies_the_leafs_log_and_output_for_a_mark_with_no_user_name_or_email_in_any_git_config(
        tmp_path, monkeypatch, run_cli, preserve_attempt):
    repo = dirty_repo(tmp_path / "repo")
    leaf_output(repo, "streamed progress", "final result text")
    no_identity(monkeypatch, tmp_path)
    code, out, err = run_cli(preserve_attempt, ["409", "3", "develop-green", "1", "reject"], cwd=repo)
    copies = repo / ".tdd" / "attempts"
    assert (copies / "3-develop-green-1-reject.log").read_text() == "streamed progress\n"
    assert (copies / "3-develop-green-1-reject.out").read_text() == "final result text\n"
