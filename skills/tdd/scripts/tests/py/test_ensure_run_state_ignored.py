"""In-process cases for veri/ensure_run_state_ignored.py, the module ensure-run-state-ignored.sh is a shim over."""
import importlib
import pathlib
import shutil
import subprocess

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
RULE = ".tdd/*\n!.tdd/issue-*.md\n.tdd/issue-*-spec.md\n"


@pytest.fixture
def ensure_run_state_ignored():
    return importlib.import_module("veri.ensure_run_state_ignored")


def fake_rev_parse(monkeypatch, code, stdout):
    """subprocess.run answering `git -C <root> rev-parse --git-common-dir` with <code> and <stdout>."""
    def fake_run(args, **kwargs):
        if list(args[:2]) != ["git", "-C"] or list(args[3:]) != ["rev-parse", "--git-common-dir"]:
            raise AssertionError("unexpected command: %r" % (args,))
        captured = stdout if kwargs.get("stdout") == subprocess.PIPE else None
        if captured is not None and not kwargs.get("text"):
            captured = captured.encode()
        return subprocess.CompletedProcess(args, code, captured, None)

    monkeypatch.setattr(subprocess, "run", fake_run)


def test_main_adds_the_rule_to_both_files_and_returns_2_when_rev_parse_fails(tmp_path, monkeypatch, capsys,
                                                                              ensure_run_state_ignored):
    root = tmp_path / "repo"
    (root / ".git").mkdir(parents=True)
    fake_rev_parse(monkeypatch, 0, ".git\n")

    code = ensure_run_state_ignored.main([str(root)])

    assert (code, capsys.readouterr()[:]) == (0, ("added\n", ""))
    assert (root / ".gitignore").read_text() == RULE
    assert (root / ".git" / "info" / "exclude").read_text() == RULE

    broken = tmp_path / "broken"
    (broken / ".git").mkdir(parents=True)
    fake_rev_parse(monkeypatch, 128, "")

    assert ensure_run_state_ignored.main([str(broken)]) == 2
    assert not (broken / ".gitignore").exists()
    assert not (broken / ".git" / "info" / "exclude").exists()


def test_main_does_not_refuse_a_gitignore_holding_other_lines_but_not_the_spec_line(tmp_path, monkeypatch, capsys,
                                                                                     ensure_run_state_ignored):
    fake_rev_parse(monkeypatch, 0, ".git\n")
    for name, original in (("node_modules", b"node_modules/\n"), ("non_utf8", b"\xff\xfe\n")):
        root = tmp_path / name
        (root / ".git").mkdir(parents=True)
        (root / ".gitignore").write_bytes(original)

        code = ensure_run_state_ignored.main([str(root)])

        assert (code, capsys.readouterr()[:]) == (0, ("added\n", ""))
        assert (root / ".gitignore").read_bytes() == original + RULE.encode()


def test_main_refuses_a_gitignore_holding_only_the_spec_line(tmp_path, monkeypatch, capsys, ensure_run_state_ignored):
    root = tmp_path / "repo"
    (root / ".git" / "info").mkdir(parents=True)
    (root / ".gitignore").write_bytes(b".tdd/issue-*-spec.md\n")
    (root / ".git" / "info" / "exclude").write_bytes(b"")
    fake_rev_parse(monkeypatch, 0, ".git\n")

    code = ensure_run_state_ignored.main([str(root)])

    assert (code, capsys.readouterr()[:]) == (2, ("", "ensure-run-state-ignored: %s/.gitignore carries veri's run-state "
                                                      "rule only in part, or with its lines out of order — fix it by "
                                                      "hand\n" % root))
    assert (root / ".gitignore").read_bytes() == b".tdd/issue-*-spec.md\n"
    assert (root / ".git" / "info" / "exclude").read_bytes() == b""


def test_main_reports_already_present_from_the_gitignore_alone_and_leaves_both_files_on_a_second_run(
        tmp_path, monkeypatch, capsys, ensure_run_state_ignored):
    fake_rev_parse(monkeypatch, 0, ".git\n")
    root = tmp_path / "repo"
    (root / ".git").mkdir(parents=True)
    assert ensure_run_state_ignored.main([str(root)]) == 0
    capsys.readouterr()

    code = ensure_run_state_ignored.main([str(root)])

    assert (code, capsys.readouterr()[:]) == (0, ("already present\n", ""))
    assert (root / ".gitignore").read_text() == RULE
    assert (root / ".git" / "info" / "exclude").read_text() == RULE

    carried = tmp_path / "carried"
    (carried / ".git" / "info").mkdir(parents=True)
    (carried / ".gitignore").write_text(RULE)
    (carried / ".git" / "info" / "exclude").write_text("")

    code = ensure_run_state_ignored.main([str(carried)])

    assert (code, capsys.readouterr()[:]) == (0, ("already present\n", ""))
    assert (carried / ".gitignore").read_text() == RULE
    assert (carried / ".git" / "info" / "exclude").read_text() == RULE


def test_main_appends_after_a_newline_only_where_one_is_missing_and_refuses_a_misordered_rule(
        tmp_path, monkeypatch, capsys, ensure_run_state_ignored):
    fake_rev_parse(monkeypatch, 0, ".git\n")
    appended = (
        ("newline_terminated", b"node_modules/\n", b"node_modules/\n"),
        ("misordered", b".tdd/*\n.tdd/issue-*-spec.md\n!.tdd/issue-*.md\n", None),
        ("no_trailing_newline", b"node_modules/", b"node_modules/\n"),
        ("crlf", b"node_modules/\r\n", b"node_modules/\r\n"),
        ("empty", b"", b""),
        ("trailing_space", b".tdd/*\n!.tdd/issue-*.md\n.tdd/issue-*-spec.md \n",
         b".tdd/*\n!.tdd/issue-*.md\n.tdd/issue-*-spec.md \n"),
        ("trailing_cr", b".tdd/*\r\n!.tdd/issue-*.md\r\n.tdd/issue-*-spec.md\r\n",
         b".tdd/*\r\n!.tdd/issue-*.md\r\n.tdd/issue-*-spec.md\r\n"),
        ("ignore_all_only", b".tdd/*\n", b".tdd/*\n"),
    )
    for name, original, before_rule in appended:
        root = tmp_path / name
        (root / ".git").mkdir(parents=True)
        (root / ".gitignore").write_bytes(original)
        if before_rule is None:
            (root / ".git" / "info").mkdir()
            (root / ".git" / "info" / "exclude").write_bytes(b"")

        code = ensure_run_state_ignored.main([str(root)])

        if before_rule is None:
            assert (name, code, capsys.readouterr()[:]) == (name, 2, (
                "", "ensure-run-state-ignored: %s/.gitignore carries veri's run-state rule only in part, or with its "
                    "lines out of order — fix it by hand\n" % root))
            assert (root / ".gitignore").read_bytes() == original
            assert (root / ".git" / "info" / "exclude").read_bytes() == b""
        else:
            assert (name, code, capsys.readouterr()[:]) == (name, 0, ("added\n", ""))
            assert (name, (root / ".gitignore").read_bytes()) == (name, before_rule + RULE.encode())
            assert (name, (root / ".git" / "info" / "exclude").read_bytes()) == (name, RULE.encode())


def test_main_builds_paths_by_concatenation_checks_gitignore_then_exclude_and_writes_exclude_first(
        tmp_path, monkeypatch, capsys, ensure_run_state_ignored):
    refusal = ("ensure-run-state-ignored: %s carries veri's run-state rule only in part, or with its lines out of "
               "order — fix it by hand\n")
    roots = []

    def answer(stdout):
        fake_rev_parse(monkeypatch, 0, stdout)
        faked = subprocess.run
        monkeypatch.setattr(subprocess, "run", lambda args, **kwargs: (roots.append(args[2]), faked(args, **kwargs))[1])

    monkeypatch.chdir(tmp_path)
    common = tmp_path / "common"
    (common / "info").mkdir(parents=True)
    (common / "info" / "exclude").write_bytes(b".tdd/issue-*-spec.md\n")
    pathlib.Path("a").mkdir()
    answer(str(common) + "\n")
    assert (ensure_run_state_ignored.main(["a"]), capsys.readouterr()[:]) == (2, ("", refusal % (str(common) +
                                                                                                "/info/exclude")))
    assert not pathlib.Path("a/.gitignore").exists()

    pathlib.Path("r/sub").mkdir(parents=True)
    pathlib.Path("r/.git/info").mkdir(parents=True)
    pathlib.Path("r/.git/info/exclude").write_bytes(b".tdd/issue-*-spec.md\n")
    pathlib.Path("r/.gitignore").write_bytes(b".tdd/issue-*-spec.md\n")
    answer(".git\n")
    assert (ensure_run_state_ignored.main(["r/"]), capsys.readouterr()[:]) == (2, ("", refusal % "r//.gitignore"))
    answer("../.git\n")
    assert (ensure_run_state_ignored.main(["r/sub", "--bogus", "x"]), capsys.readouterr()[:]) == (
        2, ("", refusal % "r/sub/../.git/info/exclude"))
    assert not pathlib.Path("r/sub/.gitignore").exists()
    assert pathlib.Path("r/.git/info/exclude").read_bytes() == b".tdd/issue-*-spec.md\n"

    monkeypatch.chdir(tmp_path / "r")
    answer(".git\n")
    for argv in ([""], []):
        assert (ensure_run_state_ignored.main(argv), capsys.readouterr()[:]) == (2, ("", refusal % "./.gitignore"))
    assert roots == ["a", "r/", "r/sub", ".", "."]

    monkeypatch.chdir(tmp_path)
    pathlib.Path("w/.gitignore").mkdir(parents=True)
    answer(".git\n")
    assert ensure_run_state_ignored.main(["w"]) == 2
    assert not pathlib.Path("w/.git/info/exclude").exists()

    patched = "monkeypatch.setattr(" + "ensure_run_state_ignored"
    assert patched not in pathlib.Path(__file__).read_text()


def test_main_leaves_info_exclude_byte_identical_and_returns_2_when_the_gitignore_write_fails_777(
        tmp_path, monkeypatch, capsys, ensure_run_state_ignored):
    root = tmp_path / "repo"
    (root / ".git" / "info").mkdir(parents=True)
    (root / ".git" / "info" / "exclude").write_bytes(b"*.swp\n")
    (root / ".gitignore").mkdir()
    fake_rev_parse(monkeypatch, 0, ".git\n")

    try:
        outcome = ensure_run_state_ignored.main([str(root)])
    except OSError as error:
        outcome = type(error).__name__

    assert ((root / ".git" / "info" / "exclude").read_bytes(), outcome) == (b"*.swp\n", 2)


def test_main_leaves_gitignore_byte_identical_and_fails_on_stderr_when_the_info_exclude_write_fails_777(
        tmp_path, monkeypatch, capsys, ensure_run_state_ignored):
    root = tmp_path / "repo"
    (root / ".git" / "info" / "exclude").mkdir(parents=True)
    (root / ".gitignore").write_bytes(b"node_modules/\n")
    fake_rev_parse(monkeypatch, 0, ".git\n")

    try:
        outcome = ensure_run_state_ignored.main([str(root)])
    except OSError as error:
        outcome = type(error).__name__
    stderr = capsys.readouterr().err

    assert ((root / ".gitignore").read_bytes(), isinstance(outcome, int) and outcome != 0,
            stderr.startswith("ensure-run-state-ignored: ") and "info/exclude" in stderr) == (
        b"node_modules/\n", True, True)


def test_main_leaves_no_gitignore_and_fails_on_stderr_when_there_was_none_and_the_info_exclude_write_fails_777(
        tmp_path, monkeypatch, capsys, ensure_run_state_ignored):
    root = tmp_path / "repo"
    (root / ".git" / "info" / "exclude").mkdir(parents=True)
    fake_rev_parse(monkeypatch, 0, ".git\n")

    try:
        outcome = ensure_run_state_ignored.main([str(root)])
    except OSError as error:
        outcome = type(error).__name__
    stderr = capsys.readouterr().err

    assert ((root / ".gitignore").exists(), isinstance(outcome, int) and outcome != 0,
            stderr.startswith("ensure-run-state-ignored: ") and "info/exclude" in stderr) == (
        False, True, True)


def test_main_leaves_a_gitignore_already_carrying_the_rule_byte_identical_when_the_info_exclude_write_fails_777(
        tmp_path, monkeypatch, capsys, ensure_run_state_ignored):
    root = tmp_path / "repo"
    (root / ".git" / "info" / "exclude").mkdir(parents=True)
    carried = b"node_modules/\n.tdd/*\n!.tdd/issue-*.md\n.tdd/issue-*-spec.md\n"
    (root / ".gitignore").write_bytes(carried)
    fake_rev_parse(monkeypatch, 0, ".git\n")

    try:
        outcome = ensure_run_state_ignored.main([str(root)])
    except OSError as error:
        outcome = type(error).__name__
    stderr = capsys.readouterr().err
    after = (root / ".gitignore").read_bytes() if (root / ".gitignore").exists() else None

    assert (after, isinstance(outcome, int) and outcome != 0,
            stderr.startswith("ensure-run-state-ignored: ") and "info/exclude" in stderr) == (
        carried, True, True)


def test_main_returns_2_when_the_info_exclude_write_fails_as_when_the_gitignore_write_fails_777(
        tmp_path, monkeypatch, capsys, ensure_run_state_ignored):
    root = tmp_path / "repo"
    (root / ".git" / "info" / "exclude").mkdir(parents=True)
    fake_rev_parse(monkeypatch, 0, ".git\n")

    try:
        outcome = ensure_run_state_ignored.main([str(root)])
    except OSError as error:
        outcome = type(error).__name__

    assert outcome == 2


def git(repo, *args, **kwargs):
    return subprocess.run(["git", "-C", str(repo), "-c", "user.name=veri", "-c", "user.email=veri@example.test", *args],
                          capture_output=True, text=True, **kwargs)


def make_repo(path):
    path.mkdir(parents=True)
    git(path, "init", "-q", "-b", "main")
    return path


def ignored(repo, name):
    return git(repo, "check-ignore", "-q", name).returncode


@pytest.mark.process("git: check-ignore over the .gitignore the script wrote in a real scratch repository")
def test_no_gitignore_creates_one_ignoring_the_run_log_but_not_the_ledger(tmp_path, run_cli, ensure_run_state_ignored):
    repo = make_repo(tmp_path / "fresh")

    run_cli(ensure_run_state_ignored, [str(repo)])

    assert (ignored(repo, ".tdd/develop-red.log"), ignored(repo, ".tdd/issue-7.md")) == (0, 1)


@pytest.mark.process("git: check-ignore over a .gitignore the script appended to in a real scratch repository")
def test_an_unrelated_gitignore_keeps_every_existing_line_and_reports_added(tmp_path, run_cli,
                                                                            ensure_run_state_ignored):
    repo = make_repo(tmp_path / "unrelated")
    (repo / ".gitignore").write_bytes(b"node_modules/\n*.log")

    code, out, err = run_cli(ensure_run_state_ignored, [str(repo)])

    assert (code, out) == (0, "added\n")
    assert (ignored(repo, "node_modules/x"), ignored(repo, "debug.log"), ignored(repo, ".tdd/develop-red.log"),
            ignored(repo, ".tdd/issue-7.md")) == (0, 0, 0, 1)


@pytest.mark.process("git: the caller's checkout and a linked worktree under .tdd/wt/1, both real")
def test_the_callers_checkout_stays_clean_while_the_worktree_holding_the_rule_exists(tmp_path, run_cli,
                                                                                      ensure_run_state_ignored):
    repo = make_repo(tmp_path / "caller")
    git(repo, "commit", "-q", "--allow-empty", "-m", "initial")
    git(repo, "worktree", "add", str(repo / ".tdd" / "wt" / "1"), "-b", "tdd/1")
    wt = repo / ".tdd" / "wt" / "1"

    run_cli(ensure_run_state_ignored, [str(wt)])
    git(wt, "add", ".gitignore")
    git(wt, "commit", "-q", "-m", "chore: ignore veri run state (#1)")

    assert (git(repo, "status", "--porcelain").stdout, wt.is_dir()) == ("", True)


@pytest.mark.process("git: check-ignore in a real worktree whose common directory also carries the rule")
def test_a_worktree_with_the_rule_in_info_exclude_too_still_ignores_the_run_log_and_not_the_ledger(
        tmp_path, run_cli, ensure_run_state_ignored):
    repo = make_repo(tmp_path / "caller")
    git(repo, "commit", "-q", "--allow-empty", "-m", "initial")
    git(repo, "worktree", "add", str(repo / ".tdd" / "wt" / "1"), "-b", "tdd/1")
    wt = repo / ".tdd" / "wt" / "1"

    run_cli(ensure_run_state_ignored, [str(wt)])
    git(wt, "add", ".gitignore")
    git(wt, "commit", "-q", "-m", "chore: ignore veri run state (#1)")

    assert (ignored(wt, ".tdd/develop-red.log"), ignored(wt, ".tdd/issue-1.md")) == (0, 1)


@pytest.mark.process("git: rev-parse run for real outside any repository, its own diagnostic on stderr")
def test_not_a_git_repository_exits_2_prints_nothing_on_stdout_and_lets_gits_own_diagnostic_through(
        tmp_path, monkeypatch, run_cli, ensure_run_state_ignored):
    target = tmp_path / "not-a-repo"
    target.mkdir()
    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", str(tmp_path))
    want = subprocess.run(["git", "-C", str(target), "rev-parse", "--git-common-dir"], capture_output=True,
                          text=True).stderr

    code, out, err = run_cli(ensure_run_state_ignored, [str(target)])

    assert want != ""
    assert (code, out, err) == (2, "", want)


def test_a_gitignore_that_is_a_directory_exits_2_says_why_on_stderr_and_leaves_info_exclude_unchanged(
        tmp_path, monkeypatch, run_cli, ensure_run_state_ignored):
    root = tmp_path / "repo"
    (root / ".git" / "info").mkdir(parents=True)
    (root / ".git" / "info" / "exclude").write_bytes(b"*.swp\n")
    (root / ".gitignore").mkdir()
    fake_rev_parse(monkeypatch, 0, ".git\n")

    code, out, err = run_cli(ensure_run_state_ignored, [str(root)])

    assert (code, out, err != "") == (2, "", True)
    assert (root / ".git" / "info" / "exclude").read_bytes() == b"*.swp\n"


@pytest.mark.process("ensure-run-state-ignored.sh run as a real process through a symlink to the skill directory")
def test_a_run_through_a_symlink_to_the_skill_directory_from_another_directory_answers_as_in_place(tmp_path):
    (tmp_path / "linked-skill").symlink_to(SCRIPTS.parent, target_is_directory=True)
    in_place = make_repo(tmp_path / "in-place")
    linked = make_repo(tmp_path / "linked")

    ran_in_place = subprocess.run([str(SCRIPTS / "ensure-run-state-ignored.sh")], cwd=in_place,
                                  capture_output=True, text=True)
    ran_linked = subprocess.run([str(tmp_path / "linked-skill" / "scripts" / "ensure-run-state-ignored.sh")],
                                cwd=linked, capture_output=True, text=True)

    assert (ran_in_place.returncode, ran_in_place.stdout, ran_in_place.stderr) == (0, "added\n", "")
    assert (ran_linked.returncode, ran_linked.stdout, ran_linked.stderr) == (0, "added\n", "")
    assert (linked / ".gitignore").read_bytes() == (in_place / ".gitignore").read_bytes()


@pytest.mark.process("a mutated ensure-run-state-ignored.sh run as a real process from its own directory beside a decoy repository")
@pytest.mark.tree_audit("copies the skill's veri/ module directory into a decoy tree")
def test_1158_a_shim_that_drops_its_root_argument_and_runs_from_its_own_directory_writes_nothing_outside_the_scratch_repository(
        tmp_path):
    repo = make_repo(tmp_path / "pinned-scratch")
    decoy = make_repo(tmp_path / "decoy")
    exclude_before = (decoy / ".git" / "info" / "exclude").read_bytes()
    mutant = decoy / "skills" / "tdd" / "scripts"
    mutant.mkdir(parents=True)
    shutil.copytree(SCRIPTS / "veri", mutant / "veri", ignore=shutil.ignore_patterns("__pycache__"))
    lines = []
    for line in (SCRIPTS / "ensure-run-state-ignored.sh").read_text().splitlines():
        if line.startswith("exec python3"):
            lines.append('cd "$(dirname "$0")"')
            line = line.replace(' "$@"', "")
        lines.append(line)
    (mutant / "ensure-run-state-ignored.sh").write_text("\n".join(lines) + "\n")
    (mutant / "ensure-run-state-ignored.sh").chmod(0o755)

    ran = subprocess.run([str(mutant / "ensure-run-state-ignored.sh"), str(repo)], capture_output=True, text=True)

    assert not (decoy / ".gitignore").exists()
    assert not (mutant / ".gitignore").exists()
    assert (decoy / ".git" / "info" / "exclude").read_bytes() == exclude_before
    if ran.returncode == 0:
        assert ignored(repo, ".tdd/develop-red.log") == 0
    else:
        assert not (repo / ".gitignore").exists()


def test_a_symlink_beside_no_scripts_still_finds_the_real_scripts_directory(tmp_path):
    import importlib.util
    import os
    farm = tmp_path.resolve() / "farm" / "veri"
    farm.mkdir(parents=True)
    os.symlink(SCRIPTS / "veri" / "ensure_run_state_ignored.py", farm / "ensure_run_state_ignored.py")
    spec = importlib.util.spec_from_file_location("symlinked_ensure_run_state_ignored",
                                                  farm / "ensure_run_state_ignored.py")
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)

    assert loaded.inside_own_scripts(str(SCRIPTS)) is True
